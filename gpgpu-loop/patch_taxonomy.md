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
`gpgpu-runtime` and must not change
`SYSTEM_CONTRACT_IR` unless the root cause is reclassified as a
`CONTRACT_PATCH`.

`RUNTIME_PATCH` targets runtime argument buffer encoding, kernel launch
sequence, CSR start/done sequencing, completion observation, and fault
observation. It routes to `gpgpu-runtime`.

`PASS_EVIDENCE_PATCH` targets missing pass evidence, unstable fingerprints,
trace coverage gaps, or incomplete evidence collection. It routes to
`gpgpu-simppa` and does not imply design
behavior is wrong.

`GOLDEN_MODEL_PATCH` targets executable semantics or golden coverage derived
from `SYSTEM_CONTRACT_IR`. It routes to
`gpgpu-golden`.
