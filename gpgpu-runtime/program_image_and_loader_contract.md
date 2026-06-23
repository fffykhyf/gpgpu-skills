# Program Image and Loader Contract

`PROGRAM_IMAGE_IR` defines how assembled bytes become an executable memory image.

Required `PROGRAM_IMAGE_IR` fields:

- `contract_hash`
- `image_format_version`
- `entry_symbol`
- `entry_pc`
- `segments`
- `symbol_table`
- `relocation_table`
- `initial_memory_objects`
- `metadata`
- `canonical_hash`

Minimal segment rules:

- `text`: base address, size, bytes, permissions `rx`
- `data`: base address, size, bytes, permissions `rw`
- `rodata`: optional base address, size, bytes, permissions `r`

`LOADER_CONTRACT_IR` defines how the image enters RTL-visible memories.

Required fields:

- `imem_init_path`
- `dmem_init_path`
- `entry_pc_source`
- `symbol_resolution_rule`
- `alignment_rule`
- `endian_rule`
- `reset_visibility`
- `rtl_loader_interface`
- `memory_initialization_hash`

Rules:

- Resolve `entry_pc` from `entry_symbol` using `SYSTEM_CONTRACT_IR.launch_model.program_image_format.entry_symbol_rule`.
- Load instruction memory from `PROGRAM_IMAGE_IR.segments[text]`.
- Load data memory from `PROGRAM_IMAGE_IR.segments[data]` and `initial_memory_objects`.
- Require loader reset visibility for entry PC, instruction memory, data memory, and runtime argument buffer.
- Reject image layouts that cannot prove byte layout equivalence.

Failure modes:

- `PROGRAM_IMAGE_LAYOUT_FAIL`
- `ENTRY_SYMBOL_RESOLVE_FAIL`
- `LOADER_CONTRACT_FAIL`
