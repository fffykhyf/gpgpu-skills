# Runtime Launch Artifact Rules

`RUNTIME_LAUNCH_IR` is the concrete launch artifact consumed by RTL binding and simulation.

Required structure:

```yaml
runtime_launch_ir:
  public_launch_abi:
    kernel_name: string
    args_host: string
    args_size: integer
    ndim: integer
    grid_dim: [x, y, z]
    block_dim: [x, y, z]
    local_memory_size: integer
    cluster_dim_or_workgroup_cluster: optional map
  program_image_entry:
    image_format: string
    symbol_table: map
    entry_symbol: string
    entry_pc: integer
    fallback_symbol: string
  arg_staging:
    host_pointer: string
    device_scratch_addr: string
    arg_buffer_bytes: bytes
    alignment: integer
  control_plane_sequence:
    queue_record_optional: optional map
    mmio_writes_optional: optional list
    dcr_writes_optional: optional list
    csr_writes: list
    start_command: map
  device_dispatch_view:
    startup_pc: integer
    kernel_entry_pc: integer
    arg_pointer: string
    grid_dim: map
    block_dim: map
    derived_cluster_fields: map
  completion_fault_observation:
    done_bit_or_seqnum: string
    event_completion: string
    fault_code: string
    timeout_policy: string
  backend_capability: map
  launch_trace_chain: list
```

Rules:

- Derive `public_launch_abi` from `SYSTEM_CONTRACT_IR.launch_model.abi`.
- Derive grid/block/thread mapping from `SYSTEM_CONTRACT_IR.launch_model.grid_block_thread_mapping`.
- Derive `program_image_entry.entry_pc` from `PROGRAM_IMAGE_IR.entry_pc`.
- Encode scalar and pointer arguments from `SYSTEM_CONTRACT_IR.launch_model.argument_buffer_layout`.
- Emit queue, MMIO, DCR, or CSR writes for kernel entry, argument base, grid dim, block dim, derived cluster fields, and start.
- Observe completion through done bit, seqnum, event completion, fault code, and timeout fields declared by `SYSTEM_CONTRACT_IR.launch_model.completion_fault_observation`.
- Any public ABI field that cannot trace through `launch_trace_chain` to `device_dispatch_view` or explicit unsupported behavior must fail closed.

Failure modes:

- `RUNTIME_ARG_ENCODING_FAIL`
- `ENTRY_SYMBOL_RESOLVE_FAIL`
- `SOURCE_OF_TRUTH_DRIFT`
- `UNWIRED_LAUNCH_ABI_FIELD`
- `LAUNCH_FIELD_TRACE_BREAK`
- `COMPLETION_FAULT_UNOBSERVABLE`
- `BACKEND_CAPABILITY_MISMATCH`
- `RUNTIME_PRIVATE_STATE_LEAKED_AS_ABI`
