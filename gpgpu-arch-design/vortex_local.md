# Vortex Local Notes For `gpgpu-arch-design`

This file is the local Vortex reference for the architecture-design skill. It summarizes the parts of Vortex that matter for staged GPGPU architecture work, including both design documents and code implementation patterns. It is not a request to clone Vortex.

Terminology note: this file preserves Vortex source names such as `warp`, `warp ID`, `tmask`, and `CTA`. In the skill contract, map them to `SIMT group`, `simt_group_id`, `active lane mask`, and `CTA/workgroup`; use Vortex names only when quoting source behavior.

## What To Learn From Vortex

Vortex is useful here because it treats a GPGPU as a full-stack system, not as a standalone RTL core. Its design keeps these layers tied together:

- hardware RTL: `ref_submodule/vortex/hw/rtl/`
- cycle-approximate simulator: `ref_submodule/vortex/sim/simx/`
- runtime and backend drivers: `ref_submodule/vortex/sw/runtime/`
- device-side kernel ABI: `ref_submodule/vortex/sw/kernel/`
- tests and backend runner: `ref_submodule/vortex/tests/`, `ref_submodule/vortex/ci/blackbox.sh`
- configuration and ABI sources: `ref_submodule/vortex/VX_config.toml`, `ref_submodule/vortex/VX_types.toml`
- PPA and synthesis evidence: `ref_submodule/vortex/docs/synthesis_analysis.md`, `ref_submodule/vortex/hw/syn/`

The architecture-design takeaway is that every new feature should declare its layer impact, state contract, config contract, launch contract, and verification gate before implementation starts.

## Full-Stack Layout

### Design documents

`ref_submodule/vortex/README.md` presents Vortex as a full-stack RISC-V GPGPU. It explicitly lists multiple backend drivers: SimX, RTL simulation, and FPGA targets. The important design idea is that one workload can be routed through different backends, which makes architecture work testable at multiple fidelity levels.

`ref_submodule/vortex/docs/codebase.md` shows the ownership split:

- `hw/rtl`: core pipeline, cache, memory, FPU, interfaces, libs, tensor core.
- `hw/syn`: synthesis flows for FPGA, ASIC, and open-source flows.
- `sw/runtime`: host runtime APIs and backend drivers.
- `sw/kernel`: device-side APIs, startup code, and link scripts.
- `sim`: SimX and RTL/AFU simulators.
- `tests`: RISC-V, kernel, regression, OpenCL, runtime, graphics, and backend tests.

### Skill implication

When designing architecture locally, do not stop at an RTL block diagram. Ask what changes in:

- ISA or device-visible state
- simulator reference behavior
- RTL state and valid-ready contract
- runtime launch/API path
- kernel ABI or entry assumptions
- shared/private configuration
- tests and trace evidence
- counters/PPA evidence

## SIMT State And Core Pipeline

### Design documents

`ref_submodule/vortex/docs/microarchitecture.md` defines Vortex's SIMT model:

- A thread is the smallest execution unit.
- A warp shares a PC and uses a thread/active mask for per-lane participation.
- `TMC` changes thread mask.
- `WSPAWN` activates multiple warps and jumps to a PC.
- `SPLIT`, `JOIN`, and `PRED` manage divergence and reconvergence through IPDOM state.
- `BAR` stalls warps until a barrier releases.
- The pipeline is schedule, fetch, decode, issue, execute, commit.

This is the reason `gpgpu-arch-design` asks for an explicit state contract: PC, active mask, warp state, registers, memory, CSR/DCR, and launch state are architecture-level concepts.

### RTL implementation details

`ref_submodule/vortex/hw/rtl/core/VX_core.sv` wires the core as a set of explicit pipeline and control boundaries:

- `VX_scheduler` owns warp scheduling and SIMT control state.
- `VX_fetch` consumes `schedule_if` and talks to I-cache.
- `VX_decode` translates fetched instruction data and reports scheduler unlock information.
- `VX_issue` owns per-issue slices, instruction buffers, scoreboard/operand path ownership, and dispatch to execution units.
- `VX_execute` owns ALU/FPU/LSU/SFU/TCU execution and exposes `warp_ctl_if`, `branch_ctl_if`, and LSU client interfaces.
- `VX_commit` arbitrates results, produces writeback, and reports committed warps back to the scheduler.
- `VX_lsu_scheduler` and `VX_mem_unit` sit between execute and memory.
- `VX_dcr_data` and DCR flush interfaces connect runtime-visible control to core/cache behavior.

