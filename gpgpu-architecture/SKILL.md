---
name: gpgpu-architecture
description: Use when converting a GPGPU request or specification into architecture intent, resolved configuration, system composition, architecture IR, and capability profile candidates before contract freeze.
---

# gpgpu-architecture

## Role

Convert a request or specification into `DESIGN_INTENT_IR`, `CONFIG_STACK_IR`, `RESOLVED_CONFIG_IR`, `SYSTEM_COMPOSITION_IR`, `ARCH_IR`, and `CAPABILITY_PROFILE_IR`.

This skill produces a candidate architecture, not frozen semantics. It must not produce final system contract truth, define ISA encoding truth, or define RTL implementation details.

## Inputs

- User request, design spec, constraints, prior `RUN_STATE.yaml`.
- Optional source lessons from `shared/references/reference_lessons.yaml`.

## Core Files

- Read `architecture_core.md` for request normalization, evidence classification, simulator-only rejection, issue/non-issue taxonomy, and performance attribution rules.
- Read `capability_profiles.md` for capability presets, scheduler-visible state, SM hierarchy, warp state, and capability pack selection.
- All generated IR and derived artifacts must obey `shared/references/canonical_generation_rules.md` before hash calculation, comparison, validation, or rewrite routing.

## Capability Pack Selection

Choose optional packs in `CAPABILITY_PROFILE_IR.enabled_packs` only when required:

- `memory_path`
- `interconnect`
- `atomic_sync`

## Output Policy

Default:

- `ITERATION_SUMMARY.zh.md`
- `RUN_STATE.yaml` delta

Contract freeze only:

- `ARCH_IR.yaml`
- `CAPABILITY_PROFILE_IR.yaml`

## Boundaries

- Do not freeze `SYSTEM_CONTRACT_IR`.
- Do not define final ISA behavior, memory semantics, atomic/fence/barrier semantics, or observable state semantics.
- Do not bind wires or modules; leave that to `gpgpu-rtl`.
