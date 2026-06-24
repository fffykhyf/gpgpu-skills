---
name: gpgpu-validation
description: Use when validating golden, toolchain, RTL, and Yosys backend evidence agreement; collecting compact pass evidence; debugging first divergence or root cause; or performing GPGPU performance, PPA, stall, energy, and bottleneck analysis.
---

# gpgpu-validation

## Role

Validate golden/toolchain/RTL agreement and performance evidence.

Also validate Yosys backend evidence when a claim includes Yosys elaboration,
Yosys synthesis, a Yosys PPA baseline, or generated RTL with requested Yosys
compatibility.

## Loading Policy

- Default mode loads only `validation_core.md`.
- Load `debug_attribution_pack.md` only when correctness fails or the user requests debug/regression.
- Load `performance_pack.md` only when the user requests performance/PPA/stall/energy/bottleneck analysis.

## Default Outputs

- `PASS_EVIDENCE_REPORT` compact
- `REGRESSION_FINGERPRINT`
- `RUN_STATE.yaml` delta

## Failure-Only Outputs

- `FIRST_DIVERGENCE_REPORT`
- `MISMATCH_PACKAGE`
- `ROOT_CAUSE_REPORT`
- `DEBUG_SUMMARY.zh.md`

## Performance-Only Outputs

- `PERFORMANCE_METRIC_IR`
- `PERF_ATTRIBUTION_GRAPH`
- `STALL_REASON_MATRIX`
- `MEMORY_ATTRIBUTION_MATRIX`
- `POWER_ENERGY_PROVENANCE`

## Backend Evidence Inputs

- `YOSYS_FLOW_IR`
- `YOSYS_RTL_COMPATIBILITY_REPORT`
- `YOSYS_EVIDENCE_BUNDLE`

All generated IR and derived artifacts must obey `shared/references/canonical_generation_rules.md` before hash calculation, comparison, validation, or rewrite routing.
RTL correctness cannot be marked strong unless relevant `formal_assertion_pack.md` entries are proven, bounded-checked, simulated as assertions, or explicitly waived with a contract-path-bound reason.

## Boundaries

Do not generate full root-cause reports when golden and RTL match. Generate minimal pass evidence and regression fingerprint by default.
