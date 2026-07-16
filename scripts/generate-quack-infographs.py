#!/usr/bin/env python3
"""Generate the QuACK kernel swimlanes from a compact, reviewable specification."""

from pathlib import Path
from xml.sax.saxutils import escape


OUT = Path(__file__).resolve().parents[1] / "graphs" / "quack-kernels"


GRAPHS = [
    {
        "file": "softmax-forward-reduction",
        "title": "QuACK softmax forward · row/cluster reduction",
        "subtitle": "One CTA tile per row group; wide rows span a CTA cluster along N.",
        "source": "quack/softmax.py · Softmax.kernel()",
        "lanes": [
            ("Global → shared", "Vectorized, predicated cp.async", ["Tile X by row + N", "cp.async X → sX", "wait group 0", "OOB → −∞"]),
            ("Shared → registers", "FP32 working fragments", ["sX → rX", "convert to FP32", "retain exp(x−m)", "prepare output"]),
            ("Row reduction", "Warp, block, or cluster scope", ["online (max,sum)|or max pass", "cluster exchange|through mbarrier", "sum exp(x−max)", "reciprocal denom"]),
            ("Normalize + store", "Every valid lane writes its slice", ["y = exp / denom", "convert output dtype", "predicated rO → gO", "next row tile"]),
        ],
        "note": "Invariant: the same predicate covers load and store; OOB logits cannot enter max or denominator.",
    },
    {
        "file": "softmax-backward-jacobian",
        "title": "QuACK softmax backward · fused Jacobian-vector product",
        "subtitle": "The dense Jacobian is never materialized: dxᵢ = yᵢ(dyᵢ − Σⱼ dyⱼyⱼ).",
        "source": "quack/softmax.py · SoftmaxBackward.kernel()",
        "lanes": [
            ("Global → shared", "dy and saved y move together", ["Tile dy + y", "cp.async → sdY,sY", "commit + wait", "OOB zero-fill"]),
            ("Registers", "FP32 elementwise products", ["sdY,sY → rmem", "convert FP32", "pᵢ = dyᵢyᵢ", "hold dyᵢ,yᵢ"]),
            ("Row reduction", "Cluster-aware for wide N", ["Σ local pᵢ", "exchange partials", "broadcast dot", "dot ready"]),
            ("Gradient + store", "Single fused output pass", ["dyᵢ − dot", "× yᵢ", "convert dx dtype", "predicated store"]),
        ],
        "note": "Saved forward output y is sufficient; no logits, exponentials, or full Jacobian are reloaded.",
    },
    {
        "file": "top-k-forward-bitonic",
        "title": "QuACK top-k forward · bitonic select with stable ties",
        "subtitle": "Power-of-two N and k≤128; values and indices stay in registers through selection.",
        "source": "quack/topk.py · TopK.kernel()",
        "lanes": [
            ("Load + tag", "Vectorized gmem → rmem", ["Load row tile", "convert FP32", "encode index|in low bits", "OOB → −∞"]),
            ("Sorting network", "Cooperative thread group", ["local compare/swap", "warp shuffles", "bitonic_topk(k)", "thread 0 owns k"]),
            ("Redistribute", "Spread k across row threads", ["shuffle from lane 0", "extract index bits", "restore clean value", "vectorize fragments"]),
            ("Optional softmax + store", "Only selected k participate", ["max of top-k", "exp + warp sum", "normalize if enabled", "store values + indices"]),
        ],
        "note": "Tie-breaking is encoded into otherwise discarded mantissa bits so earlier columns win deterministically.",
    },
    {
        "file": "top-k-backward-scatter",
        "title": "QuACK top-k backward · sparse scatter through shared memory",
        "subtitle": "Selected gradients are transformed, scattered into a zero tile, then written densely.",
        "source": "quack/topk.py · TopKBackward.kernel()",
        "lanes": [
            ("Inputs", "k selected entries per row", ["Load dvalues", "load indices", "load values|if softmax", "zero sdX tile"]),
            ("Selected-space math", "Only k entries are active", ["plain: grad=dvalue", "softmax: Σ dv·v", "v(dv−dot)", "convert dx dtype"]),
            ("Scatter", "Indices address shared output", ["barrier after zero", "sdX[row,index]=grad", "barrier after scatter", "unselected stay zero"]),
            ("Dense output", "Coalesced full-row write", ["sdX → rmem", "apply N predicate", "vector store dx", "next row tile"]),
        ],
        "note": "Shared memory turns irregular k-way writes into a coalesced dense dx store without global atomics.",
    },
    {
        "file": "cross-entropy-forward-fused",
        "title": "QuACK cross entropy forward · loss, LSE, optional dx",
        "subtitle": "One reduction over logits feeds loss, log-sum-exp, and an optional fused gradient.",
        "source": "quack/cross_entropy.py · CrossEntropy.kernel()",
        "lanes": [
            ("Load + metadata", "Rows may span an N-cluster", ["Load logits → sX", "read target + weight", "read target logit", "ignore-index gate"]),
            ("Stable reduction", "Online or two-pass softmax", ["row max", "exp(x−max)", "row/cluster sum", "lse=max+log(sum)"]),
            ("Loss outputs", "One elected lane writes scalars", ["lse−target logit", "× class weight", "ignored → 0", "store loss + LSE"]),
            ("Optional fused dx", "Enabled by return_dx", ["p = exp / sum", "target lane p−1", "× target weight", "predicated dx store"]),
        ],
        "note": "When dx is requested the implementation keeps exp(x−max), avoiding a second logits kernel.",
    },
    {
        "file": "cross-entropy-backward-fused",
        "title": "QuACK cross entropy backward · reconstruct probabilities from LSE",
        "subtitle": "Independent N tiles use saved LSE; no cross-CTA reduction is needed in backward.",
        "source": "quack/cross_entropy.py · CrossEntropyBackward.kernel()",
        "lanes": [
            ("Tile inputs", "2-D grid over rows and N chunks", ["cp.async logits → sX", "read target", "read dloss + LSE", "read class weight"]),
            ("Probability", "FP32 per-element reconstruction", ["x → FP32", "p=exp(x−LSE)", "build target mask", "p_target → p−1"]),
            ("Gradient scaling", "Broadcast row scalars", ["select p or p−1", "× dloss", "× target weight", "ignored dloss → 0"]),
            ("Store", "Each N tile is independent", ["convert dx dtype", "predicate tail N", "vector store", "next grid tile"]),
        ],
        "note": "Saved LSE replaces max/sum reduction, so backward parallelizes freely across 16K-wide N chunks.",
    },
    {
        "file": "rmsnorm-layernorm-forward",
        "title": "QuACK RMSNorm / LayerNorm forward · clustered row pipeline",
        "subtitle": "One configurable kernel handles residual fusion, affine terms, RMSNorm, and LayerNorm.",
        "source": "quack/rmsnorm.py · RMSNorm.kernel()",
        "lanes": [
            ("Load + fuse", "X and optional residual", ["cp.async X (+residual)", "wait + FP32", "x = X + residual", "optional residual-out"]),
            ("Statistics", "Cluster reduction for wide rows", ["RMS: Σx²", "LN: Σx → mean", "LN: Σ(x−mean)²", "rstd=rsqrt(var+ε)"]),
            ("Reload + affine", "rmem, smem, or gmem policy", ["reload x if needed", "x̂=(x−μ)rstd", "× (weight+offset)", "+ optional bias"]),
            ("Outputs", "Scalar stats elected once", ["store rstd", "store mean for LN", "convert y dtype", "vector store y"]),
        ],
        "note": "LayerNorm uses two ordered reductions; RMSNorm skips mean and reduces x² directly.",
    },
    {
        "file": "rmsnorm-layernorm-backward",
        "title": "QuACK RMSNorm / LayerNorm backward · pipelined rows and reductions",
        "subtitle": "Persistent CTAs overlap X/dO movement with correction reductions and partial parameter gradients.",
        "source": "quack/rmsnorm.py · RMSNormBackward.kernel()",
        "lanes": [
            ("Row prefetch", "TMA or cp.async ring", ["prefetch X + dO", "stage in sX,sdO", "consume current stage", "prefetch future row"]),
            ("Correction terms", "Warp/block/cluster exchange", ["w·dO and x̂", "RMS: mean(x̂wdy)", "LN: two means", "publish reduced terms"]),
            ("Input gradients", "Apply normalization Jacobian", ["form corrected dx", "optional dResidualOut", "convert/store dx", "optional dResidual"]),
            ("Parameter gradients", "Accumulate partials in FP32", ["dW += dO·x̂", "dB += dO", "one partial per CTA", "final reduce kernel"]),
        ],
        "note": "The shared-memory stage ring and reduction-buffer stage ring advance in lockstep across persistent row work.",
    },
    {
        "file": "rotary-forward-backward",
        "title": "QuACK rotary embedding · forward and conjugate backward",
        "subtitle": "The same kernel rotates forward or backward; backward negates sin via conjugate=True.",
        "source": "quack/rotary.py · RotaryKernel.kernel()",
        "lanes": [
            ("Indexing", "Fixed or variable-length batches", ["decode batch/head/row", "apply seq offset", "guard cu_seqlens", "tile rotary dim"]),
            ("Loads", "Cos/sin stay in registers", ["load cos + sin", "backward: sin=−sin", "load X interleaved|or cp.async split", "wait per head"]),
            ("Complex rotation", "FP32 pairwise math", ["x₀′=x₀c−x₁s", "x₁′=x₀s+x₁c", "interleaved pairs|or half split", "keep tail unchanged"]),
            ("Store", "In-place and out-of-place APIs", ["convert output dtype", "predicate rotary dim", "vector store", "advance head tile"]),
        ],
        "note": "Negating sin applies the inverse 2×2 rotation, so one device kernel serves autograd forward and backward.",
    },
    {
        "file": "hadamard-forward-backward",
        "title": "QuACK Hadamard transform · hierarchical butterfly exchange",
        "subtitle": "Forward and backward reuse the same self-inverse transform, with caller-selected scaling.",
        "source": "quack/transform/hadamard.py · HadamardTransform.kernel()",
        "lanes": [
            ("Persistent load loop", "One or more rows per CTA", ["load row tile", "optional cp.async", "wait current row", "prefetch next row"]),
            ("Thread-local butterflies", "Register-resident radix stages", ["reshape by radix", "a+b / a−b", "repeat local bits", "hold FP32 values"]),
            ("Cross-thread exchange", "Shuffle for small plans, smem otherwise", ["warp shuffle path", "or store s_exchange", "warp/CTA barrier", "load permuted bits"]),
            ("Scale + store", "Tail may store directly", ["final butterfly stage", "× scale", "direct tail layout|or rmem output", "predicated vector store"]),
        ],
        "note": "H(H(x)) = N·x; autograd invokes the same kernel again with the matching normalization scale.",
    },
    {
        "file": "rms-final-reduce",
        "title": "QuACK RMS final reduction · partial sums to reciprocal stddev",
        "subtitle": "A compact reduction kernel closes multi-stage RMS statistics.",
        "source": "quack/rms_final_reduce.py · RmsFinalReduce.kernel()",
        "lanes": [
            ("Load partials", "One row of accumulated statistics", ["tile partial-sum matrix", "predicate tail N", "load to registers", "zero invalid lanes"]),
            ("Local reduction", "FP32 fragments", ["sum register values", "warp reduction", "shared partials", "synchronize"]),
            ("Row reduction", "ReductionBase machinery", ["combine warp sums", "optional mbarrier", "broadcast sum", "one scalar per row"]),
            ("Finalize", "Only column-zero owner writes", ["sum × scale", "+ ε", "rsqrt", "store rstd[row]"]),
        ],
        "note": "This kernel reduces sums (not squares itself); scale encodes the normalization applied to upstream partials.",
    },
    {
        "file": "split-k-reduce",
        "title": "QuACK split-K reduction · deterministic sum and one epilogue",
        "subtitle": "Workspace partials are accumulated in ascending split order before the linear epilogue runs once.",
        "source": "quack/split_k_reduce.py · SplitKReduce.kernel()",
        "lanes": [
            ("Load split workspace", "Fixed split order", ["tile output MN", "load W₀…Wₛ₋₁", "load optional C/vectors", "predicate edges"]),
            ("Deterministic reduce", "FP32 register accumulation", ["acc = W₀", "acc += W₁", "… ascending order", "complete tile sum"]),
            ("Linear epilogue", "Shared GEMM epilogue math", ["alpha × acc", "+ beta × C", "+ row vector", "+ column vector"]),
            ("Output", "Optional accumulation into D", ["+ old output if enabled", "convert output dtype", "vector store", "next MN/batch tile"]),
        ],
        "note": "Applying the epilogue after—not within—split accumulation preserves its semantics and avoids repeated bias terms.",
    },
    {
        "file": "gemm-sm90-pipeline",
        "title": "QuACK GEMM SM90 · TMA producer, WGMMA consumer, TMA epilogue",
        "subtitle": "Persistent Hopper tiles flow through staged A/B, register accumulators, and staged output stores.",
        "source": "quack/gemm_sm90.py · GemmSm90.kernel()",
        "lanes": [
            ("Scheduler + load warps", "Persistent work and TMA multicast", ["get tile (M,N,K,L)", "acquire A/B stage", "TMA A + B → smem", "commit / advance"]),
            ("MMA warpgroup(s)", "WGMMA consumes staged operands", ["wait A/B full", "issue WGMMA k-tile", "wait prior group", "release A/B stage"]),
            ("Ping-pong + split-K", "Optional scheduling modes", ["WG0 ⇄ WG1 token", "next persistent tile", "nonfinal split → ws", "finalizer sums partials"]),
            ("Epilogue", "Registers ↔ smem ↔ global", ["visit accumulator", "load C / apply ops", "rmem → sD", "TMA store D"]),
        ],
        "note": "Load warps and MMA warpgroups use different register budgets; pipeline barriers carry ownership between them.",
    },
    {
        "file": "gemm-sm100-pipeline",
        "title": "QuACK GEMM SM100 · UMMA, tensor memory, and specialized warps",
        "subtitle": "Blackwell adds TMEM accumulator stages, optional block scales, 2-CTA MMA, and CLC scheduling.",
        "source": "quack/gemm_sm100.py · GemmSm100.kernel()",
        "lanes": [
            ("Persistent scheduler / loads", "CLC or static work distribution", ["query next work tile", "TMA A,B (+SFA/SFB)", "multicast within cluster", "commit A/B stage"]),
            ("UMMA warp", "SMEM operands → TMEM accumulators", ["allocate TMEM", "wait operand stage", "tcgen05 / blockscaled MMA", "publish acc stage"]),
            ("Epilogue warps", "TMEM subtiles stream to registers", ["wait acc stage", "TMEM → rmem", "load C + visit ops", "rmem → sD"]),
            ("Stores + retirement", "Overlap output with next tile", ["TMA store D", "release acc early", "advance scheduler ring", "cancel/drain CLC tail"]),
        ],
        "note": "Accumulator and scale-factor regions can alternate across TMEM columns so epilogue release overlaps the next MMA tile.",
    },
    {
        "file": "gemm-sm120-pipeline",
        "title": "QuACK GEMM SM120 · persistent warp-MMA pipeline",
        "subtitle": "The SM90 host/pipeline structure is reused, but operands enter registers through ldmatrix for warp MMA.",
        "source": "quack/gemm_sm120.py · GemmSm120.kernel()",
        "lanes": [
            ("Scheduler + TMA loads", "Persistent A/B stage ring", ["get work tile", "TMA A + B → smem", "commit stage", "prefetch next tile"]),
            ("Warp-MMA consumers", "No WGMMA/TMEM path", ["wait A/B stage", "ldmatrix sA,sB → rmem", "warp MMA k-loop", "release stage"]),
            ("Optional ping-pong", "Two consumer warpgroups", ["WG0 start token", "compute current tile", "handoff WG1", "advance work"]),
            ("Inherited epilogue", "Same composable output path", ["visit accumulator", "load optional C", "stage D in smem", "TMA store output"]),
        ],
        "note": "SM120 changes the compute datapath while preserving QuACK's persistent scheduling and staged epilogue structure.",
    },
]


