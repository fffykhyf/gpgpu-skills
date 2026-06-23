# GPGPU Design Flow

This flow is a self-correcting GPGPU design system. Skills are modules. Schemas define accepted IR. Tables define decisions. Examples and tests define regression behavior. The active abstraction is a CU-centric wavefront execution contract model.

## Artifact Visibility Policy

All structured IRs and evidence reports are AI-facing artifacts by default.
Human-facing outputs must be concise Chinese reports. A skill must not expose
full machine IR to the user unless one of these triggers applies:

1. The user explicitly asks for the full artifact.
2. Contract freeze requires human review of exact semantics.
3. Root cause evidence is ambiguous.
4. A regression reappears and needs exact historical fields.
5. A downstream owner needs exact fields to implement or validate a patch.

Default behavior:

- Human Reports are written in Chinese, use `.zh.md`, and are shown by default.
- AI Artifacts are written in English, use `.yaml`, `.json`, or `.en.md`, and
  are registered in `ARTIFACT_MANIFEST_IR` instead of shown by default.
- Debug Evidence is retained in English and summarized for humans in Chinese
  dashboards, debug summaries, or patch cards.

The guiding rule is: keep complete engineering evidence, but reduce what a
human must read by default.

## Output Modes

The active output mode is defined by `shared/schemas/output_mode_ir.schema.yaml`
and `shared/tables/output_mode_table.yaml`.

- `FAST_ITERATION`: quick design and early implementation loops. Humans see
  a small Chinese design brief, architecture decision, implementation dashboard,
  validation dashboard, and a patch card only on failure.
- `CONTRACT_FREEZE`: review before freezing ISA, ABI, memory model, launch ABI,
  interface semantics, and config ownership. Humans see a Chinese freeze
  summary and the relevant decision/dashboard reports; AI keeps complete English
  IRs.
- `DEBUG_REGRESSION`: failure, ambiguous root cause, recurring regression, or
  insufficient trace evidence. Humans see Chinese debug summary, patch card, and
  regression summary; AI keeps normalized traces, root cause reports, rewrite
  plans, and regression tracking artifacts.

## Active Flow

```text
Architecture Generator
  -> System Contract + Golden Semantics Engine
  -> Toolchain + Runtime Artifact Engine
  -> Incremental RTL Binding Engine
  -> Interconnect Contract Engine
  -> Memory System Contract Engine
  -> Atomic and Synchronization Contract Engine
  -> Simulation + Performance Attribution Engine
  -> Architecture Rewrite Loop Controller
  -> back to Architecture Generator / Contract / Toolchain / RTL Binding / Memory
```

## L3 contract layer

CU is the canonical execution island. L3 contracts add:

- `wavefront_state_contract.md`: wavefront lifecycle, EXEC mask evolution,
  branch divergence model, and reconvergence stack.
- `cu_hierarchy_model.md`: CU hierarchy with wavepool, exec context table, LDS,
  LSU front-end, SIMD lanes, and CU issue model.
- `memory_coalescing_contract.md`: rule-based coalescing before issue.
- `lsu_instruction_bundle.md`: decode-stage `MEMORY_BUNDLE` contract.
- `cu_instance_layout.md`: CU_ID routing, wave dispatch mapping, and no
  cross-CU dependency.
- `multi_cu_trace_model.md`: CU-level trace partitioning and memory ordering per
  CU.

## L4 system memory and synchronization layer

L4 contracts add:

- `gpgpu-interconnect`: explicit NoC routing, CU-to-L2 routing, request queues,
  request merging across CU, and congestion evidence.
- `gpgpu-memory`: DRAM controller contract, bank-level parallelism model,
  writeback/write-through policy, and cross-CU coherence.
- `gpgpu-atomic-sync`: atomic serialization point, per-CU atomic ordering,
  global atomic consistency, hierarchical barriers, and fence ordering
  semantics.

## Module 1: Architecture Generator

Input: user intent, optional spec, optional trace, patch request, presets, constraints, and reference evidence.

Output:

- `DESIGN_INTENT_IR`
- `ARCH_IR`
- `MICRO_CONSTRAINT_ESTIMATE_IR`
- Human reports: `DESIGN_BRIEF.zh.md`, `ARCHITECTURE_DECISION.zh.md`

This module estimates area, memory pressure, wavefront occupancy, register pressure, LDS pressure, bandwidth need, and unrealizable risks before contract freeze.

## Module 2: System Contract + Golden Semantics Engine

Input: `ARCH_IR` and micro-constraint estimates.

Output:

- `SYSTEM_CONTRACT_IR`
- `GOLDEN_CONTRACT_MODEL`
- `CONTRACT_SEMANTICS_REPORT`
- Human report: `CONTRACT_FREEZE_SUMMARY.zh.md`

`SYSTEM_CONTRACT_IR` is the only semantic truth source. `GOLDEN_CONTRACT_MODEL` is executable reference semantics derived from it, not a second simulator or second ISA source.

## Module 3: Toolchain + Runtime Artifact Engine

Input: `SYSTEM_CONTRACT_IR` and `GOLDEN_CONTRACT_MODEL`.

Output:

- `TOOLCHAIN_ARTIFACT_IR`
- `ASSEMBLY_IR`
- `PROGRAM_IMAGE_IR`
- `RUNTIME_LAUNCH_IR`
- `LOADER_CONTRACT_IR`
- `TOOLCHAIN_SMOKE_REPORT`
- Human dashboard contribution: toolchain/runtime fields in `VALIDATION_DASHBOARD.zh.md`
- Human failure report: `PATCH_CARD.zh.md` when toolchain or runtime evidence fails

This module derives assembler, disassembler, ISA table, program image, runtime launch, and loader artifacts from `SYSTEM_CONTRACT_IR`. It must not define independent ISA, ABI, program image, loader, or runtime truth.

## Module 4: Incremental RTL Binding Engine

Input: `SYSTEM_CONTRACT_IR`, `GOLDEN_CONTRACT_MODEL`, `TOOLCHAIN_ARTIFACT_IR`, `PROGRAM_IMAGE_IR`, `RUNTIME_LAUNCH_IR`, `LOADER_CONTRACT_IR`, module catalog, and interface tables.

Output:

- `INCREMENTAL_RTL_MAP`
- `MODULE_INTERFACE_REPORT`
- `RTL_PARTIAL_SIM_REPORT`
- Human report: `IMPLEMENTATION_DASHBOARD.zh.md`

RTL is assembled module by module. Each module declares consumed contract paths, provided signals, required signals, latency contract, local trace schema, and partial simulation evidence.

## Module 5: Simulation + Performance Attribution Engine

Input: assembler, disassembler, program-image, loader, runtime-launch, memory,
RTL, waveform-derived, module partial-sim, and golden program-image execution
traces, plus `GOLDEN_CONTRACT_MODEL`, `INCREMENTAL_RTL_MAP`,
`TOOLCHAIN_ARTIFACT_IR`, `PROGRAM_IMAGE_IR`, `RUNTIME_LAUNCH_IR`, and
`LOADER_CONTRACT_IR`.

Output:

- `NORMALIZED_TRACE_IR`
- `CORRECTNESS_GATE_REPORT`
- `FIRST_DIVERGENCE_REPORT` in failure mode
- `PASS_EVIDENCE_REPORT` in pass mode
- `TRACE_COVERAGE_REPORT`
- `PERFORMANCE_METRIC_IR`
- `REGRESSION_FINGERPRINT`
- `PERF_ATTRIBUTION_GRAPH`
- `ROOT_CAUSE_REPORT`
- `TOOLCHAIN_ATTRIBUTION_REPORT`
- `SIM_PERF_ATTRIBUTION_REPORT`
- Human reports: `VALIDATION_DASHBOARD.zh.md`, and on failure `DEBUG_SUMMARY.zh.md`

The correctness gate selects Failure Attribution Mode or Pass Evidence Mode.
`RTL == golden` is not a skip: a passing run still records pass evidence,
coverage, performance metrics, and a regression fingerprint. Failure mode finds
the first deterministic divergence before producing root cause and rewrite
routing. Performance conclusions must connect cycle, CU, wavefront, bottleneck evidence,
contract path, and RTL module or toolchain artifact evidence.

## Module 6: Architecture Rewrite Loop Controller

Input: `PERF_ATTRIBUTION_GRAPH`, `ROOT_CAUSE_REPORT`, `ARCH_IR`, `SYSTEM_CONTRACT_IR`, `GOLDEN_CONTRACT_MODEL`, `TOOLCHAIN_ARTIFACT_IR`, `INCREMENTAL_RTL_MAP`, and regression history.

Output:

- `ARCH_REWRITE_PLAN`
- `REWRITE_DECISION_REPORT`
- `REGRESSION_TRACKING_REPORT`
- Human reports: `PATCH_CARD.zh.md`, `REGRESSION_SUMMARY.zh.md`

The controller may propose Architecture Patch, Contract Patch, Toolchain Patch, RTL Patch, or Test Evidence Patch. It must not directly mutate IR. Every patch routes to the owning module and triggers revalidation.

## Legacy Migration Path

Legacy v4 top-level skills and the old `legacy/` skill archive are not active wrappers. They were deleted after their useful constraints were migrated into the current owner modules and core constraint files:

- `gpgpu-front-end` and `gpgpu-architecture-synthesizer` constraints live in `gpgpu-arch/legacy_request_and_candidate_constraints.md`.
- `gpgpu-spec-lock` and `gpgpu-canonical-state-engine` constraints live in `gpgpu-golden/contract_truth_and_state_model.md`.
- `gpgpu-artifact-contract-engine`, structural memory-path, runtime interface, and implementation binding constraints live in `gpgpu-rtl/module_binding_rules.md`.
- `gpgpu-runtime-validator`, memory validation, and implementation trace constraints live in `gpgpu-simppa/legacy_validation_and_trace_constraints.md`.
- `gpgpu-closure-refinement-engine` constraints live in `gpgpu-loop/legacy_closure_repair_constraints.md`.

## Fail Closed Policy

Missing schema, missing table row, hidden default, unsupported enum, forbidden provenance, unmapped contract paths, interface mismatches, missing causal evidence, and unowned rewrite triggers must reject or emit `INSUFFICIENT_SKILL_ASSET`.
