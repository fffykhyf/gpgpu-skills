# gpgpusim Source Summary

Distilled active summary from archived reference notes.

## README

# GPGPU-Sim Evidence References

This directory is evidence reference, not a design source of truth.

All imported mechanisms must be rewritten into project-owned contracts before
they can affect architecture, golden semantics, runtime ABI, RTL, counters, or
rewrite routing. The raw reader reports remain archived outside the compact package; skill files must cite
the rule they adopt, not paste GPGPU-Sim implementation details as design truth.

Required intake order:

1. `source_map.md`
2. `design_rules.md`
3. `do_not_copy.md`
4. `config_parameter_taxonomy.md`
5. `scheduler_scoreboard_simt.md`
6. `memory_coalescing.md`
7. `l2_noc_dram.md`
8. `atomic_fence_barrier.md`
9. `counter_stall_taxonomy.md`
10. `performance_attribution.md`
11. `power_energy_boundary.md`

Global rule: classify every imported state, parameter, and counter before a
skill uses it.

## atomic_fence_barrier

# Atomic, Fence, and Barrier Rules

Synchronization is not a generic memory stall.

Atomic contracts must define operation type, address, lane mask, byte mask,
return-value behavior, destination register if any, completion event,
serialization domain, and scoreboard release condition.

Fence contracts must define scope, ordering domain, affected memory spaces,
visibility point, completion condition, cache flush or invalidate policy, and
stall reason.

Barrier contracts must define CTA id, expected participant count, arrival mask,
release condition, waiting warp list, and release event.

Important caveat: the GPGPU-Sim atomics/fence notes in this reference set are
timing-side evidence only. Full memory consistency semantics must be defined in
the project-owned golden contract or by a future deeper `cuda-sim/memory.cc`
reader pass.

Raw basis: `archived_raw:gpgpu-sim-atomics-fence-consistency-notes.md`.

## config_parameter_taxonomy

# Config Parameter Taxonomy

Every external reference parameter must be classified before use:

- `hardware-private`: internal architectural or microarchitectural knob.
- `simulator-private`: simulator mode, calibration, idealization, queue
  artifact, fixed latency, or implementation control.
- `HW/SW ABI`: visible to compiler, runtime, kernel launch, occupancy, or
  compatibility contract.
- `test-only`: regression, benchmark, stopping, or harness control.
- `debug-only`: trace, visualization, print, checkpoint, or debug control.

Exposure policy:

- `Yes`: may become a simple-gpgpu design knob after provenance and range are
  recorded.
- `Guarded`: only under caveat or optional compatibility profile.
- `No`: must stay out of hardware contracts.

Every exposed parameter must include category, default/provenance, legal range
or `unknown`, performance effect, owner skill, and whether it enters a hardware
contract.

Raw basis: `archived_raw:gpgpu-sim-config-parameter-taxonomy.md`.

## counter_stall_taxonomy

# Counter and Stall Taxonomy

Counter status classes:

- `producer-backed`: source path emits or updates the counter.
- `defined-only`: enum, printer, schema, or declaration exists, but producer is
  not proven.
- `parser-only`: visualization/parser variable exists without producer proof.

Stable stall reasons:

- `idle_control`
- `ibuffer_empty`
- `simt_redirect`
- `scoreboard_wait`
- `pipe_unavailable`
- `barrier_wait`
- `membar_wait`
- `atomic_wait`
- `shared_bank_conflict`
- `coalescing_stall`
- `cache_miss`
- `cache_reservation_fail`
- `mshr_fail`
- `icnt_req_backpressure`
- `icnt_return_backpressure`
- `l2_queue_full`
- `dram_queue_full`
- `dram_timing_wait`
- `return_path_stall`
- `scoreboard_release_wait`

Root-cause reports must cite producer-backed counters for stable conclusions.
Defined-only and parser-only counters can explain gaps or motivate producer
patches, but cannot be the sole regression gate.

Raw basis: `archived_raw:gpgpu-sim-counter-and-stall-reason-taxonomy.md`.

## design_rules

