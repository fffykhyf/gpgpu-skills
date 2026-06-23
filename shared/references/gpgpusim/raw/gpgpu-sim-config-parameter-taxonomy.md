# GPGPU-Sim Config Parameter Taxonomy

Source repo: `ref_submodule/gpgpu-sim`

Seed config:

- `configs/tested-cfgs/SM86_RTX3070/gpgpusim.config`
- `configs/tested-cfgs/SM86_RTX3070/config_ampere_islip.icnt`

Category set:

- `hardware-private`: architectural or microarchitectural design knob.
- `simulator-private`: simulator mode, calibration, fixed latency, queue artifact, idealization, or implementation control.
- `HW/SW ABI`: visible to compiler/runtime/kernel contract, including CUDA-compatibility fields.
- `test-only`: regression/benchmark stopping or harness controls.
- `debug-only`: trace, visualization, print, checkpoint, debug controls.

Exposure policy:

- `Yes`: good candidate for a simple-gpgpu skill knob.
- `Guarded`: expose only with caveat or under an optional CUDA/GPGPU-Sim compatibility profile.
- `No`: keep internal to simulator/debug/test notes.

## Functional / Frontend Parameters

| Parameter | Example | Category | Meaning / performance effect | Expose |
|---|---:|---|---|---|
| `-gpgpu_ptx_instruction_classification` | `0` | debug-only | PTX instruction classification/stat support | No |
| `-gpgpu_ptx_sim_mode` | `0` | simulator-private | selects functional-vs-performance simulation behavior | No |
| `-gpgpu_ptx_force_max_capability` | `86` | HW/SW ABI | CUDA/PTX capability compatibility | Guarded |
| `-gpgpu_ptx_convert_to_ptxplus` | `0` | simulator-private | legacy PTXPlus/SASS conversion | No |
| `-gpgpu_ptx_save_converted_ptxplus` | `0` | debug-only | saves converted PTXPlus | No |
| `-gpgpu_compute_capability_major` | `8` | HW/SW ABI | reported CUDA compute capability | Guarded |
| `-gpgpu_compute_capability_minor` | `6` | HW/SW ABI | reported CUDA compute capability | Guarded |

## Launch / Runtime Limits

| Parameter | Example | Category | Meaning / performance effect | Expose |
|---|---:|---|---|---|
| `-gpgpu_stack_size_limit` | `1024` | HW/SW ABI | CUDA-like device stack limit | Guarded |
| `-gpgpu_heap_size_limit` | `8388608` | HW/SW ABI | CUDA-like device heap limit | Guarded |
| `-gpgpu_runtime_sync_depth_limit` | `2` | HW/SW ABI | dynamic parallelism sync depth | Guarded |
| `-gpgpu_runtime_pending_launch_count_limit` | `2048` | HW/SW ABI | pending launch count limit | Guarded |
| `-gpgpu_kernel_launch_latency` | `5000` | simulator-private | launch delay calibration | No |
| `-gpgpu_TB_launch_latency` | `0` | simulator-private | thread-block launch delay calibration | No |
| `-gpgpu_max_concurrent_kernel` | `128` | hardware-private | concurrent kernel capacity model | Guarded |

## Topology / Clock / Occupancy

| Parameter | Example | Category | Meaning / performance effect | Expose |
|---|---:|---|---|---|
| `-gpgpu_n_clusters` | `46` | hardware-private | shader cluster count | Yes |
| `-gpgpu_n_cores_per_cluster` | `1` | hardware-private | SMs per cluster | Yes |
| `-gpgpu_n_mem` | `16` | hardware-private | memory channel count | Yes |
| `-gpgpu_n_sub_partition_per_mchannel` | `2` | hardware-private | L2/memory subpartitions per channel | Yes |
| `-gpgpu_clock_domains` | `1132:1132:1132:3500.5` | hardware-private | core/icnt/L2/DRAM clock domains | Guarded |
| `-gpgpu_shader_registers` | `65536` | hardware-private | registers per shader | Yes |
| `-gpgpu_registers_per_block` | `65536` | HW/SW ABI | per-block register limit visible to occupancy | Yes |
| `-gpgpu_occupancy_sm_number` | `86` | HW/SW ABI | occupancy-tool hint | Guarded |
| `-gpgpu_shader_core_pipeline` | `1536:32` | hardware-private | threads/warp-size style core pipeline config | Yes |
| `-gpgpu_shader_cta` | `32` | hardware-private | max CTA residency | Yes |
| `-gpgpu_simd_model` | `1` | simulator-private | internal SIMD timing model selector | No |

