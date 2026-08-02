"""Render an attention kernel as phase flow, cyclic mainloop, and storage views."""

from __future__ import annotations

from html import escape
from typing import Any

from .model import resolve_point, resources_by_allocation
from .render_svg import OBJECT_COLORS


def render_attention_cycle_overview(spec: dict[str, Any]) -> str:
    """Render a reconstruction-friendly overview without forcing the loop into a line."""
    width = 3000
    page_fill = "#f8fafb"
    panel_fill = "#ffffff"
    ink = "#172734"
    muted = "#526a79"
    grid = "#dce6ec"
    edge = "#294251"
    gold = "#ad7616"

    configuration = {item["id"]: item for item in spec.get("configuration", [])}

    def display_value(value: Any) -> str:
        if isinstance(value, bool):
            return "yes" if value else "no"
        return str(value)

    config_text = "  ·  ".join(
        f'{item["label"]}: {display_value(item["value"])}'
        for item in spec.get("configuration", [])
        if item.get("display", True)
    )
    source = spec.get("sources", [{}])[0]
    source_text = source.get("label", "")
    if source.get("observed"):
        source_text += f' · inspected {source["observed"]}'

    relation_notes = []
    for relation in spec.get("storage_relations", []):
        conditions = []
        for condition in relation["when"]:
            item = configuration[condition["configuration"]]
            conditions.append(f'{item["label"]}={display_value(condition["equals"])}')
        note = f'{relation["label"]} (when {", ".join(conditions)})'
        if relation.get("alternate"):
            note += f'; alternate: {relation["alternate"]}'
        relation_notes.append(note + ".")
    notes = relation_notes + spec.get("reconstruction_notes", [])

    phase_top = 225
    phase_height = 330
    cycle_title_y = 610
    cycle_top = 635
    cycle_height = 760
    memory_title_y = 1450
    memory_top = 1475
    memory_row_h = 52
    memory_rows_top = memory_top + 82
    memory_bottom = memory_rows_top + len(spec["allocations"]) * memory_row_h + 25
    footer_top = memory_bottom + 30
    footer_height = max(116, 66 + len(notes) * 23)
    height = footer_top + footer_height + 35

    timeline = spec["timeline"]
    t0 = timeline["start"]
    t1 = timeline["end"]
    plot_x = 560
    plot_right = width - 60
    plot_width = plot_right - plot_x
    sections = timeline.get("sections", [])
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

    parts: list[str] = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{escape(spec["title"])} overview</title>
  <desc id="desc">Phase flow, repeated attention mainloop, warp-role synchronization, and physical SMEM/TMEM lifetimes.</desc>
  <defs>
    <style>
      text {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: {ink}; }}
      .title {{ font-size: 42px; font-weight: 760; }} .subtitle {{ font-size: 20px; fill: #425869; }}
      .source {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 15px; fill: #607887; }}
      .section {{ font-size: 18px; font-weight: 760; fill: {muted}; letter-spacing: 1.1px; }}
      .panel-title {{ font-size: 25px; font-weight: 760; }} .panel-note {{ font-size: 15px; fill: {muted}; }}
      .phase-title {{ font-size: 23px; font-weight: 760; }} .phase-role {{ font-size: 14px; font-weight: 720; fill: #425869; }}
      .body {{ font-size: 17px; fill: #334b59; }} .body-strong {{ font-size: 17px; font-weight: 720; }}
      .node-title {{ font-size: 20px; font-weight: 760; text-anchor: middle; }} .node-role {{ font-size: 14px; font-weight: 720; fill: #425869; text-anchor: middle; }}
      .node-detail {{ font-size: 15px; fill: #334b59; text-anchor: middle; }} .chip {{ font-size: 15px; font-weight: 700; text-anchor: middle; }}
      .edge-label {{ font-size: 13px; font-weight: 700; fill: #80570c; text-anchor: middle; paint-order: stroke; stroke: #fff; stroke-width: 5px; }}
      .memory {{ font-size: 15px; font-weight: 730; }} .extent {{ font-size: 12px; fill: #607887; }}
      .life {{ font-size: 12px; font-weight: 700; text-anchor: middle; }} .reuse {{ font-size: 10px; font-weight: 720; fill: #8a5e0c; text-anchor: middle; }}
      .phase-axis {{ font-size: 13px; font-weight: 760; fill: #425869; text-anchor: middle; letter-spacing: .7px; }}
      .foot {{ font-size: 14px; fill: #425869; }} .foot-strong {{ font-size: 15px; font-weight: 760; }}
      .panel {{ fill: {panel_fill}; stroke: #d4e0e7; stroke-width: 1.5; }}
      .node {{ stroke: {edge}; stroke-width: 1.7; }} .chip-box {{ stroke: #6e8491; stroke-width: 1.1; }}
      .flow {{ fill: none; stroke: {gold}; stroke-width: 2.6; marker-end: url(#gold); }}
      .flow-dashed {{ fill: none; stroke: {gold}; stroke-width: 2.3; stroke-dasharray: 8 6; marker-end: url(#gold); }}
      .grid {{ stroke: {grid}; stroke-width: 1.1; }} .lane {{ stroke: #e4ebef; stroke-width: 1.1; }}
      .life-box {{ stroke: {edge}; stroke-width: 1.4; }}
      .release-line {{ stroke: {gold}; stroke-width: 2; stroke-dasharray: 7 5; }}
      .release-label {{ font-size: 10px; font-weight: 720; fill: #80570c; text-anchor: end; paint-order: stroke; stroke: #fff; stroke-width: 4px; }}
    </style>
    <marker id="gold" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="{gold}"/></marker>
  </defs>
  <rect width="{width}" height="{height}" fill="{page_fill}"/>
  <text class="title" x="68" y="62">{escape(spec["title"])}</text>
  <text class="subtitle" x="68" y="98">Phase flow, cyclic mainloop, and physical storage · semantic order, not cycle time.</text>
  <text class="subtitle" x="68" y="132">{escape(spec["architecture"])} · {escape(config_text)}</text>
  <text class="source" x="68" y="164">{escape(source_text)}</text>
  <text class="section" x="68" y="205">1 · KERNEL FLOW</text>
  <rect class="panel" x="50" y="{phase_top}" width="2900" height="{phase_height}" rx="14"/>
''']

    def phase_card(x: int, width_: int, title: str, role: str, lines: list[str], fill: str) -> None:
        parts.append(f'<rect class="node" x="{x}" y="272" width="{width_}" height="220" rx="14" fill="{fill}"/>')
        parts.append(f'<text class="phase-title" x="{x + 26}" y="312">{escape(title)}</text>')
        parts.append(f'<text class="phase-role" x="{x + 26}" y="340">{escape(role)}</text>')
        for index, line in enumerate(lines):
            parts.append(f'<text class="body" x="{x + 26}" y="{374 + index * 25}">• {escape(line)}</text>')

    phase_card(90, 500, "Prologue", "load producer · warp 14", [
        "prime Kⱼ and Vⱼ",
        "load Q₀ and Q₁ once",
        "publish Q/KV ready events",
    ], "#e6f0f6")
    phase_card(690, 860, "Repeated mainloop", "one K/V iteration shown · repeat over j", [
        "Q₀/Q₁ stay resident across the sweep",
        "QK₀/QK₁ → softmax₀/softmax₁ → PV₀/PV₁",
        "prefetch Kⱼ₊₁ and Vⱼ₊₁ while current compute runs",
        "rotate the three-stage K/V ring",
    ], "#e3f1ec")
    phase_card(1650, 500, "Loop drain", "after the last QK pair", [
        "release Q₀ and Q₁",
        "finish the final PV pair",
        "complete online statistics",
    ], "#edf1f4")
    phase_card(2250, 650, "Epilogue", "correction warps 8–11 · store warp 13", [
        "TMEM O₀/O₁ → registers → sO",
        "wait for both output stages",
        "TMA store sO → GMEM",
    ], "#fff0cf")
    for x1, x2 in ((590, 690), (1550, 1650), (2150, 2250)):
        parts.append(f'<path class="flow" d="M{x1} 382 H{x2 - 8}"/>')
    parts.append('<path class="flow" d="M1465 470 C1465 520 780 520 780 470"/>')
    parts.append('<text class="edge-label" x="1120" y="523">repeat for the next K/V block</text>')

    parts += [f'''
  <text class="section" x="68" y="{cycle_title_y - 15}">2 · MAINLOOP CYCLE</text>
  <text class="panel-note" x="310" y="{cycle_title_y - 15}">Q stays pinned while K/V stages rotate; paired chips preserve Q-stage identity.</text>
  <rect class="panel" x="50" y="{cycle_top}" width="2900" height="{cycle_height}" rx="14"/>
  <text class="panel-title" x="86" y="680">iteration j</text>
  <text class="panel-note" x="86" y="707">solid arrows are readiness; dashed arrows are release or loop exit.</text>
''']

    def node(x: int, y: int, w: int, h: int, title: str, role: str, details: list[str], fill: str) -> None:
        parts.append(f'<rect class="node" x="{x}" y="{y}" width="{w}" height="{h}" rx="15" fill="{fill}"/>')
        parts.append(f'<text class="node-title" x="{x + w / 2:.1f}" y="{y + 37}">{escape(title)}</text>')
        parts.append(f'<text class="node-role" x="{x + w / 2:.1f}" y="{y + 63}">{escape(role)}</text>')
        for index, detail in enumerate(details):
            parts.append(f'<text class="node-detail" x="{x + w / 2:.1f}" y="{y + 93 + index * 23}">{escape(detail)}</text>')

    node(90, 780, 430, 310, "Pinned Q operands", "loaded once by warp 14", [
        "held until the K/V loop exits",
    ], "#e6f0f6")
    parts.append('<rect class="chip-box" x="155" y="905" width="300" height="55" rx="10" fill="#d7e8f2"/><text class="chip" x="305" y="939">Q₀ · every Q₀Kᵢ</text>')
    parts.append('<rect class="chip-box" x="155" y="972" width="300" height="55" rx="10" fill="#d7e8f2"/><text class="chip" x="305" y="1006">Q₁ · every Q₁Kᵢ</text>')

    node(650, 730, 400, 165, "Load current K/V", "warp 14 · TMA", [
        "Kⱼ / Vⱼ ready in ring slots",
        "prefetch Kⱼ₊₁ / Vⱼ₊₁",
    ], "#d7e8f2")
    node(1210, 720, 500, 185, "Issue QK₀ and QK₁", "warp 12 · tcgen05", [
        "Q₀ × Kⱼ → TMEM S₀",
        "Q₁ × Kⱼ → TMEM S₁",
    ], "#c9e6dc")
    node(1920, 710, 770, 205, "Consume scores; publish probabilities", "warps 0–3 / 4–7 · softmax stage 0 / 1", [
        "S₀/S₁: TMEM → registers · mask · max · exp",
        "registers → reused TMEM P₀/P₁",
        "publish α and P-ready barriers",
    ], "#ded7eb")
    node(2020, 1070, 570, 170, "Rescale prior O", "warps 8–11 · correction", [
        "wait for α₀/α₁",
        "TMEM O → registers; release O to PV",
    ], "#b4dccf")
    node(1250, 1060, 500, 190, "Issue PV₀ and PV₁", "warp 12 · tcgen05", [
        "P₀ × Vⱼ → accumulate O₀",
        "P₁ × Vⱼ → accumulate O₁",
        "O persists in TMEM across iterations",
    ], "#c9e6dc")
    node(650, 1075, 400, 165, "Rotate K/V ring", "pipeline_kv release", [
        "release consumed V stage",
        "advance K/V producer and consumer state",
    ], "#d7e8f2")

    parts += [
        '<path class="flow" d="M1050 812 H1202"/><text class="edge-label" x="1128" y="800">Kⱼ ready</text>',
        '<path class="flow" d="M520 912 C760 912 930 860 1202 835"/><text class="edge-label" x="850" y="882">Q₀/Q₁ reused</text>',
        '<path class="flow" d="M1710 812 H1912"/><text class="edge-label" x="1811" y="800">S₀/S₁ ready · mbar</text>',
        '<path class="flow" d="M2305 915 V1062"/><text class="edge-label" x="2398" y="995">α ready · stats barrier</text>',
        '<path class="flow" d="M2020 1155 H1758"/><text class="edge-label" x="1889" y="1142">O rescaled / reusable</text>',
        '<path class="flow" d="M2030 915 C1960 1000 1845 1080 1758 1105"/><text class="edge-label" x="1905" y="1033">P₀/P₁ ready</text>',
        '<path class="flow" d="M1250 1155 H1058"/><text class="edge-label" x="1154" y="1142">release Vⱼ</text>',
        '<path class="flow" d="M650 1160 C575 1160 575 812 642 812"/><text class="edge-label" x="568" y="986">j ← j+1</text>',
        '<path class="flow-dashed" d="M520 1045 C545 1305 1895 1320 2705 1230"/><text class="edge-label" x="1640" y="1332">loop exit: release Q₀/Q₁, drain final PV, then enter epilogue</text>',
    ]

    parts += [f'''
  <text class="section" x="68" y="{memory_title_y - 15}">3 · PHYSICAL STORAGE OVER PHASES</text>
  <text class="panel-note" x="560" y="{memory_title_y - 15}">one row is one physical allocation; adjacent bars in a row are validated aliases.</text>
  <rect class="panel" x="50" y="{memory_top}" width="2900" height="{memory_bottom - memory_top}" rx="14"/>
  <line class="grid" x1="{plot_x - 22}" y1="{memory_top}" x2="{plot_x - 22}" y2="{memory_bottom}"/>
''']

    for boundary, gap in gaps:
        before = tx(boundary, "before")
        parts.append(f'<rect x="{before:.1f}" y="{memory_top}" width="{gap:.1f}" height="{memory_bottom - memory_top}" fill="#f3f6f8"/>')
        parts.append(f'<line class="grid" x1="{before + gap:.1f}" y1="{memory_top}" x2="{before + gap:.1f}" y2="{memory_bottom}"/>')
    for section in sections:
        x1 = tx(section["start"], "after")
        x2 = tx(section["end"], "before")
        parts.append(f'<text class="phase-axis" x="{(x1 + x2) / 2:.1f}" y="{memory_top + 34}">{escape(section["label"])}</text>')
    for tick in timeline["ticks"]:
        x = tx(tick["at"])
        parts.append(f'<line class="grid" x1="{x:.1f}" y1="{memory_top + 52}" x2="{x:.1f}" y2="{memory_bottom}"/>')

    grouped = resources_by_allocation(spec)
    allocation_index = {allocation["id"]: index for index, allocation in enumerate(spec["allocations"])}
    for event in spec.get("events", []):
        affected = [
            resource for resource in spec["resources"]
            if resource["lifetime"]["until"].get("event") == event["id"]
        ]
        if event["kind"] != "release" or not affected:
            continue
        indices = [allocation_index[resource["allocation"]] for resource in affected]
        x = tx(event["at"], "before")
        y1 = memory_rows_top + min(indices) * memory_row_h - 18
        y2 = memory_rows_top + max(indices) * memory_row_h + 16
        parts.append(f'<line class="release-line" x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y2}"/>')
        parts.append(f'<text class="release-label" x="{x - 6:.1f}" y="{y1 - 5}">{escape(event["label"])}</text>')

    previous_memory = None
    for index, allocation in enumerate(spec["allocations"]):
        y = memory_rows_top + index * memory_row_h
        if index:
            parts.append(f'<line class="lane" x1="50" y1="{y - 9}" x2="2950" y2="{y - 9}"/>')
        memory = allocation["memory"].upper()
        if memory != previous_memory:
            parts.append(f'<text class="section" x="76" y="{y + 3}">{memory}</text>')
            previous_memory = memory
        parts.append(f'<text class="memory" x="150" y="{y + 3}">{escape(allocation["label"])}</text>')
        parts.append(f'<text class="extent" x="150" y="{y + 23}">{escape(allocation["extent"])}</text>')
        for resource_index, resource in enumerate(grouped[allocation["id"]]):
            start = resolve_point(spec, resource["lifetime"]["from"])
            end = resolve_point(spec, resource["lifetime"]["until"])
            x = tx(start, "after") + 3
            x2 = tx(end, "before") - 3
            w = max(48, x2 - x)
            center = x + w / 2
            fill = OBJECT_COLORS[resource["category"]]
            parts.append(f'<rect class="life-box" x="{x:.1f}" y="{y - 18}" width="{w:.1f}" height="34" rx="7" fill="{fill}"/>')
            parts.append(f'<text class="life" x="{center:.1f}" y="{y + 3}">{escape(resource["label"])}</text>')
            if resource_index:
                parts.append(f'<text class="reuse" x="{tx(start):.1f}" y="{y - 24}">REUSE</text>')

    parts.append(f'<rect x="50" y="{footer_top}" width="2900" height="{footer_height}" rx="12" fill="#fff7df" stroke="#b87912" stroke-width="1.5"/>')
    parts.append(f'<text class="foot-strong" x="76" y="{footer_top + 29}">RECONSTRUCTION NOTES</text>')
    parts.append(f'<text class="foot" x="{width - 1420}" y="{footer_top + 29}">solid = ready · dashed = release/loop exit · same row = physical alias</text>')
    for index, note in enumerate(notes):
        parts.append(f'<text class="foot" x="76" y="{footer_top + 56 + index * 23}">• {escape(note)}</text>')
    parts.append('</svg>\n')
    return "".join(parts)
