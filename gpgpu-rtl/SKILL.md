---
name: gpgpu-rtl
description: Use when binding GPGPU RTL modules to frozen contract paths, negotiated interfaces, adapter contracts, protocol monitors, partial simulation evidence, traces, and counter tap points.
---

# gpgpu-rtl

## Role

Perform module-by-module RTL binding from `SYSTEM_CONTRACT_IR`, `TOOLCHAIN_ARTIFACT_IR`, and `NEGOTIATED_INTERFACE_IR`.

This skill owns `INCREMENTAL_RTL_MAP`. It must not change architecture semantics or ISA semantics. It must not use raw wire binding unless it comes from a negotiated interface edge.

## Core File

Read `rtl_binding_core.md` for module binding rules, interface/checker binding, partial simulation gates, trace/counter hooks, simulator-artifact rejection, SM instance layout, and warp execution mapping.

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
