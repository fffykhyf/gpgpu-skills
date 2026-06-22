# SPEC_IR Contract

## Purpose

Lock only complete architecture facts. Required groups are ISA, isa_source_of_truth, warp model, grid/block/thread model, scheduler, register file, memory hierarchy, CSR/DCR, launch ABI, config defaults, and hooks. Docs, RTL defines, and tool opcode tables must be derived from SPEC_IR.isa.

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
