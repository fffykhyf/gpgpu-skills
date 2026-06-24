# Rewrite Loop Core

## Merged Source Material

### Source ID: `gpgpu-loop/attribution_driven_rewrite_trigger.md`

# Attribution-Driven Rewrite Trigger

Rewrite when attribution is invalid even if output is correct:

- missing symptom counter;
- missing exclusion counter;
- missing queue/stage owner;
- root cause uses parser-only counters;
- power evidence is used as primary proof;
- memory bottleneck lacks lifecycle boundary.

### Source ID: `gpgpu-loop/config_drift_guard.md`

# Config Drift Guard

Reject rewrite plans when:

- a simulator-private parameter enters a hardware contract;
- CUDA/PTX compatibility fields enter the native ABI;
- fixed latencies become pipeline truth without a project-defined stage;
- queue depths from tested configs become defaults;
- parameter classification is missing.

## XiangShan Runtime DSE Drift Guard

Reject `DSE_EXPERIMENT_MANIFEST` when any `RUNTIME_DSE_KNOB` mutates structural
compile-time or ABI-visible fields. Debug trace knobs must be separated from
performance ranking inputs so enabling full transaction diff or trace DB writes
does not contaminate throughput comparisons.

### Source ID: `gpgpu-loop/counter_gated_regression.md`

# Counter-Gated Regression

Functional pass does not imply regression pass.

Trigger rewrite when:

- coalesced transaction count unexpectedly increases;
- scoreboard wait rises without explanation;
- barrier/membar/atomic wait lacks a sync contract;
- cache reservation fail spikes;
- ICNT `has_buffer` fail spikes;
- L2 queue full is misattributed to DRAM;
- a counter lacks producer proof.

## XiangShan Weighted Perf Gate

Performance rewrite decisions must consume `WEIGHTED_PERF_REPORT` and
`TOPDOWN_GPGPU_ATTRIBUTION` when representative checkpoints exist. Reject a
performance patch when correctness diff fails, checkpoint replay is missing, a
high-weight phase regresses without owner explanation, or debug trace knobs
contaminate the measured ranking.

### Source ID: `gpgpu-loop/legacy_closure_repair_constraints.md`

# Legacy Closure Repair Constraints

This reference migrates the useful constraints from the removed
`gpgpu-closure-refinement-engine`, legacy `gpgpu-synthesis-closure-engine`, and
their causal trace analysis behavior. The active owner is
`gpgpu-loop`.

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

### Source ID: `gpgpu-loop/patch_routing_rule.md`

# Patch Routing Rule

Patch classes include:

- `ARCHITECTURE_PATCH`
- `CONTRACT_PATCH`
- `RTL_PATCH`
- `MEMORY_PATCH`
- `INTERCONNECT_PATCH`
- `ATOMIC_SYNC_PATCH`
- `RUNTIME_ABI_PATCH`
- `COUNTER_SCHEMA_PATCH`
- `TEST_EVIDENCE_PATCH`
- `SIMULATOR_ARTIFACT_REMOVAL_PATCH`

Route by owner, not by symptom wording.

### Source ID: `gpgpu-loop/patch_taxonomy.md`

# Patch Taxonomy

## Patch Classes

- `ARCHITECTURE_PATCH`
- `CONTRACT_PATCH`
- `GOLDEN_MODEL_PATCH`
- `TOOLCHAIN_PATCH`
- `RUNTIME_PATCH`
- `RTL_PATCH`
- `PASS_EVIDENCE_PATCH`
- `TEST_EVIDENCE_PATCH`

## Patch Record

Each patch must include:

- patch target
- owner module
- expected impact
- required revalidation gates
- regression risks
- rejected alternatives

## Forbidden Behavior

The controller must not directly mutate IR. It emits patch plans that route back to the owning module.

`TOOLCHAIN_PATCH` targets assembler/disassembler derivation, program image layout,
loader contract binding, or toolchain smoke evidence. It routes to
`gpgpu-toolchain-runtime` and must not change
`SYSTEM_CONTRACT_IR` unless the root cause is reclassified as a
`CONTRACT_PATCH`.

`RUNTIME_PATCH` targets runtime argument buffer encoding, kernel launch
sequence, CSR start/done sequencing, completion observation, and fault
observation. It routes to `gpgpu-toolchain-runtime`.

`PASS_EVIDENCE_PATCH` targets missing pass evidence, unstable fingerprints,
trace coverage gaps, or incomplete evidence collection. It routes to
`gpgpu-validation` and does not imply design
behavior is wrong.

`GOLDEN_MODEL_PATCH` targets executable semantics or golden coverage derived
from `SYSTEM_CONTRACT_IR`. It routes to
`gpgpu-contract`.

### Source ID: `gpgpu-loop/regression_tracking.md`

# Regression Tracking

Regression tracking prevents repeated failed repairs from being treated as new problems.

## Required Fields

- `failure_signature`
- `previous_verdict`
- `repaired_by`
- `reappeared_in_run`
- `blocked_module`
- `next_required_evidence`
- `same_patch_attempt_count`
- `last_patch_type`
- `last_owner_module`
- `worsened_gates`
- `rollback_required`
- `escalation_policy`

