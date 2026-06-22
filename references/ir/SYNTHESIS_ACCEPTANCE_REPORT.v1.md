# SYNTHESIS_ACCEPTANCE_REPORT v1

## Role

`SYNTHESIS_ACCEPTANCE_REPORT` is the closure result for a candidate generated in DESIGN mode.

It does not design architecture. It records whether the candidate has enough evidence to be accepted, rejected, refined, or marked insufficient.

## Schema

```text
SYNTHESIS_ACCEPTANCE_REPORT = {
  schema_version,
  candidate_id,
  input_hash,
  spec_ir_hash,
  gpu_state_hash,
  hard_constraint_result,
  requirement_coverage_result,
  spec_round_trip_result,
  state_invariant_result,
  artifact_mapping_result,
  config_lock_result,
  trace_smoke_result,
  quality_gate_result,
  stability_result,
  verdict,
  repair_request
}
```

## Verdict Enum

```text
ACCEPT
REJECT
REFINE_REQUIRED
INSUFFICIENT_EVIDENCE
```

## Required Gates

| Gate | Required evidence |
|---|---|
| `requirement_coverage_result` | Every intent requirement is mapped to `ARCH_IR` or non-goal. |
| `spec_round_trip_result` | Synthesized draft locks to `SPEC_IR` without drift. |
| `state_invariant_result` | `GPU_STATE_IR` invariants pass. |
| `artifact_mapping_result` | Every consumed state field maps through deterministic tables. |
| `config_lock_result` | Config ownership and ABI visibility are correct. |
| `trace_smoke_result` | Minimal runtime, memory, RTL, and sim traces align. |
| `quality_gate_result` | Quality target satisfies the locked design intent. |
| `stability_result` | Same input gives stable output or deterministic ranking. |

## Rules

- `ACCEPT` requires all mandatory gates to pass.
- `REJECT` requires a failed hard correctness gate.
- `REFINE_REQUIRED` requires a repairable failed quality or trace gate.
- `INSUFFICIENT_EVIDENCE` requires missing evidence, not a hidden pass.

