"""Semantic validation beyond the structural JSON schema."""

from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any

from .model import resolve_point, resources_by_allocation


ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SUBSCRIPT_CHARS = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
    "+": "₊", "-": "₋", "=": "₌", "(": "₍", ")": "₎",
    "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ",
    "k": "ₖ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ",
    "r": "ᵣ", "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "x": "ₓ",
}


class SpecError(ValueError):
    """Raised when a kernel graph specification is internally inconsistent."""


def _subscript(value: str | int) -> str:
    text = str(value)
    try:
        return "".join(SUBSCRIPT_CHARS[character] for character in text)
    except KeyError as error:
        raise SpecError(f"cannot render loop index {text!r} as a subscript") from error


def _iteration_token(
    object_name: str,
    iterator: str,
    seed: int,
    position: str,
) -> str:
    if position == "seed":
        suffix = _subscript(seed)
    elif position == "current":
        suffix = _subscript(iterator)
    elif position == "next":
        suffix = _subscript(iterator) + _subscript("+1")
    else:
        suffix = _subscript(iterator) + _subscript("-1")
    return object_name + suffix


def _unique(items: list[dict[str, Any]], kind: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = item.get("id")
        if not item_id:
            raise SpecError(f"{kind} is missing an id")
        if not isinstance(item_id, str) or ID_PATTERN.fullmatch(item_id) is None:
            raise SpecError(f"invalid {kind} id: {item_id}")
        if item_id in result:
            raise SpecError(f"duplicate {kind} id: {item_id}")
        result[item_id] = item
    return result


def _validate_evidence(
    owner: str,
    evidence: list[dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    *,
    required: bool = False,
) -> None:
    if required and not evidence:
        raise SpecError(f"{owner}: source evidence is required")
    for item in evidence:
        if item.get("source") not in sources:
            raise SpecError(f'{owner}: unknown evidence source {item.get("source")}')
        if not item.get("locator") or not item.get("note"):
            raise SpecError(f"{owner}: evidence requires locator and note")


def _resolve_checked_point(
    spec: dict[str, Any],
    owner: str,
    point: dict[str, Any],
    operations: dict[str, dict[str, Any]],
    loops: dict[str, dict[str, Any]],
    events: dict[str, dict[str, Any]],
) -> float:
    reference_kinds = [kind for kind in ("timeline", "operation", "loop", "event") if kind in point]
    if len(reference_kinds) != 1:
        raise SpecError(f"{owner}: lifecycle point must contain exactly one reference")
    kind = reference_kinds[0]
    if kind == "timeline":
        if point["timeline"] not in {"start", "end"} or len(point) != 1:
            raise SpecError(f"{owner}: invalid timeline point")
    elif kind == "operation":
        if point["operation"] not in operations:
            raise SpecError(f'{owner}: unknown operation point {point["operation"]}')
        if point.get("edge") not in {"start", "end"} or len(point) != 2:
            raise SpecError(f"{owner}: operation point requires start or end edge")
    elif kind == "loop":
        if point["loop"] not in loops:
            raise SpecError(f'{owner}: unknown loop point {point["loop"]}')
        if point.get("edge") not in {"start", "end"} or len(point) != 2:
            raise SpecError(f"{owner}: loop point requires start or end edge")
    else:
        if point["event"] not in events or len(point) != 1:
            raise SpecError(f'{owner}: unknown event point {point.get("event")}')
    return resolve_point(spec, point)


def validate_spec(spec: dict[str, Any]) -> None:
    """Validate causal references, loop residency, and physical storage reuse."""
    if spec.get("schema_version") != "0.2":
        raise SpecError("schema_version must be 0.2")

    timeline = spec.get("timeline", {})
    start = timeline.get("start")
    end = timeline.get("end")
    if not isinstance(start, (int, float)) or not isinstance(end, (int, float)) or start >= end:
        raise SpecError("timeline must have numeric start < end")

    configuration = _unique(spec.get("configuration", []), "configuration entry")
    sources = _unique(spec.get("sources", []), "source")
    views = _unique(spec.get("views", []), "view")
    sections = _unique(timeline.get("sections", []), "timeline section")
    loops = _unique(spec.get("loops", []), "loop")
    events = _unique(spec.get("events", []), "event")
    roles = _unique(spec.get("roles", []), "role")
    operations = _unique(spec.get("operations", []), "operation")
    _unique(spec.get("handoffs", []), "handoff")
    allocations = _unique(spec.get("allocations", []), "allocation")
    resources = _unique(spec.get("resources", []), "resource")
    relations = _unique(spec.get("storage_relations", []), "storage relation")

    del relations  # uniqueness is the relevant global check

    primary_views = [view for view in views.values() if view.get("primary") is True]
    if len(primary_views) != 1:
        raise SpecError("exactly one view must be primary")
    view_outputs: set[str] = set()
    for view in views.values():
        output = view.get("output", "")
        path = PurePosixPath(output)
        if path.is_absolute() or not path.parts or path.parts[0] != "graphs" or ".." in path.parts:
            raise SpecError(f'{view["id"]}: view output must be a safe path below graphs/')
        if path.suffix != ".svg":
            raise SpecError(f'{view["id"]}: view output must end in .svg')
        if spec.get("topic") and (len(path.parts) < 2 or path.parts[1] != spec["topic"]):
            raise SpecError(f'{view["id"]}: view output must stay inside graphs/{spec["topic"]}/')
        if output in view_outputs:
            raise SpecError(f'{view["id"]}: duplicate view output {output}')
        view_outputs.add(output)

    previous_end = start
    for section in sorted(sections.values(), key=lambda item: item["start"]):
        if not start <= section.get("start", start - 1) < section.get("end", end + 1) <= end:
            raise SpecError(f'{section["id"]}: section lies outside the timeline')
        if section["start"] < previous_end:
            raise SpecError(f'{section["id"]}: timeline sections overlap')
        previous_end = section["end"]
    for tick in timeline.get("ticks", []):
        if not start <= tick.get("at", start - 1) <= end:
            raise SpecError("timeline tick lies outside the timeline")

    for loop in loops.values():
        section = sections.get(loop.get("section"))
        if section is None:
            raise SpecError(f'{loop["id"]}: unknown timeline section {loop.get("section")}')
        if loop.get("display") == "representative-iteration":
            indexing = loop.get("indexing", {})
            if indexing.get("mode") != "concrete-prologue-symbolic-mainloop":
                raise SpecError(f'{loop["id"]}: representative iteration requires an indexing contract')
            if not isinstance(indexing.get("seed"), int) or indexing["seed"] < 0:
                raise SpecError(f'{loop["id"]}: indexing seed must be a non-negative integer')
            if indexing.get("adjacent") not in {"previous", "next"}:
                raise SpecError(f'{loop["id"]}: indexing adjacent must be previous or next')
        _validate_evidence(loop["id"], loop.get("evidence", []), sources, required=True)

    for event in events.values():
        if not start <= event.get("at", start - 1) <= end:
            raise SpecError(f'{event["id"]}: event lies outside the timeline')
        if event.get("scope") is not None and event["scope"] not in loops:
            raise SpecError(f'{event["id"]}: unknown loop scope {event["scope"]}')
        _validate_evidence(event["id"], event.get("evidence", []), sources)

    for operation in operations.values():
        if operation.get("role") not in roles:
            raise SpecError(f'{operation["id"]}: unknown role {operation.get("role")}')
        if not start <= operation.get("start", start - 1) < operation.get("end", end + 1) <= end:
            raise SpecError(f'{operation["id"]}: operation lies outside the timeline')
        scope = operation.get("scope")
        frequency = operation.get("frequency", "once")
        if scope is not None and scope not in loops:
            raise SpecError(f'{operation["id"]}: unknown loop scope {scope}')
        if frequency in {"each-iteration", "loop-tail"} and scope is None:
            raise SpecError(f'{operation["id"]}: {frequency} requires a loop scope')
        if scope is not None:
            loop = loops[scope]
            section = sections[loop["section"]]
            if operation["start"] < section["start"] or operation["end"] > section["end"]:
                raise SpecError(f'{operation["id"]}: operation lies outside loop scope {scope}')
        iteration = operation.get("iteration")
        if iteration is not None:
            loop_id = iteration.get("loop")
            if loop_id not in loops:
                raise SpecError(f'{operation["id"]}: unknown iteration loop {loop_id}')
            loop = loops[loop_id]
            section = sections[loop["section"]]
            position = iteration.get("position")
            if position == "seed":
                if operation["end"] > section["start"] or scope is not None:
                    raise SpecError(
                        f'{operation["id"]}: seed operation must finish before loop {loop_id}'
                    )
            elif position in {"previous", "current", "next"}:
                if (
                    scope != loop_id
                    or operation["start"] < section["start"]
                    or operation["end"] > section["end"]
                ):
                    raise SpecError(
                        f'{operation["id"]}: {position} operation must stay inside loop {loop_id}'
                    )
                adjacent = loop.get("indexing", {}).get("adjacent")
                if position in {"previous", "next"} and position != adjacent:
                    raise SpecError(
                        f'{operation["id"]}: {position} conflicts with loop {loop_id} adjacent={adjacent}'
                    )
            else:
                raise SpecError(f'{operation["id"]}: invalid iteration position {position}')
            objects = iteration.get("objects")
            if not isinstance(objects, list) or not objects or not all(
                isinstance(object_name, str) and object_name for object_name in objects
            ):
                raise SpecError(f'{operation["id"]}: iteration objects must be non-empty strings')
            display_text = f'{operation.get("label", "")} {operation.get("detail", "")}'
            indexing = loop.get("indexing", {})
            for object_name in objects:
                expected = _iteration_token(
                    object_name,
                    loop["iterator"],
                    indexing["seed"],
                    position,
                )
                if expected not in display_text:
                    raise SpecError(
                        f'{operation["id"]}: label/detail must contain {expected} '
                        f'for {position} iteration'
                    )
        for access in ("reads", "writes"):
            for resource_id in operation.get(access, []):
                if resource_id not in resources:
                    raise SpecError(f'{operation["id"]}: unknown resource {resource_id} in {access}')

    for handoff in spec.get("handoffs", []):
        source = operations.get(handoff.get("from"))
        target = operations.get(handoff.get("to"))
        if source is None or target is None:
            raise SpecError(f'{handoff["id"]}: unknown operation reference')
        if source["role"] == target["role"]:
            raise SpecError(f'{handoff["id"]}: handoffs must cross role lanes')
        if not start <= handoff.get("at", start - 1) <= end:
            raise SpecError(f'{handoff["id"]}: handoff lies outside the timeline')

    resource_times: dict[str, tuple[float, float]] = {}
    for resource in resources.values():
        owner = resource["id"]
        if resource.get("allocation") not in allocations:
            raise SpecError(f'{owner}: unknown allocation {resource.get("allocation")}')
        lifetime = resource.get("lifetime", {})
        lifetime_start = _resolve_checked_point(
            spec, f"{owner}/from", lifetime.get("from", {}), operations, loops, events
        )
        lifetime_end = _resolve_checked_point(
            spec, f"{owner}/until", lifetime.get("until", {}), operations, loops, events
        )
        if not start <= lifetime_start < lifetime_end <= end:
            raise SpecError(f"{owner}: invalid resource lifetime")
        resource_times[owner] = (lifetime_start, lifetime_end)
        _validate_evidence(owner, resource.get("evidence", []), sources)

        residency = resource.get("residency")
        if residency is not None:
            loop_id = residency.get("scope")
            if residency.get("kind") != "loop" or loop_id not in loops:
                raise SpecError(f"{owner}: invalid loop residency")
            loop = loops[loop_id]
            section = sections[loop["section"]]
            if lifetime_start > section["start"] or lifetime_end < section["end"]:
                raise SpecError(f"{owner}: loop-resident resource must cover the full {loop_id} scope")
            until = lifetime.get("until", {})
            release = events.get(until.get("event")) if "event" in until else None
            if release is None or release.get("kind") != "release" or release.get("scope") != loop_id:
                raise SpecError(f"{owner}: loop residency must end at a scoped release event")
            _validate_evidence(owner, resource.get("evidence", []), sources, required=True)

        if resource.get("carry") == "next-iteration":
            scoped_loops = {
                operation.get("scope")
                for operation in operations.values()
                if owner in operation.get("writes", []) and operation.get("scope") is not None
            }
            if len(scoped_loops) != 1:
                raise SpecError(f"{owner}: next-iteration carry requires one producing loop scope")
            loop_id = next(iter(scoped_loops))
            loop = loops[loop_id]
            if lifetime_end < sections[loop["section"]]["end"]:
                raise SpecError(f"{owner}: next-iteration carry must reach the loop boundary")

    for operation in operations.values():
        for access in ("reads", "writes"):
            for resource_id in operation.get(access, []):
                lifetime_start, lifetime_end = resource_times[resource_id]
                if operation["start"] < lifetime_start or operation["end"] > lifetime_end:
                    raise SpecError(
                        f'{operation["id"]}: {access[:-1]} of {resource_id} lies outside its lifetime'
                    )

    grouped = resources_by_allocation(spec)
    for allocation_id, allocation_resources in grouped.items():
        allocation = allocations[allocation_id]
        if not allocation_resources:
            raise SpecError(f"{allocation_id}: allocation has no logical resources")
        reuse = allocation.get("reuse", {})
        if len(allocation_resources) > 1 and reuse.get("mode") != "sequential-alias":
            raise SpecError(f"{allocation_id}: multiple resources require an explicit reuse policy")
        if reuse:
            _validate_evidence(allocation_id, reuse.get("evidence", []), sources, required=True)
        for previous, current in zip(allocation_resources, allocation_resources[1:]):
            previous_end = resource_times[previous["id"]][1]
            current_start = resource_times[current["id"]][0]
            if current_start < previous_end:
                raise SpecError(
                    f'{allocation_id}: {previous["id"]} and {current["id"]} '
                    "overlap in one physical allocation"
                )

    for relation in spec.get("storage_relations", []):
        relation_resources = []
        for resource_id in relation.get("objects", []):
            if resource_id not in resources:
                raise SpecError(f'{relation["id"]}: unknown resource {resource_id}')
            relation_resources.append(resources[resource_id])
        allocation_ids = {resource["allocation"] for resource in relation_resources}
        if relation.get("kind") == "alias" and len(allocation_ids) != 1:
            raise SpecError(f'{relation["id"]}: alias assertion requires one physical allocation')
        if relation.get("kind") == "distinct" and len(allocation_ids) != len(relation_resources):
            raise SpecError(f'{relation["id"]}: distinct assertion requires separate physical allocations')
        for condition in relation.get("when", []):
            configuration_id = condition.get("configuration")
            if configuration_id not in configuration:
                raise SpecError(f'{relation["id"]}: unknown configuration {configuration_id}')
            actual = configuration[configuration_id].get("value")
            if actual != condition.get("equals"):
                raise SpecError(
                    f'{relation["id"]}: storage relation does not apply to the current configuration '
                    f'({configuration_id}={actual!r})'
                )
        _validate_evidence(relation["id"], relation.get("evidence", []), sources, required=True)
