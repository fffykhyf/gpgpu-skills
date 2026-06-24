---
name: gpgpu-loop
description: Use when routing GPGPU patches from validation evidence, regression fingerprints, root-cause results, config drift, or performance evidence back to the responsible skill.
---

# gpgpu-loop

## Role

Route patches based on validation evidence.

This skill must not directly rewrite architecture, contract, runtime, or RTL semantics. It generates patch cards and revalidation routes.

## Core File

Read `rewrite_loop_core.md` for rewrite triggers, config drift guard, counter-gated regression, patch routing, patch taxonomy, regression tracking, revalidation routing, and simulator-artifact guards.
All generated IR and derived artifacts must obey `shared/references/canonical_generation_rules.md` before hash calculation, comparison, validation, or rewrite routing.

## Patch Classes

- Architecture Patch
- Contract Patch
- Toolchain Patch
- RTL Patch
- Validation Harness Patch
- Performance Tuning Patch

## Required Rejection

Reject simulator-only patches that do not map to real hardware contract or RTL behavior.

## Outputs

- `PATCH_CARD.zh.md`
- `REWRITE_DECISION_REPORT`
- `RUN_STATE.yaml` delta
- revalidation route with target skill, touched contract paths, and required gates
