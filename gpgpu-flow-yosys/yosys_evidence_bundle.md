# Yosys Evidence Bundle

## Required Bundle

`YOSYS_EVIDENCE_BUNDLE` binds a Yosys profile result to reproducible artifacts.
It must include paths, hashes, parsed metrics, warnings, errors, and claim
boundary text.

## Required Fields

```yaml
bundle_id:
profile_id:
yosys_version:
flow_hash:
filelist_hash:
script_hash:
build_dir:
report_dir:
logs:
reports:
parsed_metrics:
warnings:
errors:
claim_boundary:
```

## Required Reports

For `yosys_ppa_baseline`, the bundle must include at least:

- Yosys log
- `check` report or equivalent parsed check output
- `stat` report
- script used to produce the result
- filelist hash
- script hash
- warning summary
- error summary
- explicit claim boundary

Missing `stat` report rejects PPA baseline claims. A build_dir/report_dir/log
path mismatch rejects the bundle until `REPORT_PATH_PATCH` repairs it.

## Warning and Error Handling

Warnings are not automatically fatal, but warnings that map to fail-closed RTL
style rules must route to `YOSYS_RTL_STYLE_PATCH`. Any Yosys error in the
selected profile yields `YOSYS_EVIDENCE_MISSING` unless the profile explicitly
declares the error as outside claim scope.

## Claim Boundary

The bundle must state what the evidence can and cannot prove. Yosys-only PPA
baseline evidence cannot prove timing closure, MHz frequency, backend signoff,
or frequency closure.
