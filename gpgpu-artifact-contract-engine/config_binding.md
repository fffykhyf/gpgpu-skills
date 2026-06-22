# Config Binding

## Purpose

Classify config fields as hardware_private, simulator_private, hw_sw_abi, test_only, or debug_only. Validate owner and allowed consumers. Magic constants such as total_threads, block_dim, base_data_addr, base_a, base_b, base_c, dump_range, and finish_delay must be bound through CONFIG_BINDING_IR or rejected as MAGIC_CONSTANT_UNBOUND.

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
