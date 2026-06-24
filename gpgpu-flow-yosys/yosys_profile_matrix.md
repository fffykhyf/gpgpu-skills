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

### yosys_elaborate_only

Use for parse and hierarchy elaboration only. Required evidence includes
`read_verilog_log`, `hierarchy_check`, and `proc_check`. It may claim syntax
parse and hierarchy elaboration, but not Fmax, timing closure, bounded protocol
correctness, or proof.

### yosys_synth_hygiene

Use for generic synthesis hygiene. Required evidence includes `check.rpt`,
`stat.rpt`, and `yosys.log`. It may claim cell count, wire bits, hierarchy
size, and synthesis hygiene, but not timing closure, Fmax, or proof.

### sby_bmc_interface_protocol

Use for bounded valid/ready and tag protocol checking with SymbiYosys. Required
evidence includes `sby_status`, `engine_log`, and
`counterexample_or_proof_log`. It may claim bounded absence of protocol
violation, never unbounded correctness.

### smtbmc_assertion_pack

Use for bounded assertion-pack checks through `smtbmc`. Required evidence
includes `smtbmc_log`, `assertion_status`, and `witness_or_vcd_on_fail`. It may
claim bounded assertion pass or counterexample found, never exhaustive proof.

## Selection Rule

Choose the lowest profile that can support the user-visible claim. When the
claim asks for more than the selected profile can support, route a
`BACKEND_CLAIM_PATCH` through validation and loop.

Yosys-only profiles must not claim Fmax or timing closure. Bounded formal
profiles must not claim unbounded correctness, and simulation-only assertions
must not claim proof.
