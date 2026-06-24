---
name: gpgpu-rtl
description: Use when binding GPGPU RTL modules to frozen contract paths, negotiated interfaces, adapter contracts, protocol monitors, partial simulation evidence, Yosys RTL compatibility reports, traces, and counter tap points.
---

# gpgpu-rtl

## Role

Perform module-by-module RTL binding from `SYSTEM_CONTRACT_IR`, `TOOLCHAIN_ARTIFACT_IR`, and `NEGOTIATED_INTERFACE_IR`.

This skill owns `INCREMENTAL_RTL_MAP` and contributes
`YOSYS_RTL_COMPATIBILITY_REPORT` findings when RTL is targeting Yosys. It must
not change architecture semantics or ISA semantics. It must not use raw wire
binding unless it comes from a negotiated interface edge.

## Core File

Read `rtl_binding_core.md` for module binding rules, interface/checker binding,
Yosys RTL compatibility gates, partial simulation gates, trace/counter hooks,
simulator-artifact rejection, SM instance layout, and warp execution mapping.
All generated IR and derived artifacts must obey `shared/references/canonical_generation_rules.md` before hash calculation, comparison, validation, or rewrite routing.
RTL correctness cannot be marked strong unless relevant `gpgpu-validation/formal_assertion_pack.md` entries are proven, bounded-checked, simulated as assertions, or explicitly waived with a contract-path-bound reason.

## Core Execution Loop

```text
select module
  -> list consumed contract paths
  -> list produced contract paths
  -> bind negotiated interface
  -> generate or update RTL
  -> attach trace/counter hooks
  -> run partial sim
  -> update INCREMENTAL_RTL_MAP
```

## Evidence

Produce partial sim evidence, maintain observable trace hooks, and maintain counter tap points for validation.

When backend evidence names Yosys, also emit `YOSYS_RTL_COMPATIBILITY_REPORT`
and `RTL_SYNTH_HYGIENE_REPORT` for the RTL style surface owned by this skill.