## Execution Units / Scheduler / Register File

| Parameter | Example | Category | Meaning / performance effect | Expose |
|---|---:|---|---|---|
| `-gpgpu_pipeline_widths` | `4,...,8,4,4` | hardware-private | ID/OC/EX/WB pipe widths | Yes |
| `-gpgpu_num_sp_units` | `4` | hardware-private | SP units per core | Yes |
| `-gpgpu_num_sfu_units` | `4` | hardware-private | SFU units per core | Yes |
| `-gpgpu_num_dp_units` | `4` | hardware-private | DP units per core | Yes |
| `-gpgpu_num_int_units` | `4` | hardware-private | INT units per core | Yes |
| `-gpgpu_tensor_core_avail` | `1` | hardware-private | tensor core availability | Guarded |
| `-gpgpu_num_tensor_core_units` | `4` | hardware-private | tensor core unit count | Guarded |
| `-ptx_opcode_latency_int/fp/dp/sfu/tensor` | varies | simulator-private | PTX timing calibration | No |
| `-ptx_opcode_initiation_int/fp/dp/sfu/tensor` | varies | simulator-private | PTX initiation interval calibration | No |
| `-gpgpu_sub_core_model` | `1` | hardware-private | per-scheduler isolated resources | Yes |
| `-gpgpu_enable_specialized_operand_collector` | `0` | hardware-private | operand collector organization | Yes |
| `-gpgpu_operand_collector_num_units_gen` | `8` | hardware-private | generic collector units | Yes |
| `-gpgpu_operand_collector_num_in_ports_gen` | `8` | hardware-private | collector input ports | Yes |
| `-gpgpu_operand_collector_num_out_ports_gen` | `8` | hardware-private | collector output ports | Yes |
| `-gpgpu_num_reg_banks` | `8` | hardware-private | register bank count | Yes |
| `-gpgpu_reg_file_port_throughput` | `2` | hardware-private | RF port/service throughput | Yes |
| `-gpgpu_num_sched_per_core` | `4` | hardware-private | warp schedulers per SM | Yes |
| `-gpgpu_scheduler` | `lrr` | hardware-private | scheduler policy | Yes |
| `-gpgpu_max_insn_issue_per_warp` | `1` | hardware-private | per-warp issue limit | Yes |
| `-gpgpu_dual_issue_diff_exec_units` | `1` | hardware-private | dual-issue restriction | Yes |

## L1 / Shared / Coalescing

