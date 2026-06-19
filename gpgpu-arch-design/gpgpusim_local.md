# GPGPU-Sim Local Reference For GPGPU Architecture Design

This note expands the GPGPU-Sim references that matter for the `gpgpu-arch-design` skill. It focuses on the end-to-end simulator system: CUDA/OpenCL runtime interception, kernel launch, functional PTX execution, cycle-level SIMT timing, memory hierarchy, configuration, trace/statistics, and power modeling.

Terminology note: this file preserves GPGPU-Sim source names such as `warp`, `warp_id`, `active_mask`, `CTA`, and `shader core`. In the skill contract, map them to `SIMT group`, `simt_group_id`, `active lane mask`, `CTA/workgroup`, and `compute core/CU`; use GPGPU-Sim names only when quoting source behavior.

## What GPGPU-Sim Teaches For This Skill

GPGPU-Sim is most useful as an executable architecture-control reference. It is not a synthesizable RTL design, but it shows how a GPGPU system can keep these layers tied together:

- host runtime calls become kernel descriptors and stream operations;
- functional PTX execution and timing simulation share kernel, thread, warp, and memory abstractions;
- cycle-level shader core, scheduler, LSU, cache, interconnect, L2, and DRAM models are configured from one option system;
- trace, statistics, visualization, and AccelWattch power modeling are connected to the same workload/config path.

For architecture work, copy the full-stack evidence chain. Do not copy C++ simulator control flow as RTL.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/gpgpusim.md` | Local extraction of GPGPU-Sim lessons for all seven skills. |
| `ref_submodule/gpgpu-sim/README.md` | System scope: cycle-level GPU simulator, CUDA/OpenCL workloads, AerialVision, AccelWattch, SASS trace mode. |
| `ref_submodule/gpgpu-sim/libcuda/cuda_runtime_api.cc` | CUDA launch stack, argument setup, kernel launch, PDOM analysis entry. |
| `ref_submodule/gpgpu-sim/src/stream_manager.*` | Stream operation queue, memcpy/event/kernel launch, functional/performance dispatch. |
| `ref_submodule/gpgpu-sim/src/abstract_hardware_model.*` | `kernel_info_t`, `warp_inst_t`, `simt_stack`, active masks, memory access abstractions. |
| `ref_submodule/gpgpu-sim/src/cuda-sim/` | Functional PTX parser, IR, instruction semantics, thread state, memory model. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/gpu-sim.*` | GPU top-level, config registration, running kernels, CTA dispatch, memory partitions. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/shader.*` | Shader core pipeline, warp scheduler, scoreboard, operand collector, LSU. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/{gpu-cache,l2cache,dram,icnt_wrapper}.*` | Cache, L2, DRAM, memory partition, interconnect boundaries. |
| `ref_submodule/gpgpu-sim/configs/tested-cfgs/SM86_RTX3070/gpgpusim.config` | Example architecture/config instance tying runtime, core, memory, stats, trace, and power. |

## End-To-End Architecture Chain

Use this chain when checking whether a local architecture proposal is complete:

1. CUDA/OpenCL frontend intercepts host calls.
2. Launch config records grid, block, shared memory, arguments, and stream.
3. Runtime creates `kernel_info_t`.
4. `stream_manager` chooses functional or performance simulation.
5. `gpgpu_sim::launch()` admits the kernel into running-kernel slots.
6. `select_kernel()` chooses a kernel with remaining CTAs.
7. `issue_block2core()` allocates CTA resources, threads, warps, SIMT stacks, and barriers.
8. `shader_core_ctx::cycle()` advances writeback, execute, read operands, issue, decode, and fetch.
9. `scheduler_unit::cycle()` gates issue using SIMT stack PC, active mask, scoreboard, pipeline availability, and FU type.
10. `ldst_unit` generates memory requests that travel through L1, interconnect, L2, memory partition, and DRAM.
11. Stats, traces, visualization, and power events are attributed to the same kernel/config path.

Local architecture docs should have an equivalent path even if early implementations collapse several steps.

## Architecture Questions To Borrow

| Contract | GPGPU-Sim anchor | Local question |
|---|---|---|
| Runtime entry | `cudaConfigureCallInternal`, `cudaSetupArgumentInternal`, `cudaLaunchInternal` | What object represents a launch before hardware sees it? |
| Kernel descriptor | `kernel_info_t` | Where are grid/block dimensions, stream, entry, CTA progress, and launch latency stored? |
| Functional oracle | `cuda-sim` | Which executable model proves ISA and memory semantics? |
| Timing model | `shader_core_ctx`, `scheduler_unit`, `warp_inst_t` | Which state is timing-only, and which state is architectural? |
| Memory hierarchy | `ldst_unit`, `mem_fetch`, L1/L2/DRAM/ICNT | What request carrier preserves SIMT context across memory layers? |
| Config | `option_parser`, `gpgpusim.config` | Which values define this architecture instance? |
| Evidence | stats, trace, AerialVision, AccelWattch | Which counters and reports support the claim? |

## What Not To Copy

- Do not treat GPGPU-Sim as RTL. Its C++ queues and function calls need RTL state machines, valid/ready, flush, reset, and arbitration if implemented in hardware.
- Do not use PTX/CUDA assumptions as the local ISA contract unless the project explicitly targets PTX-like execution.
- Do not claim PPA from GPGPU-Sim timing or power counters as silicon evidence without RTL/synthesis/power-flow validation.
- Do not add the full cache/DRAM/trace stack before the minimal launch, functional oracle, and SIMT loop are stable.

