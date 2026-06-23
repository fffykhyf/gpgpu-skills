# Memory Coalescing Contract

This file defines the runtime/toolchain-visible memory coalescing contract for
L3. It is inspired by MIAOW's explicit LSU/address/memory-space observability,
but upgrades the contract to decode-time memory bundle formation and rule-based
coalescing.

## Coalescing Rules

Coalescing Rules:
1. lanes with contiguous addresses -> merge
2. aligned accesses -> single transaction
3. bank conflict -> split transaction
4. divergence -> per-lane issue fallback

These rules are ordered. The artifact must record which rule split or merged
each memory bundle.

## Bundle Formation

wavefront memory bundle formation BEFORE issue is required.

Decode and toolchain artifacts must distinguish:
- arithmetic instruction record
- scalar/control instruction record
- memory instruction record
- `MEMORY_BUNDLE`

The LSU must consume a bundle, not re-discover all lane semantics from a raw
instruction word.

## Not Per-Instruction LSQ Only

The contract is not per-instruction LSQ only. A load/store queue may exist, but
it is downstream from decode-time bundle formation and upstream from coalescer
or memory fabric issue.

Required bundle fields:
- `bundle_id`
- `cu_id`
- `wavefront_id`
- `pc`
- `address_vector`
- `lane_mask`
- `byte_enable_vector`
- `access_type`
- `memory_space`
- `ordering_scope`
- `coalescing_rule_trace`

## LDS and Global Memory

The contract must separate:
- `LDS`
- `global`
- `constant`
- `scratch`
- implementation-specific spaces

LDS accesses route to CU-local storage. Global accesses route to L1/L2/DRAM
fabric. A bundle with mixed spaces must split before issue.

## Failure Modes

Coalescing evidence must identify:
- unaligned split
- bank conflict split
- divergence split
- byte-enable mismatch
- lane-mask mismatch
- memory-space mismatch
- unsupported access width

## Human Output Boundary

Human-facing reports should show only concise status:
- coalescer: pass/fail
- merged transaction count
- split transaction count
- top split reason
- affected CU/wavefront

Full bundle YAML is AI-facing and must be registered in `ARTIFACT_MANIFEST_IR`.
