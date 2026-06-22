# ABI Validation

## Purpose

Check argument layout, scalar size, pointer size, alignment, ABI version, CSR/runtime interface ownership, blockIdx/threadIdx/blockDim/gridDim mapping, total_threads, block_dim, and base address bindings.

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
