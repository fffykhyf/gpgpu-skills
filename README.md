# GPGPU Skills

This repository defines an IR-centered GPGPU design compiler flow.

## Goals

1. Reproduce a GPGPU from a complete spec.
2. Design a GPGPU from intent through candidate synthesis and closure.
3. Prevent hidden defaults, unstable outputs, and uncontrolled model inference.
4. Provide a runnable vertical-slice proof path for CUDA-like kernel -> program image -> RTL simulation -> memory dump -> golden check.

## Top-Level Skills

1. gpgpu-front-end
2. gpgpu-architecture-synthesizer
3. gpgpu-spec-lock
4. gpgpu-canonical-state-engine
5. gpgpu-artifact-contract-engine
6. gpgpu-runtime-validator
7. gpgpu-memory-subsystem
8. gpgpu-implementation-validator
9. gpgpu-closure-refinement-engine

## Flow

Intent -> Candidate -> Spec -> State -> Contract -> Validation -> Closure

Vertical-slice prototype path: CUDA-like Python kernel -> frontend -> assembler -> program.hex -> RTL simulation -> memory dump -> Python golden check.

## Shared Assets

- schemas
- tables
- examples
- tests
- flow
- references

## Legacy

The former 13 top-level GPGPU skills are preserved under `legacy/`. Their capabilities are retained as subpasses inside the 9 v4 top-level skills.
