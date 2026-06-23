# Rewrite Trigger

Rewrite triggers map root causes to patch classes and revalidation routes.

## Trigger Mapping

| Root cause | Patch options |
|---|---|
| `CONTRACT_ROOT_CAUSE` | Contract Patch |
| `GOLDEN_MODEL_ROOT_CAUSE` | Golden Model Patch or Contract Patch |
| `TOOLCHAIN_ROOT_CAUSE` | Toolchain Patch |
| `RUNTIME_LAUNCH_ROOT_CAUSE` | Runtime Patch or Toolchain Patch |
| `RTL_FUNCTIONAL_ROOT_CAUSE` | RTL Patch |
| `RTL_INTERFACE_ROOT_CAUSE` | RTL Patch |
| `MEMORY_SYSTEM_ROOT_CAUSE` | RTL Patch or Architecture Patch |
| `SCHEDULER_ROOT_CAUSE` | RTL Patch or Architecture Patch |
| `PERFORMANCE_ARCH_ROOT_CAUSE` | Architecture Patch |
| `TEST_EVIDENCE_ROOT_CAUSE` | Test Evidence Patch or Pass Evidence Patch |
| `INSUFFICIENT_TRACE_EVIDENCE` | Test Evidence Patch |
| `ROOT_CAUSE_AMBIGUOUS` | Test Evidence Patch |

## Gate

Do not trigger a behavior-changing patch without `PERF_ATTRIBUTION_GRAPH`
evidence and a `ROOT_CAUSE_REPORT`. A `PASS_EVIDENCE_PATCH` may be triggered by
`PASS_EVIDENCE_REPORT` evidence gaps, trace coverage gaps, or unstable
`REGRESSION_FINGERPRINT` evidence.
