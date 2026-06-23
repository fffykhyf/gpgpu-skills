# Toolchain Runtime Core

## Merged Source Material

### Source: `skill/gpgpu-toolchain-runtime/argument_layout_contract.md`

# Argument Layout Contract

Argument layout must derive from `SYSTEM_CONTRACT_IR.launch_model` and record:

- argument name or ordinal;
- byte offset;
- size;
- alignment;
- signedness or pointer class when relevant;
- constant/global/shared-memory binding.

Runtime artifacts must round-trip this layout through assembler, loader, and
golden image execution.

### Source: `skill/gpgpu-toolchain-runtime/assembler_disassembler_roundtrip.md`

# Assembler/Disassembler Round Trip

## Gate A: Encode

Input: `ASSEMBLY_IR`.

Output: encoded instruction bytes.

Check:

- mnemonic exists in `SYSTEM_CONTRACT_IR.isa_model.opcodes`
- operand count matches `SYSTEM_CONTRACT_IR.isa_model.operand_fields`
- operand width and signedness match contract fields
- immediate value is encodable
- branch offset follows alignment and range rules
- unsupported instruction is rejected or trapped according to `unsupported_instruction_behavior`

Failure: `ASM_ENCODE_FAIL`.

## Gate B: Decode

Input: encoded instruction bytes.

Output: `DISASSEMBLY_IR`.

Check:

- opcode table derives from the same `SYSTEM_CONTRACT_IR`
- decode class is correct
- operand field extraction is correct
- unsupported encoding behavior matches contract

Failure: `DISASM_DECODE_FAIL`.

## Gate C: Round Trip

Path:

```text
ASM -> bytes -> DISASM -> bytes
```

Require byte-equivalent output when formatting is canonical. Allow semantic-equivalent output only when the contract declares aliases or pseudo-instruction expansion rules.

Failure modes:

- `DISASM_ROUNDTRIP_FAIL`
- `UNSUPPORTED_INSTRUCTION_BEHAVIOR_MISMATCH`
- `SOURCE_OF_TRUTH_DRIFT`

### Source: `skill/gpgpu-toolchain-runtime/assembly_ir_rules.md`

# Assembly IR Rules

`ASSEMBLY_IR` is the canonical input to assembler generation. It may come from hand-written assembly or a lowered pseudo-assembly frontend. A full CUDA-like frontend is not required for the first vertical slice.

Required fields:

- `contract_hash`
- `source_kind`: `hand_written_asm` or `lowered_frontend`
- `sections`: `.text`, `.data`, `.rodata`
- `symbols`: name, section, offset, visibility
- `instructions`: pc, mnemonic, operands, predicate or active-mask info, source line, contract path
- `data_objects`: name, address, bytes
- `relocations`: symbol, relocation kind, patch site
- `canonical_hash`

Rules:

- Parse mnemonics only from `SYSTEM_CONTRACT_IR.isa_model.opcodes`.
- Parse registers, immediates, labels, sections, and comments only from `SYSTEM_CONTRACT_IR.isa_model.assembly_syntax`.
- Preserve source line and contract path for every instruction so later trace attribution can point back to assembly.
- Reject unresolved labels before program-image emission.

Failure modes:

- `ASM_PARSE_FAIL`
- `ENTRY_SYMBOL_RESOLVE_FAIL`
- `SOURCE_OF_TRUTH_DRIFT`

### Source: `skill/gpgpu-toolchain-runtime/coalescer_input_trace_generation.md`

# Coalescer Input Trace Generation

Runtime/toolchain output must generate enough memory-bundle information for
coalescer input traces:

- instruction id;
- warp id when known;
- access type;
- memory space;
- lane address expression or vector;
- active mask;
- byte enables;
- ordering scope;
- coalescing policy reference.

This trace is input to memory formation, not a cache or DRAM timing result.

### Source: `skill/gpgpu-toolchain-runtime/compatibility_mapping_rules.md`

# Optional CUDA/OpenCL Compatibility Mapping

CUDA and OpenCL frontends may map into the native launch descriptor, but their
object models must not leak into the base ABI.

Compatibility-only fields include:

- CUDA stream stack and stream policy;
- kernel launch latency;
- compute capability;
- OpenCL object handles;
- PTX capability and memory-space quirks.

