---
name: gpgpu-contract
description: Use when freezing GPGPU system contract truth, deriving the golden contract model, or loading memory/interconnect/atomic synchronization contract packs from a capability profile.
---

# gpgpu-contract

## Role

Freeze `SYSTEM_CONTRACT_IR` and derive `GOLDEN_CONTRACT_MODEL`.

This skill owns architectural semantics. It is the only owner of final ISA behavior, memory semantics, atomic/fence/barrier semantics, and observable state semantics. The golden model must be derived only from `SYSTEM_CONTRACT_IR`.

## Core Files

- Read `system_contract_core.md` for truth ownership, freeze rules, functional/timing boundaries, and compatibility profile contracts.
- Read `golden_semantics.md` for executable semantics, coverage, module twins, SIMT traces, memory transactions, and synchronization semantics.
- All generated IR and derived artifacts must obey `shared/references/canonical_generation_rules.md` before hash calculation, comparison, validation, or rewrite routing.

## Optional Packs

Load packs based on `CAPABILITY_PROFILE_IR.enabled_packs`:

```yaml
packs:
  memory_path:
    loaded_when:
      - capability_profile requires shared memory
      - global memory
      - coalescer
      - cache
      - L1/global adapter
      - L2/DRAM
  interconnect:
    loaded_when:
      - capability_profile requires multi-SM
      - NoC
      - L2 slice routing
      - fabric backpressure
      - request/response routing
  atomic_sync:
    loaded_when:
      - capability_profile requires atomics
      - fence
      - barrier
      - CTA synchronization
      - memory consistency
```

## Boundaries

- Do not invent independent ISA, runtime, or RTL semantics.
- Do not accept simulator-only behavior unless converted into hardware contract truth with provenance.
- Runtime/toolchain and RTL must consume contract paths from `SYSTEM_CONTRACT_IR`.
