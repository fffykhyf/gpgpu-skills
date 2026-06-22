---
name: gpgpu-spec-lock
description: Use when converting GPGPU spec.md, prose requirements, ISA notes, warp model notes, memory hierarchy notes, scheduling policy text, or config defaults into ambiguity-free SPEC_IR.
---

# GPGPU Spec Lock

## Objective

Convert `spec.md` into structured, ambiguity-free `SPEC_IR`.

```text
spec.md -> SPEC_IR
```

This skill stabilizes input. It does not design architecture, choose heuristics, infer missing defaults, or generate downstream artifacts.

## Input Contract

Input is human-written spec text plus optional tables. Accept prose only as source material; never pass prose downstream.

## Output Contract

Emit:

```text
SPEC_IR = {
  ISA: canonical,
  warp_model: explicit,
  memory_hierarchy: explicit,
  scheduling_policy: explicit,
  config_defaults: resolved
}
```

Every enum must be resolved. Every default must be explicit. Every ambiguous sentence must either be rewritten into a field or rejected.

## Locking Rules

- No implicit defaults.
- No natural language ambiguity.
- No unresolved enums.
- No "implementation-defined" behavior unless encoded as an enum value with allowed consumers.
- No architecture inference from examples.
- No mode-dependent fields unless `gpgpu-mode-controller` selected the mode first.

## Required Fields

| Section | Required fields |
|---|---|
| `ISA` | opcode set, operand types, mask behavior, memory ops, barriers, CSR access, illegal behavior |
| `warp_model` | warp width, lane IDs, active mask semantics, divergence model, reconvergence rule |
| `memory_hierarchy` | address spaces, cache policy enum, ordering model, bandwidth limits, atomic/fence semantics |
| `scheduling_policy` | scheduler enum, arbitration rule, stall causes, fairness guarantee |
| `config_defaults` | resolved scalar defaults, enum defaults, limits, derived-value owner |

## Lock API

| API | Behavior |
|---|---|
| `parse(spec_md)` | extract candidate fields without resolving ambiguity |
| `resolve(field)` | convert exactly one candidate into canonical enum/scalar/table value |
| `reject(reason)` | fail closed when the spec lacks information |
| `emit_spec_ir()` | output canonical `SPEC_IR` only after every required field is locked |
| `diff_lock(old_ir, new_ir)` | report deterministic field-level changes |

## Verification Gate

- All required fields exist.
- All enums are in declared enum tables.
- No free-form prose remains in `SPEC_IR`.
- Defaults are explicit and traceable to spec text.
- `diff_lock` is stable for repeated runs.

## Failure Modes

- Filling a missing value because it is common in GPUs.
- Leaving "TBD", "default", "typical", "maybe", or "implementation-defined" in IR.
- Passing spec prose to the canonical state engine.
- Resolving conflicting requirements without rejection.
