# Pass Evidence Engine

This component is required only in Pass Evidence Mode. It proves that a pass is
credible enough for regression tracking and performance comparison.

## Trigger

- RTL final architectural state matches golden
- final memory dump matches golden
- completion and fault status match golden
- no architectural trace divergence is detected

## Required Outputs

- `PASS_EVIDENCE_REPORT`
- `TRACE_COVERAGE_REPORT`
- `REGRESSION_FINGERPRINT`

## PASS_EVIDENCE_REPORT Shape

```yaml
pass_evidence_report:
  verdict: CORRECTNESS_PASS_STRONG | CORRECTNESS_PASS_WEAK | PASS_WITH_INSUFFICIENT_EVIDENCE | PASS_WITH_PERFORMANCE_WARNING | PASS_WITH_TRACE_DIVERGENCE_WARNING
  evidence_completeness:
    system_contract_hash: string
    golden_model_hash: string
    rtl_hash: string
    toolchain_artifact_hash: optional string
    program_image_hash: optional string
    runtime_launch_hash: optional string
    input_memory_hash: string
    final_memory_hash: string
    golden_trace_present: bool
    rtl_trace_present: bool
    completion_status_present: bool
    fault_status_present: bool
  architectural_state_comparison:
    final_memory_match: bool
    final_pc_match: bool
    observable_register_state_match: bool
    csr_state_match: bool
    fault_status_match: bool
    completion_status_match: bool
  coverage_summary_ref: TRACE_COVERAGE_REPORT
  performance_metric_ref: PERFORMANCE_METRIC_IR
  regression_fingerprint_ref: REGRESSION_FINGERPRINT
  warnings:
    - uncovered_contract_paths
    - insufficient_trace_detail
    - performance_below_target
    - unstable_trace_hash
```

## Pass Strength

`CORRECTNESS_PASS_STRONG` requires:

- final state match
- completion/fault match
- trace schema complete
- first-divergence diff clean
- required backend matrix passed

`CORRECTNESS_PASS_WEAK` means:

- final state matches
- trace misses key fields, runtime launch evidence is incomplete, or backend
  matrix is incomplete

Weak pass is valid for local iteration but cannot support FPGA, PPA, or release
claims.

## REGRESSION_FINGERPRINT Shape

```yaml
regression_fingerprint:
  contract_hash: string
  golden_model_hash: string
  rtl_hash: string
  toolchain_artifact_hash: optional string
  program_image_hash: optional string
  runtime_launch_hash: optional string
  loader_contract_hash: optional string
  input_memory_hash: string
  final_memory_hash: string
  trace_summary_hash: string
  performance_metric_hash: string
  coverage_hash: string
```

## Coverage Rules

`TRACE_COVERAGE_REPORT` must record:
- observed contract paths
- unobserved required contract paths
- observed RTL module paths
- observed toolchain artifact paths
- source completeness by trace type
- coverage hash

## Warning Rules

- `PASS_WITH_INSUFFICIENT_EVIDENCE`: final outputs match but required hashes,
  traces, launch config, or completion/fault evidence are missing.
- `PASS_WITH_PERFORMANCE_WARNING`: correctness passes but metrics violate target
  thresholds.
- `PASS_WITH_TRACE_DIVERGENCE_WARNING`: final outputs match but architectural
  traces diverge. This escalates to Failure Attribution Mode for first
  divergence reporting.

## XiangShan Capture Evidence

Passing CI evidence may include `BATCH_AUTO_CAPTURE` disabled by policy, but
failure evidence must include `FAILURE_CAPTURE_PACKAGE` or an explicit
test-evidence gap. A failure package must include replay command, trace slice,
waveform slice or absent reason, config hash, program image hash, golden state,
RTL state summary, memory store log, counter snapshot, and normalized report.
