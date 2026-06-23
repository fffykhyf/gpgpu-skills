# Launch Semantics

Launch semantics define executable reference behavior for host-visible kernel launch and completion.

## Required Functions

| Semantics function | Purpose |
|---|---|
| `abi_decode` | Decode launch arguments from the ABI layout. |
| `grid_block_thread_map` | Map grid and block dimensions to logical threads and warps. |
| `kernel_entry_resolve` | Resolve the program image entry point. |
| `completion_or_fault_observe` | Produce observable completion or fault state. |

## Required Evidence

Each function must include:

- ABI contract path
- input fields
- output fields
- deterministic rule id
- fault behavior

## Fail Closed Rules

- Reject ABI fields not present in `SYSTEM_CONTRACT_IR.launch_model`.
- Reject grid/block dimensions that cannot map to declared execution resources.
- Reject completion behavior that cannot be observed by runtime-visible state.
