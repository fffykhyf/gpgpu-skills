# Legacy Request and Candidate Constraints

This reference migrates the useful constraints from the removed
`gpgpu-front-end`, `gpgpu-architecture-synthesizer`,
`gpgpu-mode-controller`, and `gpgpu-design-intent-lock` skills. These rules
are owned by `gpgpu-architecture-generator`; they must not be reintroduced as
separate top-level skills.

## Request Classification

The generator must classify the request before producing `DESIGN_INTENT_IR`.
Supported classes include:

- complete GPU design request
- vertical-slice design request
- architecture patch request
- trace-driven redesign request
- clarification-required request

Classification must record the evidence used for the decision. If target
behavior, workload class, validation goal, or platform constraints are missing,
the output must either reject with `INSUFFICIENT_REQUEST` or record an explicit
non-goal. The generator must not silently infer a GPU family, warp size, memory
hierarchy, ISA subset, or runtime ABI from common practice.

Mode routing from the old mode controller is now local to this generator. It
must recognize reproduce, from-zero design, patch request, and trace-debug
requests, but it may only route to the current v5 owner modules. It must not
emit legacy `SPEC_IR`, `GPU_STATE_IR`, or legacy next-skill names.

## Design Intent Lock

`DESIGN_INTENT_IR` must lock only user intent and explicitly approved
assumptions. It must include:

- requested GPU scope and non-goals
- workload and kernel profile
- required execution model features
- validation target and deliverable type
- platform and toolchain constraints
- allowed presets and forbidden presets
- provenance for every inferred or selected field

The intent layer must not define ISA semantics, memory ordering, warp state,
launch ABI, register layout, scheduler behavior, or RTL module interfaces.
Unresolved natural language must not be passed downstream as a source of hidden
architecture facts.

## Candidate Architecture Generation

`ARCH_IR` is a candidate graph, not system truth. The generator may create
multiple candidates, but each candidate must expose:

- selected preset and rejected alternatives
- SM count, warp size, issue width, pipeline class, and scheduler class
- register file, scoreboard, shared memory, cache, global memory, and runtime
  interface shape
- hard-constraint pass/fail evidence
- quality target coverage
- unresolved architecture risks
- downstream contract obligations

Every architecture parameter must have allowed provenance. `MODEL_GUESS`,
`COMMON_GPU_DEFAULT`, `UNKNOWN`, or unowned table rows are invalid provenance.

## Micro-Constraint Estimation

The merged generator must preserve the old synthesizer's hard-constraint
screening while adding v5 feasibility estimates. `MICRO_CONSTRAINT_ESTIMATE_IR`
must include assumptions and bounds for:

- area estimate
- memory pressure estimate
- warp occupancy bound
- register pressure bound
- shared-memory pressure bound
- minimum bandwidth need
- known unrealizable risks

These estimates are pre-contract feasibility evidence only. They must not be
treated as final PPA truth or override later verification evidence.

## Failure Rules

The generator must fail closed for:

- insufficient request information
- unsupported requirement
- missing explicit preset when inference would be required
- hard-constraint failure
- forbidden provenance
- unrealizable micro-constraint
- missing schema, table, example, or regression case
