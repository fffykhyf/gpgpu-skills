---
name: gpgpu-causal-trace-analyzer
description: Use when failed GPGPU validation reports, traces, performance deltas, stalls, bottlenecks, or divergence evidence must be converted into a structured refinement request.
---

# GPGPU Causal Trace Analyzer

## Skill Role

This skill is the causal evidence pass.

```text
failed report | trace delta | performance delta -> REFINEMENT_REQUEST_IR
```

It explains failure or performance change. It does not repair architecture directly.

## Input IR

Allowed inputs:

- failed `VALIDATION_REPORT_IR`
- runtime, memory, RTL, or golden trace
- `SYNTHESIS_ACCEPTANCE_REPORT_IR`
- performance delta report
- `GPU_STATE_IR` hash and transition rule IDs

## Output IR

Emit:

```text
REFINEMENT_REQUEST_IR = {
  root_cause,
  affected_state_field,
  failed_gate,
  proposed_repair_type,
  evidence_trace
}
```

## Allowed Transformations

- Map metric delta to trace event delta.
- Map trace event delta to `GPU_STATE_IR` field.
- Map affected field to transition rule ID.
- Attribute warp stalls, memory bottlenecks, scheduler inefficiency, execution-unit pressure, or launch overhead.
- Propose repair type without editing architecture.

## Forbidden Actions

- Do not modify `ARCH_CANDIDATE_IR`.
- Do not modify `SPEC_IR`.
- Do not modify `GPU_STATE_IR`.
- Do not directly repair synthesizer output.
- Do not report metrics without a state or trace causal chain.

## Required Invariants

- Every root cause cites evidence trace.
- Every affected state field exists in `GPU_STATE_IR` or is marked `UNKNOWN_FIELD`.
- Every failed gate is named.
- Proposed repair type is advisory only.
- Same trace evidence produces stable attribution.

## Failure Modes

Reject or mark insufficient when:

- no evidence trace exists
- metric delta cannot be tied to trace events
- trace event cannot be tied to state field or rule ID
- multiple root causes cannot be ranked deterministically

## Report Schema

```text
CAUSAL_TRACE_REPORT = {
  input_hash,
  root_cause,
  affected_state_field,
  failed_gate,
  evidence_trace,
  confidence,
  refinement_request,
  verdict
}
```

`verdict = ATTRIBUTED | INSUFFICIENT_EVIDENCE`.

## Downstream Contract

Repair routing is:

```text
gpgpu-causal-trace-analyzer
 -> gpgpu-synthesis-closure-engine
 -> gpgpu-architecture-synthesizer
```

The causal analyzer must never bypass closure.
