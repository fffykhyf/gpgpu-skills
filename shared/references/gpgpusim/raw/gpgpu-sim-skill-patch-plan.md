# GPGPU-Sim Skill Patch Plan

Source repo: `ref_submodule/gpgpu-sim`

This file maps extracted design rules to existing simple-gpgpu skills.

## `gpgpu-arch`

Section to add or modify:

- architecture evidence intake;
- microarchitecture config taxonomy.

New required output:

- parameter classification table for any imported simulator profile;
- issue/non-issue reason taxonomy for SM design;
- explicit "simulator-only" caveat section.

New checklist:

- Does every parameter have category and provenance?
- Does every scheduler claim cite state and event evidence?
- Are CUDA/PTX-specific fields isolated behind compatibility profile?

New counter/test gate:

- issue-stall reason coverage: control, scoreboard, pipe, barrier/membar, memory.

New performance attribution rule:

- never tune DRAM before ruling out coalescing/L1/ICNT/L2.

## `gpgpu-memory`

Section to add or modify:

- memory request contract;
- memory hierarchy attribution;
- atomics/fence consistency.

New required output:

- normalized `warp_memory_transaction` contract: type, address, size, warp mask, byte mask, sector mask.
- memory path queue map: L1, ICNT, L2 subpartition, DRAM, return path.
- cache status and reservation-fail taxonomy.

New checklist:

- Does request formation happen before cache analysis?
- Are shared-memory conflicts separate from global memory coalescing?
- Are cache misses separate from reservation failures?
- Are atomics/fences/barriers modeled as correctness events and performance stalls?

New counter/test gate:

- transaction count per warp instruction;
- bank conflict count;
- cache status distribution;
- MSHR/fail reason;
- DRAM row locality and bank skew.

New attribution rule:

- memory bottlenecks must name queue boundary and release event.

## `gpgpu-interconnect`

Section to add or modify:

- packet contract and NoC provenance.

New required output:

- packet class: read request, read reply, write request, write reply, atomic;
- source/destination;
- byte size/flit count;
- buffer/backpressure contract.

New checklist:

- Is the design using a local xbar, mesh/NoC, or abstract fabric?
- Are BookSim `.icnt` parameters treated as inspiration only?
- Is packet-size semantics explicit?

New counter/test gate:

- `has_buffer` failures;
- request/response packet counts;
- return-path FIFO pressure;
- congestion by packet class.

New attribution rule:

- ICNT bottleneck requires both packet-volume and buffer-full evidence.

## `gpgpu-simppa`

Section to add or modify:

- counter schema;
- stall reason schema;
- performance attribution method;
- power-report provenance.

New required output:

- producer-backed / defined-only / parser-only counter status;
- `(access_type, stall_reason)` memory stall matrix;
- cache status plus reservation-fail matrix;
- ICNT/L2/DRAM queue attribution;
- power counter provenance and mode.

New checklist:

- Does every counter have producer path?
- Are parser-only AerialVision names excluded from stable schema?
- Does every bottleneck conclusion cite at least one symptom and one exclusion counter?

New counter/test gate:

- stable telemetry manifest checked against source producers.

New attribution rule:

- power is derivative of activity counters and cannot independently validate a bottleneck.

## `gpgpu-golden`

Section to add or modify:

- simulator evidence boundary.

New required output:

- distinction between PTX/CUDA functional behavior and simple-gpgpu ISA truth.
- optional compatibility profile if PTX/SASS/CUDA is used.

New checklist:

- Is behavior from `src/cuda-sim/*` treated as NVIDIA PTX behavior?
- Is timing state excluded from functional correctness?
- Are atomics/fence semantics confirmed in functional source, not only timing source?

New counter/test gate:

- golden tests for launch descriptor, lane mask, divergence, memory transaction semantics.

New attribution rule:

- a timing stall cannot justify a functional semantic.

## `gpgpu-runtime`

Section to add or modify:

- launch artifact and memory bundle generation.

New required output:

- launch descriptor fields: kernel id, grid/block dims, shared memory, argument layout.
- optional CUDA/OpenCL compatibility mapping.
- memory bundle fields needed by coalescer.

New checklist:

- Does runtime expose only selected ABI, not entire CUDA stack?
- Are launch latencies kept out of ABI?
- Is compute capability isolated as compatibility metadata?

New counter/test gate:

- launch descriptor round-trip test;
- argument layout test;
- coalescer input trace test.

## `gpgpu-rtl`

Section to add or modify:

- RTL contract extraction from simulators.

New required output:

- what may become RTL: scoreboard, SIMT state, memory request interface, packet interface, counter tap points.
- what must not become RTL: C++ queues, AccelWattch objects, BookSim configs, CUDA launch stack.

New checklist:

- Is every imported mechanism rewritten as a hardware contract?
- Are fixed simulator latencies rejected unless linked to a pipeline stage?
- Are counter tap points separate from performance model code?

New counter/test gate:

- RTL trace must expose issue reason, memory transaction, cache status, ICNT status, and DRAM queue state if implemented.

## `gpgpu-loop`

Section to add or modify:

- regression and rewrite triggers.

New required output:

- config snapshot per run;
- counter schema version;
- producer audit status;
- performance attribution summary.

New checklist:

- Did a simulator-only parameter enter a hardware contract?
- Did parser/producer counter drift occur?
- Did a regression pass functional output but fail counter expectations?

New counter/test gate:

- smoke tests must check selected counters/stalls, not just final output.

New attribution rule:

- rewrite when a bottleneck conclusion lacks source-path evidence.
