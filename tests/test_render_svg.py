from __future__ import annotations

import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpu_graph.model import load_spec  # noqa: E402
from gpu_graph.qa import inspect_svg  # noqa: E402
from gpu_graph.renderers import render_view  # noqa: E402


SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"


class RenderSvgQaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec(
            ROOT / "specs" / "kernels" / "flash-attention-4" / "forward-sm100.json"
        )
        self.view = self.spec["views"][0]
        self.content = render_view(self.spec, self.view)

    def _root(self) -> ElementTree.Element:
        return ElementTree.fromstring(self.content)

    def test_reference_timeline_passes_automated_svg_qa(self) -> None:
        self.assertEqual(inspect_svg(self.spec, self.view, self.content), [])

    def test_operation_collision_is_detected(self) -> None:
        root = self._root()
        groups = [
            element
            for element in root.iter(f"{SVG_NAMESPACE}g")
            if element.get("class") == "operation"
        ]
        first_rect = next(groups[0].iter(f"{SVG_NAMESPACE}rect"))
        second_rect = next(groups[1].iter(f"{SVG_NAMESPACE}rect"))
        second_rect.set("x", first_rect.get("x", "0"))
        second_rect.set("y", first_rect.get("y", "0"))

        issues = inspect_svg(
            self.spec,
            self.view,
            ElementTree.tostring(root, encoding="unicode"),
        )
        self.assertTrue(any("timeline.operation-overlap" in issue for issue in issues))

    def test_operation_text_overflow_is_detected(self) -> None:
        root = self._root()
        operation_group = next(
            element
            for element in root.iter(f"{SVG_NAMESPACE}g")
            if element.get("class") == "operation"
        )
        operation_text = next(operation_group.iter(f"{SVG_NAMESPACE}text"))
        operation_text.set("x", "0")

        issues = inspect_svg(
            self.spec,
            self.view,
            ElementTree.tostring(root, encoding="unicode"),
        )
        self.assertTrue(any("timeline.operation-text" in issue for issue in issues))

    def test_handoff_annotation_collision_is_detected(self) -> None:
        root = self._root()
        operation_group = next(
            element
            for element in root.iter(f"{SVG_NAMESPACE}g")
            if element.get("class") == "operation"
        )
        operation_rect = next(operation_group.iter(f"{SVG_NAMESPACE}rect"))
        annotation_group = next(
            element
            for element in root.iter(f"{SVG_NAMESPACE}g")
            if element.get("class") == "handoff-annotation"
        )
        annotation_text = list(annotation_group.iter(f"{SVG_NAMESPACE}text"))
        x = float(operation_rect.get("x", "0")) + 4
        y = float(operation_rect.get("y", "0")) + 24
        annotation_text[0].set("x", str(x))
        annotation_text[0].set("y", str(y))
        annotation_text[1].set("x", str(x))
        annotation_text[1].set("y", str(y + 15))

        issues = inspect_svg(
            self.spec,
            self.view,
            ElementTree.tostring(root, encoding="unicode"),
        )
        self.assertTrue(any("timeline.annotation-overlap" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
