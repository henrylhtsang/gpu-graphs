# CUTLASS warp-specialized examples and tutorials

Large role-timeline diagrams for every runnable example or tutorial detected as
warp-specialized in the local CUTLASS checkout at commit `2802e228`.
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
| `111_hopper_ssd` | [cpp-111-hopper-ssd.svg](cpp-111-hopper-ssd.svg) | C++ example |
| `112_blackwell_ssd` | [cpp-112-blackwell-ssd.svg](cpp-112-blackwell-ssd.svg) | C++ example |
| `113_hopper_gemm_activation_fusion` | [cpp-113-hopper-gemm-activation-fusion.svg](cpp-113-hopper-gemm-activation-fusion.svg) | C++ example |
| `48_hopper_warp_specialized_gemm` | [cpp-48-hopper-warp-specialized-gemm.svg](cpp-48-hopper-warp-specialized-gemm.svg) | C++ example |
| `49_hopper_gemm_with_collective_builder` | [cpp-49-hopper-gemm-with-collective-builder.svg](cpp-49-hopper-gemm-with-collective-builder.svg) | C++ example |
| `50_hopper_gemm_with_epilogue_swizzle` | [cpp-50-hopper-gemm-with-epilogue-swizzle.svg](cpp-50-hopper-gemm-with-epilogue-swizzle.svg) | C++ example |
| `51_hopper_gett` | [cpp-51-hopper-gett.svg](cpp-51-hopper-gett.svg) | C++ example |
| `52_hopper_gather_scatter_fusion` | [cpp-52-hopper-gather-scatter-fusion.svg](cpp-52-hopper-gather-scatter-fusion.svg) | C++ example |
| `54_hopper_fp8_warp_specialized_gemm` | [cpp-54-hopper-fp8-warp-specialized-gemm.svg](cpp-54-hopper-fp8-warp-specialized-gemm.svg) | C++ example |
| `55_hopper_mixed_dtype_gemm` | [cpp-55-hopper-mixed-dtype-gemm.svg](cpp-55-hopper-mixed-dtype-gemm.svg) | C++ example |
| `56_hopper_ptr_array_batched_gemm` | [cpp-56-hopper-ptr-array-batched-gemm.svg](cpp-56-hopper-ptr-array-batched-gemm.svg) | C++ example |
| `57_hopper_grouped_gemm` | [cpp-57-hopper-grouped-gemm.svg](cpp-57-hopper-grouped-gemm.svg) | C++ example |
| `61_hopper_gemm_with_topk_and_softmax` | [cpp-61-hopper-gemm-with-topk-and-softmax.svg](cpp-61-hopper-gemm-with-topk-and-softmax.svg) | C++ example |
| `63_hopper_gemm_with_weight_prefetch` | [cpp-63-hopper-gemm-with-weight-prefetch.svg](cpp-63-hopper-gemm-with-weight-prefetch.svg) | C++ example |
| `65_distributed_gemm` | [cpp-65-distributed-gemm.svg](cpp-65-distributed-gemm.svg) | C++ example |
| `67_hopper_fp8_warp_specialized_gemm_with_blockwise_scaling` | [cpp-67-hopper-fp8-warp-specialized-gemm-with-blockwise-scaling.svg](cpp-67-hopper-fp8-warp-specialized-gemm-with-blockwise-scaling.svg) | C++ example |
| `68_hopper_fp8_warp_specialized_grouped_gemm_with_blockwise_scaling` | [cpp-68-hopper-fp8-warp-specialized-grouped-gemm-with-blockwise-scaling.svg](cpp-68-hopper-fp8-warp-specialized-grouped-gemm-with-blockwise-scaling.svg) | C++ example |
| `69_hopper_mixed_dtype_grouped_gemm` | [cpp-69-hopper-mixed-dtype-grouped-gemm.svg](cpp-69-hopper-mixed-dtype-grouped-gemm.svg) | C++ example |
| `70_blackwell_gemm` | [cpp-70-blackwell-gemm.svg](cpp-70-blackwell-gemm.svg) | C++ example |
| `71_blackwell_gemm_with_collective_builder` | [cpp-71-blackwell-gemm-with-collective-builder.svg](cpp-71-blackwell-gemm-with-collective-builder.svg) | C++ example |
| `72_blackwell_narrow_precision_gemm` | [cpp-72-blackwell-narrow-precision-gemm.svg](cpp-72-blackwell-narrow-precision-gemm.svg) | C++ example |
| `73_blackwell_gemm_preferred_cluster` | [cpp-73-blackwell-gemm-preferred-cluster.svg](cpp-73-blackwell-gemm-preferred-cluster.svg) | C++ example |
| `74_blackwell_gemm_streamk` | [cpp-74-blackwell-gemm-streamk.svg](cpp-74-blackwell-gemm-streamk.svg) | C++ example |
| `75_blackwell_grouped_gemm` | [cpp-75-blackwell-grouped-gemm.svg](cpp-75-blackwell-grouped-gemm.svg) | C++ example |
| `76_blackwell_conv` | [cpp-76-blackwell-conv.svg](cpp-76-blackwell-conv.svg) | C++ example |
| `77_blackwell_fmha` | [cpp-77-blackwell-fmha.svg](cpp-77-blackwell-fmha.svg) | C++ example |
| `78_blackwell_emulated_bf16x9_gemm` | [cpp-78-blackwell-emulated-bf16x9-gemm.svg](cpp-78-blackwell-emulated-bf16x9-gemm.svg) | C++ example |
| `79_blackwell_geforce_gemm` | [cpp-79-blackwell-geforce-gemm.svg](cpp-79-blackwell-geforce-gemm.svg) | C++ example |
| `80_blackwell_geforce_sparse_gemm` | [cpp-80-blackwell-geforce-sparse-gemm.svg](cpp-80-blackwell-geforce-sparse-gemm.svg) | C++ example |
| `81_blackwell_gemm_blockwise` | [cpp-81-blackwell-gemm-blockwise.svg](cpp-81-blackwell-gemm-blockwise.svg) | C++ example |
| `82_blackwell_distributed_gemm` | [cpp-82-blackwell-distributed-gemm.svg](cpp-82-blackwell-distributed-gemm.svg) | C++ example |
| `83_blackwell_sparse_gemm` | [cpp-83-blackwell-sparse-gemm.svg](cpp-83-blackwell-sparse-gemm.svg) | C++ example |
| `84_blackwell_narrow_precision_sparse_gemm` | [cpp-84-blackwell-narrow-precision-sparse-gemm.svg](cpp-84-blackwell-narrow-precision-sparse-gemm.svg) | C++ example |
| `86_blackwell_mixed_dtype_gemm` | [cpp-86-blackwell-mixed-dtype-gemm.svg](cpp-86-blackwell-mixed-dtype-gemm.svg) | C++ example |
| `87_blackwell_geforce_gemm_blockwise` | [cpp-87-blackwell-geforce-gemm-blockwise.svg](cpp-87-blackwell-geforce-gemm-blockwise.svg) | C++ example |
| `88_hopper_fmha` | [cpp-88-hopper-fmha.svg](cpp-88-hopper-fmha.svg) | C++ example |
| `89_sm103_fp4_ultra_gemm` | [cpp-89-sm103-fp4-ultra-gemm.svg](cpp-89-sm103-fp4-ultra-gemm.svg) | C++ example |
| `90_sm103_fp4_ultra_grouped_gemm` | [cpp-90-sm103-fp4-ultra-grouped-gemm.svg](cpp-90-sm103-fp4-ultra-grouped-gemm.svg) | C++ example |
| `92_blackwell_moe_gemm` | [cpp-92-blackwell-moe-gemm.svg](cpp-92-blackwell-moe-gemm.svg) | C++ example |
| `93_blackwell_low_latency_gqa` | [cpp-93-blackwell-low-latency-gqa.svg](cpp-93-blackwell-low-latency-gqa.svg) | C++ example |
| `95_blackwell_gemm_green_context` | [cpp-95-blackwell-gemm-green-context.svg](cpp-95-blackwell-gemm-green-context.svg) | C++ example |
| `python/CuTeDSL/cute/blackwell/efc/activation_custom_epilogue_dense_gemm.py` | [python-cute-blackwell-efc-activation-custom-epilogue-dense-gemm.svg](python-cute-blackwell-efc-activation-custom-epilogue-dense-gemm.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/efc/custom_epilogue_dense_gemm.py` | [python-cute-blackwell-efc-custom-epilogue-dense-gemm.svg](python-cute-blackwell-efc-custom-epilogue-dense-gemm.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/efc/synthetic_custom_epilogue_dense_gemm.py` | [python-cute-blackwell-efc-synthetic-custom-epilogue-dense-gemm.svg](python-cute-blackwell-efc-synthetic-custom-epilogue-dense-gemm.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/attention/fmha/fmha.py` | [python-cute-blackwell-kernel-attention-fmha-fmha.svg](python-cute-blackwell-kernel-attention-fmha-fmha.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/attention/fmha/fmha_bwd.py` | [python-cute-blackwell-kernel-attention-fmha-fmha-bwd.svg](python-cute-blackwell-kernel-attention-fmha-fmha-bwd.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/attention/mamba2_ssd/mamba2_ssd.py` | [python-cute-blackwell-kernel-attention-mamba2-ssd-mamba2-ssd.svg](python-cute-blackwell-kernel-attention-mamba2-ssd-mamba2-ssd.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/attention/mixed_input_fmha/mixed_input_fmha_decode.py` | [python-cute-blackwell-kernel-attention-mixed-input-fmha-mixed-input-fmha-decode.svg](python-cute-blackwell-kernel-attention-mixed-input-fmha-mixed-input-fmha-decode.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/attention/mixed_input_fmha/mixed_input_fmha_prefill_d256.py` | [python-cute-blackwell-kernel-attention-mixed-input-fmha-mixed-input-fmha-prefill-d256.svg](python-cute-blackwell-kernel-attention-mixed-input-fmha-mixed-input-fmha-prefill-d256.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/attention/mixed_input_fmha/mixed_input_fmha_prefill_d512.py` | [python-cute-blackwell-kernel-attention-mixed-input-fmha-mixed-input-fmha-prefill-d512.svg](python-cute-blackwell-kernel-attention-mixed-input-fmha-mixed-input-fmha-prefill-d512.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/attention/mla/mla_decode_fp16.py` | [python-cute-blackwell-kernel-attention-mla-mla-decode-fp16.svg](python-cute-blackwell-kernel-attention-mla-mla-decode-fp16.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/attention/mla/mla_decode_fp8.py` | [python-cute-blackwell-kernel-attention-mla-mla-decode-fp8.svg](python-cute-blackwell-kernel-attention-mla-mla-decode-fp8.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/blockscaled_gemm/dense_blockscaled_gemm_persistent.py` | [python-cute-blackwell-kernel-blockscaled-gemm-dense-blockscaled-gemm-persistent.svg](python-cute-blackwell-kernel-blockscaled-gemm-dense-blockscaled-gemm-persistent.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/blockscaled_gemm/dense_blockscaled_gemm_persistent_amax.py` | [python-cute-blackwell-kernel-blockscaled-gemm-dense-blockscaled-gemm-persistent-amax.svg](python-cute-blackwell-kernel-blockscaled-gemm-dense-blockscaled-gemm-persistent-amax.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/blockscaled_gemm/dense_blockscaled_gemm_persistent_prefetch.py` | [python-cute-blackwell-kernel-blockscaled-gemm-dense-blockscaled-gemm-persistent-prefetch.svg](python-cute-blackwell-kernel-blockscaled-gemm-dense-blockscaled-gemm-persistent-prefetch.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/blockscaled_gemm/sm103_dense_blockscaled_gemm_persistent.py` | [python-cute-blackwell-kernel-blockscaled-gemm-sm103-dense-blockscaled-gemm-persistent.svg](python-cute-blackwell-kernel-blockscaled-gemm-sm103-dense-blockscaled-gemm-persistent.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/blockscaled_grouped_gemm/grouped_blockscaled_gemm.py` | [python-cute-blackwell-kernel-blockscaled-grouped-gemm-grouped-blockscaled-gemm.svg](python-cute-blackwell-kernel-blockscaled-grouped-gemm-grouped-blockscaled-gemm.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/blockscaled_grouped_gemm/sm103_grouped_blockscaled_gemm.py` | [python-cute-blackwell-kernel-blockscaled-grouped-gemm-sm103-grouped-blockscaled-gemm.svg](python-cute-blackwell-kernel-blockscaled-grouped-gemm-sm103-grouped-blockscaled-gemm.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/blockwise_gemm/blockwise_gemm.py` | [python-cute-blackwell-kernel-blockwise-gemm-blockwise-gemm.svg](python-cute-blackwell-kernel-blockwise-gemm-blockwise-gemm.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/blockwise_gemm/contiguous_grouped_gemm.py` | [python-cute-blackwell-kernel-blockwise-gemm-contiguous-grouped-gemm.svg](python-cute-blackwell-kernel-blockwise-gemm-contiguous-grouped-gemm.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/blockwise_gemm/masked_grouped_gemm.py` | [python-cute-blackwell-kernel-blockwise-gemm-masked-grouped-gemm.svg](python-cute-blackwell-kernel-blockwise-gemm-masked-grouped-gemm.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/dense_gemm/dense_gemm_alpha_beta_persistent.py` | [python-cute-blackwell-kernel-dense-gemm-dense-gemm-alpha-beta-persistent.svg](python-cute-blackwell-kernel-dense-gemm-dense-gemm-alpha-beta-persistent.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/dense_gemm/dense_gemm_persistent.py` | [python-cute-blackwell-kernel-dense-gemm-dense-gemm-persistent.svg](python-cute-blackwell-kernel-dense-gemm-dense-gemm-persistent.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/dense_gemm/dense_gemm_persistent_dynamic.py` | [python-cute-blackwell-kernel-dense-gemm-dense-gemm-persistent-dynamic.svg](python-cute-blackwell-kernel-dense-gemm-dense-gemm-persistent-dynamic.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/dense_gemm/dense_gemm_persistent_prefetch.py` | [python-cute-blackwell-kernel-dense-gemm-dense-gemm-persistent-prefetch.svg](python-cute-blackwell-kernel-dense-gemm-dense-gemm-persistent-prefetch.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/distributed/all_reduce_tma.py` | [python-cute-blackwell-kernel-distributed-all-reduce-tma.svg](python-cute-blackwell-kernel-distributed-all-reduce-tma.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/distributed/distributed_all_gather_gemm_blackwell.py` | [python-cute-blackwell-kernel-distributed-distributed-all-gather-gemm-blackwell.svg](python-cute-blackwell-kernel-distributed-distributed-all-gather-gemm-blackwell.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/distributed/distributed_gemm_all_reduce_blackwell.py` | [python-cute-blackwell-kernel-distributed-distributed-gemm-all-reduce-blackwell.svg](python-cute-blackwell-kernel-distributed-distributed-gemm-all-reduce-blackwell.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/distributed/distributed_gemm_all_reduce_lamport_blackwell.py` | [python-cute-blackwell-kernel-distributed-distributed-gemm-all-reduce-lamport-blackwell.svg](python-cute-blackwell-kernel-distributed-distributed-gemm-all-reduce-lamport-blackwell.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/distributed/distributed_gemm_all_reduce_ldxstmc_blackwell.py` | [python-cute-blackwell-kernel-distributed-distributed-gemm-all-reduce-ldxstmc-blackwell.svg](python-cute-blackwell-kernel-distributed-distributed-gemm-all-reduce-ldxstmc-blackwell.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/distributed/distributed_gemm_blockscaled_all_reduce_ldmcxstmc_blackwell.py` | [python-cute-blackwell-kernel-distributed-distributed-gemm-blockscaled-all-reduce-ldmcxstmc-blackwell.svg](python-cute-blackwell-kernel-distributed-distributed-gemm-blockscaled-all-reduce-ldmcxstmc-blackwell.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/distributed/distributed_gemm_reduce_scatter_blackwell.py` | [python-cute-blackwell-kernel-distributed-distributed-gemm-reduce-scatter-blackwell.svg](python-cute-blackwell-kernel-distributed-distributed-gemm-reduce-scatter-blackwell.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/grouped_gemm/grouped_gemm.py` | [python-cute-blackwell-kernel-grouped-gemm-grouped-gemm.svg](python-cute-blackwell-kernel-grouped-gemm-grouped-gemm.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/mixed_input_gemm/grouped_mixed_input_gemm.py` | [python-cute-blackwell-kernel-mixed-input-gemm-grouped-mixed-input-gemm.svg](python-cute-blackwell-kernel-mixed-input-gemm-grouped-mixed-input-gemm.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/mixed_input_gemm/grouped_mixed_input_gemm_acc_scale.py` | [python-cute-blackwell-kernel-mixed-input-gemm-grouped-mixed-input-gemm-acc-scale.svg](python-cute-blackwell-kernel-mixed-input-gemm-grouped-mixed-input-gemm-acc-scale.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/mixed_input_gemm/mixed_input_gemm.py` | [python-cute-blackwell-kernel-mixed-input-gemm-mixed-input-gemm.svg](python-cute-blackwell-kernel-mixed-input-gemm-mixed-input-gemm.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/moe/torch_grouped_mm.py` | [python-cute-blackwell-kernel-moe-torch-grouped-mm.svg](python-cute-blackwell-kernel-moe-torch-grouped-mm.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/kernel/moe/torch_scaled_grouped_mm.py` | [python-cute-blackwell-kernel-moe-torch-scaled-grouped-mm.svg](python-cute-blackwell-kernel-moe-torch-scaled-grouped-mm.svg) | Python example |
| `python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/fp16_gemm_2.py` | [python-cute-blackwell-tutorial-tutorial-gemm-fp16-gemm-2.svg](python-cute-blackwell-tutorial-tutorial-gemm-fp16-gemm-2.svg) | tutorial |
| `python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/fp16_gemm_3.py` | [python-cute-blackwell-tutorial-tutorial-gemm-fp16-gemm-3.svg](python-cute-blackwell-tutorial-tutorial-gemm-fp16-gemm-3.svg) | tutorial |
| `python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/fp16_gemm_3_1.py` | [python-cute-blackwell-tutorial-tutorial-gemm-fp16-gemm-3-1.svg](python-cute-blackwell-tutorial-tutorial-gemm-fp16-gemm-3-1.svg) | tutorial |
| `python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/fp16_gemm_4.py` | [python-cute-blackwell-tutorial-tutorial-gemm-fp16-gemm-4.svg](python-cute-blackwell-tutorial-tutorial-gemm-fp16-gemm-4.svg) | tutorial |
| `python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/fp16_gemm_5.py` | [python-cute-blackwell-tutorial-tutorial-gemm-fp16-gemm-5.svg](python-cute-blackwell-tutorial-tutorial-gemm-fp16-gemm-5.svg) | tutorial |
| `python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/fp16_gemm_6.py` | [python-cute-blackwell-tutorial-tutorial-gemm-fp16-gemm-6.svg](python-cute-blackwell-tutorial-tutorial-gemm-fp16-gemm-6.svg) | tutorial |
| `python/CuTeDSL/cute/blackwell/tutorial/tutorial_tma/tma_v1.py` | [python-cute-blackwell-tutorial-tutorial-tma-tma-v1.svg](python-cute-blackwell-tutorial-tutorial-tma-tma-v1.svg) | tutorial |
| `python/CuTeDSL/cute/blackwell/tutorial/tutorial_tma/tma_v2.py` | [python-cute-blackwell-tutorial-tutorial-tma-tma-v2.svg](python-cute-blackwell-tutorial-tutorial-tma-tma-v2.svg) | tutorial |
| `python/CuTeDSL/cute/blackwell_geforce/kernel/blockscaled_gemm/dense_blockscaled_gemm_persistent_cooperative.py` | [python-cute-blackwell-geforce-kernel-blockscaled-gemm-dense-blockscaled-gemm-persistent-cooperative.svg](python-cute-blackwell-geforce-kernel-blockscaled-gemm-dense-blockscaled-gemm-persistent-cooperative.svg) | Python example |
| `python/CuTeDSL/cute/blackwell_geforce/kernel/blockscaled_gemm/dense_blockscaled_gemm_persistent_pingpong.py` | [python-cute-blackwell-geforce-kernel-blockscaled-gemm-dense-blockscaled-gemm-persistent-pingpong.svg](python-cute-blackwell-geforce-kernel-blockscaled-gemm-dense-blockscaled-gemm-persistent-pingpong.svg) | Python example |
| `python/CuTeDSL/cute/blackwell_geforce/kernel/dense_gemm/dense_gemm.py` | [python-cute-blackwell-geforce-kernel-dense-gemm-dense-gemm.svg](python-cute-blackwell-geforce-kernel-dense-gemm-dense-gemm.svg) | Python example |
| `python/CuTeDSL/cute/hopper/kernel/attention/fmha.py` | [python-cute-hopper-kernel-attention-fmha.svg](python-cute-hopper-kernel-attention-fmha.svg) | Python example |
| `python/CuTeDSL/cute/hopper/kernel/dense_gemm/dense_gemm.py` | [python-cute-hopper-kernel-dense-gemm-dense-gemm.svg](python-cute-hopper-kernel-dense-gemm-dense-gemm.svg) | Python example |
| `python/CuTeDSL/cute/hopper/kernel/dense_gemm/dense_gemm_fp8_2xacc.py` | [python-cute-hopper-kernel-dense-gemm-dense-gemm-fp8-2xacc.svg](python-cute-hopper-kernel-dense-gemm-dense-gemm-fp8-2xacc.svg) | Python example |
| `python/CuTeDSL/cute/hopper/kernel/dense_gemm/dense_gemm_fp8_gelu_persistent.py` | [python-cute-hopper-kernel-dense-gemm-dense-gemm-fp8-gelu-persistent.svg](python-cute-hopper-kernel-dense-gemm-dense-gemm-fp8-gelu-persistent.svg) | Python example |
| `python/CuTeDSL/cute/hopper/kernel/dense_gemm/dense_gemm_persistent.py` | [python-cute-hopper-kernel-dense-gemm-dense-gemm-persistent.svg](python-cute-hopper-kernel-dense-gemm-dense-gemm-persistent.svg) | Python example |
| `python/CuTeDSL/cute/hopper/kernel/grouped_gemm/grouped_gemm.py` | [python-cute-hopper-kernel-grouped-gemm-grouped-gemm.svg](python-cute-hopper-kernel-grouped-gemm-grouped-gemm.svg) | Python example |
| `python/CuTeDSL/cute_ext/blackwell/dense_block_scaled_gemm.py` | [python-cute-ext-blackwell-dense-block-scaled-gemm.svg](python-cute-ext-blackwell-dense-block-scaled-gemm.svg) | Python example |
| `python/CuTeDSL/cute_ext/blackwell/dense_gemm.py` | [python-cute-ext-blackwell-dense-gemm.svg](python-cute-ext-blackwell-dense-gemm.svg) | Python example |
| `python/CuTeDSL/cute_ext/blackwell/dense_gemm_2sm.py` | [python-cute-ext-blackwell-dense-gemm-2sm.svg](python-cute-ext-blackwell-dense-gemm-2sm.svg) | Python example |
| `python/CuTeDSL/cute_ext/blackwell/dense_gemm_cute_pipeline.py` | [python-cute-ext-blackwell-dense-gemm-cute-pipeline.svg](python-cute-ext-blackwell-dense-gemm-cute-pipeline.svg) | Python example |
| `python/CuTeDSL/cute_ext/blackwell/dense_gemm_ptr_array.py` | [python-cute-ext-blackwell-dense-gemm-ptr-array.svg](python-cute-ext-blackwell-dense-gemm-ptr-array.svg) | Python example |

Total: **41 C++ examples and 59 Python
examples/tutorials (100 diagrams).**