def box_text(lines, x, y):
    parts = lines.split("|")
    if len(parts) == 1:
        return f'<text class="box" x="{x}" y="{y}">{escape(parts[0])}</text>'
    return (
        f'<text class="box" x="{x}" y="{y - 10}">{escape(parts[0])}</text>'
        f'<text class="mini" x="{x}" y="{y + 15}">{escape(parts[1])}</text>'
    )


def render(g):
    lane_y = [205, 365, 525, 685]
    box_x = [355, 675, 995, 1315]
    colors = ["#d7e8f2", "#cfe9df", "#8bcdb8", "#f2d394"]
    rows = []
    for idx, (name, note, boxes) in enumerate(g["lanes"]):
        y = lane_y[idx]
        rows.append(f'<text class="lane" x="72" y="{y + 31}">{escape(name)}</text>')
        rows.append(f'<text class="lane-note" x="72" y="{y + 57}">{escape(note)}</text>')
        for j, label in enumerate(boxes):
            x = box_x[j]
            rows.append(f'<rect class="node" x="{x}" y="{y}" width="245" height="70" rx="10" fill="{colors[idx]}"/>')
            rows.append(box_text(label, x + 122.5, y + 36))
            if j:
                rows.append(f'<path class="arrow" d="M{box_x[j-1] + 245} {y + 35} H{x - 2}"/>')
    for j in range(3):
        x = box_x[j] + 122.5
        rows.append(f'<path class="dep" d="M{x} {lane_y[j] + 70} V{lane_y[j+1] - 2}"/>')
    desc = f'{g["title"]}. {g["subtitle"]} {g["note"]}'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1000" viewBox="0 0 1800 1000" role="img" aria-labelledby="title desc">
  <title id="title">{escape(g["title"])}</title>
  <desc id="desc">{escape(desc)}</desc>
  <defs>
    <style>
      text {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #172734; }}
      .title {{ font-size: 34px; font-weight: 760; }} .subtitle {{ font-size: 17px; fill: #425869; }}
      .lane {{ font-size: 17px; font-weight: 730; }} .lane-note {{ font-size: 13px; fill: #526a79; }}
      .phase {{ font-size: 13px; font-weight: 700; fill: #607887; text-anchor: middle; letter-spacing: .6px; }}
      .box {{ font-size: 15px; font-weight: 700; text-anchor: middle; dominant-baseline: middle; }}
      .mini {{ font-size: 12px; font-weight: 650; fill: #425869; text-anchor: middle; dominant-baseline: middle; }}
      .node {{ stroke: #294251; stroke-width: 1.6; }} .grid {{ stroke: #dce6ec; stroke-width: 1.2; }}
      .arrow {{ fill: none; stroke: #526d7c; stroke-width: 2.2; marker-end: url(#arrow); }}
      .dep {{ fill: none; stroke: #b87912; stroke-width: 2; stroke-dasharray: 6 5; marker-end: url(#gold); }}
      .note {{ font-size: 15px; font-weight: 650; fill: #704b09; }} .source {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; fill: #526a79; }}
    </style>
    <marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#526d7c"/></marker>
    <marker id="gold" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#b87912"/></marker>
  </defs>
  <rect width="1800" height="1000" fill="#f8fafb"/>
  <text class="title" x="60" y="58">{escape(g["title"])}</text>
  <text class="subtitle" x="60" y="94">{escape(g["subtitle"])}</text>
  <text class="subtitle" x="60" y="122">CuTe DSL entry point: <tspan class="source">{escape(g["source"])}</tspan></text>
  <rect x="50" y="160" width="1700" height="700" rx="9" fill="#fff" stroke="#d4e0e7" stroke-width="1.4"/>
  <line class="grid" x1="320" y1="160" x2="320" y2="860"/>
  <line class="grid" x1="50" y1="340" x2="1750" y2="340"/><line class="grid" x1="50" y1="500" x2="1750" y2="500"/><line class="grid" x1="50" y1="660" x2="1750" y2="660"/>
  <text class="phase" x="477" y="185">SET UP / LOAD</text><text class="phase" x="797" y="185">TRANSFORM</text><text class="phase" x="1117" y="185">SYNCHRONIZE / REDUCE</text><text class="phase" x="1437" y="185">PUBLISH / ADVANCE</text>
  {''.join(rows)}
  <rect x="60" y="892" width="1680" height="62" rx="10" fill="#fff7df" stroke="#b87912" stroke-width="1.5"/>
  <text class="note" x="85" y="929">{escape(g["note"])}</text>
</svg>
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for graph in GRAPHS:
        (OUT / f'{graph["file"]}.svg').write_text(render(graph), encoding="utf-8")


if __name__ == "__main__":
    main()