# GPGPU-Sim Derived Design Rules

These rules are imported methodology, not copied implementation.

1. Classify before copying: every external parameter is `hardware-private`,
   `simulator-private`, `HW/SW ABI`, `test-only`, or `debug-only`.
2. Separate functional semantics from timing behavior. A stall cannot define
   correctness.
3. Issue must explain non-issue with explicit reasons.
4. Keep SIMT control state separate from scoreboard dependency state.
5. Memory request formation is a first-class boundary.
6. Memory stalls are layered: formation, shared/L1, cache/MSHR, ICNT, L2,
   DRAM, return path, scoreboard release.
7. Cache miss and reservation failure are different root-cause families.
8. NoC contracts preserve packet class, source, destination, byte size, flits,
   and buffer result.
9. DRAM tuning requires address mapping, row locality, queue, and bank-skew
   evidence.
10. Synchronization is not just a stall; atomics, fences, and barriers need
    correctness contracts and timing stall counters.
11. Visualization variables require producer audit.
12. Power is derivative of activity counters.
13. Tested configs are profiles, not defaults.
14. Regression must gate counters, not only functional output.
15. NVIDIA-specific CUDA/PTX/SASS behavior requires an optional compatibility
    profile.

Raw basis: `archived_raw:gpgpu-sim-design-rules-for-gpgpu-skills.md`.

## do_not_copy

# GPGPU-Sim Do-Not-Copy Boundary

Never copy these into RTL:

- C++ queue/container implementations;
- fixed simulator latencies;
- SM86 queue depths or response FIFO sizes as defaults;
- CUDA stream stack or stream-zero policy;
- BookSim allocator, VC, topology, or routing knobs as fabric truth;
- AccelWattch object hierarchy, XML coefficients, or McPAT terms;
- AerialVision parser logic or parser-only metric names.

Never copy these into ISA or ABI:

- NVIDIA PTX/SASS semantics as native simple-gpgpu ISA truth;
- CUDA compute capability as a native field unless a compatibility profile is
  explicitly selected;
- CUDA stack, heap, dynamic parallelism, stream, or object model behavior;
- texture/constant cache behavior unless exposed by the project ISA.

Safe methodology to import:

- parameter classification;
- functional/timing separation;
- issue and non-issue reason contracts;
- scoreboard reserve/check/release;
- SIMT PC and active-mask state;
- memory transaction normalization;
- queue-boundary memory attribution;
- producer-backed counter manifests.

Raw basis: `archived_raw:gpgpu-sim-do-not-copy.md`.

## l2_noc_dram

# L2, NoC, and DRAM Queue Boundary Rules

Memory hierarchy attribution must name the queue boundary where a request waits:

- SM/LSU to ICNT request injection;
- ICNT to L2 subpartition;
- L2 miss queue;
- L2 to DRAM queue;
- DRAM scheduling/timing queue;
- DRAM to L2 return queue;
- L2 to ICNT return queue;
- ICNT to shader response FIFO;
- scoreboard release.

NoC packet contracts must preserve packet class, source, destination, byte size,
flit count, VC class if used, buffer result, push cycle, and pop cycle.

DRAM bottlenecks require evidence for queue occupancy or latency plus at least
one of row locality, bank/chip skew, scheduler command activity, utilization, or
efficiency. Do not conclude "DRAM is slow" from high memory latency alone.

Raw basis: `archived_raw:gpgpu-sim-l2-noc-dram-notes.md`.

## memory_coalescing

# Memory Formation and Cache Rules

Memory path order:

```text
lane access
-> warp_memory_transaction
-> coalesced request
-> shared/L1 decision
-> cache status
-> MSHR decision
-> lower memory packet
-> return
-> scoreboard release
```

No cache, L2, or DRAM attribution is valid without a recorded
`warp_memory_transaction` containing lane addresses, active mask, byte mask,
sector mask, transaction address, transaction size, access type, and read/write
or atomic class.

Cache status taxonomy:

- `HIT`
- `HIT_RESERVED`
- `MISS`
- `SECTOR_MISS`
- `MSHR_HIT`
- `RESERVATION_FAIL`

