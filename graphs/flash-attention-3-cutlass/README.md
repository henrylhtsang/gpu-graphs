# FlashAttention-3 CUTLASS

Diagrams explaining the CUTLASS implementation of FlashAttention-3 on NVIDIA
Hopper GPUs.

- `hopper-forward-overlap.svg`: the head-dimension-128 forward path with two
  consumer warpgroups, RS-PV, and intra-warpgroup QK/PV overlap.

In this graph, **ping-pong** is informal shorthand for ownership of the
named-barrier scheduler token alternating between consumer WG0 and WG1. It is
not the two-stage circular K/V buffer: the token controls which consumer WG may
issue its ordered QK/PV pair, while the K/V pipeline independently alternates
shared-memory stage 0 and stage 1.
