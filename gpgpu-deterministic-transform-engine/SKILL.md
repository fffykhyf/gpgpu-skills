---
name: gpgpu-deterministic-transform-engine
description: Use when mapping canonical GPU_STATE into downstream RTL, simulator behavior, runtime, memory, or PPA artifacts through fixed table-driven transforms without heuristic design inference.
---

# GPGPU Deterministic Transform Engine

## Objective

Transform `GPU_STATE` into all downstream artifacts through fixed tables.

```text
GPU_STATE -> RTL_MAPPING | SIM_BEHAVIOR | RUNTIME_CONTRACT | MEMORY_MODEL | PPA_MODEL
```

No LLM inference-based design, heuristic mapping, or opportunistic architecture choice is allowed.

## Input Contract

Input must include:

- `GPU_STATE` from `gpgpu-canonical-state-engine`.
- transform target.
- mapping table version.
- mode selection provenance.

Reject prose specs and partially locked state.

## Output Contract

Emit only target artifacts:

| Target | Output |
|---|---|
| `STATE_TO_RTL` | RTL module map, signal map, fixed FSM mapping, hardware trace schema |
| `STATE_TO_SIM` | simulator state model, event interpreter, semantic trace schema |
| `STATE_TO_RUNTIME` | ABI-visible launch/execution contract |
| `STATE_TO_MEMORY` | memory execution model tables |
| `STATE_TO_PPA` | counter map, bottleneck buckets, estimation inputs |

## Table-Driven Mapping

Every mapping must be keyed by fixed enum tables:

| GPU_STATE enum | Mapping requirement |
|---|---|
| `warp_sched_type` | maps to one fixed scheduler implementation |
| `cache_policy` | maps to one fixed cache behavior table |
| `memory_model` | maps to one fixed ordering and bandwidth model |
| `issue_policy` | maps to one fixed issue/scoreboard mapping |
| `exec_unit_type` | maps to one fixed latency/port/trace mapping |
| `launch_abi_version` | maps to one fixed runtime layout |

If a value is missing from a mapping table, fail closed. Do not synthesize an implementation.

## Transform API

| API | Behavior |
|---|---|
| `select_target(target)` | choose one downstream artifact target |
| `lookup(enum_value)` | resolve one enum through the fixed mapping table |
| `emit_artifact()` | produce deterministic artifact payload |
| `emit_trace_schema()` | produce trace fields required by downstream execution |
| `validate_mapping()` | verify every consumed state field has exactly one mapping |

## Verification Gate

- Every consumed `GPU_STATE` field is mapped or explicitly unused.
- Every mapped enum has exactly one table entry.
- Outputs contain mapping table version and `GPU_STATE` snapshot hash.
- Repeated runs produce byte-stable artifacts.
- No prose rationale is used as a mapping rule.

## Failure Modes

- Inferring RTL structure from natural language.
- Choosing a cache or scheduler because it seems better.
- Mapping one enum to multiple implementations.
- Generating artifacts from `SPEC_IR` directly instead of `GPU_STATE`.
- Hiding unmapped state fields.
