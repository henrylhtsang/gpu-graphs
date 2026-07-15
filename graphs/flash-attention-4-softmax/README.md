# FlashAttention-4 SM100 softmax warpgroups

Diagrams focused on the softmax warpgroups in the Blackwell forward kernel,
implemented in
[`flash_attn/cute/flash_fwd_sm100.py`](https://github.com/Dao-AILab/flash-attention/blob/main/flash_attn/cute/flash_fwd_sm100.py).

- `sm100-softmax-warpgroup.svg`: the dense, head-dimension-128, `q_stage=2`
  path. It follows one score tile from TMEM through masking, online-softmax
  updates, split P production, and the handoffs to correction and PV.

There are two four-warp softmax groups in this configuration: warps 0–3 handle
Q stage 0 and warps 4–7 handle Q stage 1. Correction is intentionally shown as
a separate consumer: warps 8–11 rescale the accumulated O tile when the
softmax group publishes an update factor.

