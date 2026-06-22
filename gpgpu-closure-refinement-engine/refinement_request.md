# Refinement Request

## Purpose

Emit structured repair requests with root cause, affected state field, failed gate, repair owner skill, repair type, and evidence trace.

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