The key implementation pattern is that architecture state is not hidden in a monolithic block. Pipeline stages exchange typed interfaces such as `schedule_if`, `fetch_if`, `decode_if`, `dispatch_if`, `commit_if`, `writeback_if`, `warp_ctl_if`, and `branch_ctl_if`.

`ref_submodule/vortex/hw/rtl/core/VX_scheduler.sv` is the best concrete source for SIMT architectural state. It stores:

- `active_warps`: which warps are live.
- `stalled_warps`: which warps cannot be scheduled.
- `thread_masks`: active lane masks per warp.
- `warp_pcs`: PC per warp.
- `mscratch_r`: per-warp kernel argument pointer/state.
- `cta_id_per_warp_r`: mapping from warp to CTA.
- trap CSRs such as `mstatus_r`, `mtvec_r`, `mepc_r`, `mcause_r`, `mtval_r`.
- per-CTA and per-warp context RAMs containing CTA size, block index, block dim, grid dim, lmem address, cluster size, and entry PC.

The scheduler updates those states in response to:

- CTA dispatch from `VX_cta_dispatch`.
- `WSPAWN`, `TMC`, `SPLIT`, `JOIN`, `BAR`, `wsync`.
- branch resolution and trap/mret handling.
- schedule fire, decode unlock, and commit events.

It selects ready work as `active_warps & ~stalled_warps`, filters on instruction-buffer fullness, chooses a warp with `VX_priority_encoder`, then emits `schedule_if.data` containing thread mask, PC, warp ID, CTA ID, and UUID. This is exactly the type of state contract a local architecture design should spell out before implementing a scheduler.

`ref_submodule/vortex/hw/rtl/core/VX_issue.sv` shows how issue width is handled without mixing all behavior in one module. It splits decode traffic by `wid_to_isw`, creates one `VX_issue_slice` per issue slot, transposes dispatch interfaces by execution unit, and reports issued warp IDs to the scheduler. This supports the architecture rule: issue width and warp partitioning are config-sensitive contracts, not scattered constants.

`ref_submodule/vortex/hw/rtl/core/VX_commit.sv` shows commit/writeback as another explicit boundary. It arbitrates results from execution units per issue slot, builds `committed_warp_mask` from EOP results, and writes back lane-masked data with byte enables. It also emits debug trace fields including warp ID, CTA ID, PC, thread mask, writeback metadata, data, and UUID. This is why local designs should keep trace identity and writeback semantics visible.

### Skill implication

For architecture design, require at least this state table:

| State | Owner | Must answer |
|---|---|---|
| PC | scheduler or warp table | when it increments, branches, traps, or rewinds |
| active mask | scheduler/divergence unit | how inactive lanes affect writeback and memory |
| warp lifecycle | scheduler | inactive, ready, stalled, barrier, replay, done |
| CTA context | launch/CTA dispatcher/scheduler | grid/block/thread IDs, CTA rank, local memory |
| register state | operand/register file path | read/writeback, hazards, byte enables |
| memory state | LSU/memory path | request tags, response routing, ordering |
| control state | CSR/DCR/runtime | host-visible knobs and device-visible state |

## Kernel Launch, CTA Dispatch, And Runtime Boundary

### Design documents

`ref_submodule/vortex/docs/designs/vortex_runtime_api.md` describes the public runtime API. The stable surface is handle-based: device, buffer, queue, event, module, and kernel handles. The important architecture lesson is that host software does not poke arbitrary RTL internals; it goes through a runtime and backend transport.

`ref_submodule/vortex/docs/designs/command_processor_control_plane.md` describes the command processor. Host code builds command cache lines in a ring in host memory, rings a doorbell, and the command processor fetches commands. Commands include memory copy, DCR write/read, launch, fence, event wait/signal, and cache flush. This makes launch, synchronization, DMA, and cache maintenance part of the architecture boundary.

`ref_submodule/vortex/docs/designs/kernel_entry_and_dispatch.md` describes kernel entry. The runtime loads a module, resolves a named kernel to an entry PC, stages arguments, and programs startup and entry DCRs. Device-side startup code receives the args pointer and jumps through the selected entry.

`ref_submodule/vortex/docs/designs/cta_clustering_and_dispatch.md` describes how the KMU emits CTA requests and how the per-core dispatcher maps them to warps and local-memory placement.

