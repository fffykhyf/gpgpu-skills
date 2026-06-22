# Closure Gate

## Purpose

Evaluate coverage, spec lock, state invariant, artifact mapping, cross_artifact_consistency_gate, declared_test_coverage_gate, runtime, memory, implementation, vertical-slice validation, PPA, and stability gates.

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
