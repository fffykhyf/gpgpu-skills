# GPGPU-Sim Atomics / Fence / Consistency Notes

Source repo: `ref_submodule/gpgpu-sim`

Primary files read in this pass:

- `src/gpgpu-sim/shader.cc`
- `src/abstract_hardware_model.cc`
- `src/gpgpu-sim/mem_fetch.cc`
- `src/gpgpu-sim/l2cache.cc`

Important gap:

- `src/cuda-sim/memory.cc` was not deeply read in the memory reader pass. Treat these notes as timing-side evidence, not a complete ISA memory-consistency specification.

## Atomics

Observed mechanisms:

- `warp_inst_t::generate_mem_accesses()` routes atomic memory requests through `memory_coalescing_arch_atomic`.
- atomic coalescing can split overlapping byte ranges into separate transactions.
- `mem_fetch::isatomic()` detects atomic requests.
- `mem_fetch::do_atomic()` executes the atomic action on memory return using the instruction object and warp mask.
- shader-side warp waiting tracks outstanding atomics.

Modeled behavior:

- global atomics complete when the memory response returns;
- shared-memory atomics are handled on the shader/writeback side;
- atomic completion is coupled to pending write / warp waiting behavior.

RTL contract candidates:

- atomics need explicit request type, lane mask, byte mask, destination register, and completion event.
- warp scheduler must know whether atomics create a wait condition.
- performance counters should distinguish atomic request count, atomic replay/split, and atomic completion latency.

Simulator-only:

- C++ callback through `warp_inst_t` on `mem_fetch::do_atomic`;
- exact coalescing behavior for NVIDIA PTX atomics unless simple-gpgpu chooses matching semantics.

## Memory Barrier / Fence

Observed mechanisms:

- `MEMORY_BARRIER_OP` in `shader_core_ctx::issue_warp` calls `shd_warp_t::set_membar()`.
- waiting logic checks membar state and scoreboard pending writes.
- reader pass found L1 invalidation behavior and a TODO-style fixed-stall comment around membar timing.

Design implication:

- GPGPU-Sim's membar timing is not a clean hardware contract.
- simple-gpgpu needs an explicit fence contract: scope, ordering domain, affected caches, completion condition, and counter/stall reason.

RTL contract candidates:

- `fence_issued` event with warp id and scope.
- `fence_pending` state until all prior memory operations reach required visibility point.
- optional cache invalidate/flush policy, if architecturally required.
- stall reason: `membar_wait`.

Simulator-only:

- fixed fence delay comments;
- direct L1 invalidation as a substitute for a complete consistency model.

## Barrier

Observed mechanisms:

- `BARRIER_OP` in `shader_core_ctx::issue_warp` calls barrier-set logic.
- warp state stores last instruction info at barrier.
- scheduler excludes waiting warps.

RTL contract candidates:

- CTA-scoped barrier arrival mask;
- expected participant count;
- release event;
- barrier wait stall counter.

Simulator-only:

- exact GPGPU-Sim barrier-set implementation details.

## Memory Consistency Boundary

Confirmed limitation:

- the timing-side files show atomics/fence/barrier hooks and some completion behavior, but do not by themselves define a full memory consistency model.

Reader-agent follow-up:

- read `src/cuda-sim/memory.cc`;
- read PTX instruction semantics for memory fences and atomics in `src/cuda-sim/instructions.cc`;
- connect functional semantics to timing events in `shader.cc`, `mem_fetch.cc`, and `l2cache.cc`.

## Design Rule

Rule name: synchronization is not just a stall

Problem solved: prevents atomics/fences/barriers from being collapsed into generic memory latency.

Required state contract:

- atomic outstanding count or completion tokens;
- fence pending state and scope;
- barrier arrival/release state;
- pending writes visible to synchronization logic.

Required config contract:

- no fixed latency should be exposed unless it models a deliberate hardware mechanism.

Required counter/stall reason:

- `atomic_wait`
- `membar_wait`
- `barrier_wait`
- `atomic_split_or_replay`
- `fence_flush_or_invalidate`

Applicable skill:

- `gpgpu-memory`
- `gpgpu-golden`
- `gpgpu-rtl`
- `gpgpu-simppa`

Implementation anchor:

- `src/gpgpu-sim/shader.cc:shader_core_ctx::issue_warp`
- `src/gpgpu-sim/shader.cc:shd_warp_t::waiting`
- `src/gpgpu-sim/mem_fetch.cc:mem_fetch::do_atomic`
- future read: `src/cuda-sim/memory.cc`