### Runtime implementation details

`ref_submodule/vortex/sw/runtime/common/device.cpp` implements CP setup and command submission:

- `Device::cp_init()` allocates host-visible command ring, head, and completion memory.
- It programs queue registers such as ring base, head address, completion address, ring size, queue enable, and global CP enable.
- It reads device capability registers to discover features such as VM support instead of hard-coding assumptions in runtime code.
- `Device::cp_submit_cl_()` writes one 64-byte command line into the ring, bumps the tail, uses a release fence before the doorbell, writes `Q_TAIL_LO/HI`, then polls `Q_SEQNUM` until completion.

This is the concrete implementation behind the skill rule "do not let testbench pokes become the runtime interface." Even if a local project starts smaller than Vortex, it should still define load, args, start, wait, completion, and result paths.

`ref_submodule/vortex/sw/runtime/common/queue.cpp` implements launch:

- `Queue::enqueue_launch()` validates `vx_launch_info_t`.
- It retains a `Kernel` handle so module image and kernel PC survive until launch retirement.
- It copies the host args blob immediately, then stages it into a device scratch slot.
- It queries runtime capabilities for number of threads and warps.
- It computes `block_size` and warp step values.
- It programs KMU DCRs for startup PC, kernel entry PC, args address, block dims, grid dims, local memory size, block size, warp steps, and cluster dims.
- It submits `CMD_LAUNCH` through `Device::cp_submit_launch()` and only releases staged args after launch retirement.

This is the concrete implementation behind the `Launch contract` in `SKILL.md`: program/module, kernel entry, args, grid/block shape, start, wait, done, and cleanup must be specified together.

### Control-plane RTL implementation details

`ref_submodule/vortex/hw/rtl/cp/VX_cp_pkg.sv` defines the command ABI:

- command opcodes: `CMD_MEM_WRITE`, `CMD_MEM_READ`, `CMD_MEM_COPY`, `CMD_DCR_WRITE`, `CMD_DCR_READ`, `CMD_LAUNCH`, `CMD_FENCE`, `CMD_EVENT_SIGNAL`, `CMD_EVENT_WAIT`, `CMD_CACHE_FLUSH`.
- command header fields: reserved bits, flags, opcode.
- `cmd_t` payload: header plus three 64-bit args and optional profile slot.
- per-queue state: ring base, ring mask, head/completion addresses, tail, head, seqnum, priority, enable, profile flag.

`ref_submodule/vortex/hw/rtl/cp/VX_cp_core.sv` integrates the command processor:

- `VX_cp_axil_regfile` is the host-visible AXI-Lite control register block.
- One fetch+engine pair exists per queue.
- Four resource arbiters serialize access to KMU launch, DMA, DCR, and event resources.
- A host AXI crossbar carries command fetch, completion writes, and host side DMA.
- A device AXI crossbar carries device side DMA and event traffic.
- The GPU-facing interface connects DCR and start/busy handshakes to Vortex.

This shows how Vortex turns host/device control into a real hardware boundary. A smaller project can use a simpler command path, but the architecture design should still name which layer owns launch, DCR/config writes, memory movement, completion, and synchronization.

### KMU and CTA RTL implementation details

`ref_submodule/vortex/hw/rtl/VX_kmu.sv` receives launch DCRs:

- startup PC
- kernel entry PC
- startup args pointer
- grid dimensions
- block dimensions
- local memory size
- block size
- warp steps
- cluster dimensions

It then walks the grid and emits one CTA request at a time. The implementation uses `group_origin` and `intra_offset` to walk clustered CTAs contiguously. It precomputes `cluster_size`, aligned local-memory size, and cluster span so downstream dispatch can avoid expensive per-CTA multiplication.

`ref_submodule/vortex/hw/rtl/core/VX_cta_dispatch.sv` accepts KMU CTA requests and maps them to available warps. It maintains:

- CTA slot ring state.
- remaining-warps tables.
- local-memory ring allocation.
- `cta_slot_per_warp_r` reverse lookup for retirement.
- per-dispatch registers for PC, entry, block/grid dimensions, args, local memory, cluster size, thread index, and active mask.

It also enforces local-memory admission. For cluster starts, it reserves the whole cluster span so cluster members remain contiguous. This is a concrete example of a launch-time architecture rule becoming hardware state, scheduler-visible CSR state, and runtime-visible config.

