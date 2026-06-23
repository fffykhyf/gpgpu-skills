# Contract Truth and State Model

This reference defines the mandatory truth ownership and canonical state rules
for `gpgpu-golden`. It carries forward the still-active
constraints migrated from `gpgpu-spec-lock`, `gpgpu-canonical-state-engine`,
truth-bearing artifact checks, launch truth, memory truth, config truth, and
golden replay truth.

## Single Truth Ownership

`SYSTEM_CONTRACT_IR` is the only semantic truth source. It owns:

- `isa_model`: opcode, instruction encoding, decode class, operand, and trap
  truth
- `architecture_model`: architecture parameters selected by `ARCH_IR`
- `execution_model`: scheduler, SIMT, scoreboard, and pipeline semantic truth
- `state_model`: canonical state visible to executable semantics and trace diff
- `memory_model`: address-space, ordering, fence, atomic, request lifecycle, and
  fault truth
- `launch_model`: launch ABI, grid/block/thread mapping, queue, doorbell,
  completion, and fault observation truth
- `interface_semantics_model`: system-level request/response lifecycle truth
- `config_contract`: config ownership, visibility, consumers, and defaults
- `source_of_truth_map`: every generated artifact's contract source path

Generated artifacts, runtime stubs, RTL maps, simulators, validators, markdown
docs, and examples are derived artifacts. They must reference contract paths and
contract hashes; they must not become independent truth owners.

## Vortex-Derived Source-of-Truth Rule

`SYSTEM_CONTRACT_IR` is the only allowed source for ISA, launch ABI, state, and
trace semantics. These artifacts are derived views only:

- assembler opcode table
- disassembler table
- RTL decode table
- simulator decode table
- intrinsic header
- startup assembly
- ISA documentation

Every derived view must carry the same `isa_model_hash` and cite the exact
`SYSTEM_CONTRACT_IR.isa_model` paths for opcode, field layout, variant bits,
overloaded fields, and pseudo-instruction expansion. Docs may explain the ISA,
but docs must never become the ISA source.

## Contract Freeze Algorithm

1. Import `ARCH_IR` and `DESIGN_INTENT_IR`.
2. Enumerate all semantic fields required by the selected architecture preset.
3. Assign each field one truth owner.
4. Validate enum values and provenance.
5. Reject hidden defaults and duplicate owners.
6. Build the canonical `state_model`.
7. Build `source_of_truth_map`.
8. Emit `SYSTEM_CONTRACT_IR` with canonical hash.
9. Derive `GOLDEN_CONTRACT_MODEL`.
10. Run coverage and forbidden-truth checks.

## Spec Lock Requirements

The contract freeze must reject hidden defaults and duplicate owners. Every
semantic field must carry:

- owner module
- source evidence
- allowed enum value
- provenance
- generated-artifact consumers
- validation gates

Unknown enum values, magic constants, undocumented CSR fields, implicit memory
ordering, implicit ABI layout, implicit ISA encoding, or implicit launch
behavior must fail closed.

Vortex-derived failure modes:

- `SOURCE_OF_TRUTH_DRIFT`
- `DERIVED_OPCODE_TABLE_MISMATCH`
- `DOC_IMPL_SEMANTIC_CONFLICT`
- `INTRINSIC_ENCODING_MISMATCH`
- `SIMULATOR_RTL_DECODE_MISMATCH`

## Canonical State Model

`SYSTEM_CONTRACT_IR.state_model` must be structured. It must include:

- `pc_table`
- `exec_mask_table`
- `warp_state`
- `scheduler_state`
- `register_file_state`
- `scoreboard_state`
- `simt_stack_state`
- `pipeline_visible_state`
- `memory_stall_state`
- `csr_state`
- `launch_state`
- `completion_fault_state`

State transition rules must define reset, fetch/decode/issue/commit,
divergence, reconvergence, memory stall, wakeup, completion, and fault
transitions as applicable to enabled features. Every transition used by
`GOLDEN_CONTRACT_MODEL` must map to a contract path.

## Interface Semantics Model

`SYSTEM_CONTRACT_IR.interface_semantics_model` defines system-level interface
lifecycle semantics, not RTL-level wires. It must cover:

- whether an accepted request must eventually receive a response
- whether payload must remain stable when `ready = 0`
- whether a tag must remain unique until response
- whether responses with the same tag preserve ordering
- whether a fault response can retire, trap, or poison the instruction

RTL binding may choose signal names later, but it must not invent these
lifecycle semantics.

## Config Class Semantics

Config fields must be classified as `hw_sw_abi`, `hardware_private`,
`simulator_private`, `test_only`, or `debug_only`.

- `hw_sw_abi` fields must appear in launch/runtime contract paths.
- `hardware_private` fields must not be runtime-controlled.
- `simulator_private` fields must not alter RTL trace semantics.
- `test_only` and `debug_only` fields must not alter canonical execution
  semantics.
- Missing config defaults must not be generated.

## Artifact Truth Hygiene

Artifact generation does not define truth. It only proves that the frozen
contract can be consumed deterministically:

- deterministic serialization is required for contract-derived artifacts
- generated files must carry the source contract hash
- config fields must have one owner and declared consumers
- cross-artifact consistency is checked against `SYSTEM_CONTRACT_IR`
- declared tests must map to contract paths

Golden traces must replay deterministically from `GOLDEN_CONTRACT_MODEL`, cite
contract hashes, cover mandatory semantic fields, and locate first divergence by
field and rule path. They must not redefine ISA, warp model, state transitions,
or memory behavior.

## XiangShan Executable Reference Model

Use `XIANGSHAN_GOLDEN_EXECUTABLE_REF` as a development-closure pattern only.
`GOLDEN_REF_API` must define two separated modes:

- live diff mode: `gpgpu_ref_init`, `gpgpu_ref_memcpy`,
  `gpgpu_ref_statecpy`, `gpgpu_ref_step_event`, `gpgpu_ref_query_event`, and
  `gpgpu_ref_status`
- offline analysis mode: standalone run, profiling run, checkpoint generation,
  checkpoint restore, and host-side performance attribution

`ARCHITECTURE_STATE_BLOB` is the only diff-visible state container. It includes
per-warp PC, active mask, reconvergence state, architectural registers, lane
predicates, committed memory-visible store sequence, launch/grid/CTA state, and
trap/fault state.

`GOLDEN_SIDECAR_STATE` may hold scoreboard, outstanding memory, barrier phase,
atomic pending, fault injection, and debug query state. Sidecar state is allowed
to synchronize or localize evidence, but it must not become ISA-visible truth.
