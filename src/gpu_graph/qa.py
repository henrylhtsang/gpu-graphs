"""Automated QA contracts for generated kernel graph artifacts."""

from __future__ import annotations

import struct
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"


@dataclass(frozen=True)
class Box:
    """An estimated visual bounding box used by collision checks."""

    item_id: str
    left: float
    top: float
    right: float
    bottom: float


def _overlaps(left: Box, right: Box) -> bool:
    return (
        min(left.right, right.right) > max(left.left, right.left)
        and min(left.bottom, right.bottom) > max(left.top, right.top)
    )


def _inside(inner: Box, outer: Box, tolerance: float = 0.5) -> bool:
    return (
        inner.left >= outer.left - tolerance
        and inner.top >= outer.top - tolerance
        and inner.right <= outer.right + tolerance
        and inner.bottom <= outer.bottom + tolerance
    )


def _rect_box(element: ElementTree.Element, item_id: str) -> Box:
    x = float(element.get("x", "0"))
    y = float(element.get("y", "0"))
    width = float(element.get("width", "0"))
    height = float(element.get("height", "0"))
    return Box(item_id, x, y, x + width, y + height)


def _class_elements(root: ElementTree.Element, tag: str, class_name: str) -> list[ElementTree.Element]:
    return [
        element
        for element in root.iter(f"{SVG_NAMESPACE}{tag}")
        if element.get("class") == class_name
    ]


def _check_pairwise_overlap(boxes: list[Box], check: str) -> list[str]:
    issues = []
    for index, left in enumerate(boxes):
        for right in boxes[index + 1 :]:
            if _overlaps(left, right):
                issues.append(f"{check}: {left.item_id} overlaps {right.item_id}")
    return issues


def _timeline_issues(
    spec: dict[str, Any],
    root: ElementTree.Element,
    canvas: Box,
) -> list[str]:
    issues: list[str] = []
    expected_operation_ids = {operation["id"] for operation in spec["operations"]}
    operation_groups = _class_elements(root, "g", "operation")
    rendered_operation_ids = {
        group.get("data-operation-id", "") for group in operation_groups
    }
    if rendered_operation_ids != expected_operation_ids:
        missing = sorted(expected_operation_ids - rendered_operation_ids)
        extra = sorted(rendered_operation_ids - expected_operation_ids)
        issues.append(
            "timeline.operation-coverage: "
            f"missing={missing or 'none'}, extra={extra or 'none'}"
        )

    operation_boxes: list[Box] = []
    for group in operation_groups:
        operation_id = group.get("data-operation-id", "unknown-operation")
        rects = _class_elements(group, "rect", "op-box")
        if len(rects) != 1:
            issues.append(
                f"timeline.operation-box: {operation_id} has {len(rects)} boxes; expected 1"
            )
            continue
        operation_box = _rect_box(rects[0], operation_id)
        operation_boxes.append(operation_box)
        if not _inside(operation_box, canvas):
            issues.append(f"timeline.canvas-bounds: {operation_id} leaves the SVG canvas")

        for text_element in group.iter(f"{SVG_NAMESPACE}text"):
            text_class = text_element.get("class")
            font_size = 15.0 if text_class == "op" else 12.0
            x = float(text_element.get("x", "0"))
            baseline = float(text_element.get("y", "0"))
            text_width = len(text_element.text or "") * font_size * 0.56
            text_box = Box(
                f"{operation_id}:{text_element.text or ''}",
                x - text_width / 2,
                baseline - font_size * 0.82,
                x + text_width / 2,
                baseline + font_size * 0.25,
            )
            if not _inside(text_box, operation_box, tolerance=1.0):
                issues.append(
                    f"timeline.operation-text: {operation_id} text "
                    f"{text_element.text!r} leaves its box"
                )

    issues.extend(_check_pairwise_overlap(operation_boxes, "timeline.operation-overlap"))

    expected_handoff_ids = {handoff["id"] for handoff in spec["handoffs"]}
    handoff_groups = _class_elements(root, "g", "handoff-annotation")
    rendered_handoff_ids = {
        group.get("data-handoff-id", "") for group in handoff_groups
    }
    if rendered_handoff_ids != expected_handoff_ids:
        missing = sorted(expected_handoff_ids - rendered_handoff_ids)
        extra = sorted(rendered_handoff_ids - expected_handoff_ids)
        issues.append(
            "timeline.handoff-coverage: "
            f"missing={missing or 'none'}, extra={extra or 'none'}"
        )

    handoff_boxes: list[Box] = []
    for group in handoff_groups:
        handoff_id = group.get("data-handoff-id", "unknown-handoff")
        labels = _class_elements(group, "text", "handoff")
        mechanisms = _class_elements(group, "text", "handoff-mech")
        if len(labels) != 1 or len(mechanisms) != 1:
            issues.append(
                f"timeline.handoff-text: {handoff_id} requires one label and one mechanism"
            )
            continue
        label = labels[0]
        mechanism = mechanisms[0]
        x = float(label.get("x", "0"))
        label_y = float(label.get("y", "0"))
        mechanism_y = float(mechanism.get("y", "0"))
        width = max(len(label.text or "") * 7.5, len(mechanism.text or "") * 6.2)
        handoff_box = Box(handoff_id, x - 2, label_y - 13, x + width + 2, mechanism_y + 3)
        handoff_boxes.append(handoff_box)
        if not _inside(handoff_box, canvas):
            issues.append(f"timeline.canvas-bounds: {handoff_id} leaves the SVG canvas")
        for operation_box in operation_boxes:
            if _overlaps(handoff_box, operation_box):
                issues.append(
                    f"timeline.annotation-overlap: {handoff_id} overlaps {operation_box.item_id}"
                )

    issues.extend(_check_pairwise_overlap(handoff_boxes, "timeline.annotation-overlap"))

    sync_paths = [
        element
        for element in root.iter(f"{SVG_NAMESPACE}path")
        if element.get("class") in {"ready", "release"}
    ]
    if len(sync_paths) != len(spec["handoffs"]):
        issues.append(
            "timeline.handoff-paths: "
            f"rendered {len(sync_paths)}, expected {len(spec['handoffs'])}"
        )

    lifetime_boxes = [
        _rect_box(element, f"lifetime-{index}")
        for index, element in enumerate(_class_elements(root, "rect", "life-box"))
    ]
    if len(lifetime_boxes) != len(spec["resources"]):
        issues.append(
            "timeline.lifetime-coverage: "
            f"rendered {len(lifetime_boxes)}, expected {len(spec['resources'])}"
        )
    issues.extend(_check_pairwise_overlap(lifetime_boxes, "timeline.lifetime-overlap"))
    return issues


