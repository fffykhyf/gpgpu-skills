# GPGPU-Sim Shader Core And Warp Scheduler Notes

Source repo: `ref_submodule/gpgpu-sim`

Primary files:

- `src/gpgpu-sim/shader.{h,cc}`
- `src/gpgpu-sim/scoreboard.{h,cc}`
- `src/abstract_hardware_model.{h,cc}`
- `src/gpgpu-sim/stats.h`
- `configs/tested-cfgs/SM86_RTX3070/gpgpusim.config`

## Microarchitecture State To Extract

Shader/SM state:

- CTA allocation state in `shader_core_ctx::issue_block2core`.
- per-warp state in `shd_warp_t`: CTA id, warp id, next PC, ibuffer, outstanding stores, atomic count, membar state, depbar/LDGSTS bookkeeping.
- SIMT state in `simt_stack`: PC, active mask, reconvergence PC, call depth, branch divergence cycle.
- scheduler state in `scheduler_unit` and derived scheduler policies.
- pipeline register sets for SP/INT/DP/SFU/MEM/TENSOR/specialized units.
- scoreboard pending destination registers.
- operand collector and register-bank state.
- LSU state: response FIFO, pending writes, L1/const/texture/shared paths.

## Scheduler Issue Gate

Confirmed issue gate in `scheduler_unit::cycle`:

1. Warp is valid and not exited.
2. Warp is not waiting at barrier, membar, atomics, or depbar.
3. Ibuffer has a valid next instruction.
4. SIMT stack top PC matches instruction PC; mismatch flushes ibuffer and redirects next PC.
5. `Scoreboard::checkCollision` reports no RAW/WAW collision.
6. The target execution pipe has a free slot.
7. Dual-issue policy allows the chosen execution unit type.
8. `shader_core_ctx::issue_warp` is called.

`issue_warp` then:

- copies static instruction fields into the pipe register;
- adds dynamic issue metadata;
- calls `func_exec_inst`, which generates memory accesses for loads/stores;
- handles barrier, membar, LDGSTS/DEPBAR bookkeeping;
- updates SIMT stack;
- reserves scoreboard destination registers;
- advances per-warp next PC.

## Config Parameters

Hardware-private candidates:

- `-gpgpu_n_clusters`
- `-gpgpu_n_cores_per_cluster`
- `-gpgpu_shader_core_pipeline`
- `-gpgpu_shader_cta`
- `-gpgpu_shader_registers`
- `-gpgpu_registers_per_block`
- `-gpgpu_pipeline_widths`
- `-gpgpu_num_sp_units`
- `-gpgpu_num_int_units`
- `-gpgpu_num_dp_units`
- `-gpgpu_num_sfu_units`
- `-gpgpu_tensor_core_avail`
- `-gpgpu_num_tensor_core_units`
- `-gpgpu_num_sched_per_core`
- `-gpgpu_scheduler`
- `-gpgpu_max_insn_issue_per_warp`
- `-gpgpu_dual_issue_diff_exec_units`
- `-gpgpu_sub_core_model`
- `-gpgpu_num_reg_banks`
- operand collector counts and ports

Simulator-private / guarded:

- `-ptx_opcode_latency_*`
- `-ptx_opcode_initiation_*`
- `-gpgpu_l1_latency`
- `-gpgpu_smem_latency`
- `m_num_writeback_clients = 5`
- `-gpgpu_num_mem_units`, registered with note that it is not hooked up.

HW/SW ABI relevant:

- register/shared-memory limits that affect occupancy and launch acceptance;
- compute capability only if CUDA compatibility is part of the intended frontend.

## Counters And Stall Reasons

Scheduler/issue counters:

- `shader_cycle_distro[0]`: idle/control style bucket.
- `shader_cycle_distro[1]`: scoreboard wait bucket.
- `shader_cycle_distro[2]` and active-count buckets: pipeline/issue accounting.
- `single_issue_nums`, `dual_issue_nums`.
- `WarpIssueSlotBreakdown`.
- `WarpIssueDynamicIdBreakdown`.
- `shaderinsncount`, `shaderwarpinsncount`, `shaderwarpdiv` in visualizer output.

Shader-memory stalls:

- `BK_CONF`: shared/L1 bank conflict.
- `ICNT_RC_FAIL`: interconnect injection/backpressure failure.
- `COAL_STALL`: coalescing/access queue still not drained.
- `DATA_PORT_STALL`: cache data-port pressure.

Defined but not proven live in this commit:

- `MSHR_RC_FAIL`
- `TLB_STALL`
- `WB_ICNT_RC_FAIL`
- `WB_CACHE_RSRV_FAIL`

## Performance Attribution Rules

- High `shader_cycle_distro[1]` with low issue counts points first to scoreboard dependencies, long-latency loads, or occupancy/resource pressure.
- High `BK_CONF` points to shared/L1 bank layout or access pattern.
- High `COAL_STALL` points to fragmented memory transaction formation or access queue drain limits.
- High `DATA_PORT_STALL` points to L1 data-port pressure.
- High `ICNT_RC_FAIL` should be checked against ICNT buffers and return-path counters before DRAM timing is blamed.

## RTL Contract Candidates

Safe to convert into design contracts:

- issue gate ordering and observable reasons for not issuing;
- per-warp PC and active-mask ownership;
- scoreboard reserve/check/release semantics;
- register-bank and operand-collector arbitration as a resource model;
- LSU request-generation interface and stall reason taxonomy.

Simulator-only:

- exact scheduler names such as `lrr` as final policy;
- exact issue width and FU counts from SM86;
- opcode latencies from PTX config;
- fixed queue depths;
- dynamic warp ID implementation;
- LDGSTS/DEPBAR if simple-gpgpu ISA does not include NVIDIA-specific behavior.

## Design Rule

Rule name: issue must explain non-issue

Problem solved: a GPGPU skill should never report low IPC without a mutually exclusive reason taxonomy.

Required state contract:

- warp valid/waiting state;
- SIMT top PC and active mask;
- scoreboard collision state;
- pipe availability;
- LSU backpressure state.

Required counter/stall reason:

- `idle/control`, `scoreboard`, `pipe unavailable`, `bank conflict`, `coalescing`, `ICNT`, `data port`.

Applicable skill:

- `gpgpu-arch`
- `gpgpu-rtl`
- `gpgpu-simppa`

Implementation anchor:

- `src/gpgpu-sim/shader.cc:scheduler_unit::cycle`
- `src/gpgpu-sim/shader.cc:shader_core_ctx::issue_warp`