### Skill implication

For any architecture feature involving launch or work distribution, require:

- host-visible launch representation
- device-side state representation
- runtime programming sequence
- simulator representation
- RTL ownership
- test workload that uses the real launch path

## SimX As Architecture Twin

### Design documents

`ref_submodule/vortex/docs/designs/simx_simulator_architecture.md` states the important rule: SimX has no central `Emulator`. ISA semantics and timing behavior live in module-like simulator objects matching hardware boundaries. Scheduler, decoder, scoreboard, operands, functional units, LSU, coalescer, caches, and memory are separate owners.

This matters for architecture design because a simulator should not be a separate world that only checks final outputs. It should be able to explain why RTL and reference behavior diverge.

### SimX implementation details

`ref_submodule/vortex/sim/simx/core.cpp` constructs a module graph similar to RTL:

- `Scheduler`
- `Decoder`
- optional `Decompressor`
- `Scoreboard`
- one `Sequencer` per warp
- `Operands`
- per-warp instruction buffers
- memory coalescers
- local memory and local-memory switch
- LSU memory adapters
- optional MMUs
- dispatchers for ALU, FPU, LSU, SFU, and optional TCU
- functional units such as `AluUnit`, `FpuUnit`, `LsuUnit`, `SfuUnit`
- commit arbiters

This is not just a software convenience. It lets architecture work be prototyped in SimX and then compared against RTL at similar boundaries.

`ref_submodule/vortex/sim/simx/scheduler.cpp` mirrors scheduler-owned state:

- `warp_t` carries thread mask, PC, UUID, mscratch, FCSR, trap CSRs, and CTA CSRs.
- `Scheduler::activate_warp()` loads CTA context into warp state, sets PC/tmask/mscratch, clears IPDOM stack, activates the warp, and clears stall state.
- `Scheduler::schedule()` dispatches one CTA warp if available, processes `wspawn`, picks an active non-stalled warp, creates an `instr_trace_t` with UUID, core ID, warp ID, CTA ID, PC, and thread mask, then suspends the warp until later decode/commit/FU progress.
- `suspend()` and `resume()` operate on next-state stall masks, matching hardware's registered scheduling behavior.
- `setTmask()` updates a warp thread mask and retires a warp/CTA when no lanes remain active.

This is the concrete basis for the skill rule: for every architecture feature, decide what the simulator twin owns and what trace fields prove behavior.

### Skill implication

Before complex RTL, define:

- simulator module owner
- corresponding RTL owner
- trace identity fields
- first-divergence comparison plan

For architecture-level work, a minimum trace should include cycle or sequence, core, warp, CTA, PC, instruction, active mask, writeback, memory request/response, and stall/replay reason when relevant.

## Configuration Boundary

### Design documents

`ref_submodule/vortex/docs/designs/build_configuration_system.md` explains Vortex's two-file split:

- `VX_config.toml`: hardware/simulator-private build configuration such as core count, warp count, thread count, issue width, cache sizes, queue depths, extension enables, pipeline latencies, and debug knobs.
- `VX_types.toml`: software-visible ISA/ABI contract such as CSR/DCR numbers, memory map, VM page format, CTA CSRs, device-visible constants, performance counter addresses, and enums.

The design rule is that private microarchitecture parameters and HW/SW ABI constants must not drift into each other accidentally.

### Implementation details

`ref_submodule/vortex/ci/gen_config.py` reads TOML, supports `expr:` values, public uppercase symbols, private lowercase helper values, enums, builtins, and multiple output formats:

- Verilog headers
- C/C++ headers
- compiler flags

It can emit unresolved preprocessor-friendly definitions or resolved constants. This lets RTL, simulator, runtime, and tests share config without copying values by hand.

`ref_submodule/vortex/configure` drives generation:

- copies project files into the build directory
- exports `XLEN`
- generates `<build>/hw/VX_config.vh` and `<build>/sw/VX_config.h`
- generates `<build>/hw/VX_types.vh` and `<build>/sw/VX_types.h`
- uses resolved output for `VX_types`

`ref_submodule/vortex/hw/rtl/VX_define.vh` is the RTL include point for generated config/type macros. Runtime capability logic is in `ref_submodule/vortex/sw/runtime/common/caps.h` and device initialization reads capability registers in `device.cpp`.

### Skill implication

