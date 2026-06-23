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

warp memory bundle formation BEFORE issue is required.

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
- `sm_id`
- `warp_id`
- `pc`
- `address_vector`
- `lane_mask`
- `byte_enable_vector`
- `access_type`
- `memory_space`
- `ordering_scope`
- `coalescing_rule_trace`

## Response Shape Restore

Coalescer correctness requires both request reduction and response restoration.
The coalescer must preserve the original lane shape before merging and prove
that every response can be restored to that shape.

```yaml
coalescer_request_record:
  original_bundle_id: string
  original_request_tag: string
  original_lane_mask: string
  original_byte_enable_vector: list
  per_lane_offset: list
  merged_line_addr: string
  coalesced_request_tag: string
  split_reason_or_merge_rule: string

coalescer_response_restore:
  response_tag: string
  original_request_tag: string
  restored_lane_mask: string
  restored_lane_data: list
  restored_byte_enable: list
  final_eop: bool
```

The coalescer must not only prove that it reduced request count; it must prove
that `coalescer_response_restore` reconstructs the original lane-shaped response.

## LDS and Global Memory

The contract must separate:
- `LDS`
- `global`
- `constant`
- `scratch`
- implementation-specific spaces

LDS accesses route to SM-local storage. Global accesses route to L1/L2/DRAM
fabric. A bundle with mixed spaces must split before issue.

## Failure Modes

Coalescing evidence must identify:
- unaligned split
- bank conflict split
- divergence split
- byte-enable mismatch
- lane-mask mismatch
- coalescer response shape mismatch
- coalescer tag restore mismatch
- memory-space mismatch
- unsupported access width

## Human Output Boundary

Human-facing reports should show only concise status:
- coalescer: pass/fail
- merged transaction count
- split transaction count
- top split reason
- affected SM/warp

Full bundle YAML is AI-facing and must be registered in `ARTIFACT_MANIFEST_IR`.
