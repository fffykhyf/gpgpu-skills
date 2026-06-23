# Capability Profile and Preset Contract

`gpgpu-arch` selects a `capability_profile` before emitting `ARCH_IR`.
Profiles name GPU capability domains, not development stages. Numeric stage
names are not valid profile names because they conflict with hardware cache
terms such as L1 cache and L2 cache.

## Capability Profile

```yaml
capability_profile:
  name: minimal_simt_core |
        single_sm_warp_pipeline |
        toolchain_runtime_vertical_slice |
        multi_sm_memory_path |
        full_memory_sync_system

  enabled_subsystems:
    - simt_core
    - warp_scheduler
    - scoreboard
    - divergence_unit
    - lsu
    - shared_memory
    - coalescer
    - l1_cache_or_global_adapter
    - interconnect_fabric
    - l2_cache_slice
    - dram_controller
    - atomic_unit
    - fence_unit
    - barrier_unit
```

## Presets

```yaml
MINIMAL_SIMT_CORE:
  capability_profile: minimal_simt_core
  sm_count: 1
  warp_count: 1
  memory_path: simple_global_memory
  runtime_required: false

SINGLE_SM_WARP_PIPELINE:
  capability_profile: single_sm_warp_pipeline
  sm_count: 1
  warp_count: multiple
  scoreboard: required
  divergence: required
  lsu: required

TOOLCHAIN_RUNTIME_VERTICAL_SLICE:
  capability_profile: toolchain_runtime_vertical_slice
  assembler: required
  disassembler: required
  program_image: required
  loader: required
  runtime_launch: required
  rtl_smoke: required
  golden_dump: required

MULTI_SM_MEMORY_PATH:
  capability_profile: multi_sm_memory_path
  sm_count: multiple
  shared_memory: required
  coalescer: required
  l1_cache_or_global_adapter: required
  response_restore: required
  sm_id_routing: required

FULL_MEMORY_SYNC_SYSTEM:
  capability_profile: full_memory_sync_system
  fabric: required
  l2_cache_slice: required
  mshr: required
  dram_controller: required
  atomic_unit: required
  fence_unit: required
  barrier_unit: required
  memory_visibility_model: required
```

## Ownership Rules

- `gpgpu-arch` chooses the profile and emits candidate architecture nodes.
- `gpgpu-interconnect`, `gpgpu-memory`, and `gpgpu-atomic-sync` emit
  `contract_fragment_ir` for enabled subsystems before golden freeze.
- `gpgpu-golden` freezes fragments into `SYSTEM_CONTRACT_IR`.
- Cache terms remain hardware terms only: write `L1 cache`, `L2 cache`, or
  `L2 cache slice` only when describing real cache hierarchy.

## Required Acceptance

A generated `ARCH_IR` is accepted only if:

- it contains `capability_profile`;
- enabled subsystems match the selected profile;
- graph nodes name the owner skill for every fragment-producing subsystem;
- unsupported subsystems are explicit non-goals;
- the selected preset is recorded with provenance and rejected alternatives.

## XiangShan Runtime DSE Boundary

`XIANGSHAN_SAFE_RUNTIME_DSE` adds a required parameter classification before
DSE. Every parameter must produce `KNOB_CLASSIFICATION`:

- `structural_compile_time`: module count, wire width, queue depth, bank count,
  data width, warp size, register-file geometry
- `abi_visible`: ISA encoding, launch descriptor layout, MMIO register map,
  memory consistency scope
- `runtime_behavior_knob`: scheduler policy select, coalescer policy select,
  prefetch enable, replay threshold, throttle threshold
- `debug_trace_knob`: memory trace, scoreboard trace, barrier trace, full
  transaction diff, counter selection

Only runtime behavior and debug trace knobs may become `RUNTIME_DSE_KNOB`.
