"""Render a validated kernel model as an aligned role and memory timeline."""

from __future__ import annotations

from html import escape
from textwrap import wrap
from typing import Any

from .model import resolve_point, resources_by_allocation


OP_COLORS = {
    "load": "#d7e8f2",
    "wait": "#edf1f4",
    "mma": "#c9e6dc",
    "compute": "#b4dccf",
    "transfer": "#d9d0e8",
    "store": "#f2d394",
}

OBJECT_COLORS = {
    "input": "#d7e8f2",
    "score": "#c9e6dc",
    "probability": "#b7dccc",
    "stats": "#f0dfaa",
    "output": "#d9d0e8",
    "scratch": "#e6ebee",
}


def _wrap_operation_text(value: str, width: float, font_size: float) -> list[str]:
    """Wrap an operation label to the usable width of its timeline box."""
    usable_width = max(36.0, width - 14.0)
    max_chars = max(6, int(usable_width / (font_size * 0.56)))
    return wrap(
        value,
        width=max_chars,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [value]


def render_svg(spec: dict[str, Any]) -> str:
    view = next(
        (
            item
            for item in spec.get("views", [])
            if item.get("renderer") == "reconstruction-timeline" and item.get("primary")
        ),
        {},
    )
    width = int(view.get("width", 3000))
    plot_x = 500
    plot_right = width - 75
    plot_width = plot_right - plot_x

    t0 = spec["timeline"]["start"]
    t1 = spec["timeline"]["end"]
    sections = spec["timeline"].get("sections", [])
    gaps = [
        (section["start"], section.get("gap_before", 0))
        for section in sections
        if section.get("gap_before", 0) > 0
    ]
    linear_plot_width = plot_width - sum(gap for _, gap in gaps)

    def tx(value: float, boundary_side: str = "after") -> float:
        extra = sum(
            gap
            for boundary, gap in gaps
            if boundary < value or (boundary == value and boundary_side == "after")
        )
        return plot_x + (value - t0) / (t1 - t0) * linear_plot_width + extra

    roles = {role["id"]: role for role in spec["roles"]}
    operations = {operation["id"]: operation for operation in spec["operations"]}

    # Assign overlapping operations to vertical sublanes. Most roles need one;
    # roles that interleave stages get another instead of drawing boxes on top
    # of each other.
    operation_sublane: dict[str, int] = {}
    sublane_count: dict[str, int] = {}
    for role_id in roles:
        lane_ends: list[float] = []
        role_operations = sorted(
            (operation for operation in spec["operations"] if operation["role"] == role_id),
            key=lambda operation: (operation["start"], operation["end"]),
        )
        for operation in role_operations:
            lane = next(
                (
                    index
                    for index, lane_end in enumerate(lane_ends)
                    if operation["start"] >= lane_end
                ),
                len(lane_ends),
            )
            if lane == len(lane_ends):
                lane_ends.append(operation["end"])
            else:
                lane_ends[lane] = operation["end"]
            operation_sublane[operation["id"]] = lane
        sublane_count[role_id] = max(1, len(lane_ends))

    # Assign synchronization annotations to as many horizontal tiers as each
    # role needs. Intervals use conservative text-width estimates and padding.
    handoff_label_layout: dict[str, tuple[float, int]] = {}
    label_tiers: dict[str, list[list[tuple[float, float]]]] = {
        role_id: [] for role_id in roles
    }
    for handoff in spec["handoffs"]:
        source_role = operations[handoff["from"]]["role"]
        event_x = tx(handoff["at"])
        label_width = max(
            len(handoff["label"]) * 7.5,
            len(handoff["mechanism"]) * 6.2,
        )
        label_x = min(event_x + 7, plot_right - label_width - 6)
        interval = (label_x - 6, label_x + label_width + 6)
        tiers = label_tiers[source_role]
        tier = next(
            (
                index
                for index, occupied in enumerate(tiers)
                if all(interval[1] + 12 < left or interval[0] - 12 > right for left, right in occupied)
            ),
            len(tiers),
        )
        if tier == len(tiers):
            tiers.append([])
        tiers[tier].append(interval)
        handoff_label_layout[handoff["id"]] = (label_x, tier)

    op_box_height = 92
    op_sublane_gap = 10
    role_top_padding = 18
    annotation_gap = 18
    annotation_tier_height = 31
    role_bottom_padding = 12
    role_top = 292
    role_y: dict[str, int] = {}
    next_role_y = role_top
    for role_id in roles:
        operation_height = (
            sublane_count[role_id] * op_box_height
            + (sublane_count[role_id] - 1) * op_sublane_gap
        )
        annotation_height = len(label_tiers[role_id]) * annotation_tier_height
        height_for_role = (
            role_top_padding
            + operation_height
            + (annotation_gap if annotation_height else 0)
            + annotation_height
            + role_bottom_padding
        )
        role_y[role_id] = next_role_y
        next_role_y += height_for_role
    role_bottom = next_role_y

    memory_title_y = role_bottom + 72
    memory_top = memory_title_y + 30
    memory_row_h = 66
    memory_rows_top = memory_top + 38
    memory_bottom = memory_rows_top + len(spec["allocations"]) * memory_row_h + 18
    configuration_by_id = {item["id"]: item for item in spec.get("configuration", [])}
    relation_notes = []
    for relation in spec.get("storage_relations", []):
        conditions = []
        for condition in relation["when"]:
            item = configuration_by_id[condition["configuration"]]
            value = condition["equals"]
            if isinstance(value, bool):
                value = "yes" if value else "no"
            conditions.append(f'{item["label"]}={value}')
        note = f'{relation["label"]} (when {", ".join(conditions)})'
        if relation.get("alternate"):
            note += f'; alternate: {relation["alternate"]}'
        relation_notes.append(note + ".")
    notes = relation_notes + spec.get("reconstruction_notes", [])
    footer_top = memory_bottom + 34
    footer_height = max(110, 64 + len(notes) * 23)
    height = footer_top + footer_height + 35

    def display_value(value: Any) -> str:
        if isinstance(value, bool):
            return "yes" if value else "no"
        return str(value)

    config = "  ·  ".join(
        f'{escape(item["label"])}: {escape(display_value(item["value"]))}'
        for item in spec.get("configuration", [])
        if item.get("display", True)
    )
    source = spec.get("sources", [{}])[0]
    source_text = escape(source.get("label", ""))
    if source.get("observed"):
        source_text += f' · inspected {escape(source["observed"])}'

    parts: list[str] = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{escape(spec["title"])}</title>
  <desc id="desc">{escape(spec.get("subtitle", ""))} Warp-role operations, cross-role synchronization, and aligned SMEM/TMEM lifetimes.</desc>
  <defs>
    <style>
      text {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #172734; }}
      .title {{ font-size: 42px; font-weight: 760; }} .subtitle {{ font-size: 20px; fill: #425869; }}
      .source {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 15px; fill: #607887; }}
      .section {{ font-size: 18px; font-weight: 760; fill: #526a79; letter-spacing: 1.1px; }}
      .phase {{ font-size: 13px; font-weight: 760; fill: #334b59; text-anchor: middle; letter-spacing: .8px; }}
      .axis {{ font-size: 14px; font-weight: 680; fill: #607887; text-anchor: middle; }}
      .role {{ font-size: 19px; font-weight: 740; }} .role-note {{ font-size: 15px; fill: #526a79; }}
      .op {{ font-size: 15px; font-weight: 720; text-anchor: middle; }} .op-detail {{ font-size: 12px; fill: #425869; text-anchor: middle; }}
      .handoff {{ font-size: 12px; font-weight: 700; fill: #80570c; paint-order: stroke; stroke: #f8fafb; stroke-width: 5px; stroke-linejoin: round; }}
      .handoff-mech {{ font-size: 10px; font-weight: 650; fill: #8c6a2c; paint-order: stroke; stroke: #f8fafb; stroke-width: 4px; stroke-linejoin: round; }}
      .memory {{ font-size: 16px; font-weight: 730; }} .extent {{ font-size: 13px; fill: #607887; }}
      .life {{ font-size: 14px; font-weight: 700; text-anchor: middle; }} .reuse {{ font-size: 11px; font-weight: 700; fill: #8a5e0c; text-anchor: middle; }}
      .lifecycle-event {{ fill: none; stroke: #ad7616; stroke-width: 2; stroke-dasharray: 7 5; }}
      .lifecycle-event-label {{ font-size: 11px; font-weight: 700; fill: #80570c; text-anchor: end; paint-order: stroke; stroke: #fff; stroke-width: 4px; }}
      .foot {{ font-size: 15px; fill: #425869; }} .foot-strong {{ font-size: 15px; font-weight: 720; }}
      .grid {{ stroke: #dce6ec; stroke-width: 1.2; }} .lane {{ stroke: #e4ebef; stroke-width: 1.2; }}
      .op-box, .life-box {{ stroke: #294251; stroke-width: 1.5; }}
      .ready {{ fill: none; stroke: #ad7616; stroke-width: 2.2; marker-end: url(#gold); }}
      .release {{ fill: none; stroke: #ad7616; stroke-width: 2.2; stroke-dasharray: 7 5; marker-end: url(#gold); }}
    </style>
    <marker id="gold" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#ad7616"/></marker>
    <pattern id="wait-pattern" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M-2 2L2-2M0 8L8 0M6 10L10 6" stroke="#c7d1d7" stroke-width="2"/></pattern>
  </defs>
  <rect width="{width}" height="{height}" fill="#f8fafb"/>
  <text class="title" x="68" y="62">{escape(spec["title"])}</text>
  <text class="subtitle" x="68" y="98">{escape(spec.get("subtitle", ""))}</text>
  <text class="subtitle" x="68" y="132">{escape(spec["architecture"])} · {config}</text>
  <text class="source" x="68" y="164">{source_text}</text>
  <text class="section" x="68" y="214">WARP-ROLE EXECUTION · REPRESENTATIVE STEADY STATE</text>
  <text class="axis" x="{(plot_x + plot_right) / 2}" y="214">{escape(spec["timeline"].get("label", "event order, not cycle time"))}</text>
  <rect x="50" y="230" width="{width - 100}" height="{role_bottom - 222}" rx="12" fill="#fff" stroke="#d4e0e7" stroke-width="1.5"/>
  <line class="grid" x1="{plot_x - 22}" y1="230" x2="{plot_x - 22}" y2="{role_bottom + 8}"/>
''']

    for boundary, gap in gaps:
        before = tx(boundary, "before")
        parts.append(f'<rect x="{before:.1f}" y="230" width="{gap:.1f}" height="{role_bottom - 222}" fill="#f3f6f8"/>')
        parts.append(f'<line class="grid" x1="{before + gap:.1f}" y1="230" x2="{before + gap:.1f}" y2="{role_bottom + 8}"/>')

    for section in sections:
        x1 = tx(section["start"], "after")
        x2 = tx(section["end"], "before")
        parts.append(f'<text class="phase" x="{(x1 + x2) / 2:.1f}" y="249">{escape(section["label"])}</text>')

    for tick in spec["timeline"]["ticks"]:
        x = tx(tick["at"])
        parts.append(f'<line class="grid" x1="{x:.1f}" y1="230" x2="{x:.1f}" y2="{role_bottom + 8}"/>')
        parts.append(f'<text class="axis" x="{x:.1f}" y="270">{escape(tick["label"])}</text>')

    for index, role in enumerate(spec["roles"]):
        y = role_y[role["id"]]
        if index:
            parts.append(f'<line class="lane" x1="50" y1="{y}" x2="{width - 50}" y2="{y}"/>')
        parts.append(f'<text class="role" x="76" y="{y + 39}">{escape(role["label"])} · {escape(role["warps"])}</text>')
        parts.append(f'<text class="role-note" x="76" y="{y + 65}">{escape(role["responsibility"])}</text>')

    operation_parts: list[str] = []
    op_geometry: dict[str, tuple[float, float, float, float]] = {}
    for operation in spec["operations"]:
        y = (
            role_y[operation["role"]]
            + role_top_padding
            + operation_sublane[operation["id"]] * (op_box_height + op_sublane_gap)
        )
        x = tx(operation["start"], "after") + 5
        x2 = tx(operation["end"], "before") - 5
        box_width = max(44, x2 - x)
        center = x + box_width / 2
        fill = OP_COLORS[operation["kind"]]
        if operation["kind"] == "wait":
            fill = "url(#wait-pattern)"
        operation_parts.append(
            f'<g class="operation" data-operation-id="{escape(operation["id"])}">'
        )
        operation_parts.append(f'<rect class="op-box" x="{x:.1f}" y="{y}" width="{box_width:.1f}" height="{op_box_height}" rx="10" fill="{fill}"/>')
        detail = operation.get("detail")
        label_lines = _wrap_operation_text(operation["label"], box_width, 15)
        detail_lines = _wrap_operation_text(detail, box_width, 12) if detail else []
        text_lines = [("op", line) for line in label_lines] + [
            ("op-detail", line) for line in detail_lines
        ]
        line_height = 15
        first_line_y = y + op_box_height / 2 - (len(text_lines) - 1) * line_height / 2 + 5
        for line_index, (text_class, line) in enumerate(text_lines):
            operation_parts.append(
                f'<text class="{text_class}" x="{center:.1f}" '
                f'y="{first_line_y + line_index * line_height:.1f}">{escape(line)}</text>'
            )
        operation_parts.append('</g>')
        op_geometry[operation["id"]] = (x, x + box_width, y, y + op_box_height)

    handoff_paths: list[str] = []
    handoff_labels: list[str] = []
    for handoff in spec["handoffs"]:
        event_x = tx(handoff["at"])
        source_x1, source_x2, source_top, source_bottom = op_geometry[handoff["from"]]
        target_x1, target_x2, target_top, target_bottom = op_geometry[handoff["to"]]
        source_anchor = min(max(event_x, source_x1), source_x2)
        target_anchor = min(max(event_x, target_x1), target_x2)
        if (target_top + target_bottom) / 2 > (source_top + source_bottom) / 2:
            source_y = source_bottom
            target_y = target_top
        else:
            source_y = source_top
            target_y = target_bottom
        path_class = handoff["kind"]
        handoff_paths.append(
            f'<path class="{path_class}" d="M{source_anchor:.1f} {source_y:.1f} '
            f'H{event_x:.1f} V{target_y:.1f} H{target_anchor:.1f}"/>'
        )

        source_role = operations[handoff["from"]]["role"]
        label_x, tier = handoff_label_layout[handoff["id"]]
        operation_height = (
            sublane_count[source_role] * op_box_height
            + (sublane_count[source_role] - 1) * op_sublane_gap
        )
        label_y = (
            role_y[source_role]
            + role_top_padding
            + operation_height
            + annotation_gap
            + 12
            + tier * annotation_tier_height
        )
        handoff_labels.append(
            f'<g class="handoff-annotation" data-handoff-id="{escape(handoff["id"])}">'
        )
        handoff_labels.append(
            f'<text class="handoff" x="{label_x:.1f}" y="{label_y:.1f}">'
            f'{escape(handoff["label"])}</text>'
        )
        handoff_labels.append(
            f'<text class="handoff-mech" x="{label_x:.1f}" y="{label_y + 15:.1f}">'
            f'{escape(handoff["mechanism"])}</text>'
        )
        handoff_labels.append('</g>')

    # Put connectors behind operation boxes and all labels. A long cross-role
    # path can pass through a busy lane without obscuring any operation text.
    parts.extend(handoff_paths)
    parts.extend(operation_parts)
    parts.extend(handoff_labels)

    parts += [f'''
  <text class="section" x="68" y="{memory_title_y}">ON-CHIP MEMORY LIFETIMES · SAME EVENT AXIS</text>
  <rect x="50" y="{memory_top}" width="{width - 100}" height="{memory_bottom - memory_top}" rx="12" fill="#fff" stroke="#d4e0e7" stroke-width="1.5"/>
  <line class="grid" x1="{plot_x - 22}" y1="{memory_top}" x2="{plot_x - 22}" y2="{memory_bottom}"/>
''']

    for tick in spec["timeline"]["ticks"]:
        x = tx(tick["at"])
        parts.append(f'<line class="grid" x1="{x:.1f}" y1="{memory_top}" x2="{x:.1f}" y2="{memory_bottom}"/>')

    for boundary, gap in gaps:
        before = tx(boundary, "before")
        parts.append(f'<rect x="{before:.1f}" y="{memory_top}" width="{gap:.1f}" height="{memory_bottom - memory_top}" fill="#f3f6f8"/>')
        parts.append(f'<line class="grid" x1="{before + gap:.1f}" y1="{memory_top}" x2="{before + gap:.1f}" y2="{memory_bottom}"/>')

    grouped_resources = resources_by_allocation(spec)
    allocation_index = {
        allocation["id"]: index for index, allocation in enumerate(spec["allocations"])
    }
    for event in spec.get("events", []):
        if event["kind"] != "release":
            continue
        affected = [
            resource
            for resource in spec["resources"]
            if resource["lifetime"]["until"].get("event") == event["id"]
        ]
        if not affected:
            continue
        indices = [allocation_index[resource["allocation"]] for resource in affected]
        event_x = tx(event["at"], "before")
        event_y1 = memory_rows_top + min(indices) * memory_row_h - 22
        event_y2 = memory_rows_top + max(indices) * memory_row_h + 18
        parts.append(
            f'<line class="lifecycle-event" x1="{event_x:.1f}" y1="{event_y1}" '
            f'x2="{event_x:.1f}" y2="{event_y2}"/>'
        )
        parts.append(
            f'<text class="lifecycle-event-label" x="{event_x - 7:.1f}" y="{event_y1 - 6}">'
            f'{escape(event["label"])} · {escape(event["mechanism"])}</text>'
        )
    previous_memory = None
    for index, allocation in enumerate(spec["allocations"]):
        y = memory_rows_top + index * memory_row_h
        if index:
            parts.append(f'<line class="lane" x1="50" y1="{y - 10}" x2="{width - 50}" y2="{y - 10}"/>')
        memory = allocation["memory"].upper()
        if memory != previous_memory:
            parts.append(f'<text class="section" x="76" y="{y + 5}">{memory}</text>')
            previous_memory = memory
        parts.append(f'<text class="memory" x="150" y="{y + 5}">{escape(allocation["label"])}</text>')
        parts.append(f'<text class="extent" x="150" y="{y + 28}">{escape(allocation["extent"])}</text>')
        resources = grouped_resources[allocation["id"]]
        for resource_index, resource in enumerate(resources):
            lifetime = resource["lifetime"]
            lifetime_start = resolve_point(spec, lifetime["from"])
            lifetime_end = resolve_point(spec, lifetime["until"])
            x = tx(lifetime_start, "after") + 3
            x2 = tx(lifetime_end, "before") - 3
            box_width = max(48, x2 - x)
            center = x + box_width / 2
            fill = OBJECT_COLORS[resource["category"]]
            parts.append(f'<rect class="life-box" x="{x:.1f}" y="{y - 22}" width="{box_width:.1f}" height="40" rx="8" fill="{fill}"/>')
            parts.append(f'<text class="life" x="{center:.1f}" y="{y + 3}">{escape(resource["label"])}</text>')
            if resource_index:
                boundary = tx(lifetime_start)
                parts.append(f'<text class="reuse" x="{boundary:.1f}" y="{y - 29}">REUSE</text>')

    parts.append(f'<rect x="50" y="{footer_top}" width="{width - 100}" height="{footer_height}" rx="12" fill="#fff7df" stroke="#b87912" stroke-width="1.5"/>')
    parts.append(f'<text class="foot-strong" x="76" y="{footer_top + 29}">RECONSTRUCTION NOTES</text>')
    for index, note in enumerate(notes):
        parts.append(f'<text class="foot" x="76" y="{footer_top + 55 + index * 23}">• {escape(note)}</text>')
    parts.append(f'<text class="foot" x="{width - 1350}" y="{footer_top + 29}">solid sync = ready · dashed sync = released/reusable · adjacent bars in one row = physical alias</text>')
    parts.append('</svg>\n')
    return "".join(parts)
