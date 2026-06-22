---
name: gpgpu-canonical-state-engine
description: Use when converting locked GPGPU SPEC_IR into deterministic GPU_STATE, validating GPU finite-state-machine invariants, or snapshotting canonical warp, scheduler, memory, register, execution-unit, launch, or CSR state.
---

# GPGPU Canonical State Engine

## Objective

Transform `SPEC_IR` into one deterministic GPU finite-state machine.

This skill is not an architecture planner. It must not perform pipeline orchestration, heuristic design, evaluation logic, mapping inference, or tradeoff synthesis. Its only job is:

```text
SPEC_IR -> GPU_STATE
```

## Input Contract

Input must be locked by `gpgpu-spec-lock`:

```text
SPEC_IR = {
  ISA: canonical,
  warp_model: explicit,
  memory_hierarchy: explicit,
  scheduling_policy: explicit,
  config_defaults: resolved
}
```

Reject input if it contains implicit defaults, unresolved enums, ambiguous natural language, missing state dimensions, or mode-dependent behavior.

## Output Contract

Emit exactly one canonical state object:

```text
GPU_STATE = {
  warp_state,
  scheduler_state,
  memory_state,
  register_state,
  execution_units,
  launch_state,
  csr_state
}
```

Downstream skills may consume `GPU_STATE`; they must not reinterpret or mutate its schema.

## FSM API

Implement all reasoning through this API:

| API | Required behavior |
|---|---|
| `init(spec_ir)` | create the initial `GPU_STATE` with every field explicitly populated |
| `apply(event)` | apply one external or internal event through the rule table |
| `transition(rule_id)` | execute exactly one named transition rule and record rule provenance |
| `validate_invariants()` | reject illegal state before and after every transition |
| `snapshot()` | return a deterministic, serializable, diffable state snapshot |

No hidden state is allowed outside `GPU_STATE`.

## State Schema

| State | Required fields |
|---|---|
| `warp_state` | warp IDs, PC, active mask, predicate mask, reconvergence stack, lifecycle |
| `scheduler_state` | ready set, blocked set, selected warp, stall reason, policy enum |
| `memory_state` | address spaces, cache lines, outstanding requests, ordering/fence state, bandwidth counters |
| `register_state` | scalar/vector/predicate register files, scoreboard dependencies, writeback ownership |
| `execution_units` | unit type, latency, occupancy, accepted ops, completion events |
| `launch_state` | kernel image ID, entry PC, grid/block shape, arguments, resource allocation |
| `csr_state` | control/status fields, trap/fault state, counters visible to execution semantics |

## Transition Rules

Each transition rule must be table-driven:

```text
rule_id,
precondition,
input_event,
state_reads,
state_writes,
postcondition,
invariants_checked
```

Allowed event classes:

- launch events.
- fetch/decode/issue/execute/writeback events.
- warp divergence and reconvergence events.
- scheduler select/stall/release events.
- memory request/response/fence/fault events.
- CSR read/write/fault events.

If a requested transition has no rule, fail closed. Do not infer a new rule.

## Invariants

Validate at minimum:

- every valid warp has exactly one PC and one active mask.
- active masks match `warp_model.width`.
- scheduler state references only valid resident warps.
- scoreboard dependencies reference existing registers and owning events.
- every outstanding memory request has a unique tag/source and response owner.
- launch resources do not exceed resolved config defaults.
- CSR/fault state is deterministic for the same event sequence.

## Verification Gate

For the same `SPEC_IR` and same ordered event list:

- `init(spec_ir)` must produce identical snapshots.
- each `apply(event)` must select the same `rule_id`.
- `snapshot()` must be byte-stable after canonical serialization.
- `validate_invariants()` must produce the same pass/fail result and failure path.

## Failure Modes

- Using framework evidence or papers to invent state.
- Filling missing defaults inside the state engine.
- Letting downstream RTL/runtime/memory skills reinterpret state.
- Applying multiple transition rules as one informal step.
- Emitting prose instead of serializable `GPU_STATE`.