| Parameter | Example | Category | Meaning / performance effect | Expose |
|---|---:|---|---|---|
| `-gpgpu_adaptive_cache_config` | `1` | hardware-private | adaptive L1/shared split | Guarded |
| `-gpgpu_shmem_option` | `0,8,16,32,64,100` | HW/SW ABI | shared-memory size options | Guarded |
| `-gpgpu_unified_l1d_size` | `128` | hardware-private | unified L1D/shared size | Yes |
| `-gpgpu_l1_banks` | `4` | hardware-private | L1 bank count | Yes |
| `-gpgpu_cache:dl1` | `S:4:128:256,...` | hardware-private | L1D geometry/policy/MSHR | Yes |
| `-gpgpu_l1_latency` | `39` | simulator-private | fixed L1 latency calibration | No |
| `-gpgpu_gmem_skip_L1D` | `0` | HW/SW ABI | global-memory L1D bypass behavior | Guarded |
| `-gpgpu_flush_l1_cache` | `1` | simulator-private | cache flush between kernels / consistency shortcut | No |
| `-gpgpu_n_cluster_ejection_buffer_size` | `32` | hardware-private | return-path cluster buffer | Yes |
| `-gpgpu_l1_cache_write_ratio` | `25` | simulator-private | write-ratio/cache control model | Guarded |
| `-gpgpu_shmem_size` | `102400` | hardware-private | shared memory per SM | Yes |
| `-gpgpu_shmem_sizeDefault` | `102400` | HW/SW ABI | default shared memory visible to runtime | Guarded |
| `-gpgpu_shmem_per_block` | `49152` | HW/SW ABI | per-block shared memory limit | Yes |
| `-gpgpu_smem_latency` | `29` | simulator-private | fixed shared latency calibration | No |
| `-gpgpu_shmem_num_banks` | `32` | hardware-private | shared bank count | Yes |
| `-gpgpu_shmem_limited_broadcast` | `0` | hardware-private | broadcast/conflict model | Yes |
| `-gpgpu_shmem_warp_parts` | `1` | hardware-private | split warp for bank-conflict model | Guarded |
| `-gpgpu_coalesce_arch` | `86` | simulator-private | NVIDIA-generation coalescing selector | Guarded |

## L2 / Memory Partition

| Parameter | Example | Category | Meaning / performance effect | Expose |
|---|---:|---|---|---|
| `-gpgpu_cache:dl2` | `S:64:128:16,...` | hardware-private | L2 geometry/policy/MSHR | Yes |
| `-gpgpu_cache:dl2_texture_only` | `0` | simulator-private | legacy texture-only behavior | No |
| `-gpgpu_dram_partition_queues` | `64:64:64:64` | hardware-private | ICNT/L2/DRAM/L2/ICNT queue sizes | Guarded |
| `-gpgpu_perf_sim_memcpy` | `1` | simulator-private | memcpy performance-mode handling | No |
| `-gpgpu_memory_partition_indexing` | `2` | hardware-private | partition indexing policy | Yes |
| `-gpgpu_l2_rop_latency` | `187` | simulator-private | fixed ROP/L2 delay | No |

## Instruction / Texture / Const

| Parameter | Example | Category | Meaning / performance effect | Expose |
|---|---:|---|---|---|
| `-gpgpu_cache:il1` | `N:64:128:16,...` | hardware-private | instruction cache geometry | Yes |
| `-gpgpu_inst_fetch_throughput` | `4` | hardware-private | fetch throughput | Yes |
| `-gpgpu_tex_cache:l1` | `N:4:128:256,...` | HW/SW ABI | legacy texture/cache behavior | Guarded |
| `-gpgpu_const_cache:l1` | `N:128:64:8,...` | HW/SW ABI | constant cache behavior | Guarded |
| `-gpgpu_perfect_inst_const_cache` | `1` | simulator-private | idealized I/const cache option | No |

## Interconnect / NoC

| Parameter | Example | Category | Meaning / performance effect | Expose |
|---|---:|---|---|---|
| `-network_mode` | `2` | simulator-private | selects Intersim vs local xbar backend | Guarded |
| `-icnt_in_buffer_limit` | `512` | hardware-private | ICNT input buffer capacity | Guarded |
| `-icnt_out_buffer_limit` | `512` | hardware-private | ICNT output buffer capacity | Guarded |
| `-icnt_subnets` | `2` | hardware-private | request/reply subnet count | Yes |
| `-icnt_flit_size` | `40` | hardware-private | flit size / packetization | Yes |
| `-icnt_arbiter_algo` | `1` | hardware-private | local xbar arbiter selector | Guarded |

BookSim `.icnt` fields:

