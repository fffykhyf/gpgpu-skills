---
name: gpgpu-closure-refinement-engine
description: Use when architecture candidates, locked specs, state, artifact reports, runtime/memory/implementation validation, PPA evidence, and trace divergences must be accepted, rejected, or routed to refinement.
---

# GPGPU Closure Refinement Engine

## Role

This skill is the final acceptance, failure attribution, and refinement-request compiler pass.

## Position in Flow

Upstream:
- gpgpu-architecture-synthesizer
- gpgpu-spec-lock
- gpgpu-canonical-state-engine
- gpgpu-artifact-contract-engine
- gpgpu-runtime-validator
- gpgpu-memory-subsystem
- gpgpu-implementation-validator

Downstream:
- User-facing closure decision
- Repair owner skill for refinement loops

## Input IR

Consumes:
- ARCH_CANDIDATE_IR
- SPEC_IR
- GPU_STATE_IR
- ARTIFACT_CONTRACT_REPORT
- RUNTIME_VALIDATION_REPORT
- MEMORY_VALIDATION_REPORT
- IMPLEMENTATION_VALIDATION_REPORT
- PPA_REPORT
- TRACE_DIVERGENCE_REPORT

## Output IR

Produces:
- SYNTHESIS_ACCEPTANCE_REPORT_IR
- REFINEMENT_REQUEST_IR

## Owned Decisions

This skill owns:
- Closure gate evaluation
- Failure attribution
- Refinement request generation
- Repair routing

## Forbidden Actions

This skill must not:
- Design architecture
- Bypass failed gates
- Accept evidence-free candidates
- Directly mutate ARCH_CANDIDATE_IR, SPEC_IR, or GPU_STATE_IR

## Required Tables

This skill must use:
- shared/tables/closure_gate_table.yaml
- shared/tables/verdict_decision_table.yaml
- shared/tables/failure_taxonomy_table.yaml
- shared/tables/repair_routing_table.yaml

## Required Schemas

This skill must validate:
- shared/schemas/synthesis_acceptance_report_ir.schema.yaml
- shared/schemas/refinement_request_ir.schema.yaml

## Required Invariants

The output must satisfy:
- Verdict is one of ACCEPT, REJECT, REFINE_REQUIRED, INSUFFICIENT_EVIDENCE
- Every failed gate has owner, affected field, evidence, and repair route
- Hard correctness failures reject
- Repairable trace failures refine

## Failure Modes

This skill must emit:
- INSUFFICIENT_EVIDENCE
- HARD_CORRECTNESS_FAIL
- REPAIRABLE_TRACE_FAIL
- UNROUTED_FAILURE
- INSUFFICIENT_SKILL_ASSET

## Report Schema

The report must include:
- verdict
- consumed_ir_hash
- produced_ir_hash
- gate_results
- failed_fields
- missing_assets
- downstream_contract
- refinement_request

## Concrete Assets Required

This skill is incomplete unless the following exist:
- closure_gate.md
- causal_trace_analysis.md
- refinement_request.md
- shared/schemas/synthesis_acceptance_report_ir.schema.yaml
- shared/schemas/refinement_request_ir.schema.yaml
- shared/tables/closure_gate_table.yaml
- shared/tables/verdict_decision_table.yaml
- shared/tables/failure_taxonomy_table.yaml
- shared/tables/repair_routing_table.yaml

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
