# QuACK CuTe DSL kernels

These diagrams cover every launchable `@cute.kernel` entry point under
`quack/` at QuACK commit
[`b66e4ec`](https://github.com/Dao-AILab/quack/tree/b66e4ec8b364b54c8f7f147a29524d3dcdf4fe15).
The inventory is decorator-based: `@cute.jit` helpers and host-side PyTorch/JAX
wrappers are not counted as separate GPU kernels.

| Source kernel | Diagram | Direction / role |
| --- | --- | --- |
| `Softmax.kernel` | `softmax-forward-reduction.svg` | forward |
| `SoftmaxBackward.kernel` | `softmax-backward-jacobian.svg` | backward |
| `TopK.kernel` | `top-k-forward-bitonic.svg` | forward |
| `TopKBackward.kernel` | `top-k-backward-scatter.svg` | backward |
| `CrossEntropy.kernel` | `cross-entropy-forward-fused.svg` | forward, optional fused gradient |
| `CrossEntropyBackward.kernel` | `cross-entropy-backward-fused.svg` | backward |
| `RMSNorm.kernel` | `rmsnorm-layernorm-forward.svg` | RMSNorm / LayerNorm forward |
| `RMSNormBackward.kernel` | `rmsnorm-layernorm-backward.svg` | RMSNorm / LayerNorm backward |
| `RotaryKernel.kernel` | `rotary-forward-backward.svg` | forward and conjugate backward |
| `HadamardTransform.kernel` | `hadamard-forward-backward.svg` | self-inverse forward/backward |
| `RmsFinalReduce.kernel` | `rms-final-reduce.svg` | final statistics reduction |
| `SplitKReduce.kernel` | `split-k-reduce.svg` | split-K workspace finalizer |
| `GemmSm90.kernel` | `gemm-sm90-pipeline.svg` | Hopper GEMM |
| `GemmSm100.kernel` | `gemm-sm100-pipeline.svg` | Blackwell GEMM |
| `GemmSm120.kernel` | `gemm-sm120-pipeline.svg` | SM120 GEMM |

Rotary forward and backward deliberately share one device kernel: the backward
path negates sine (`conjugate=True`) to apply the inverse rotation. Hadamard
also shares one kernel because the transform is self-inverse up to scale.

Primary source files:

- [softmax.py](https://github.com/Dao-AILab/quack/blob/b66e4ec8b364b54c8f7f147a29524d3dcdf4fe15/quack/softmax.py)
- [topk.py](https://github.com/Dao-AILab/quack/blob/b66e4ec8b364b54c8f7f147a29524d3dcdf4fe15/quack/topk.py)
- [cross_entropy.py](https://github.com/Dao-AILab/quack/blob/b66e4ec8b364b54c8f7f147a29524d3dcdf4fe15/quack/cross_entropy.py)
- [rmsnorm.py](https://github.com/Dao-AILab/quack/blob/b66e4ec8b364b54c8f7f147a29524d3dcdf4fe15/quack/rmsnorm.py)
- [rotary.py](https://github.com/Dao-AILab/quack/blob/b66e4ec8b364b54c8f7f147a29524d3dcdf4fe15/quack/rotary.py)
- [transform/hadamard.py](https://github.com/Dao-AILab/quack/blob/b66e4ec8b364b54c8f7f147a29524d3dcdf4fe15/quack/transform/hadamard.py)
- [rms_final_reduce.py](https://github.com/Dao-AILab/quack/blob/b66e4ec8b364b54c8f7f147a29524d3dcdf4fe15/quack/rms_final_reduce.py)
- [split_k_reduce.py](https://github.com/Dao-AILab/quack/blob/b66e4ec8b364b54c8f7f147a29524d3dcdf4fe15/quack/split_k_reduce.py)
- [gemm_sm90.py](https://github.com/Dao-AILab/quack/blob/b66e4ec8b364b54c8f7f147a29524d3dcdf4fe15/quack/gemm_sm90.py)
- [gemm_sm100.py](https://github.com/Dao-AILab/quack/blob/b66e4ec8b364b54c8f7f147a29524d3dcdf4fe15/quack/gemm_sm100.py)
- [gemm_sm120.py](https://github.com/Dao-AILab/quack/blob/b66e4ec8b364b54c8f7f147a29524d3dcdf4fe15/quack/gemm_sm120.py)

SVG is the editable source of truth. The generator in `scripts/` keeps the
shared visual grammar synchronized; after any SVG change, regenerate the PNG
companions with `make png` (or `make png-force`).
