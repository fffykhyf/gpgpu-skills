# Artifact Mapping

## Purpose

Emit downstream contracts for RTL, simulator, runtime, software stack, program image, test app, memory subsystem, validation plan, and PPA counters. Validate cross_artifact_consistency_gate and declared_test_coverage_gate before closure.

## Required Inputs

- Upstream IR named in `SKILL.md`
- Required schema assets
- Required table assets

## Output Contract

- Emit only the IR/report fields owned by the parent skill.
- Preserve consumed IR hashes.
- Record failed fields and missing assets.

## Fail Closed Rule

If a required schema row, table row, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET`. If a field is ambiguous or unsupported, reject instead of inferring.
