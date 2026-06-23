# Wavefront Execution Model

This file defines the RTL binding contract for wavefront execution. It replaces
generic warp scheduler and execution pipeline language with a wavefront
scheduler plus CU issue model.

## Execution Granularity

Execution Granularity:
- wavefront = 32/64 threads
- the exact width must be a parameter from `SYSTEM_CONTRACT_IR`
- lane count must not be copied from MIAOW constants without derivation

The RTL binding must preserve:
- `cu_id`
- `wavefront_id`
- `pc`
- `exec_mask`
- `decoded_instruction_record`
- `issue_ready_terms`
- `memory_bundle_id` for LSU operations

## State

Required local state:
- VGPR bank
- SGPR bank
- EXEC mask register
- VCC/SCC flags
- special state table
- decoded entry valid table
- pending branch table
- memory wait table
- barrier wait table
- reconvergence stack when enabled

## EXEC-mask driven SIMD gating

SIMD lane enable must be derived from:
- current `EXEC mask register`
- instruction predicate mask
- wavefront lane count
- fault or trap lane suppression if present

Forbidden bindings:
- tying all lanes active because the wavefront is valid
- hiding lane gating inside an unnamed ALU wrapper
- treating VCC/SCC/EXEC writes as ordinary SGPR writes without special-state release evidence

## Per-wave context switching

Required phrase: per-wave context switching.

The CU issue model may switch between resident wavefronts every issue slot.

Required binding evidence:
- wavefront ID selects SGPR/VGPR bases or physical banks
- issue readout selects decoded instruction record by wavefront ID
- special-state reads are indexed by wavefront ID
- LSU memory bundles carry wavefront ID until completion
- trace events include CU ID and wavefront ID

## Scoreboard interaction with EXEC mask

Required phrase: scoreboard interaction with EXEC mask.

Scoreboard readiness must combine:
- GPR readiness
- special-state readiness for EXEC/VCC/SCC/M0 or target replacement
- pending branch state
- memory wait state
- barrier wait state
- max in-flight state

EXEC writes must set and release special-state dependencies. A wavefront blocked
on EXEC must not issue a dependent branch, predicate, SIMD, or LSU operation.

## Partial Simulation Gate

Required partial tests:
- launch initializes EXEC
- SIMD lane gating follows EXEC
- branch or mask instruction mutates EXEC
- dependent instruction stalls until EXEC writeback release
- zero EXEC path follows contract-defined reconvergence or retirement

## Artifact Expectations

The RTL skill must produce AI-facing English artifacts:
- `INCREMENTAL_RTL_MAP`
- `MODULE_INTERFACE_REPORT`
- `RTL_PARTIAL_SIM_REPORT`

These artifacts must reference this model when binding wavefront scheduler,
special-state, SIMD, scoreboard, and LSU modules.
