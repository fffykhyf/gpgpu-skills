# Legacy Binding and Module Constraints

This reference migrates the useful constraints from the removed
`gpgpu-artifact-contract-engine`, the structural memory-path portions of
`gpgpu-memory-subsystem`, the hardware-visible runtime interface portions of
`gpgpu-runtime-validator`, the useful transform behavior from legacy
`gpgpu-deterministic-transform-engine`, `gpgpu-config`,
`gpgpu-memory-path`, and the implementability gates from legacy
`gpgpu-rtl-simt-core` and `gpgpu-implementation-validator`.

## Deterministic Binding

`INCREMENTAL_RTL_MAP` must be derived from `SYSTEM_CONTRACT_IR` and
`GOLDEN_CONTRACT_MODEL` with deterministic transforms. Each RTL module binding
must record:

- consumed contract paths
- provided signals
- required signals
- local state bindings
- latency contract
- handshake protocol
- reset behavior
- local trace schema
- partial simulation gate
- source contract hash and golden-model hash

The binding engine must reject magic constants, undocumented widths,
unprovenanced RTL parameters, and cross-artifact drift.

The old deterministic transform rule is preserved: each consumed enum, state
field, contract path, and config field must map through fixed tables. Unused
fields must be marked explicitly. Repeated runs with the same inputs must be
byte-stable or explain the nondeterminism as a failure.

## Required Module Decomposition

The old global RTL map is replaced by module-by-module assembly. The module
catalog must include the relevant subset of:

- SM core
- warp scheduler
- fetch/decode/execute pipeline
- register file
- scoreboard
- SIMT stack or reconvergence unit
- load/store queue
- coalescer
- shared memory and bank conflict logic
- cache and global memory interface
- interconnect or memory fabric adapter
- CSR and runtime interface
- completion and fault reporting block

No full-system simulation may be treated as valid until each required module
has interface evidence and partial simulation evidence.

## Memory-Path Structural Rules

Memory truth belongs to `SYSTEM_CONTRACT_IR`; structural realization belongs
here. Memory modules must bind:

- address-space selection
- request lifecycle
- duplicate-request prevention
- request replay policy
- coalescing lanes and masks
- byte enables
- load/store queue tags
- shared-memory bank selection
- cache/global request and response protocol
- atomics and fences as contract-bound operations
- fault propagation
- scoreboard wakeup
- stall and backpressure propagation

Every memory signal and tag must be traceable to a contract path or module
interface field. Structural optimizations must not change contract semantics.

## Interface Contract Checker

The checker must validate:

- signal name, width, signedness, and reset consistency
- valid/ready or request/response protocol correctness
- latency compatibility
- pipeline boundary correctness
- stall and backpressure behavior
- tag preservation
- fault and completion propagation
- CSR visibility and runtime handoff

Interface mismatch prevents full-system RTL simulation and routes the failure
to an RTL patch, not to an architectural rewrite.

The RTL SIMT core must not reinterpret architecture, add execution units, change
scheduler behavior for RTL convenience, or silently drop unsupported state
fields. Unsupported fields must appear in the module report.

## Partial Simulation Gate

Each module must produce a local simulation trace and compare it to the
corresponding `GOLDEN_CONTRACT_MODEL` slice. Required evidence includes:

- local input and output transactions
- local scoreboard or state check
- local latency and stall check
- mismatch report with contract path and module path
- first failing cycle when available
