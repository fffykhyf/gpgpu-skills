# Module Binding Rules

This reference defines deterministic module-by-module RTL binding rules for
`gpgpu-rtl`. It carries forward the active rules
migrated from `gpgpu-artifact-contract-engine`, structural memory-path pieces of
`gpgpu-memory-subsystem`, runtime-interface checks, deterministic transform
checks, config checks, and implementability gates.

The Interface Contract Checker consumes these module records and rejects
incomplete load/store queue and memory-path bindings before full-system RTL
simulation.

## Deterministic Binding

`INCREMENTAL_RTL_MAP` must be derived from `SYSTEM_CONTRACT_IR`,
`GOLDEN_CONTRACT_MODEL`, `TOOLCHAIN_ARTIFACT_IR`, `PROGRAM_IMAGE_IR`,
`RUNTIME_LAUNCH_IR`, and `LOADER_CONTRACT_IR` with deterministic transforms.
Each module binding must record:

- `module_id`
- `template_id`
- `module_kind`
- consumed contract paths
- required local state
- input and output interface IDs
- local state bindings
- latency contract
- reset behavior
- local trace schema
- partial simulation cases
- timing and synthesis feedback
- source contract hash and golden-model hash
- toolchain artifact hash when the module consumes program image, runtime launch,
  or loader state

Reject magic constants, undocumented widths, unprovenanced RTL parameters,
hidden state, and cross-artifact drift. Each consumed enum, state field,
contract path, config field, and interface field must map through fixed tables.
Unused fields must be marked explicitly. Repeated runs with the same inputs must
be byte-stable or fail as nondeterministic.

## Module Binding Template

Every module record must reference a `MODULE_BINDING_TEMPLATE` from
`shared/tables/rtl_module_catalog.yaml`. A template defines:

- required contract paths
- required local state
- required input interfaces
- required output interfaces
- required partial simulation cases
- required trace fields
- forbidden hidden state
- timing checks

Required templates:

- `wavefront_scheduler_template`
- `scoreboard_template`
- `register_file_template`
- `lsq_template`
- `coalescer_template`
- `lds_bank_unit_template`
- `l1_cache_or_global_adapter_template`
- `memory_response_router_template`
- `fault_completion_unit_template`
- `csr_runtime_template`
- `program_image_loader_template`
- `instruction_memory_init_template`
- `runtime_arg_buffer_template`

## Required Module Decomposition

The old global RTL map is replaced by module-by-module assembly. The catalog
must include the relevant subset of:

- `cu_top`
- `wavefront_scheduler`
- `decode_issue_unit`
- `register_file`
- `scoreboard`
- `simt_stack`
- `load_store_queue`
- `coalescer`
- `lds_bank_unit`
- `l1_cache_or_global_adapter`
- `memory_response_router`
- `fault_completion_unit`
- `interconnect`
- `csr_runtime_interface`
- `program_image_loader_interface`
- `instruction_memory_init`
- `runtime_arg_buffer_interface`

No full-system simulation may be treated as valid until each required module
has interface evidence, partial simulation evidence, and timing feedback.

## Memory Path Structural Rules

Memory truth belongs to `SYSTEM_CONTRACT_IR`; structural realization belongs
here. Memory modules must bind:

- address-space selection
- request lifecycle
- duplicate-request prevention
- request replay policy
- coalescing lanes and masks
- byte enables
- load/store queue tags
- LDS bank selection and bank conflict stalls
- cache/global request and response protocol
- atomics and fences as contract-bound operations or reject/trap paths
- fault propagation
- completion reporting
- scoreboard wakeup
- stall and backpressure propagation

Every memory signal and tag must be traceable to a contract path or module
interface field. Structural optimizations must not change contract semantics.

## Toolchain Runtime Binding Rules

Program-image and launch artifacts are owned by
`gpgpu-runtime`; RTL binding consumes them but does not
redefine their format.

RTL bindings must prove:

- instruction memory initialization consumes `PROGRAM_IMAGE_IR.segments[text]`
- data memory initialization consumes `PROGRAM_IMAGE_IR.segments[data]`
- entry PC comes from `LOADER_CONTRACT_IR.entry_pc_rule`
- first instruction decode uses contract-derived encoding tables
- runtime CSR writes match `RUNTIME_LAUNCH_IR.csr_write_sequence`
- argument buffer visibility matches `RUNTIME_LAUNCH_IR.arg_buffer_bytes`
- loader reset behavior matches `LOADER_CONTRACT_IR.reset_rule`

## Timing And Synthesis Feedback

Each module binding must include timing feedback hooks:

- `local_timing_risk`
- `critical_signal_paths`
- `estimated_register_count`
- `estimated_sram_macro_need`
- `fanout_risk`
- `combinational_ready_loop_check`

`combinational_ready_loop_check.no_combinational_ready_loop` must be true before
full-system assembly. A valid/ready network that forms a combinational ready
loop must fail interface checking instead of being deferred to synthesis.

## Fail Closed Rules

- Reject modules without consumed contract paths.
- Reject modules without a known binding template.
- Reject provided signals that no downstream interface consumes unless marked
  debug-only.
- Reject local state bindings that do not map to `SYSTEM_CONTRACT_IR`.
- Reject hidden state not declared in the selected template.
- Reject missing timing feedback or any combinational ready loop.
