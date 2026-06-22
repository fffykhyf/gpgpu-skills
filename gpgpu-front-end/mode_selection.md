# Mode Selection

## Purpose

Classify the request using shared/tables/mode_decision_table.yaml. A complete spec routes to REPRODUCE, a vague design goal routes to DESIGN, a runnable end-to-end prototype request routes to DESIGN with prototype_kind VERTICAL_SLICE_PROTOTYPE, an edit against locked IR routes to PATCH_REQUEST, and trace or divergence evidence routes to TRACE_DEBUG.

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
