#!/usr/bin/env python3
"""Generate CUTLASS warp-specialization timelines from a pinned source inventory.

The inventory was audited against ~/cutlass at CUTLASS_COMMIT.  ``--check``
rescans a checkout and fails when a runnable example/tutorial enters or leaves
the detected warp-specialized set.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "graphs" / "cutlass-warp-specialization"
CUTLASS_COMMIT = "2802e228"

CPP_EXAMPLES = [
    "111_hopper_ssd", "112_blackwell_ssd", "113_hopper_gemm_activation_fusion",
    "48_hopper_warp_specialized_gemm", "49_hopper_gemm_with_collective_builder",
    "50_hopper_gemm_with_epilogue_swizzle", "51_hopper_gett",
    "52_hopper_gather_scatter_fusion", "54_hopper_fp8_warp_specialized_gemm",
    "55_hopper_mixed_dtype_gemm", "56_hopper_ptr_array_batched_gemm",
    "57_hopper_grouped_gemm", "61_hopper_gemm_with_topk_and_softmax",
    "63_hopper_gemm_with_weight_prefetch", "65_distributed_gemm",
    "67_hopper_fp8_warp_specialized_gemm_with_blockwise_scaling",
    "68_hopper_fp8_warp_specialized_grouped_gemm_with_blockwise_scaling",
    "69_hopper_mixed_dtype_grouped_gemm", "70_blackwell_gemm",
    "71_blackwell_gemm_with_collective_builder", "72_blackwell_narrow_precision_gemm",
    "73_blackwell_gemm_preferred_cluster", "74_blackwell_gemm_streamk",
    "75_blackwell_grouped_gemm", "76_blackwell_conv", "77_blackwell_fmha",
    "78_blackwell_emulated_bf16x9_gemm", "79_blackwell_geforce_gemm",
    "80_blackwell_geforce_sparse_gemm", "81_blackwell_gemm_blockwise",
    "82_blackwell_distributed_gemm", "83_blackwell_sparse_gemm",
    "84_blackwell_narrow_precision_sparse_gemm", "86_blackwell_mixed_dtype_gemm",
    "87_blackwell_geforce_gemm_blockwise", "88_hopper_fmha",
    "89_sm103_fp4_ultra_gemm", "90_sm103_fp4_ultra_grouped_gemm",
    "92_blackwell_moe_gemm", "93_blackwell_low_latency_gqa",
    "95_blackwell_gemm_green_context",
]

PY_EXAMPLES = [
    "python/CuTeDSL/cute/blackwell/efc/activation_custom_epilogue_dense_gemm.py",
    "python/CuTeDSL/cute/blackwell/efc/custom_epilogue_dense_gemm.py",
    "python/CuTeDSL/cute/blackwell/efc/synthetic_custom_epilogue_dense_gemm.py",
    "python/CuTeDSL/cute/blackwell/kernel/attention/fmha/fmha.py",
    "python/CuTeDSL/cute/blackwell/kernel/attention/fmha/fmha_bwd.py",
    "python/CuTeDSL/cute/blackwell/kernel/attention/mamba2_ssd/mamba2_ssd.py",
    "python/CuTeDSL/cute/blackwell/kernel/attention/mixed_input_fmha/mixed_input_fmha_decode.py",
    "python/CuTeDSL/cute/blackwell/kernel/attention/mixed_input_fmha/mixed_input_fmha_prefill_d256.py",
    "python/CuTeDSL/cute/blackwell/kernel/attention/mixed_input_fmha/mixed_input_fmha_prefill_d512.py",
    "python/CuTeDSL/cute/blackwell/kernel/attention/mla/mla_decode_fp16.py",
    "python/CuTeDSL/cute/blackwell/kernel/attention/mla/mla_decode_fp8.py",
    "python/CuTeDSL/cute/blackwell/kernel/blockscaled_gemm/dense_blockscaled_gemm_persistent.py",
    "python/CuTeDSL/cute/blackwell/kernel/blockscaled_gemm/dense_blockscaled_gemm_persistent_amax.py",
    "python/CuTeDSL/cute/blackwell/kernel/blockscaled_gemm/dense_blockscaled_gemm_persistent_prefetch.py",
    "python/CuTeDSL/cute/blackwell/kernel/blockscaled_gemm/sm103_dense_blockscaled_gemm_persistent.py",
    "python/CuTeDSL/cute/blackwell/kernel/blockscaled_grouped_gemm/grouped_blockscaled_gemm.py",
    "python/CuTeDSL/cute/blackwell/kernel/blockscaled_grouped_gemm/sm103_grouped_blockscaled_gemm.py",
    "python/CuTeDSL/cute/blackwell/kernel/blockwise_gemm/blockwise_gemm.py",
    "python/CuTeDSL/cute/blackwell/kernel/blockwise_gemm/contiguous_grouped_gemm.py",
    "python/CuTeDSL/cute/blackwell/kernel/blockwise_gemm/masked_grouped_gemm.py",
    "python/CuTeDSL/cute/blackwell/kernel/dense_gemm/dense_gemm_alpha_beta_persistent.py",
    "python/CuTeDSL/cute/blackwell/kernel/dense_gemm/dense_gemm_persistent.py",
    "python/CuTeDSL/cute/blackwell/kernel/dense_gemm/dense_gemm_persistent_dynamic.py",
    "python/CuTeDSL/cute/blackwell/kernel/dense_gemm/dense_gemm_persistent_prefetch.py",
    "python/CuTeDSL/cute/blackwell/kernel/distributed/all_reduce_tma.py",
    "python/CuTeDSL/cute/blackwell/kernel/distributed/distributed_all_gather_gemm_blackwell.py",
    "python/CuTeDSL/cute/blackwell/kernel/distributed/distributed_gemm_all_reduce_blackwell.py",
    "python/CuTeDSL/cute/blackwell/kernel/distributed/distributed_gemm_all_reduce_lamport_blackwell.py",
    "python/CuTeDSL/cute/blackwell/kernel/distributed/distributed_gemm_all_reduce_ldxstmc_blackwell.py",
    "python/CuTeDSL/cute/blackwell/kernel/distributed/distributed_gemm_blockscaled_all_reduce_ldmcxstmc_blackwell.py",
    "python/CuTeDSL/cute/blackwell/kernel/distributed/distributed_gemm_reduce_scatter_blackwell.py",
    "python/CuTeDSL/cute/blackwell/kernel/grouped_gemm/grouped_gemm.py",
    "python/CuTeDSL/cute/blackwell/kernel/mixed_input_gemm/grouped_mixed_input_gemm.py",
    "python/CuTeDSL/cute/blackwell/kernel/mixed_input_gemm/grouped_mixed_input_gemm_acc_scale.py",
    "python/CuTeDSL/cute/blackwell/kernel/mixed_input_gemm/mixed_input_gemm.py",
    "python/CuTeDSL/cute/blackwell/kernel/moe/torch_grouped_mm.py",
    "python/CuTeDSL/cute/blackwell/kernel/moe/torch_scaled_grouped_mm.py",
    "python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/fp16_gemm_2.py",
    "python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/fp16_gemm_3.py",
    "python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/fp16_gemm_3_1.py",
    "python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/fp16_gemm_4.py",
    "python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/fp16_gemm_5.py",
    "python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/fp16_gemm_6.py",
    "python/CuTeDSL/cute/blackwell/tutorial/tutorial_tma/tma_v1.py",
    "python/CuTeDSL/cute/blackwell/tutorial/tutorial_tma/tma_v2.py",
    "python/CuTeDSL/cute/blackwell_geforce/kernel/blockscaled_gemm/dense_blockscaled_gemm_persistent_cooperative.py",
    "python/CuTeDSL/cute/blackwell_geforce/kernel/blockscaled_gemm/dense_blockscaled_gemm_persistent_pingpong.py",
    "python/CuTeDSL/cute/blackwell_geforce/kernel/dense_gemm/dense_gemm.py",
    "python/CuTeDSL/cute/hopper/kernel/attention/fmha.py",
    "python/CuTeDSL/cute/hopper/kernel/dense_gemm/dense_gemm.py",
    "python/CuTeDSL/cute/hopper/kernel/dense_gemm/dense_gemm_fp8_2xacc.py",
    "python/CuTeDSL/cute/hopper/kernel/dense_gemm/dense_gemm_fp8_gelu_persistent.py",
    "python/CuTeDSL/cute/hopper/kernel/dense_gemm/dense_gemm_persistent.py",
    "python/CuTeDSL/cute/hopper/kernel/grouped_gemm/grouped_gemm.py",
    "python/CuTeDSL/cute_ext/blackwell/dense_block_scaled_gemm.py",
    "python/CuTeDSL/cute_ext/blackwell/dense_gemm.py",
    "python/CuTeDSL/cute_ext/blackwell/dense_gemm_2sm.py",
    "python/CuTeDSL/cute_ext/blackwell/dense_gemm_cute_pipeline.py",
    "python/CuTeDSL/cute_ext/blackwell/dense_gemm_ptr_array.py",
]


def slug(source: str) -> str:
    if source in CPP_EXAMPLES:
        raw = f"cpp-{source}"
    else:
        raw = source.removeprefix("python/CuTeDSL/").removesuffix(".py")
        raw = f"python-{raw}"
    return re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")


def pretty(source: str) -> str:
    name = source if source in CPP_EXAMPLES else Path(source).stem
    return re.sub(r"[_-]+", " ", name).strip()


def category(source: str) -> str:
    s = source.lower()
    if "tutorial_tma" in s:
        return "tma"
    if "gqa" in s:
        return "gqa"
    if "distributed" in s or "all_reduce" in s or "reduce_scatter" in s:
        return "distributed"
    if "ssd" in s or "mamba" in s:
        return "blackwell-attention" if "blackwell" in s or "112_" in s else "hopper-attention"
    if any(k in s for k in ("fmha", "attention", "mla", "gqa")):
        return "hopper-attention" if "hopper" in s or "88_" in s else "blackwell-attention"
    if "hopper" in s or re.match(r"(?:cpp-)?(?:4[89]|5[0-7]|6[13789]|113)_", s):
        return "hopper-gemm"
    return "blackwell-gemm"


def focus(source: str) -> str:
    """Return the source-specific design delta visible in this example."""
    s = source.lower()
    exact = {
        "fp16_gemm_2.py": "first tutorial with separate TMA, MMA, and epilogue warps plus TMA store",
        "fp16_gemm_3.py": "static persistent tile scheduling across successive GEMM tiles",
        "fp16_gemm_3_1.py": "CLC dynamic persistent scheduling for better load balance",
        "fp16_gemm_4.py": "runtime, preferred, and fallback cluster shapes",
        "fp16_gemm_5.py": "initial and rolling TMA prefetch into L2 ahead of the load ring",
        "fp16_gemm_6.py": "programmatic dependent launch around the persistent GEMM",
        "tma_v1.py": "single-stage load → transpose → store producer-consumer chain",
        "tma_v2.py": "multi-stage load/store pipelines with a persistent scheduler",
    }
    if Path(source).name in exact:
        return exact[Path(source).name]
    rules = [
        (("fmha_bwd",), "backward-attention compute and reduction roles"),
        (("mamba2", "ssd"), "state-space recurrence with distinct load, intra/inter MMA, and preprocess roles"),
        (("mla",), "latent-attention decode with load, MMA, softmax, correction, and epilogue roles"),
        (("gqa",), "low-latency grouped-query attention with DMA-Q, DMA-KV, MMA, and epilogue warps"),
        (("decode",), "attention decode role split and persistent K/V traversal"),
        (("prefill_d256",), "mixed-input prefill at head dimension 256"),
        (("prefill_d512",), "mixed-input prefill at head dimension 512"),
        (("fmha",), "fused attention load, MMA, online-softmax, correction, and epilogue overlap"),
        (("topk_and_softmax",), "GEMM with a fused top-k and softmax output path"),
        (("activation_fusion",), "regular/grouped GEMM with fused activation or gated activation"),
        (("weight_prefetch",), "a dedicated weight-prefetch stage ahead of Hopper WGMMA"),
        (("gather_scatter",), "gather/scatter address transforms around the GEMM pipeline"),
        (("epilogue_swizzle",), "swizzled epilogue ownership and output staging"),
        (("preferred_cluster",), "preferred/fallback cluster scheduling and TMA multicast"),
        (("streamk",), "Stream-K work decomposition inside the persistent scheduler"),
        (("green_context",), "GEMM constrained to a CUDA green-context SM partition"),
        (("distributed", "all_reduce", "reduce_scatter"), "communication-fused operand or result collective overlap"),
        (("moe",), "Mixture-of-Experts grouped scheduling and expert metadata movement"),
        (("grouped",), "grouped-problem metadata scheduling across persistent tiles"),
        (("ptr_array",), "pointer-array operands selected by the producer warp"),
        (("sparse",), "structured-sparse operands and metadata staged with the mainloop"),
        (("blockscaled", "block_scaled", "blockwise", "groupwise"), "block/group scale movement alongside operands and accumulators"),
        (("amax",), "fused epilogue amax reduction alongside output conversion"),
        (("mixed_input", "mixed_dtype", "int4"), "mixed-input conversion and scale handling in the producer path"),
        (("conv",), "implicit-GEMM convolution across fprop/dgrad/wgrad variants"),
        (("2xacc",), "two FP8 accumulator sets used to increase overlap"),
        (("gelu",), "persistent Hopper GEMM with fused GELU epilogue"),
        (("pingpong",), "two consumer warp-groups alternate persistent tiles"),
        (("cooperative",), "cooperative consumer warp-group scheduling"),
        (("prefetch",), "operand prefetch added ahead of the normal stage ring"),
        (("dynamic",), "dynamic persistent tile scheduling"),
        (("fp8", "fp4", "narrow_precision"), "narrow-precision operands with scale-aware staging"),
        (("collective_builder",), "schedule and collective composition through CUTLASS builders"),
    ]
    for needles, description in rules:
        if any(needle in s for needle in needles):
            return description
    return "the source-selected persistent warp-specialized schedule and epilogue"


ARCHETYPES = {
    "blackwell-gemm": {
        "architecture": "Blackwell / SM100-family",
        "roles": [
            ("TMA / scheduler warp", "persistent producer", ["obtain work tile", "acquire operand stage", "TMA A/B (+ scales)", "commit + advance"]),
            ("MMA warp", "tcgen05 issuer", ["wait A/B ready", "allocate / address TMEM", "issue UMMA K-loop", "publish accumulator"]),
            ("Epilogue warps", "TMEM consumers", ["wait accumulator", "TMEM → registers", "fused visitor / convert", "registers → sD"]),
            ("Store / auxiliary", "overlapped retirement", ["TMA store D", "release acc stage", "rejoin scheduler ring", "drain pipeline tail"]),
        ],
        "smem": [("A stage ring", "TMA operands"), ("B stage ring", "TMA operands"), ("scales / metadata", "when enabled"), ("C / D epilogue", "load + store staging")],
        "tmem": [("accumulator stage(s)", "UMMA output"), ("scale-factor region", "block-scaled paths"), ("reused columns", "after epilogue release")],
        "note": "Exact warp IDs, stage counts, and 1-SM/2-SM ownership are selected by the example configuration.",
    },
    "hopper-gemm": {
        "architecture": "Hopper / SM90",
        "roles": [
            ("Producer warp-group", "elected TMA issuing warp", ["obtain work tile", "acquire A/B stage", "TMA A/B multicast", "commit + prefetch"]),
            ("Consumer WG0", "WGMMA + epilogue", ["wait operands", "issue WGMMA groups", "visit accumulators", "stage / store D"]),
            ("Consumer WG1", "ping-pong when selected", ["wait scheduler token", "issue next tile MMA", "handoff token", "advance tile"]),
            ("Scheduler / auxiliary", "grouped or fused work", ["decode metadata", "prefetch / gather", "fused output work", "retire persistent tile"]),
        ],
        "smem": [("A stage ring", "TMA → WGMMA"), ("B stage ring", "TMA → WGMMA"), ("metadata / scales", "variant-dependent"), ("D epilogue stages", "TMA store")],
        "tmem": [("not available on SM90", "accumulators remain in registers")],
        "note": "Producer and consumer register budgets differ; mbarriers transfer stage ownership in steady state.",
    },
    "blackwell-attention": {
        "architecture": "Blackwell attention / sequence kernel",
        "roles": [
            ("Load / scheduler warp(s)", "TMA + persistent work", ["select sequence tile", "load Q/K/V or state", "commit SMEM stages", "prefetch next tile"]),
            ("MMA warp(s)", "QK / PV or state-space MMA", ["wait operands", "issue tcgen05 MMA", "publish TMEM tile", "advance K/V stage"]),
            ("Compute warps", "softmax / preprocess", ["load TMEM fragments", "mask + row reduction", "publish scale / P", "signal correction"]),
            ("Correction / epilogue", "output ownership", ["rescale partial output", "consume PV / state", "stage final output", "TMA / vector store"]),
        ],
        "smem": [("Q / state", "resident or staged"), ("K/V stage ring", "TMA producer"), ("P / reductions", "handoff scratch"), ("output stages", "epilogue")],
        "tmem": [("score / state tiles", "MMA output"), ("output accumulators", "PV / recurrence"), ("partition varies", "head dim + mode")],
        "note": "Role counts and TMEM columns vary by forward/backward, decode/prefill, head dimension, and cluster shape.",
    },
    "gqa": {
        "architecture": "Blackwell low-latency grouped-query attention",
        "roles": [
            ("Warp 0 · DMA-Q", "single-stage TMA producer", ["load Q tile", "commit Q barrier", "publish Q ready", "advance work tile"]),
            ("Warp 1 · DMA-KV", "K then V / paged indices", ["load K (+ page index)", "commit K stage", "load V (+ next index)", "release K/V stage"]),
            ("Warp 2 · MMA", "dual-BMM tcgen05 issuer", ["allocate Acc1 / Acc2 TMEM", "BMM1: K × Q → scores", "BMM2: V × P → output", "signal TMEM consumers"]),
            ("Warps 4–7 · epilogue", "warp 3 intentionally unused", ["TMEM Acc1 → scores", "online max / sum + P", "correct TMEM Acc2", "cluster reduce + output"]),
        ],
        "smem": [("Q + K/V stages", "DMA operands"), ("S / P aliased views", "dual-BMM handoff"), ("max/sum mailboxes", "warp + cluster reduce"), ("Acc / page-index scratch", "split + paged modes")],
        "tmem": [("Acc1 columns", "BMM1 scores"), ("Acc2 columns", "BMM2 output"), ("< half capacity", "allows next-kernel overlap")],
        "note": "The paged path adds a double-buffered page-index view while preserving the same four role classes.",
    },
    "hopper-attention": {
        "architecture": "Hopper attention / sequence kernel",
        "roles": [
            ("TMA producer WG", "Q/K/V or state loads", ["select sequence tile", "acquire SMEM stage", "issue TMA loads", "commit + prefetch"]),
            ("Compute WG0", "WGMMA + online math", ["wait K/V stage", "issue QK / state MMA", "softmax / recurrence", "issue output MMA"]),
            ("Compute WG1", "overlapped consumer", ["wait role token", "consume next tile", "handoff token", "release SMEM stage"]),
            ("Epilogue / reduction", "register accumulator owner", ["finish normalization", "merge partial output", "stage result", "store + retire"]),
        ],
        "smem": [("Q / state", "resident tile"), ("K/V stage ring", "TMA → WGMMA"), ("P / reduction", "handoff scratch"), ("output stage", "store")],
        "tmem": [("not available on SM90", "scores and output live in registers / SMEM")],
        "note": "The timeline shows role ownership; exact producer and consumer warp-group counts are configuration-dependent.",
    },
    "distributed": {
        "architecture": "Blackwell distributed / communication-fused",
        "roles": [
            ("Communication warp(s)", "peer / multicast movement", ["publish local tile", "signal remote readiness", "load remote shard", "advance comm ring"]),
            ("TMA / scheduler warp", "persistent GEMM producer", ["select ready work", "acquire A/B stage", "TMA operands", "commit stage"]),
            ("MMA warp", "tcgen05 consumer", ["wait local + remote", "issue UMMA", "publish TMEM acc", "release operands"]),
            ("Epilogue / reduce warps", "collective output", ["TMEM → registers", "reduce / scatter work", "stage output", "notify completion"]),
        ],
        "smem": [("local operand ring", "TMA stages"), ("remote / signal slots", "communication"), ("reduction scratch", "collective"), ("D stages", "store")],
        "tmem": [("GEMM accumulators", "UMMA output"), ("collective fragments", "variant-dependent"), ("recycled columns", "after store")],
        "note": "Communication and compute use independent readiness signals so remote movement can overlap the persistent GEMM.",
    },
    "tma": {
        "architecture": "Blackwell CuTeDSL TMA tutorial",
        "roles": [
            ("TMA load warp", "producer", ["acquire input stage", "issue global → SMEM", "commit transaction", "advance stage"]),
            ("Transform warps", "SMEM consumers", ["wait input full", "load fragments", "apply tutorial transform", "publish output stage"]),
            ("TMA store warp", "output owner", ["wait output ready", "issue SMEM → global", "wait store complete", "release stage"]),
            ("All roles", "pipeline lifetime", ["initialize barriers", "steady-state overlap", "drain final stages", "destroy / return"]),
        ],
        "smem": [("input stage ring", "TMA load"), ("transform tile", "consumer view"), ("output stage ring", "TMA store"), ("mbarriers", "ownership")],
        "tmem": [("not used", "the tutorial demonstrates TMA + SMEM")],
        "note": "This is explicit load/transform/store warp specialization; fp16_gemm_0/1 are excluded because one elected warp is only initialization.",
    },
}


def text_block(lines: list[str], x: float, y: float) -> str:
    return "".join(
        f'<text class="box" x="{x}" y="{y + i * 24}">{escape(line)}</text>'
        for i, line in enumerate(lines)
    )


def memory_boxes(items: list[tuple[str, str]], x: int, y: int, width: int, fill: str) -> str:
    gap = 16
    cell_w = (width - gap * (len(items) - 1)) / len(items)
    parts = []
    for i, (name, note) in enumerate(items):
        cx = x + i * (cell_w + gap)
        parts += [
            f'<rect class="mem" x="{cx}" y="{y}" width="{cell_w}" height="92" rx="12" fill="{fill}"/>',
            f'<text class="mem-name" x="{cx + cell_w / 2}" y="{y + 37}">{escape(name)}</text>',
            f'<text class="mem-note" x="{cx + cell_w / 2}" y="{y + 66}">{escape(note)}</text>',
        ]
    return "".join(parts)


def render(source: str) -> str:
    spec = ARCHETYPES[category(source)]
    title = pretty(source)
    source_path = f"examples/{source}"
    row_y = [300, 490, 680, 870]
    col_x = [535, 985, 1435, 1885]
    colors = ["#d7e8f2", "#cfe9df", "#b9dfd3", "#f2d394"]
    rows = []
    for i, (role, note, actions) in enumerate(spec["roles"]):
        y = row_y[i]
        rows += [
            f'<text class="role" x="94" y="{y + 34}">{escape(role)}</text>',
            f'<text class="role-note" x="94" y="{y + 63}">{escape(note)}</text>',
        ]
        for j, action in enumerate(actions):
            x = col_x[j]
            rows += [
                f'<rect class="node" x="{x}" y="{y}" width="350" height="88" rx="12" fill="{colors[i]}"/>',
                text_block(action.split("|"), x + 175, y + 49),
            ]
            if j:
                rows.append(f'<path class="arrow" d="M{col_x[j-1] + 350} {y + 44} H{x - 3}"/>')
    for j in range(3):
        x = col_x[j] + 175
        rows.append(f'<path class="handoff" d="M{x} {row_y[j] + 88} V{row_y[j+1] - 3}"/>')
    source_focus = focus(source)
    desc = f"Warp and warp-group role timeline plus SMEM and TMEM partition for CUTLASS {source_path}. Focus: {source_focus}."
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1500" viewBox="0 0 2400 1500" role="img" aria-labelledby="title desc">
  <title id="title">CUTLASS {escape(title)} warp-specialization timeline</title>
  <desc id="desc">{escape(desc)}</desc>
  <defs>
    <style>
      text {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #172734; }}
      .title {{ font-size: 42px; font-weight: 780; }} .subtitle {{ font-size: 20px; fill: #425869; }}
      .source {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 16px; fill: #526a79; }}
      .panel {{ font-size: 18px; font-weight: 790; fill: #526a79; letter-spacing: 1.2px; }}
      .phase {{ font-size: 15px; font-weight: 720; text-anchor: middle; fill: #607887; letter-spacing: .7px; }}
      .role {{ font-size: 20px; font-weight: 750; }} .role-note {{ font-size: 16px; fill: #526a79; }}
      .box {{ font-size: 18px; font-weight: 700; text-anchor: middle; dominant-baseline: middle; }}
      .node, .mem {{ stroke: #294251; stroke-width: 1.6; }} .grid {{ stroke: #dce6ec; stroke-width: 1.2; }}
      .arrow {{ fill: none; stroke: #526d7c; stroke-width: 2.3; marker-end: url(#arrow); }}
      .handoff {{ fill: none; stroke: #b87912; stroke-width: 2.2; stroke-dasharray: 7 5; marker-end: url(#gold); }}
      .memory-label {{ font-size: 19px; font-weight: 770; }} .mem-name {{ font-size: 18px; font-weight: 740; text-anchor: middle; }}
      .mem-note {{ font-size: 15px; fill: #526a79; text-anchor: middle; }} .note {{ font-size: 17px; font-weight: 650; fill: #704b09; }}
    </style>
    <marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#526d7c"/></marker>
    <marker id="gold" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#b87912"/></marker>
  </defs>
  <rect width="2400" height="1500" fill="#f8fafb"/>
  <text class="title" x="70" y="66">CUTLASS · {escape(title)}</text>
  <text class="subtitle" x="70" y="108">{escape(spec["architecture"])} · representative steady-state role ownership and memory handoffs</text>
  <text class="source" x="70" y="145">{escape(source_path)} · audited at {CUTLASS_COMMIT}</text>
  <text class="panel" x="70" y="198">WARP / WARP-GROUP ROLE TIMELINE</text>
  <rect x="60" y="220" width="2280" height="770" rx="12" fill="#fff" stroke="#d4e0e7" stroke-width="1.5"/>
  <line class="grid" x1="490" y1="220" x2="490" y2="990"/>
  <line class="grid" x1="60" y1="460" x2="2340" y2="460"/><line class="grid" x1="60" y1="650" x2="2340" y2="650"/><line class="grid" x1="60" y1="840" x2="2340" y2="840"/>
  <text class="phase" x="710" y="276">ASSIGN / ACQUIRE</text><text class="phase" x="1160" y="276">LOAD / ISSUE</text><text class="phase" x="1610" y="276">CONSUME / HANDOFF</text><text class="phase" x="2060" y="276">PUBLISH / ADVANCE</text>
  {''.join(rows)}
  <text class="panel" x="70" y="1040">ON-CHIP MEMORY PARTITION</text>
  <rect x="60" y="1065" width="2280" height="310" rx="12" fill="#fff" stroke="#d4e0e7" stroke-width="1.5"/>
  <text class="memory-label" x="90" y="1120">SMEM</text>
  {memory_boxes(spec["smem"], 235, 1087, 2055, "#d7e8f2")}
  <text class="memory-label" x="90" y="1256">TMEM</text>
  {memory_boxes(spec["tmem"], 235, 1223, 2055, "#cfe9df")}
  <rect x="70" y="1405" width="2260" height="62" rx="11" fill="#fff7df" stroke="#b87912" stroke-width="1.5"/>
  <text class="note" x="100" y="1443">Example focus: {escape(source_focus)}. Exact IDs, stage counts, and extents remain configuration-dependent.</text>
</svg>
'''


def scan(cutlass: Path) -> tuple[list[str], list[str]]:
    examples = cutlass / "examples"
    strong = re.compile(r"warp[-_ ]speciali[sz]|WarpSpecialized", re.I)
    named_cpp_role = re.compile(
        r"\b(?:DMA(?:_[A-Z0-9]+)?|TMA(?:_[A-Z0-9]+)?|MMA|EPILOG|SOFTMAX|CORRECTION|"
        r"LOAD(?:_[A-Z0-9]+)?|COMPUTE(?:_[A-Z0-9]+)?)[A-Za-z0-9_]*_warp\b", re.I
    )
    roles = re.compile(
        r"(?:tma|mma|load|epilog|softmax|correction|sched|reduce|compute|trans|pre_\w+).*warp|"
        r"warp.*(?:tma|mma|load|epilog|softmax|correction|sched|reduce|compute|trans)", re.I
    )
    cpp = []
    for directory in sorted(examples.iterdir()):
        if not directory.is_dir() or not re.match(r"\d+_", directory.name):
            continue
        texts = "\n".join(
            p.read_text(errors="ignore")
            for p in directory.rglob("*")
            if p.suffix.lower() in {".cu", ".cuh", ".h", ".hpp", ".md"}
        )
        explicit_roles = {match.lower() for match in named_cpp_role.findall(texts)}
        if strong.search(texts) or len(explicit_roles) >= 2:
            cpp.append(directory.name)
    py = []
    for path in sorted((examples / "python" / "CuTeDSL").rglob("*.py")):
        source = path.read_text(errors="ignore")
        role_lines = {re.sub(r"\W+", " ", line.lower()).strip() for line in source.splitlines() if "warp" in line.lower() and roles.search(line)}
        role_split = len(role_lines) >= 2 and ("warp_idx" in source or "warpgroup_idx" in source)
        runnable = "__main__" in source or "@click.command" in source or "def main(" in source
        if runnable and (strong.search(source) or role_split):
            py.append(str(path.relative_to(examples)))
    return cpp, py


def check(cutlass: Path) -> None:
    actual_cpp, actual_py = scan(cutlass)
    expected = set(CPP_EXAMPLES + PY_EXAMPLES)
    actual = set(actual_cpp + actual_py)
    missing = sorted(expected - actual)
    added = sorted(actual - expected)
    commit = subprocess.check_output(["git", "-C", str(cutlass), "rev-parse", "--short", "HEAD"], text=True).strip()
    if missing or added:
        for path in missing:
            print(f"no longer detected: {path}")
        for path in added:
            print(f"newly detected: {path}")
        raise SystemExit("CUTLASS warp-specialization inventory is stale")
    print(f"inventory OK: {len(actual_cpp)} C++ examples + {len(actual_py)} Python examples/tutorials at {commit}")


def readme() -> str:
    entries = []
    for source in CPP_EXAMPLES + PY_EXAMPLES:
        kind = "tutorial" if "/tutorial/" in source else ("C++ example" if source in CPP_EXAMPLES else "Python example")
        entries.append(f"| `{source}` | [{slug(source)}.svg]({slug(source)}.svg) | {kind} |")
    return f'''# CUTLASS warp-specialized examples and tutorials

Large role-timeline diagrams for every runnable example or tutorial detected as
warp-specialized in the local CUTLASS checkout at commit `{CUTLASS_COMMIT}`.
Each figure includes an SMEM/TMEM partition; Hopper figures explicitly note that
TMEM is unavailable.

Coverage is source-auditable: `scripts/generate-cutlass-warp-specialization.py
--check ~/cutlass` rescans numbered C++ example directories and runnable
CuTeDSL Python files. Selection requires an explicit warp-specialization marker
or multiple distinct warp-role branches. Elected initialization-only warps do
not qualify. The C++ tutorial `wgmma_tma_sm90.cu` is excluded because its own
comment points to warp specialization as a more advanced strategy rather than
implementing it.

The diagrams intentionally describe role ownership and memory handoffs rather
than freezing one command-line tile shape. Notes identify configuration-dependent
stage counts, warp IDs, and memory extents.

| CUTLASS source | Diagram | Kind |
| --- | --- | --- |
{chr(10).join(entries)}

Total: **{len(CPP_EXAMPLES)} C++ examples and {len(PY_EXAMPLES)} Python
examples/tutorials ({len(CPP_EXAMPLES) + len(PY_EXAMPLES)} diagrams).**
'''


def write_if_changed(path: Path, content: str) -> None:
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", type=Path, metavar="CUTLASS", help="audit the pinned inventory against a checkout")
    args = parser.parse_args()
    if args.check:
        check(args.check.expanduser().resolve())
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for source in CPP_EXAMPLES + PY_EXAMPLES:
        write_if_changed(OUT / f"{slug(source)}.svg", render(source))
    write_if_changed(OUT / "README.md", readme())


if __name__ == "__main__":
    main()
