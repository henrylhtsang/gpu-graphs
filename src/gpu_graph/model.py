"""Loading and normalization for kernel graph specifications."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_spec(path: Path) -> dict[str, Any]:
    """Load a JSON kernel specification without applying presentation defaults."""
    return json.loads(path.read_text(encoding="utf-8"))


def index_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Index specification records by id without performing validation."""
    return {item["id"]: item for item in items}


def resolve_point(spec: dict[str, Any], point: dict[str, str]) -> float:
    """Resolve a semantic lifecycle endpoint to the shared event axis."""
    timeline = spec["timeline"]
    if "timeline" in point:
        return float(timeline[point["timeline"]])

    if "operation" in point:
        operation = index_by_id(spec["operations"])[point["operation"]]
        return float(operation[point["edge"]])

    if "loop" in point:
        loop = index_by_id(spec.get("loops", []))[point["loop"]]
        section = index_by_id(timeline.get("sections", []))[loop["section"]]
        return float(section[point["edge"]])

    if "event" in point:
        event = index_by_id(spec.get("events", []))[point["event"]]
        return float(event["at"])

    raise KeyError(f"unknown point reference: {point}")


def resources_by_allocation(spec: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Group logical resources by their physical SMEM or TMEM allocation."""
    grouped = {allocation["id"]: [] for allocation in spec["allocations"]}
    for resource in spec["resources"]:
        grouped.setdefault(resource["allocation"], []).append(resource)
    for resources in grouped.values():
        resources.sort(key=lambda resource: resolve_point(spec, resource["lifetime"]["from"]))
    return grouped
