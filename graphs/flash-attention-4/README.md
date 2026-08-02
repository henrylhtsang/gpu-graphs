# FlashAttention-4

Diagrams explaining FlashAttention-4 kernels and their execution on NVIDIA
Blackwell GPUs.

- `blackwell-forward-dependencies.svg`: simplified steady-state overlap and
  dependencies between loads, QK/PV matrix operations, softmax, and output
  correction in the forward pass.
- `forward-sm100-kernel-structure.svg`: three-phase timeline for the
  representative dense-TMA, `q_stage=2`, head-dimension-128 path. It aligns
  prologue, repeated mainloop, epilogue, warp-role handoffs, and physical
  SMEM/TMEM lifetimes on one semantic event axis. It is generated from
  [`specs/kernels/flash-attention-4/forward-sm100.json`](../../specs/kernels/flash-attention-4/forward-sm100.json).
  The prologue uses concrete `K0`/`V0` seed names; the representative mainloop
  consumes symbolic `Kj`/`Vj` while the TMA producer prefetches `Kj+1`/`Vj+1`.
  Each softmax lane exposes its TMEM-to-register load, mask and online row-max,
  correction-scale handoff, exp2 conversion, 96+32-column `P` publication, row
  sum update, and final-statistics handoff.
  Its loop-resident Q resources, next-iteration K/V carries, physical reuse, and
  configuration-specific Q/O separation are validated rather than encoded as
  independent drawing coordinates.