For local architecture design, every parameter must be classified:

- hardware-private: pipeline depth, queue size, MSHR size, issue width
- simulator-private: debug level, model-only timing
- HW/SW ABI: memory map, CSR/DCR numbers, launch arg layout, capability bits
- test-only: tiny test sizes
- debug-only: traces, watchdogs, assertions

If software can observe a value, define how it is generated, queried, tested, and versioned.

## Memory Path At Architecture Level

Detailed LSU/cache work belongs in `gpgpu-memory-path`, but architecture design still needs to place memory in the full-stack contract.

`ref_submodule/vortex/docs/designs/lsu_pipeline_design.md` describes a two-stage LSU:

- frontend: AGU, address classification, byte enables, store-data shifting, fence lock, response formatting
- backend: request queue, index buffer, optional coalescer, batching, out-of-order response demux

`ref_submodule/vortex/docs/cache_subsystem.md` describes bank dispatch, response merge, MSHR, memory request mux/demux, flush, and deadlock prevention.

`VX_core.sv` shows architecture-level wiring:

- execute emits LSU client interfaces.
- per-block `VX_lsu_scheduler` arbitrates clients and controls queue sizing.
- `VX_mem_unit` owns local memory, dcache path, coalescer counters, and DCR flush.
- optional `VX_mmu` instances sit between dcache/icache paths and external memory buses.
- barriers use `warp_ctl_if.lsu_sched_drained` so memory drain becomes part of warp-control behavior.
- performance counters count ifetches, loads, stores, and latency through pending-read accumulation.

### Skill implication

In architecture design, do not simply write "add memory." Specify:

- is this scalar blocking LSU, vector lane memory, non-blocking loads, coalescing, cache, or VM?
- how are lane masks, byte enables, tags, and responses represented?
- how does it interact with scheduler, barriers, runtime cache flush, and counters?

## Testing, Debug, And PPA Evidence

### Design documents

`ref_submodule/vortex/docs/simulation.md` documents the `blackbox.sh` driver. It can select backend, clusters, cores, warps, threads, cache options, debug/perf flags, app, and args. This is important because architecture claims are tied to a backend/config/workload tuple.

`ref_submodule/vortex/docs/testing.md` describes running regression and OpenCL tests under simx and rtlsim, and how a new regression test contains host code, kernel code, and Makefile integration.

`ref_submodule/vortex/docs/debugging.md` describes debug logs, VCD traces, `trace_csv.py`, UUID-sorted simx/rtlsim trace diff, and SAIF capture. This supports first-divergence debugging and power analysis.

`ref_submodule/vortex/docs/synthesis_analysis.md` describes synthesis and power flows. It requires configuration flags, isolated build prefixes, SAIF/VCD activity, utilization reports, timing reports, WNS/Fmax, and vectorless versus activity-annotated power.

### Skill implication

For architecture design, a stage is not complete because the diagram is plausible. Require one of:

- simulator smoke test
- RTL trace diff
- runtime launch test
- config matrix smoke test
- counter report
- synthesis/timing/power report

For PPA claims, always bind:

- baseline
- variant
- workload
- backend
- config
- correctness state
- counters
- report path
- interpretation

## How To Use This In `gpgpu-arch-design`

When writing or reviewing a local GPGPU architecture design, ask for this output:

| Section | Required content |
|---|---|
| Objective | one capability or hypothesis |
| Layer impact | ISA, simulator, RTL, runtime, kernel ABI, config, tests, PPA |
| State contract | PC, masks, warp state, registers, memory, CSR/DCR, launch |
| Module ownership | simulator owner and RTL owner |
| Config contract | private versus HW/SW ABI values |
| Launch contract | module/program, entry PC, args, grid/block/CTA, start/done |
| Trace contract | fields needed for simulator/RTL comparison |
| Verification gate | smallest backend/config/workload evidence |
| Deferrals | advanced Vortex-like features intentionally not implemented |

## What Not To Import From Vortex By Default

Do not make these first-stage requirements unless the user asks or the project goal needs them:

- full RISC-V compatibility
- OpenCL, HIP, Vulkan, graphics, or tensor stack
- full command processor
- FPGA shell integration
- VM/TLB/PTW
- multi-queue async runtime
- cluster-contiguous local-memory placement
- all Vortex performance counters

Use Vortex as a mature example of boundaries and evidence. Copy the discipline, not necessarily the feature set.
