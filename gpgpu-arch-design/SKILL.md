---
name: gpgpu-arch-design
description: Use when planning, staging, or reviewing GPGPU architecture across ISA, SIMT execution, simulator, RTL, runtime launch, configuration, tests, counters, memory hierarchy, PPA, FPGA bring-up, or roadmap decisions.
---

# GPGPU Architecture Design

## Overview

Use this skill as the top-level guardrail for local GPGPU work. A GPGPU is a full-stack system, so architecture work must state how ISA, simulator, RTL, runtime, kernel ABI, configuration, tests, and PPA evidence stay aligned. Use GPGPU-Sim as the reference for execution-driven runtime, functional/timing simulator separation, configurable timing models, trace/statistics, and power-evidence plumbing.

## Core Rule

Before changing or proposing any GPGPU feature, produce a layer impact table and a staged verification path.

| Layer | Typical artifacts | Required question |
|---|---|---|
| ISA | instruction semantics, encoding, CSR/DCR state | What architectural state changes? |
| Simulator | functional model, cycle model, golden trace | What is the executable reference? |
| RTL | SIMT core, LSU, cache, CP, interconnect | What is the valid-ready and stall contract? |
| Runtime | device, buffer, queue, launch, event, fence | How does host software start and observe work? |
| Kernel ABI | entry PC, args, grid/block/CTA/workgroup IDs | What does device code assume? |
| Config | private knobs, ABI constants, generated headers | Which values are visible across layers? |
| Tests | smoke, trace diff, regression, backend matrix | What proves this stage works? |
| Evaluation | counters, logs, SAIF, synthesis reports | What metric justifies the change? |

Do not silently modify multiple layers. Name each affected layer, the owner of each contract, and the smallest gate that proves it still works.

## Terminology Contract

Use canonical terms in new designs and docs. Keep source-specific names only when quoting a reference implementation.

| Canonical term | Source aliases | Meaning |
|---|---|---|
| SIMT group | warp, wavefront, wave | threads or work-items sharing PC, scheduler residency, and an active lane mask |
| simt_group_id | warp ID, `wfid`, wave ID, wavefront tag | identity for one resident SIMT group |
| active lane mask | active mask, thread mask, `tmask`, `EXEC` mask | per-lane participation mask for a SIMT group |
| CTA/workgroup | CTA, block, workgroup | launch group that contains one or more SIMT groups |
| compute core/CU | core, CU, compute unit | hardware unit that owns SIMT groups and execution resources |

Keep `simt_group_width`, `active_mask_width`, `physical_simd_width`, `resident_simt_groups`, and `test_thread_count` as separate quantities.

## Required Contracts

Every architecture design should include:

- Objective: one capability or hypothesis being tested.
- Non-goals: advanced features intentionally left out.
- State contract: PC, active lane mask, SIMT group state, registers, memory, CSR/DCR, and launch state.
- Config contract: classify each parameter as hardware-private, simulator-private, HW/SW ABI, test-only, or debug-only.
- Launch contract: program image, kernel entry, args, grid/block dimensions, start, done, result, and synchronization path.
- Simulation contract: functional oracle, timing model, shared kernel descriptor, trace schema, and backend mode selection.
- Test gate: simulator smoke, RTL trace diff, runtime launch test, counter check, or PPA report.
- Prototype credibility target: instruction unit tests, external golden trace, RTL simulation, FPGA smoke, benchmark run, synthesis report, or ASIC estimate.
- Implementation anchors: name the modules or planned modules that own the claim.

For any architecture proposal that should become a credible prototype, also record:

| Item | Required content |
|---|---|
| ISA scope | supported, planned, and explicitly unsupported instructions or features |
| CU organization | resident SIMT-group slots, issue width, active-mask width, physical SIMD width, SGPR/VGPR/LDS resources |
| Implementation anchors | fetch, wavepool, decode, issue, scoreboard, exec state, FU, LSU, dispatcher, or control-plane owner |
| Evidence path | unit test, external oracle trace, RTL tracemon diff, FPGA control path, PPA report |
| Credibility caveat | relaxed frequency, area, power, tooling, ISA, runtime, memory hierarchy, or benchmark assumptions |

