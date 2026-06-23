# LSU Instruction Bundle

This file defines the `MEMORY_BUNDLE` artifact emitted before LSU issue.

## Decode Contract

decode stage emits MEMORY_BUNDLE, not only a scalar instruction record.

The bundle is produced after:
- instruction format decode
- operand/base selection
- EXEC mask read or dependency declaration
- address mode decode
- memory-space classification
- access width and byte-enable derivation

## Required Fields

`MEMORY_BUNDLE` contains:
- `bundle_id`
- `producer_stage`
- `sm_id`
- `warp_id`
- `pc`
- `opcode`
- address vector
- lane mask
- access type
- `byte_enable_vector`
- `memory_space`
- `lds_base_ref`
- `sgpr_source_refs`
- `vgpr_source_refs`
- `destination_ref`
- `ordering_scope`
- `atomic_flag`
- `fence_flag`
- `expected_response_count`
- `coalescing_policy_ref`

## Access Type

Allowed `access type` values:
- `LOAD`
- `STORE`
- `ATOMIC`
- `FENCE`
- `PREFETCH`
- `INVALID_OR_TRAP`

## Owner and Consumer

Producer:
- `gpgpu-runtime` derives bundle rules from `SYSTEM_CONTRACT_IR`.
- `gpgpu-golden` executes bundle semantics for reference traces.
- `gpgpu-rtl` binds bundle fields to LSU and coalescer interfaces.

Consumer:
- LSU front-end
- coalescer
- LDS bank unit
- L1/global adapter
- trace adapter
- performance attribution

## Validation Gates

Required checks:
- address vector width equals warp lane count
- lane mask is derived from EXEC plus predicate constraints
- access type matches instruction class
- memory space is explicit
- LDS base is present for LDS/DS operations
- atomics and fences are routed to `full_memory_sync_system` contracts when enabled

## Patch Routing

Bundle failures route as follows:
- malformed instruction fields -> `gpgpu-runtime`
- ambiguous memory semantics -> `gpgpu-golden`
- missing RTL interface fields -> `gpgpu-rtl`
- trace-only ambiguity -> `gpgpu-simppa`
