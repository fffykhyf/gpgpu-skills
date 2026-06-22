# RTL SIMT Core Validation

## Purpose

Validate fetch, decode, issue, execute, writeback, scheduler, active mask, scoreboard, register, CSR, pipeline, memory request interface events, and vertical-slice smoke tests: app_compile_smoke, assembler_smoke, program_hex_load_smoke, rtl_sim_smoke, memory_dump_compare, and waveform_or_trace_required.

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
