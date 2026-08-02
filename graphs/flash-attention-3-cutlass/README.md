# FlashAttention-3 CUTLASS

Diagrams explaining the CUTLASS forward and backward implementations of
FlashAttention-3 on NVIDIA Hopper GPUs.

The direct-SVG authoring brief and inspected Hopper-mainloop provenance are in
[`specs/topics/flash-attention-3-cutlass.json`](../../specs/topics/flash-attention-3-cutlass.json).
The SVG is authored directly by an LLM; no layout generator is used.

- `hopper-forward-overlap.svg`: the head-dimension-128 forward path with two
  consumer warpgroups, RS-PV, and intra-warpgroup QK/PV overlap.
- `hopper-backward-pipeline.svg`: the Hopper backward path with producer warp 0
  loading operands, producer warp 1 draining dQ, five WGMMA gradient paths, and
  union-backed mainloop-to-epilogue SMEM reuse.

In this graph, **ping-pong** is informal shorthand for ownership of the
named-barrier scheduler token alternating between consumer WG0 and WG1. It is
not the two-stage circular K/V buffer: the token controls which consumer WG may
issue its ordered QK/PV pair, while the K/V pipeline independently alternates
shared-memory stage 0 and stage 1.
