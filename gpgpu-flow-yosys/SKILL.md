---
name: gpgpu-flow-yosys
description: Use when RTL targets Yosys elaboration, synthesis, PPA baseline, or Yosys-backed build/report evidence.
---

# gpgpu-flow-yosys

## Role

Own the Yosys backend flow evidence path for generated or reviewed RTL.

Use this skill when `backend_toolchain` includes Yosys, when RTL must elaborate
or synthesize under Yosys, when a Yosys PPA baseline is requested, or when a
claim cites Yosys-backed build/report evidence.

## Owned Outputs

This skill owns:

- `YOSYS_FLOW_IR`
- `YOSYS_RTL_COMPATIBILITY_REPORT`
- `YOSYS_EVIDENCE_BUNDLE`
- `YOSYS_PROFILE_RESULT`

## Boundaries

This skill must not change architecture, ISA, contract, or RTL semantics. It
owns only backend flow metadata, profile selection, build/report/log paths,
Yosys script evidence, parsed report evidence, and claim boundary text.

When a task needs RTL style repair, route the behavioral patch to
`gpgpu-rtl`; this skill only records whether the RTL is suitable for the chosen
Yosys profile and whether the evidence bundle supports the claim.

## Core Files

- `yosys_flow_core.md`: flow construction, profile selection, and evidence gate.
- `yosys_rtl_style.md`: Yosys RTL compatibility checks and fail-closed style
  rules.
- `yosys_profile_matrix.md`: supported profile matrix and claim limits.
- `yosys_evidence_bundle.md`: build_dir/BUILD_DIR, report_dir, log_dir,
  hashes, parsed metrics, report coverage, and claim boundary requirements.
- All generated IR and derived artifacts must obey `shared/references/canonical_generation_rules.md` before hash calculation, comparison, validation, or rewrite routing.
- RTL correctness cannot be marked strong unless relevant `gpgpu-validation/formal_assertion_pack.md` entries are proven, bounded-checked, simulated as assertions, or explicitly waived with a contract-path-bound reason.

## Required Shared Assets

- `shared/schemas/yosys_flow_ir.schema.yaml`
- `shared/schemas/yosys_rtl_compatibility_report_ir.schema.yaml`
- `shared/schemas/yosys_evidence_bundle_ir.schema.yaml`
- `shared/schemas/rtl_synth_hygiene_issue.schema.yaml`
- `shared/tables/yosys_profile_matrix.yaml`
- `shared/tables/yosys_rtl_style_rules.yaml`
- `shared/tables/backend_claim_boundary.yaml`
- `shared/templates/yosys_synth_bundle_report.md`
- `shared/templates/rtl_synth_hygiene_report.md`

## Execution Loop

```text
select Yosys profile
  -> create YOSYS_FLOW_IR
  -> run or validate Yosys RTL compatibility gate
  -> collect build/report/log evidence
  -> hash filelist and script
  -> parse warnings, errors, and metrics
  -> emit YOSYS_EVIDENCE_BUNDLE
  -> state claim boundary
```

## Claim Boundary

Yosys PPA baseline evidence may support cell count, wire bits, hierarchy size,
relative area trend, and synthesis hygiene. It must not claim timing closure,
frequency_mhz, backend signoff, or frequency closure without a separate backend
flow that owns those claims.
