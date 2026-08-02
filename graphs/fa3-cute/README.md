# FA3-CuTe (FlashAttention SM90)

Diagrams for the CuTeDSL SM90 forward and backward paths in the FlashAttention
repository. These are the Hopper implementations in `flash_fwd_sm90.py` and
`flash_bwd_sm90.py`, not the Blackwell SM100 paths.

The direct-SVG authoring brief and pinned implementation provenance are in
[`specs/topics/fa3-cute.json`](../../specs/topics/fa3-cute.json). The SVG is
authored directly by an LLM after code inspection; no layout generator is used.

- `sm90-forward-overlap.svg`: the dense, head-dimension-128 forward path with
  a TMA producer, two consumer warpgroups, register-sourced PV, two-stage K/V
  pipelines, and intra-warpgroup QK/PV overlap.
- `sm90-backward-pipeline.svg`: the dense, head-dimension-128 backward path with
  fixed K/V, streamed Q/dO/LSE/D row tiles, five gradient matrix products, dQ
  bulk reduce-add, and the epilogue-only `sK`/`sV` reuse for `sdK`/`sdV`.

Here **ping-pong** means the named-barrier scheduler token alternates between
consumer WG0 and WG1. The token serializes each warpgroup's ordered pair of
WGMMA issues (new QK, then old PV). It is separate from the two-stage K/V
shared-memory pipeline, whose stage index advances independently.
