# FA3-CuTe (FlashAttention-4 SM90)

Diagrams for the CuTeDSL SM90 forward path in the FlashAttention-4 repository.
This is the Hopper implementation in
[`flash_attn/cute/flash_fwd_sm90.py`](https://github.com/Dao-AILab/flash-attention/blob/main/flash_attn/cute/flash_fwd_sm90.py),
not the Blackwell SM100 path.

- `sm90-forward-overlap.svg`: the dense, head-dimension-128 forward path with
  a TMA producer, two consumer warpgroups, register-sourced PV, two-stage K/V
  pipelines, and intra-warpgroup QK/PV overlap.

Here **ping-pong** means the named-barrier scheduler token alternates between
consumer WG0 and WG1. The token serializes each warpgroup's ordered pair of
WGMMA issues (new QK, then old PV). It is separate from the two-stage K/V
shared-memory pipeline, whose stage index advances independently.

