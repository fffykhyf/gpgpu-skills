# Runtime Launch Artifact Rules

`RUNTIME_LAUNCH_IR` is the concrete launch artifact consumed by RTL binding and simulation.

Required fields:

- `contract_hash`
- `launch_abi`
- `entry_symbol`
- `entry_pc`
- `grid_dim`
- `block_dim`
- `wavefront_size`
- `arg_buffer_layout`
- `arg_buffer_bytes`
- `csr_write_sequence`
- `completion_observation`
- `canonical_hash`

Rules:

- Derive `launch_abi` from `SYSTEM_CONTRACT_IR.launch_model.abi`.
- Derive grid/block/thread mapping from `SYSTEM_CONTRACT_IR.launch_model.grid_block_thread_mapping`.
- Derive `entry_pc` from `PROGRAM_IMAGE_IR.entry_pc`.
- Encode scalar and pointer arguments from `SYSTEM_CONTRACT_IR.launch_model.argument_buffer_layout`.
- Emit CSR writes for kernel entry, argument base, grid dim, block dim, and start.
- Observe completion through done bit, fault bit, and status fields declared by `SYSTEM_CONTRACT_IR.launch_model.completion_fault_observation`.

Failure modes:

- `RUNTIME_ARG_ENCODING_FAIL`
- `ENTRY_SYMBOL_RESOLVE_FAIL`
- `SOURCE_OF_TRUTH_DRIFT`