## Rules

- If a failure reappears after the same patch class, escalate the patch owner.
- If evidence is insufficient twice, require additional trace instrumentation.
- If an architecture patch worsens a prior gate, emit `REGRESSION_RISK_UNBOUNDED`.
- If `same_patch_attempt_count` reaches two without improving the decisive
  gate, the next decision must either change owner or explain why escalation is
  unsafe.
- If `worsened_gates` is non-empty after an architecture patch, set
  `rollback_required` unless the decision report proves the regression is
  expected and accepted.
- `escalation_policy` must state when repeated RTL, runtime, architecture, or
  evidence patches escalate to another owner.

### Source ID: `gpgpu-loop/revalidation_routing.md`

# Revalidation Routing

Every patch plan must declare the modules and gates that must rerun.

## Routes

| Patch class | Required route |
|---|---|
| `ARCHITECTURE_PATCH` | Module 1 -> Module 2 -> Module 3 -> Module 4 -> Module 5 |
| `CONTRACT_PATCH` | Module 2 -> Module 3 -> Module 4 -> Module 5 |
| `GOLDEN_MODEL_PATCH` | Module 2 -> Module 3 -> Module 5 |
| `TOOLCHAIN_PATCH` | Module 3 -> Module 4 -> Module 5 |
| `RUNTIME_PATCH` | Module 3 -> Module 4 -> Module 5 |
| `RTL_PATCH` | Module 4 -> Module 5 |
| `PASS_EVIDENCE_PATCH` | Module 5 |
| `TEST_EVIDENCE_PATCH` | Module 5 |

`TOOLCHAIN_PATCH` reruns:

- regenerate `TOOLCHAIN_ARTIFACT_IR`
- assembler smoke
- disassembler roundtrip
- program image smoke
- loader contract smoke
- golden image execution
- RTL image-load smoke
- trace diff

`RUNTIME_PATCH` reruns:

- runtime arg encoding
- CSR launch sequence
- completion and fault observation
- RTL/golden trace diff

`PASS_EVIDENCE_PATCH` reruns:

- pass evidence report generation
- trace coverage check
- performance metric extraction
- regression fingerprint generation

## Gate

No rewrite is accepted until its route produces fresh evidence and a new attribution report.

### Source ID: `gpgpu-loop/rewrite_trigger.md`

# Rewrite Trigger

Rewrite triggers map root causes to patch classes and revalidation routes.

## Trigger Mapping

| Root cause | Patch options |
|---|---|
| `CONTRACT_ROOT_CAUSE` | Contract Patch |
| `GOLDEN_MODEL_ROOT_CAUSE` | Golden Model Patch or Contract Patch |
| `TOOLCHAIN_ROOT_CAUSE` | Toolchain Patch |
| `RUNTIME_LAUNCH_ROOT_CAUSE` | Runtime Patch |
| `RTL_FUNCTIONAL_ROOT_CAUSE` | RTL Patch |
| `RTL_INTERFACE_ROOT_CAUSE` | RTL Patch |
| `MEMORY_SYSTEM_ROOT_CAUSE` | RTL Patch or Architecture Patch |
| `SCHEDULER_ROOT_CAUSE` | RTL Patch or Architecture Patch |
| `PERFORMANCE_ARCH_ROOT_CAUSE` | Architecture Patch |
| `TEST_EVIDENCE_ROOT_CAUSE` | Test Evidence Patch or Pass Evidence Patch |
| `INSUFFICIENT_TRACE_EVIDENCE` | Test Evidence Patch |
| `ROOT_CAUSE_AMBIGUOUS` | Test Evidence Patch |

## Gate

Do not trigger a behavior-changing patch without `PERF_ATTRIBUTION_GRAPH`
evidence and a `ROOT_CAUSE_REPORT`. `PERFORMANCE_ARCH_ROOT_CAUSE` requires a
bottleneck cycle window, counter evidence, contract paths, RTL module paths, and
explicit rejected alternatives explaining why RTL, contract, runtime, or
test-evidence patches are insufficient. A `PASS_EVIDENCE_PATCH` may be
triggered by `PASS_EVIDENCE_REPORT` evidence gaps, trace coverage gaps, or
unstable `REGRESSION_FINGERPRINT` evidence.

## XiangShan Replay-Driven Triggers

`MISMATCH_PACKAGE` and `FAILURE_CAPTURE_PACKAGE` are first-class rewrite inputs.
The loop must route:

- first bad event owner to the matching owner skill
- absent capture artifact without valid reason to `TEST_EVIDENCE_PATCH`
- runtime structural knob mutation to `CONTRACT_PATCH` or `RUNTIME_PATCH`
- representative checkpoint performance regression to `ARCHITECTURE_PATCH`
  only after correctness diff passes and `WEIGHTED_PERF_REPORT` is complete

### Source ID: `gpgpu-loop/simulator_artifact_guard.md`

# Simulator Artifact Guard

If a plan introduces C++ queues, BookSim config, AccelWattch XML, CUDA stream
stack, fixed simulator latency, PTX opcode latency, or parser-only counters into
hardware contracts, route to `SIMULATOR_ARTIFACT_REMOVAL_PATCH`.
