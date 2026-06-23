# Warp Execution Model

This file defines the RTL binding contract for warp execution. It replaces
generic warp scheduler and execution pipeline language with a warp
scheduler plus SM issue model.

## Execution Granularity

Execution Granularity:
- warp = 32/64 threads
- the exact width must be a parameter from `SYSTEM_CONTRACT_IR`
- lane count must not be copied from MIAOW constants without derivation

The RTL binding must preserve:
- `sm_id`
- `warp_id`
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
- warp lane count
- fault or trap lane suppression if present

Forbidden bindings:
- tying all lanes active because the warp is valid
- hiding lane gating inside an unnamed ALU wrapper
- treating VCC/SCC/EXEC writes as ordinary SGPR writes without special-state release evidence

## Per-warp context switching

Required phrase: per-warp context switching.

The SM issue model may switch between resident warps every issue slot.

Required binding evidence:
- warp ID selects SGPR/VGPR bases or physical banks
- issue readout selects decoded instruction record by warp ID
- special-state reads are indexed by warp ID
- LSU memory bundles carry warp ID until completion
- trace events include SM ID and warp ID

## Scoreboard interaction with EXEC mask

Required phrase: scoreboard interaction with EXEC mask.

Scoreboard readiness must combine:
- GPR readiness
- special-state readiness for EXEC/VCC/SCC/M0 or target replacement
- pending branch state
- memory wait state
- barrier wait state
- max in-flight state

EXEC writes must set and release special-state dependencies. A warp blocked
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

These artifacts must reference this model when binding warp scheduler,
special-state, SIMD, scoreboard, and LSU modules.
