# ARCH_IR v1

## Role

`ARCH_IR` describes a candidate GPGPU architecture produced by `gpgpu-architecture-synthesizer`.

It is not the final truth source. It must be converted into a synthesized spec draft, locked by `gpgpu-spec-lock`, and then converted into `GPU_STATE_IR`.

## Schema

```text
ARCH_IR = {
  schema_version,
  design_identity,
  objective,
  non_goals,
  compute_topology,
  execution_units,
  memory_hierarchy,
  ISA_profile,
  ABI_launch_contract,
  config_contract,
  quality_model,
  provenance
}
```

## Core Sections

### `compute_topology`

```text
{
  sm_count,
  warp_size,
  max_warps_per_sm,
  lanes_per_warp,
  issue_width,
  scheduler_count,
  scoreboard_policy
}
```

### `execution_units`

```text
{
  int_units,
  fp_units,
  tensor_units,
  sfu_units,
  lsu_units,
  latency_table,
  port_table
}
```

### `memory_hierarchy`

```text
{
  register_file,
  shared_memory,
  l1_cache,
  l2_cache,
  global_memory_interface,
  coalescing_policy,
  bank_conflict_policy,
  atomic_policy,
  fence_policy
}
```

### `ISA_profile`

```text
{
  instruction_classes,
  operand_types,
  predicate_support,
  barrier_support,
  csr_support,
  illegal_instruction_behavior
}
```

### `ABI_launch_contract`

```text
{
  kernel_image,
  entry_pc,
  argument_layout,
  grid_dim,
  block_dim,
  command_queue,
  start_done_protocol,
  fault_protocol
}
```

### `config_contract`

```text
{
  hardware_private,
  simulator_private,
  hw_sw_abi,
  test_only,
  debug_only
}
```

### `quality_model`

```text
{
  area_budget,
  frequency_target,
  throughput_target,
  memory_bandwidth_target,
  energy_target,
  prototype_credibility_target
}
```

## Required Provenance

Every generated field must cite one of:

```text
USER_CONSTRAINT
DESIGN_PRESET
SOLVER_DERIVED
REPAIR_DERIVED
```

Forbidden provenance:

```text
UNKNOWN
COMMON_GPU_DEFAULT
MODEL_GUESS
```

## Verification Rules

- `warp_size == active_mask_width` must be derivable.
- ISA operation classes must have execution-unit owners.
- ABI-visible constants must appear in `config_contract.hw_sw_abi`.
- Quality estimates must remain candidate metadata and must not enter `GPU_STATE_IR`.
- Hard constraint failure produces a rejected candidate, not an acceptable architecture.

