# Launch Contract

## Purpose

Validate CUDA-like frontend subset, app compile smoke, assembler smoke, program image layout, kernel entry, command queue, doorbell/start, grid/block dimensions, argument binding, launch resource admission, memory dump contract, and golden_output_contract.

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
