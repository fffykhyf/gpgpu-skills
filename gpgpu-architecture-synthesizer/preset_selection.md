# Preset Selection

## Purpose

Select only MINIMAL_SIMT_CORE or MULTI_WARP_SINGLE_SM in v4 baseline. Unsupported presets must reject or emit refinement evidence instead of being improvised.

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