Reservation fail reasons:

- `LINE_ALLOC_FAIL`
- `MISS_QUEUE_FULL`
- `MSHR_ENTRY_FAIL`
- `MSHR_MERGE_ENTRY_FAIL`
- `MSHR_RW_PENDING`

Rule: `MISS` is a locality/cache outcome. `RESERVATION_FAIL` is a structural
resource outcome. They must not be merged.

Raw basis: `archived_raw:gpgpu-sim-memory-hierarchy-and-coalescing-notes.md`.

## performance_attribution

# Performance Attribution Order

Use this order before changing design knobs:

1. launch and occupancy;
2. scheduler issue and non-issue;
3. scoreboard and dependency;
4. SIMT divergence and control;
5. memory request formation;
6. shared memory bank conflict;
7. L1 cache status and reservation fail;
8. MSHR;
9. ICNT request path;
10. L2/subpartition queue;
11. DRAM queue, row locality, and bank skew;
12. return path;
13. scoreboard release;
14. power or energy derivative.

Every root cause must include symptom counter, exclusion counter, queue or stage
owner, possible fix target, and confidence. A conclusion without a counter path
is `INSUFFICIENT_TRACE_EVIDENCE`.

Raw basis: `archived_raw:gpgpu-sim-performance-attribution-methodology.md`.

## power_energy_boundary

# Power and Energy Boundary

Power/energy evidence is derived from activity counters. It cannot prove a
performance bottleneck by itself.

Any power report must record:

- source mode: `sim`, `hw`, or `hybrid`;
- XML/config provenance when a model is used;
- sampling window and aggregation policy;
- activity counters consumed by each bucket;
- whether the producing counters are producer-backed.

Do not copy AccelWattch XML coefficients, McPAT object hierarchy, constant-power
terms, or hybrid CSV substitution as RTL or validation truth.

Raw basis: `archived_raw:gpgpu-sim-power-energy-model-notes.md`.

## scheduler_scoreboard_simt

# Scheduler, Scoreboard, and SIMT Rules

SM issue gate:

1. warp valid and not exited;
2. not waiting at barrier, membar, atomic, or depbar-equivalent state;
3. ibuffer has an instruction;
4. SIMT top PC matches instruction PC;
5. scoreboard reports no source, destination, predicate, or address collision;
6. target pipe has a free slot;
7. dual-issue policy allows the second issue;
8. issue and reserve scoreboard destinations.

Non-issue reasons must be mutually attributable:

- `idle_control`
- `ibuffer_empty`
- `simt_redirect`
- `scoreboard_wait`
- `pipe_unavailable`
- `barrier_wait`
- `membar_wait`
- `atomic_wait`
- `memory_backpressure`

State split:

- SIMT owns PC, active mask, reconvergence PC, call depth, and divergence event.
- Scoreboard owns pending destination registers, long-op destination registers,
  reserve/release events, and collision result.

Raw basis:

- `archived_raw:gpgpu-sim-shader-core-and-warp-scheduler-notes.md`
- `archived_raw:gpgpu-sim-scoreboard-and-simt-stack-notes.md`

## source_map

# GPGPU-Sim Source Map

GPGPU-Sim is a CUDA/OpenCL execution-driven GPU simulator with PTX functional
simulation, shader/cache/interconnect/DRAM timing models, statistics,
visualization, and AccelWattch power estimation.

Use it as:

- functional evidence for PTX-like behavior boundaries;
- timing evidence for scheduler, memory, queue, cache, NoC, DRAM, and counter
  attribution;
- configuration evidence for parameter classification;
- counter evidence only after producer audit.

Do not use it as:

- synthesizable RTL;
- simple-gpgpu ISA or ABI truth;
- default hardware latency, queue depth, or NVIDIA capability source;
- AccelWattch/McPAT module hierarchy;
- AerialVision stable counter list without producer proof.

Raw basis:

- `archived_raw:gpgpu-sim-repo-structure-map.md`
- `archived_raw:gpgpu-sim-simulator-flow-index.md`
