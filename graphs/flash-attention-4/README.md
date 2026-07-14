# FlashAttention-4

Diagrams explaining FlashAttention-4 kernels and their execution on NVIDIA
Blackwell GPUs.

- `blackwell-forward-dependencies.svg`: simplified steady-state overlap and
  dependencies between loads, QK/PV matrix operations, softmax, and output
  correction in the forward pass.
