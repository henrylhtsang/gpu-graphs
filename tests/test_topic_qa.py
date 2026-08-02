from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpu_graph.model import load_spec  # noqa: E402
from gpu_graph.qa import inspect_direct_svg  # noqa: E402
from gpu_graph.validation import SpecError, validate_topic_spec  # noqa: E402


SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"


class TopicValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec(ROOT / "specs" / "topics" / "quack-kernels.json")

    def test_reference_topic_spec_is_valid(self) -> None:
        validate_topic_spec(self.spec)

    def test_topic_requires_a_pinned_implementation_source(self) -> None:
        broken = copy.deepcopy(self.spec)
        broken["sources"][0]["kind"] = "documentation"
        with self.assertRaisesRegex(SpecError, "implementation code"):
            validate_topic_spec(broken)

    def test_topic_glob_cannot_escape_its_graph_directory(self) -> None:
        broken = copy.deepcopy(self.spec)
        broken["coverage"]["glob"] = "graphs/other-topic/**/*.svg"
        with self.assertRaisesRegex(SpecError, "coverage glob"):
            validate_topic_spec(broken)


class DirectSvgQaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec(ROOT / "specs" / "topics" / "quack-kernels.json")
        self.relative_path = Path(
            "graphs/quack-kernels/gemm-sm100-pipeline/gemm-sm100-pipeline.svg"
        )
        self.content = (ROOT / self.relative_path).read_text(encoding="utf-8")

    def _root(self) -> ElementTree.Element:
        return ElementTree.fromstring(self.content)

    def test_reference_direct_svg_passes(self) -> None:
        self.assertEqual(
            inspect_direct_svg(self.spec, self.relative_path, self.content),
            [],
        )

    def test_direct_svg_requires_llm_authorship_metadata(self) -> None:
        root = self._root()
        root.attrib.pop("data-authoring")
        issues = inspect_direct_svg(
            self.spec,
            self.relative_path,
            ElementTree.tostring(root, encoding="unicode"),
        )
        self.assertTrue(any("svg.direct-root" in issue for issue in issues))

    def test_direct_svg_requires_its_topic_semantic_classes(self) -> None:
        root = self._root()
        for element in root.iter():
            if element.get("class") == "lane":
                element.set("class", "removed-lane")
        issues = inspect_direct_svg(
            self.spec,
            self.relative_path,
            ElementTree.tostring(root, encoding="unicode"),
        )
        self.assertTrue(any("svg.semantic-class" in issue for issue in issues))

    def test_direct_svg_requires_exactly_three_phase_bands(self) -> None:
        root = self._root()
        for element in root.iter():
            if element.get("class") == "phase-band" and element.get("data-phase-id") == "epilogue":
                element.set("data-phase-id", "mainloop")
        issues = inspect_direct_svg(
            self.spec,
            self.relative_path,
            ElementTree.tostring(root, encoding="unicode"),
        )
        self.assertTrue(any("svg.three-phase" in issue for issue in issues))

    def test_direct_svg_requires_memory_lifetime_bars(self) -> None:
        root = self._root()
        for element in root.iter():
            if element.get("class") == "life-box":
                element.set("class", "removed-life-box")
        issues = inspect_direct_svg(
            self.spec,
            self.relative_path,
            ElementTree.tostring(root, encoding="unicode"),
        )
        self.assertTrue(any("svg.memory-lifetimes" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
