# Legacy Spec and State Truth Constraints

This reference migrates the useful constraints from the removed
`gpgpu-spec-lock`, `gpgpu-canonical-state-engine`, the truth-bearing parts of
`gpgpu-artifact-contract-engine`, the launch-truth parts of
`gpgpu-runtime-validator`, and the memory-truth parts of
`gpgpu-memory-subsystem`, plus the truth ownership portions of legacy
`gpgpu-config` and `gpgpu-golden-sim`. These rules are now owned only by
`gpgpu-system-contract-golden-engine`.

## Single Truth Ownership

`SYSTEM_CONTRACT_IR` is the only semantic truth source. It owns:

- ISA and instruction encoding truth
- execution model truth
- warp, thread, PC, active mask, and divergence state truth
- scheduler-visible state truth
- register, scoreboard, CSR, and pipeline-visible state truth
- memory hierarchy, address space, ordering, fence, atomic, and fault truth
- launch ABI, grid/block/thread mapping, queue, doorbell, completion, and fault
  observation truth
- config, debug, and test visibility truth

Generated artifacts, runtime stubs, RTL maps, simulators, validators, markdown
docs, and examples are derived artifacts. They must reference contract paths and
contract hashes; they must not become independent truth owners.

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
ordering, implicit ABI layout, or implicit launch behavior must fail closed.

## Canonical State Requirements

The canonical state model must include the state needed for executable
semantics and trace comparison:

- `pc_table`
- `exec_mask_table`
- warp state
- scheduler cursor
- register file state
- scoreboard state
- SIMT stack or reconvergence state
- pipeline registers visible to semantics
- memory stall state
- CSR and runtime-visible launch state
- completion and fault state

State transition rules must define reset, fetch/decode/issue/commit,
divergence, reconvergence, memory stall, wakeup, completion, and fault
transitions. Every transition used by `GOLDEN_CONTRACT_MODEL` must map to a
contract path.

## Executable Golden Model Boundary

`GOLDEN_CONTRACT_MODEL` is an executable reference for the contract, not a
second simulator with its own policy. It may contain functions for:

- warp scheduling rule
- active-mask update rule
- divergence and reconvergence rule
- scoreboard dependency rule
- address-space resolution
- coalescing reference behavior
- byte-enable derivation
- ordering, fence, and atomic behavior
- launch ABI decode
- grid/block/thread mapping
- CSR-visible launch and completion behavior

Each function must reference the exact `SYSTEM_CONTRACT_IR` path it executes.
Any contract path without executable coverage must produce
`CONTRACT_PATH_UNMAPPED` or `GOLDEN_MODEL_COVERAGE_FAIL`.

## Artifact Contract Migration

The useful artifact-contract behavior is retained as truth hygiene:

- deterministic serialization is required for contract-derived artifacts
- generated files must carry the source contract hash
- config fields must have one owner and declared consumers
- cross-artifact consistency is checked against `SYSTEM_CONTRACT_IR`
- declared tests must map to contract paths

Artifact generation does not define truth. It only proves that the frozen
contract can be consumed deterministically.

## Config Class Semantics

The legacy config validator is migrated into the contract and golden semantics
boundary. Config fields must be classified as `hw_sw_abi`,
`hardware_private`, `simulator_private`, `test_only`, or `debug_only`.

- `hw_sw_abi` fields must appear in launch/runtime contract paths.
- `hardware_private` fields must not be runtime-controlled.
- `simulator_private` fields must not alter RTL trace semantics.
- `test_only` and `debug_only` fields must not alter canonical execution
  semantics.
- Missing config defaults must not be generated.

## Golden Trace Replay Boundary

The useful part of legacy `gpgpu-golden-sim` becomes golden contract evidence.
Golden traces must replay deterministically from `GOLDEN_CONTRACT_MODEL`, cite
contract hashes, cover mandatory semantic fields, and locate first divergence by
field and rule path. They must not redefine ISA, warp model, state transitions,
or memory behavior.
