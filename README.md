# Compact GPGPU Skill System

## Active Skills
1. gpgpu-architecture
2. gpgpu-contract
3. gpgpu-toolchain-runtime
4. gpgpu-rtl
5. gpgpu-validation
6. gpgpu-loop

## Optional Contract Packs
- memory_path
- interconnect
- atomic_sync

## Default Artifact Policy
Default iteration emits only:
- ITERATION_SUMMARY.zh.md
- RUN_STATE.yaml

Expanded artifacts are generated only for:
- CONTRACT_FREEZE
- DEBUG_REGRESSION
- PERF_ANALYSIS
- RELEASE_CHECK

## Source of Truth
SYSTEM_CONTRACT_IR is the semantic truth.
GOLDEN_CONTRACT_MODEL is derived only from SYSTEM_CONTRACT_IR.
RTL must bind to contract paths and negotiated interfaces.
Runtime/toolchain must derive from SYSTEM_CONTRACT_IR.
Validation compares golden/toolchain/RTL evidence.
Rewrite loop only routes patches; it does not invent semantics.
All generated IR and derived artifacts must obey
`shared/references/canonical_generation_rules.md` before hash calculation,
comparison, validation, or rewrite routing.
