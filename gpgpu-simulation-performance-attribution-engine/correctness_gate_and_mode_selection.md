# Correctness Gate and Mode Selection

This component runs immediately after trace ingestion. It compares observable
golden and RTL outcomes, decides the run mode, and emits
`CORRECTNESS_GATE_REPORT`.

## Inputs

- `golden_final_state`
- `rtl_final_state`
- `golden_memory_dump`
- `rtl_memory_dump`
- `golden_completion_status`
- `rtl_completion_status`
- `golden_fault_status`
- `rtl_fault_status`
- optional `golden_trace`
- optional `rtl_trace`
- program image, contract, launch config, and initial memory hashes

## Output

```yaml
correctness_gate_report:
  verdict: CORRECTNESS_PASS | CORRECTNESS_FAIL | PASS_WITH_INSUFFICIENT_EVIDENCE | PASS_WITH_TRACE_DIVERGENCE_WARNING
  selected_mode: PASS_EVIDENCE_MODE | FAILURE_ATTRIBUTION_MODE
  comparison_level:
    - final_memory
    - architectural_state
    - completion_fault
    - sampled_trace
    - instruction_trace
  mismatch_summary:
    memory_mismatch: bool
    register_mismatch: bool
    pc_mismatch: bool
    active_mask_mismatch: bool
    csr_mismatch: bool
    fault_mismatch: bool
    completion_mismatch: bool
  evidence_completeness:
    golden_trace_present: bool
    rtl_trace_present: bool
    program_image_hash_match: bool
    contract_hash_match: bool
    launch_config_hash_match: bool
    initial_memory_hash_match: bool
  fail_reason: optional string
```

## Mode Selection Rules

```text
if final memory mismatch:
    FAILURE_ATTRIBUTION_MODE
else if completion/fault mismatch:
    FAILURE_ATTRIBUTION_MODE
else if architectural state mismatch:
    FAILURE_ATTRIBUTION_MODE
else if trace-level architectural divergence exists:
    FAILURE_ATTRIBUTION_MODE
else if evidence incomplete:
    PASS_EVIDENCE_MODE with PASS_WITH_INSUFFICIENT_EVIDENCE
else:
    PASS_EVIDENCE_MODE with CORRECTNESS_PASS
```

If final memory matches but trace-level architectural divergence exists, select
Failure Attribution Mode. If the divergence is real but final outputs match,
the report may use `PASS_WITH_TRACE_DIVERGENCE_WARNING` as the correctness
verdict while still requiring `FIRST_DIVERGENCE_REPORT`.

## Fail-Closed Rules

- Do not infer correctness pass from final memory alone when completion, fault,
  launch, or contract hashes are missing.
- Do not run failure localization for a clean pass.
- Do not route to rewrite when evidence is incomplete; route to
  `TEST_EVIDENCE_PATCH` through pass evidence or root cause reporting.