Native runtime output remains `PROGRAM_IMAGE_IR`, `RUNTIME_LAUNCH_IR`, and
`LOADER_CONTRACT_IR` derived from `SYSTEM_CONTRACT_IR`.

### Source: `skill/gpgpu-toolchain-runtime/isa_table_derivation.md`

# ISA Table Derivation

Derive all ISA-facing toolchain artifacts from:

- `SYSTEM_CONTRACT_IR.isa_model.opcodes`
- `SYSTEM_CONTRACT_IR.isa_model.instruction_encodings`
- `SYSTEM_CONTRACT_IR.isa_model.operand_fields`
- `SYSTEM_CONTRACT_IR.isa_model.decode_classes`
- `SYSTEM_CONTRACT_IR.isa_model.assembly_syntax`

Derived artifacts include:

- `tools/isa.py`
- `tools/encoding_table.py`
- `tools/assembler.py`
- `tools/disassembler.py`
- `rtl/defines.svh`
- `rtl/decode.svh`
- `docs/isa.md`

Rules:

- Take every opcode, funct field, operand field, width, signedness, immediate layout, branch offset rule, and alignment rule from `SYSTEM_CONTRACT_IR`.
- Control instructions must explicitly record variant bits and overloaded fields in `SYSTEM_CONTRACT_IR.isa_model.control_opcode_model`.
- Pseudo-instruction expansion must preserve `source_line`, `contract_path`, and `expanded_bytes`.
- Reject hand-written opcode constants in assembler, disassembler, RTL defines, or docs.
- Reject docs or RTL as truth sources; `docs/isa.md` is generated output only.
- RTL decode and simulator decode must carry the same `isa_model_hash`.
- Compute `isa_model_hash`, `tools_isa_table_hash`, `assembler_table_hash`, `disassembler_table_hash`, `rtl_decode_hash`, `simulator_decode_hash`, and `docs_isa_hash`.
- Require Gate D: `SYSTEM_CONTRACT_IR.isa_model_hash == assembler_table_hash == disassembler_table_hash == rtl_decode_hash == simulator_decode_hash == docs_isa_hash`.

Failure modes:

- `ISA_TABLE_DERIVATION_FAIL`
- `ISA_ENCODING_DRIFT`
- `SOURCE_OF_TRUTH_DRIFT`
- `DERIVED_OPCODE_TABLE_MISMATCH`
- `INTRINSIC_ENCODING_MISMATCH`
- `SIMULATOR_RTL_DECODE_MISMATCH`
- `INSUFFICIENT_SKILL_ASSET`

### Source: `skill/gpgpu-toolchain-runtime/launch_descriptor_contract.md`

# Launch Descriptor Contract

Launch descriptor fields:

- `kernel_id`
- `entry_pc`
- `grid_dim`
- `block_dim`
- `shared_memory_bytes`
- `argument_layout`
- `program_image`
- `constant_memory`
- `global_memory_init`

Do not include CUDA streams, launch latency, compute capability, or OpenCL
object model in the native ABI unless an optional compatibility profile is
selected.

### Source: `skill/gpgpu-toolchain-runtime/lsu_instruction_bundle.md`

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
- `gpgpu-toolchain-runtime` derives bundle rules from `SYSTEM_CONTRACT_IR`.
- `gpgpu-contract` executes bundle semantics for reference traces.
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
- malformed instruction fields -> `gpgpu-toolchain-runtime`
- ambiguous memory semantics -> `gpgpu-contract`
- missing RTL interface fields -> `gpgpu-rtl`
- trace-only ambiguity -> `gpgpu-validation`

### Source: `skill/gpgpu-toolchain-runtime/memory_coalescing_contract.md`

# Memory Coalescing Contract

This file defines the runtime/toolchain-visible memory coalescing contract for
`multi_sm_memory_path`. It is inspired by MIAOW's explicit LSU/address/memory-space observability,
but upgrades the contract to decode-time memory bundle formation and rule-based
coalescing.

## Coalescing Rules

Coalescing Rules:
1. lanes with contiguous addresses -> merge
2. aligned accesses -> single transaction
3. bank conflict -> split transaction
4. divergence -> per-lane issue fallback

These rules are ordered. The artifact must record which rule split or merged
each memory bundle.

## Bundle Formation

warp memory bundle formation BEFORE issue is required.

Decode and toolchain artifacts must distinguish:
- arithmetic instruction record
- scalar/control instruction record
- memory instruction record
- `MEMORY_BUNDLE`

