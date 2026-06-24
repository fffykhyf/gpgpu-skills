# Yosys Flow Core

## Role

Create and validate a deterministic `YOSYS_FLOW_IR` for RTL that targets Yosys
elaboration, generic synthesis, or a lightweight PPA baseline. The flow records
how evidence was produced; it does not alter design semantics.

## Required Inputs

- RTL filelist
- include directories
- defines
- selected top module
- optional `chparam` values
- selected profile from `shared/tables/yosys_profile_matrix.yaml`
- build_dir, report_dir, log_dir
- Yosys script path
- claim scope

## YOSYS_FLOW_IR

The flow record must contain:

```yaml
flow_id:
yosys_version:
frontend_mode:
filelist:
include_dirs:
defines:
chparams:
top_module:
profile_id:
build_dir:
report_dir:
log_dir:
script_path:
claim_scope:
```

`filelist`, `script_path`, `build_dir`, `report_dir`, and `log_dir` must be
artifact paths, not prose-only references. Missing paths route to
`REPORT_PATH_PATCH` or `YOSYS_FLOW_PATCH`.

## Profile Selection

Use the narrowest profile that supports the requested claim:

- `yosys_lint_parse`: parse, frontend compatibility, and early script checks.
- `yosys_elaborate`: top-module elaboration and hierarchy checks.
- `yosys_synth_generic`: generic synthesis and structural hygiene.
- `yosys_ppa_baseline`: generic synthesis metrics and relative area trend.

Do not escalate a profile to produce a stronger claim unless the required
reports are present in `YOSYS_EVIDENCE_BUNDLE`.

## Flow Identity

`flow_hash` must include Yosys version, frontend mode, filelist hash, defines,
include directories, `chparam` values, top module, selected profile, and script
hash. Reusing an old report with a changed filelist or script is evidence drift.

## Failure Modes

- `YOSYS_FLOW_IR_MISSING`
- `YOSYS_PROFILE_UNSUPPORTED`
- `YOSYS_SCRIPT_MISSING`
- `BUILD_DIR_REPORT_PATH_MISMATCH`
- `FILELIST_HASH_MISMATCH`
- `SCRIPT_HASH_MISMATCH`
- `YOSYS_EVIDENCE_MISSING`

## Ownership Boundary

This skill may request an RTL style patch, but it must not rewrite the RTL
semantics. Unsupported backend claims route to validation and loop instead of
being silently weakened.
