# Yosys Profile Matrix

## Table Owner

`shared/tables/yosys_profile_matrix.yaml` is the source of truth for supported
Yosys profiles and required evidence.

## Profiles

### yosys_lint_parse

Use for frontend parse checks, filelist sanity, include/define handling, and
early RTL style evidence. This profile cannot claim elaboration success or PPA.

### yosys_elaborate

Use for top-module elaboration, hierarchy resolution, parameter override
checks, and frontend-compatible RTL proof. This profile cannot claim generic
synthesis metrics unless synthesis reports are present.

### yosys_synth_generic

Use for generic synthesis and structural hygiene checks. It may support a
synthesizes-on-Yosys claim when check/stat reports and logs are present.

### yosys_ppa_baseline

Use for generic synthesis metrics only. It can support cell count, wire bits,
hierarchy size, relative area trend, and synthesis hygiene. It cannot claim
timing closure, frequency_mhz, backend signoff, or frequency closure.

## Selection Rule

Choose the lowest profile that can support the user-visible claim. When the
claim asks for more than the selected profile can support, route a
`BACKEND_CLAIM_PATCH` through validation and loop.
