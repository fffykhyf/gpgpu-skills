---
name: gpgpu-rtl-simt-core
description: Use when GPU_STATE_IR and RTL mapping IR must be executed or checked as a SIMT hardware model with pipeline, scheduler, scoreboard, memory interface, and implementability reports.
---

# GPGPU RTL SIMT Core

## Skill Role

This skill is the pure hardware execution model pass.

```text
GPU_STATE_IR + RTL_MAPPING_IR + kernel
  -> cycle_level_simulation + hardware_trace + rtl_implementability_report
```

It implements mapped state. It does not reinterpret architecture.

## Input IR

Required inputs:

- `GPU_STATE_IR`
- `RTL_MAPPING_IR`
- kernel or instruction stream
- required trace schema

## Output IR

Emit:

```text
hardware_trace = {
  fetch_events,
  decode_events,
  issue_events,
  execute_events,
  writeback_events,
  scoreboard_events,
  memory_interface_events,
  csr_fault_events
}
```

Also emit:

```text
rtl_implementability_report = {
  unsupported_state_fields,
  unmapped_fsm_rules,
  pipeline_hazards,
  scoreboard_conflicts,
  memory_interface_conflicts,
  verdict
}
```

## Allowed Transformations

- Execute fetch, decode, issue, execute, and writeback pipeline rules.
- Apply scheduler FSM and scoreboard rules already mapped from `GPU_STATE_IR`.
- Report hazards without changing state definitions.
- Bind memory interface behavior through `RTL_MAPPING_IR`.

## Forbidden Actions

- Do not reinterpret architecture.
- Do not modify `GPU_STATE_IR`.
- Do not add execution units.
- Do not change scheduler because of RTL convenience.
- Do not silently drop unsupported state fields.

## Required Invariants

- Every hardware trace event cites state hash and mapping version.
- Unsupported fields are listed in implementability report.
- Scoreboard conflicts are explicit.
- Pipeline hazards are trace-visible.
- Memory interface conflicts are not hidden.

## Failure Modes

Reject or mark not implementable when:

- state field lacks RTL mapping
- FSM rule is unmapped
- scoreboard conflict cannot be resolved
- memory interface width conflicts with mapped request width
- trace schema cannot cover required events

## Report Schema

`rtl_implementability_report.verdict = IMPLEMENTABLE | NOT_IMPLEMENTABLE | INSUFFICIENT_MAPPING`.

## Downstream Contract

Closure uses `rtl_implementability_report` for artifact mapping, trace smoke, and prototype credibility gates.
