# Causal Trace Analysis

## Purpose

Route metric or trace deltas to GPU_STATE_IR fields, transition rules, failed gates, and owner skills.

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
