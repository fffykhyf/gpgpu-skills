# Legacy Closure Repair Constraints

This reference migrates the useful constraints from the removed
`gpgpu-closure-refinement-engine`, legacy `gpgpu-synthesis-closure-engine`, and
their causal trace analysis behavior. The active owner is
`gpgpu-architecture-rewrite-loop-controller`.

The controller emits `ARCH_REWRITE_PLAN`; it does not directly edit the
architecture, contract, golden model, RTL map, or trace inputs.

## Closure Gate Inputs

Rewrite decisions must be based on evidence, not on the presence of a failed
report alone. Inputs include:

- `ARCH_IR`
- `SYSTEM_CONTRACT_IR`
- `GOLDEN_CONTRACT_MODEL`
- `INCREMENTAL_RTL_MAP`
- `PERF_ATTRIBUTION_GRAPH`
- `ROOT_CAUSE_REPORT`
- regression history
- validation gate status
- failed owner and field paths

If the failure lacks owner, field path, evidence hash, and revalidation route,
the controller must emit `PATCH_OWNER_MISSING` or
`REVALIDATION_ROUTE_MISSING`.

Legacy closure verdicts map to v5 decisions as follows:

- `ACCEPT` maps to no rewrite plan and completed regression evidence.
- `REJECT` maps to no automatic patch unless a supported owner can be named.
- `REFINE_REQUIRED` maps to an `ARCH_REWRITE_PLAN` candidate.
- `INSUFFICIENT_EVIDENCE` maps to a Test Evidence Patch or fail-closed report.

## Failure Attribution

The old closure engine's useful behavior is retained as rewrite attribution.
Each failure must identify:

- failed gate
- responsible owner module
- affected IR path
- evidence source
- nearest causal node in `PERF_ATTRIBUTION_GRAPH`
- repair class
- regression risk
- required revalidation gates

The controller must not directly mutate IR or RTL. It emits a plan that routes
back to the owner module.

## Patch Classes

Valid patch classes are:

- Architecture Patch: warp size, SM partition, scheduler class, issue width,
  memory hierarchy, cache/shared-memory sizing, occupancy target
- Contract Patch: scheduling rule, divergence rule, memory ordering, launch
  ABI, CSR behavior, scoreboard semantics
- RTL Patch: module interface, pipeline boundary, scoreboard implementation,
  LSQ replay policy, coalescer structure, cache/global protocol
- Test Evidence Patch: missing trace, undeclared validation gate, stale
  artifact hash, missing golden output, insufficient coverage

Every accepted patch must include expected impact, owner, target paths,
validation gates, and rollback or regression criteria.

## Migrated Failure Taxonomy

The rewrite controller must preserve these legacy failure classes as
attribution inputs or patch triggers:

- `DOC_ARTIFACT_DRIFT`
- `ISA_ENCODING_DRIFT`
- `DECLARED_TEST_NOT_RUN`
- `APP_COMPILE_FAIL`
- `MAGIC_CONSTANT_UNBOUND`
- `FRONTEND_RUNTIME_MAPPING_MISMATCH`
- `MEMORY_DUMP_CONTRACT_MISMATCH`
- `FIRST_DIVERGENCE_UNATTRIBUTED`
- `TRACE_EVIDENCE_MISSING`
- `CONTRACT_PATH_UNMAPPED`
- `RTL_MODULE_UNBOUND`

These classes do not replace v5 root causes. They provide compatibility labels
that must map to v5 patch classes and revalidation routes.
