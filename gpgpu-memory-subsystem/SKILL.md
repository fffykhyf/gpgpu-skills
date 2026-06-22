---
name: gpgpu-memory-subsystem
description: Use when GPGPU memory subsystem contract, RTL-facing memory path, memory request lifecycle, duplicate request prevention, coalescing, LSQ, shared memory, cache/global interface, ordering, tags, and scoreboard wakeup must be defined and validated.
---

# GPGPU Memory Subsystem

## Role

This skill defines and validates the GPGPU memory subsystem contract and RTL-facing memory path from canonical state and memory model inputs. It must make request issue, stall, response, replay, and scoreboard wakeup observable.

## Position in Flow

Upstream:
- gpgpu-canonical-state-engine memory_request_state, warp_state, scoreboard_state
- gpgpu-artifact-contract-engine MEMORY_MODEL_IR and RTL_MAPPING_IR.memory_interface

Downstream:
- gpgpu-implementation-validator
- gpgpu-closure-refinement-engine

## Input IR

Consumes:
- GPU_STATE_IR.memory_request_state
- GPU_STATE_IR.warp_state
- GPU_STATE_IR.scoreboard_state
- MEMORY_MODEL_IR
- RTL_MAPPING_IR.memory_interface

## Output IR

Produces:
- MEMORY_SUBSYSTEM_IR
- MEMORY_VALIDATION_REPORT_IR
- memory_trace
- memory_ordering_report
- memory_rtl_interface_report

## Owned Decisions

This skill owns:
- Address spaces
- Global/shared/local/constant memory
- Load/store path
- memory_request_lifecycle
- duplicate_request_prevention
- request_replay_policy
- Coalescing policy
- Lane mask handling
- Byte enables
- Load/store queue
- Outstanding request table
- Request/response tags
- Shared memory banks
- Cache/global interface
- Atomic unit
- Fence ordering
- Memory fault contract
- Scoreboard wakeup
- Backpressure

## Forbidden Actions

This skill must not:
- Choose architecture memory hierarchy not present in SPEC_IR
- Modify scheduler policy
- Treat memory validation as runtime launch validation
- Ignore tag or lane-mask mismatches

## Required Tables

This skill must use:
- shared/tables/memory_address_space_table.yaml
- shared/tables/coalescing_rule_table.yaml
- shared/tables/shared_memory_bank_table.yaml
- shared/tables/memory_ordering_table.yaml
- shared/tables/memory_scoreboard_wakeup_table.yaml

## Required Schemas

This skill must validate:
- shared/schemas/memory_model_ir.schema.yaml
- shared/schemas/memory_subsystem_ir.schema.yaml
- shared/schemas/memory_validation_report_ir.schema.yaml

## Required Invariants

The output must satisfy:
- Lane mask drives byte enable generation
- Request tags are unique until response
- Load response wakes matching scoreboard dependency
- Fences enforce declared ordering
- Bank conflicts are detected and reported
- A stalled memory instruction does not duplicate a serviced request
- stall_release_condition is tied to response_match_policy and scoreboard_wakeup_condition

## Failure Modes

This skill must emit:
- REQUEST_TAG_MISMATCH
- BANK_CONFLICT_DETECTED
- ORDERING_VIOLATION
- SCOREBOARD_WAKEUP_MISSING
- DUPLICATE_MEMORY_REQUEST
- MEMORY_STALL_RELEASE_MISSING
- INSUFFICIENT_SKILL_ASSET

## Report Schema

The report must include:
- verdict
- consumed_ir_hash
- produced_ir_hash
- memory_trace_hash
- ordering_results
- failed_fields
- missing_assets
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- memory_model.md
- coalescer.md
- load_store_queue.md
- shared_memory.md
- cache_global_interface.md
- scoreboard_wakeup.md
- shared/schemas/memory_subsystem_ir.schema.yaml
- shared/tables/coalescing_rule_table.yaml
- shared/tables/memory_ordering_table.yaml

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
