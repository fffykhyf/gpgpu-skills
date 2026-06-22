---
name: gpgpu-mode-controller
description: Use when selecting whether a GPGPU request must run in REPRODUCE or DESIGN mode before spec locking, state generation, deterministic transformation, execution modeling, or causal trace analysis.
---

# GPGPU Mode Controller

## Objective

Select exactly one mode:

```text
MODE = REPRODUCE | DESIGN
```

This is the entry skill. It must not participate in state, mapping, design decisions, artifact generation, execution modeling, or causal analysis.

## Input Contract

Input is the user request plus available artifacts. Do not inspect architecture internals except to determine whether the user wants reproduction or constrained synthesis.

## Output Contract

Emit:

```text
MODE_SELECTION = {
  mode,
  reason,
  next_skill
}
```

`next_skill` is normally `gpgpu-spec-lock`.

## Mode Table

| Mode | Use when | Behavior |
|---|---|---|
| `REPRODUCE` | user asks to match an existing spec, trace, paper, config, bug, or result | strict mapping pipeline; reject creative synthesis |
| `DESIGN` | user asks to synthesize a new design from constraints | constrained synthesis pipeline; still requires locked enums and explicit defaults |

## Forbidden Behavior

- Do not modify `SPEC_IR`.
- Do not create `GPU_STATE`.
- Do not map state to RTL, sim, PPA, runtime, or memory artifacts.
- Do not choose scheduling, cache, memory, or ISA details.
- Do not resolve ambiguous spec language.

## Verification Gate

- Mode is exactly `REPRODUCE` or `DESIGN`.
- Reason cites user intent, not architecture preference.
- No downstream field is produced.
- Ambiguity is routed to `gpgpu-spec-lock`, not resolved here.

## Failure Modes

- Inferring design details while choosing mode.
- Treating DESIGN as permission for heuristic mapping.
- Treating REPRODUCE as permission to ignore missing fields.
- Returning both modes.