| Parameter family | Category | Note |
|---|---|---|
| `topology`, `k`, `n`, `routing_function` | hardware-private | NoC topology/routing inspiration only |
| `num_vcs`, `vc_buf_size`, `input_buffer_size`, `ejection_buffer_size` | hardware-private | flow-control inspiration only |
| `vc_allocator`, `sw_allocator`, `alloc_iters`, allocator delays | hardware-private | NoC model detail, not SM86 active path |
| `sim_type`, `injection_rate`, `traffic`, packet-size synthetic fields | simulator-private / test-only | not used by GPGPU-Sim active traffic in SM86 |

## DRAM

| Parameter | Example | Category | Meaning / performance effect | Expose |
|---|---:|---|---|---|
| `-dram_latency` | `254` | simulator-private | fixed partition-to-DRAM latency | No |
| `-gpgpu_dram_scheduler` | `1` | hardware-private | FIFO vs FR-FCFS style scheduler | Yes |
| `-gpgpu_frfcfs_dram_sched_queue_size` | `64` | hardware-private | FR-FCFS queue size | Guarded |
| `-gpgpu_dram_return_queue_size` | `192` | hardware-private | DRAM return queue | Guarded |
| `-gpgpu_n_mem_per_ctrlr` | `1` | hardware-private | memory chips/controllers per controller | Yes |
| `-gpgpu_dram_buswidth` | `2` | hardware-private | DRAM bus width model | Yes |
| `-gpgpu_dram_burst_length` | `16` | hardware-private | DRAM burst length | Yes |
| `-dram_data_command_freq_ratio` | `4` | hardware-private | data/command frequency ratio | Yes |
| `-gpgpu_mem_address_mask` | `1` | hardware-private | address-mask control | Guarded |
| `-gpgpu_mem_addr_mapping` | mapping string | hardware-private | channel/bank/row/col mapping | Yes |
| `-gpgpu_dram_timing_opt` | timing string | hardware-private | bank/bank-group timing parameters | Yes |
| `-dram_dual_bus_interface` | `0` | hardware-private | dual-bus interface model | Guarded |
| `-dram_bnk_indexing_policy` | `0` | hardware-private | bank indexing function | Yes |
| `-dram_bnkgrp_indexing_policy` | `1` | hardware-private | bank-group indexing | Yes |
| `-dram_seperate_write_queue_enable` | commented | hardware-private | separate write queue | Guarded |
| `-dram_write_queue_size` | commented | hardware-private | write queue thresholds | Guarded |

## Stats / Visualization / Power / Trace

| Parameter | Example | Category | Meaning / performance effect | Expose |
|---|---:|---|---|---|
| `-gpgpu_memlatency_stat` | `14` | debug-only | memory latency stat flags | Guarded in simppa |
| `-gpgpu_runtime_stat` | `500` | debug-only | overloaded sample frequency and flags | Guarded in simppa |
| `-enable_ptx_file_line_stats` | `1` | debug-only | PTX line stats | No |
| `-visualizer_enabled` | `0` | debug-only | AerialVision output | Guarded in simppa |
| `-power_simulation_enabled` | `0` | simulator-private | AccelWattch enable | Guarded |
| `-trace_enabled` | commented | debug-only | trace stream enable | No |
| `-trace_components` | commented | debug-only | trace component selection | No |
| `-trace_sampling_core` | commented | debug-only | trace sample selector | No |

## Taxonomy Rules

1. Latency numbers from tested configs are not RTL contracts unless tied to a named hardware pipeline stage in simple-gpgpu.
2. Queue sizes can inspire stress tests but should not be copied as defaults.
3. NVIDIA compatibility fields are `HW/SW ABI` only under a CUDA/PTX compatibility profile.
4. Parser flags and visualizer flags belong to `gpgpu-simppa`, not `gpgpu-rtl`.
5. Every exposed parameter in a skill must include category, default/provenance, legal range or "unknown", and performance effect.
