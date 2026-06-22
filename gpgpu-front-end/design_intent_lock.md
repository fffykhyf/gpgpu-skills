# Design Intent Lock

## Purpose

For DESIGN mode, normalize the user's goals into DESIGN_INTENT_IR. Required fields are objective, non_goals, workload_profile, target_platform, hard_constraints, soft_constraints, required_features, optional_features, validation_target, and prototype_credibility_target.

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