The LSU must consume a bundle, not re-discover all lane semantics from a raw
instruction word.

## Not Per-Instruction LSQ Only

The contract is not per-instruction LSQ only. A load/store queue may exist, but
it is downstream from decode-time bundle formation and upstream from coalescer
or memory fabric issue.

Required bundle fields:
- `bundle_id`
- `sm_id`
- `warp_id`
- `pc`
- `address_vector`
- `lane_mask`
- `byte_enable_vector`
- `access_type`
- `memory_space`
- `ordering_scope`
- `coalescing_rule_trace`

## Response Shape Restore

Coalescer correctness requires both request reduction and response restoration.
The coalescer must preserve the original lane shape before merging and prove
that every response can be restored to that shape.

```yaml
coalescer_request_record:
  original_bundle_id: string
  original_request_tag: string
  original_lane_mask: string
  original_byte_enable_vector: list
  per_lane_offset: list
  merged_line_addr: string
  coalesced_request_tag: string
  split_reason_or_merge_rule: string

coalescer_response_restore:
  response_tag: string
  original_request_tag: string
  restored_lane_mask: string
  restored_lane_data: list
  restored_byte_enable: list
  final_eop: bool
```

The coalescer must not only prove that it reduced request count; it must prove
that `coalescer_response_restore` reconstructs the original lane-shaped response.

## LDS and Global Memory

The contract must separate:
- `LDS`
- `global`
- `constant`
- `scratch`
- implementation-specific spaces

LDS accesses route to SM-local storage. Global accesses route to L1/L2/DRAM
fabric. A bundle with mixed spaces must split before issue.

## Failure Modes

Coalescing evidence must identify:
- unaligned split
- bank conflict split
- divergence split
- byte-enable mismatch
- lane-mask mismatch
- coalescer response shape mismatch
- coalescer tag restore mismatch
- memory-space mismatch
- unsupported access width

## Human Output Boundary

Human-facing reports should show only concise status:
- coalescer: pass/fail
- merged transaction count
- split transaction count
- top split reason
- affected SM/warp

Full bundle YAML is AI-facing and must be registered in `ARTIFACT_MANIFEST_IR`.

### Source: `skill/gpgpu-toolchain-runtime/program_image_and_loader_contract.md`

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

### Source: `skill/gpgpu-toolchain-runtime/runtime_launch_artifact_rules.md`

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

## XiangShan Runtime Switch Rules

`RUNTIME_SWITCH_IR` may select only pre-elaborated behavior with stable IO
shape. Runtime launch artifacts may carry runtime behavior knobs and debug
trace knobs, but any request to change ISA/ABI, launch descriptor layout, MMIO
map, queue depth, bank count, wire width, module presence, or warp size must be
rejected before launch.

### Source: `skill/gpgpu-toolchain-runtime/toolchain_smoke_gates.md`

# Toolchain Smoke Gates

Run these gates before passing artifacts downstream:

1. ISA table derivation smoke
2. assembler parse smoke
3. assembler encode smoke
4. disassembler decode smoke
5. asm-disasm roundtrip smoke
6. program image layout smoke
7. entry symbol resolve smoke
8. runtime argument encoding smoke
9. loader contract smoke
10. golden program image execution smoke

The golden execution smoke must execute:

```text
PROGRAM_IMAGE_IR -> GOLDEN_CONTRACT_MODEL decode/fetch/execute -> expected memory dump
```

Rules:

- Golden model must not execute only an abstract instruction list for this gate.
- It must fetch bytes from `PROGRAM_IMAGE_IR`, decode with the contract-derived table, and execute.
- Smoke report must keep evidence hashes for each stage and fail closed on missing evidence.

Failure modes:

- `ISA_TABLE_DERIVATION_FAIL`
- `ASM_PARSE_FAIL`
- `ASM_ENCODE_FAIL`
- `DISASM_DECODE_FAIL`
- `DISASM_ROUNDTRIP_FAIL`
- `PROGRAM_IMAGE_LAYOUT_FAIL`
- `ENTRY_SYMBOL_RESOLVE_FAIL`
- `RUNTIME_ARG_ENCODING_FAIL`
- `LOADER_CONTRACT_FAIL`
- `GOLDEN_IMAGE_EXECUTION_FAIL`