def _overview_issues(
    spec: dict[str, Any],
    root: ElementTree.Element,
    canvas: Box,
) -> list[str]:
    """Apply the baseline layout contract to the cyclic overview renderer."""
    issues: list[str] = []
    nodes = [
        _rect_box(element, f"node-{index}")
        for index, element in enumerate(_class_elements(root, "rect", "node"))
    ]
    for node in nodes:
        if not _inside(node, canvas):
            issues.append(f"overview.canvas-bounds: {node.item_id} leaves the SVG canvas")
    issues.extend(_check_pairwise_overlap(nodes, "overview.node-overlap"))

    lifetime_boxes = [
        _rect_box(element, f"lifetime-{index}")
        for index, element in enumerate(_class_elements(root, "rect", "life-box"))
    ]
    if len(lifetime_boxes) != len(spec["resources"]):
        issues.append(
            "overview.lifetime-coverage: "
            f"rendered {len(lifetime_boxes)}, expected {len(spec['resources'])}"
        )
    issues.extend(_check_pairwise_overlap(lifetime_boxes, "overview.lifetime-overlap"))
    return issues


SvgQaChecker = Callable[[dict[str, Any], ElementTree.Element, Box], list[str]]

SVG_QA_CHECKERS: dict[str, SvgQaChecker] = {
    "attention-cycle-overview": _overview_issues,
    "reconstruction-timeline": _timeline_issues,
}


def inspect_svg(spec: dict[str, Any], view: dict[str, Any], content: str) -> list[str]:
    """Return actionable QA issues for one generated SVG view."""
    try:
        root = ElementTree.fromstring(content)
    except ElementTree.ParseError as error:
        return [f"svg.parse: {error}"]

    issues: list[str] = []
    if root.tag != f"{SVG_NAMESPACE}svg":
        return ["svg.root: document root is not an SVG element"]

    try:
        width = float(root.get("width", "0"))
        height = float(root.get("height", "0"))
    except ValueError:
        return ["svg.dimensions: width and height must be numeric"]
    if width < float(view.get("width", 2400)):
        issues.append(
            f"svg.width: rendered width {width:g}px is below declared width "
            f"{view.get('width', 2400)}px"
        )
    if height <= 0:
        issues.append("svg.height: rendered height must be positive")

    view_box = root.get("viewBox", "").split()
    if len(view_box) != 4:
        issues.append("svg.viewbox: viewBox must contain four numbers")
    else:
        try:
            _, _, view_width, view_height = (float(value) for value in view_box)
            if view_width != width or view_height != height:
                issues.append("svg.viewbox: viewBox dimensions must match width and height")
        except ValueError:
            issues.append("svg.viewbox: viewBox must contain numeric values")

    titles = list(root.iter(f"{SVG_NAMESPACE}title"))
    descriptions = list(root.iter(f"{SVG_NAMESPACE}desc"))
    if not titles or not (titles[0].text or "").strip():
        issues.append("svg.accessibility: missing a non-empty title")
    if not descriptions or not (descriptions[0].text or "").strip():
        issues.append("svg.accessibility: missing a non-empty description")
    if root.get("role") != "img" or not root.get("aria-labelledby"):
        issues.append("svg.accessibility: root requires role=img and aria-labelledby")

    canvas = Box("canvas", 0, 0, width, height)
    checker = SVG_QA_CHECKERS.get(view["renderer"])
    if checker is None:
        issues.append(
            f"svg.qa-contract: renderer {view['renderer']} has no registered QA checker"
        )
    else:
        issues.extend(checker(spec, root, canvas))
    return issues


def png_dimensions(path: Path) -> tuple[int, int]:
    """Read PNG dimensions from its IHDR header without external packages."""
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("not a valid PNG with an IHDR header")
    return struct.unpack(">II", data[16:24])


def inspect_png(path: Path, svg_content: str) -> list[str]:
    """Check that a PNG companion exists and matches its SVG canvas."""
    if not path.exists():
        return [f"png.missing: {path}"]
    try:
        png_width, png_height = png_dimensions(path)
    except ValueError as error:
        return [f"png.parse: {path}: {error}"]

    try:
        root = ElementTree.fromstring(svg_content)
        svg_width = int(float(root.get("width", "0")))
        svg_height = int(float(root.get("height", "0")))
    except (ElementTree.ParseError, ValueError):
        return [f"png.source: cannot read SVG dimensions for {path}"]

    if (png_width, png_height) != (svg_width, svg_height):
        return [
            "png.dimensions: "
            f"{path} is {png_width}x{png_height}, expected {svg_width}x{svg_height}"
        ]
    return []
