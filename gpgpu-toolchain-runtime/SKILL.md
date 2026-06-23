---
name: gpgpu-toolchain-runtime
description: Use when deriving GPGPU assembler, disassembler, assembly IR, program image, loader contract, runtime launch, MMIO, debug counters, or toolchain smoke gates from the frozen system contract.
---

# gpgpu-toolchain-runtime

## Role

Derive assembler, disassembler, assembly IR, program image, loader contract, runtime launch, MMIO/debug counter binding, and smoke gates from `SYSTEM_CONTRACT_IR`.

## Core File

Read `toolchain_runtime_core.md` for ISA table derivation, assembly IR, assembler/disassembler roundtrip, program image and loader contract, runtime launch, LSU instruction bundle, coalescer input traces, compatibility mapping, and smoke gates.

## Required Rules

- Do not define independent ISA truth.
- Do not invent memory or coalescer behavior outside `SYSTEM_CONTRACT_IR`.
- Preserve assembler/disassembler roundtrip.
- Preserve the `START/BUSY/DONE/FAULTED/ACK` smoke gate.

## Default Outputs

- `RUN_STATE.yaml` delta
- `TOOLCHAIN_ARTIFACT_IR` only if changed
- `PROGRAM_IMAGE_IR` only if changed
- `TOOLCHAIN_SMOKE_REPORT` only if running smoke
