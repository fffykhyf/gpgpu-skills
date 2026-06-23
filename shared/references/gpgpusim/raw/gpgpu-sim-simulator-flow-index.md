# GPGPU-Sim Simulator Flow Index

Source repo: `ref_submodule/gpgpu-sim`

This document indexes the top-level control flow that reader agents should use before reading deeper modules.

## 1. Initialization And Config Parse

Entry point:

- `src/gpgpusim_entrypoint.cc:gpgpu_context::gpgpu_ptx_sim_init_perf`

Confirmed flow:

1. Creates/configures the option parser.
2. Registers PTX functional options.
3. Registers opcode latency/initiation options.
4. Registers interconnect options.
5. Registers `gpgpu_sim_config` options.
6. Parses `gpgpusim.config`.
7. Creates `exec_gpgpu_sim` or SST-mode simulator.
8. Creates `stream_manager`.

Design implication: the config surface is centralized enough that parameter taxonomy should start from this path, then fan out to option owners.

Simulator-only assumption: parsing and printing options is a simulator control-plane artifact, not hardware configuration storage.

## 2. CUDA Launch Boundary

Key files:

- `libcuda/cuda_runtime_api.cc`
- `libcuda/cuda_api_object.h`
- `src/stream_manager.*`
- `src/abstract_hardware_model.h`

Confirmed flow:

1. CUDA fatbin/function registration maps host function handles to `function_info`.
2. `cudaConfigureCallInternal` pushes grid/block/shared-memory/stream config.
3. `cudaSetupArgumentInternal` records aligned argument bytes.
4. `cudaLaunchInternal` creates a `kernel_info_t`.
5. The kernel becomes a `stream_operation`.
6. `stream_manager::operation()` eventually calls `stream_operation::do_operation()`.

Transferable contract:

- launch descriptor: grid dims, block dims, shared-memory bytes, kernel symbol/function id, argument layout;
- `kernel_info_t` style object as a golden/runtime handoff structure.

Do not copy:

- CUDA launch stack implementation;
- stream-zero priority policy;
- `gpgpu_kernel_launch_latency` as RTL truth;
- compute capability as simple-gpgpu ISA truth.

## 3. OpenCL Launch Boundary

Key file:

- `libopencl/opencl_runtime_api.cc`

OpenCL builds launch shape and arguments similarly but is not mediated by the same CUDA stream stack. The useful abstraction is that CUDA/OpenCL both reduce frontend APIs into a kernel launch descriptor; the frontend-specific ABI should not leak into the core GPGPU skill unless the project explicitly chooses to emulate it.

## 4. Functional Vs Timing Branch

Key file:

- `src/stream_manager.cc:stream_operation::do_operation`

Confirmed branch:

- functional mode calls `gpgpu_sim::functional_launch()`;
- timing mode checks `gpu->can_start_kernel()` and launch latency, then calls `gpgpu_sim::launch()`.

Functional path:

- `gpgpu_sim::functional_launch`
- `cuda_sim::gpgpu_cuda_ptx_sim_main_func`
- `functionalCoreSim::execute`
- functional SIMT update in `src/abstract_hardware_model.cc`

Timing path:

- `gpgpu_sim::launch`
- `gpgpu_sim::select_kernel`
- `shader_core_ctx::issue_block2core`
- `gpgpu_sim::cycle`

Design rule: future skills should keep a clean boundary between golden functional semantics and timing/performance attribution. A timing stall must not redefine functional correctness.

## 5. Timing Cycle Flow

GPU-level files:

- `src/gpgpu-sim/gpu-sim.cc`
- `src/gpgpu-sim/gpu-sim.h`

Core-level file:

- `src/gpgpu-sim/shader.cc:shader_core_ctx::cycle`

Confirmed core cycle order:

1. `writeback()`
2. `execute()`
3. `read_operands()`
4. `issue()`
5. decode/fetch loop bounded by instruction fetch throughput

Confirmed memory/interconnect cycle structure:

- memory partitions and DRAM are clock-domain advanced in `gpgpu_sim::cycle`;
- ICNT transfer is abstracted through `icnt_wrapper`;
- return traffic can stall at cluster response FIFO or LSU response FIFO.

## 6. Counter Hooks In Flow

Important counters and events:

- `shader_cycle_distro[0/1/2]`: idle/control, scoreboard wait, pipeline-stalled buckets.
- `gpu_stall_shd_mem_breakdown[access_type][stall_type]`: shader memory stall attribution.
- `gpu_stall_dramfull`: memory partition / DRAM ingress backpressure.
- `gpu_stall_icnt2sh`: memory-to-shader return congestion.
- `gpu_sim_cycle`, `gpu_sim_insn`, `gpu_tot_issued_cta`, occupancy printouts: simulator progress/statistics.

Do not treat top-level counters as architectural state. Treat them as report dimensions and regression gates.

## Design Rule

Rule name: two-plane simulator flow

Problem solved: keeps golden behavior and timing attribution separate.

Required state contract:

- launch descriptor and `kernel_info_t` on the frontend/golden side;
- warp/core/cache/memory state on timing side;
- counters as observations, not causal truth by themselves.

Required counter/stall reason:

- every performance conclusion must cite the flow stage that produces the stall or counter.

Applicable skill:

- `gpgpu-golden`
- `gpgpu-runtime`
- `gpgpu-arch`
- `gpgpu-simppa`

Implementation anchor:

- `src/gpgpusim_entrypoint.cc`
- `src/stream_manager.cc`
- `src/gpgpu-sim/gpu-sim.cc`
- `src/gpgpu-sim/shader.cc`
