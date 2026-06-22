---
name: gpgpu-mode-controller
description: Use when a GPGPU request must be routed as reproduction, from-zero design, patch exploration, or trace debugging before any IR lock, synthesis, transform, or validation pass.
---

# GPGPU Mode Controller

## Skill Role

This skill is the compiler entry routing pass.

```text
user request -> MODE_SELECTION_IR
```

It selects a path. It does not inspect or modify architecture state.

## Input IR

Input is the user request plus available artifacts:

- natural-language request
- optional `spec.md`
- optional trace or validation report
- optional patch intent

## Output IR

Emit:

```text
MODE_SELECTION_IR = {
  mode,
  input_kind,
  reason,
  next_skill,
  forbidden_next_skills
}
```

Allowed modes:

```text
REPRODUCE
DESIGN
```

Allowed input kinds:

```text
COMPLETE_SPEC
DESIGN_INTENT
PATCH_REQUEST
TRACE_DEBUG
```

## Allowed Transformations

Route requests using this table:

| Request shape | `mode` | `input_kind` | `next_skill` |
|---|---|---|---|
| Reproduce this spec | `REPRODUCE` | `COMPLETE_SPEC` | `gpgpu-spec-lock` |
| Generate artifacts from this complete spec | `REPRODUCE` | `COMPLETE_SPEC` | `gpgpu-spec-lock` |
| Design a GPGPU from zero | `DESIGN` | `DESIGN_INTENT` | `gpgpu-design-intent-lock` |
| Design a small FPGA GPGPU | `DESIGN` | `DESIGN_INTENT` | `gpgpu-design-intent-lock` |
| Change warp size and analyze impact | `DESIGN` | `PATCH_REQUEST` | `gpgpu-design-intent-lock` or `gpgpu-synthesis-closure-engine` |
| Analyze why a trace is slow or divergent | `REPRODUCE` | `TRACE_DEBUG` | `gpgpu-causal-trace-analyzer` |

## Forbidden Actions

- Do not emit `DESIGN_INTENT_IR`.
- Do not emit `SPEC_IR`.
- Do not emit `GPU_STATE_IR`.
- Do not choose warp size, scheduler, ISA, cache, memory hierarchy, or RTL pipeline.
- Do not route incomplete DESIGN requests directly to `gpgpu-spec-lock`.
- Do not route REPRODUCE requests through `gpgpu-architecture-synthesizer`.

## Required Invariants

- `mode` is exactly `REPRODUCE` or `DESIGN`.
- `input_kind` is one declared enum.
- `next_skill` is compatible with both `mode` and `input_kind`.
- `forbidden_next_skills` names passes that must not be called next.
- `reason` cites user intent, not architecture preference.

## Failure Modes

Reject or request clarification when:

- both REPRODUCE and DESIGN are requested without priority
- user asks for DESIGN but provides neither complete spec nor lockable intent
- user asks for TRACE_DEBUG but provides no trace or report
- route would require choosing architecture facts

## Report Schema

```text
MODE_SELECTION_REPORT = {
  request_hash,
  selected_mode,
  selected_input_kind,
  next_skill,
  forbidden_next_skills,
  rejection_reason
}
```

## Downstream Contract

The next skill must only follow `next_skill`. Passes listed in `forbidden_next_skills` must not consume this request unless a new `MODE_SELECTION_IR` is produced.