Do not merge SIMT-group width, active-mask width, physical SIMD width, resident SIMT-group slots, and test thread count into one vague "lane count".

## Stage Order

1. Define the project skeleton, ISA sketch, SIMT state, configuration boundary, and minimal launch path.
2. Establish the functional simulator or golden trace, kernel descriptor, and launch shape before complex RTL.
3. Implement the minimal SIMT core: SIMT group state, active lane mask, scheduler, register file, ALU, commit.
4. Add memory in stages: blocking LSU, lane masks and byte enables, outstanding tags, response demux, then coalescing/cache.
5. Replace testbench pokes with a runtime or launch contract: load program, load args, start, wait, copy result.
6. Add counters before tuning: cycles, instructions, SIMT-group stalls, scoreboard stalls, memory stalls, load/store counts.
7. Add cache, VM, tensor, graphics, FPGA, or software ecosystem work only after the basic loop is debuggable.
8. Use PPA only after correctness gates pass.

## GPGPU-Sim Architecture Lens

When GPGPU-Sim is the reference, map the proposal onto this chain:

| Contract | GPGPU-Sim anchor | Local architecture question |
|---|---|---|
| Runtime entry | `cudaConfigureCallInternal`, `cudaSetupArgumentInternal`, `cudaLaunchInternal` | What object captures launch config and args before backend admission? |
| Work queue | `stream_manager`, `stream_operation` | How are memcpy, kernel launch, event, wait, and completion ordered? |
| Kernel descriptor | `kernel_info_t` | Where are entry, grid/block dimensions, stream ID, CTA progress, and resource requirements stored? |
| Functional oracle | `cuda-sim` | Which executable model owns ISA and memory semantics? |
| Timing model | `shader_core_ctx`, `scheduler_unit`, `warp_inst_t` | Which state is timing-only, and which state is architectural? |
| Memory hierarchy | `ldst_unit`, `mem_fetch`, L1/L2/DRAM/ICNT | What request carrier preserves SIMT context through memory? |
| Config/evidence | `option_parser`, `gpgpusim.config`, stats, trace, AccelWattch | Which workload, config, backend, counters, and power assumptions support the claim? |

Treat GPGPU-Sim as an executable architecture reference. Translate its C++ timing behavior into RTL state, valid-ready, reset, flush, arbitration, and backpressure before using it as hardware guidance.

## Skill Routing

Use the narrower skill when the task is mostly about one boundary:

| Task shape | Use |
|---|---|
| Parameter or ABI changes | `gpgpu-config` |
| Reference behavior or trace mismatch | `gpgpu-golden-sim` |
| SIMT RTL state or pipeline | `gpgpu-rtl-simt-core` |
| LSU, cache, coalescing, memory ordering | `gpgpu-memory-path` |
| Host/device launch, queue, event, kernel entry | `gpgpu-runtime` |
| Performance, power, area, timing | `gpgpu-ppa-evaluation` |

## Local References

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It explains the full-stack contract across RTL, simulator, runtime, ABI, config, tests, and PPA.

For deeper MIAOW background tied to this skill, read `miao_local.md` in this directory. It explains the MIAOW paper scope, CU source anchors, trace/test loop, FPGA control path, and prototype credibility caveats relevant to architecture work.

For deeper GPGPU-Sim background tied to this skill, read `gpgpusim_local.md` in this directory. It explains the execution-driven runtime path, functional/timing split, shader/memory hierarchy, config, trace/statistics, and power evidence relevant to architecture decisions.

## Common Mistakes

- Drawing only an RTL block diagram and omitting runtime, config, tests, or counters.
- Treating launch ABI and configuration as script details instead of architecture contracts.
- Adding cache, VM, tensor, OpenCL, HIP, Vulkan, or FPGA bring-up before a minimal SIMT loop is traceable.
- Letting testbench-only internal pokes become the permanent runtime interface.
- Changing several variables at once and calling the result an architecture conclusion.
- Treating a C++ timing simulator path as synthesizable RTL without defining hardware state, handshakes, and reset/flush behavior.
