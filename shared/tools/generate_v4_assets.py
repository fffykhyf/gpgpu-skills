#!/usr/bin/env python3
"""Generate the GPGPU skill v4 compiler-flow assets."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def bullets(items):
    return "\n".join("- " + item for item in items)


SKILLS = {
    "gpgpu-front-end": {
        "title": "GPGPU Front End",
        "description": "Use when a user request, optional spec, optional trace, patch request, or runnable vertical-slice prototype request must be routed into the GPGPU compiler flow and design intent must be locked without architecture inference.",
        "role": "This skill is the entry compiler pass. It classifies the request and, for DESIGN mode, locks design intent into a bounded IR before any architecture synthesis occurs. Requests for a runnable CUDA-like kernel to RTL simulation proof are classified as VERTICAL_SLICE_PROTOTYPE intent.",
        "upstream": ["User Request", "optional_spec", "optional_trace", "optional_patch_request"],
        "downstream": ["gpgpu-architecture-synthesizer for DESIGN", "gpgpu-spec-lock for REPRODUCE", "gpgpu-closure-refinement-engine for TRACE_DEBUG or PATCH_REQUEST"],
        "inputs": ["user_request", "optional_spec", "optional_trace", "optional_patch_request"],
        "outputs": ["MODE_SELECTION_IR", "DESIGN_INTENT_IR when mode is DESIGN", "FRONT_END_REPORT"],
        "owned": ["Mode classification: REPRODUCE, DESIGN, PATCH_REQUEST, TRACE_DEBUG", "Prototype intent classification: VERTICAL_SLICE_PROTOTYPE", "Design intent fields: objective, non-goals, workload, platform, constraints, verification target", "Routing evidence and rejected routes"],
        "forbidden": ["Choose warp size, SM count, cache policy, scheduler policy, ISA encoding, memory hierarchy, register file size, or RTL pipeline", "Emit SPEC_IR, ARCH_CANDIDATE_IR, or GPU_STATE_IR", "Treat vague goals as complete specs"],
        "tables": ["shared/tables/mode_decision_table.yaml", "shared/tables/enum_table.yaml", "shared/tables/end_to_end_smoke_test_table.yaml"],
        "schemas": ["shared/schemas/mode_selection_ir.schema.yaml", "shared/schemas/design_intent_ir.schema.yaml"],
        "invariants": ["Every routed request has exactly one mode", "DESIGN_INTENT_IR contains no architecture parameters", "PATCH_REQUEST and TRACE_DEBUG preserve evidence anchors", "VERTICAL_SLICE_PROTOTYPE requests set prototype_credibility_target to compile_kernel_to_program_image, rtl_sim_smoke_test, and memory_dump_golden_check"],
        "failures": ["INSUFFICIENT_REQUEST", "FORBIDDEN_ARCHITECTURE_FIELD", "AMBIGUOUS_MODE", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "selected_mode", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["mode_selection.md", "design_intent_lock.md", "shared/schemas/mode_selection_ir.schema.yaml", "shared/schemas/design_intent_ir.schema.yaml", "shared/tables/mode_decision_table.yaml", "shared/tables/end_to_end_smoke_test_table.yaml", "shared/examples/vibe_minimal_vertical_slice/input_request.md", "shared/tests/front_end/cases.yaml"],
        "subpasses": {
            "mode_selection.md": ("Mode Selection", "Classify the request using shared/tables/mode_decision_table.yaml. A complete spec routes to REPRODUCE, a vague design goal routes to DESIGN, a runnable end-to-end prototype request routes to DESIGN with prototype_kind VERTICAL_SLICE_PROTOTYPE, an edit against locked IR routes to PATCH_REQUEST, and trace or divergence evidence routes to TRACE_DEBUG."),
            "design_intent_lock.md": ("Design Intent Lock", "For DESIGN mode, normalize the user's goals into DESIGN_INTENT_IR. Required fields are objective, non_goals, workload_profile, target_platform, hard_constraints, soft_constraints, required_features, optional_features, validation_target, prototype_kind, and prototype_credibility_target. For VERTICAL_SLICE_PROTOTYPE, require compile_kernel_to_program_image, rtl_sim_smoke_test, and memory_dump_golden_check."),
        },
    },
    "gpgpu-architecture-synthesizer": {
        "title": "GPGPU Architecture Synthesizer",
        "description": "Use when DESIGN_INTENT_IR must be converted into a bounded architecture candidate using preset tables, hard constraints, scoring rules, provenance, or a minimal vertical-slice GPGPU preset.",
        "role": "This skill creates architecture candidates only. It never creates final spec truth and must route every candidate through gpgpu-spec-lock. It owns the MINIMAL_VERTICAL_SLICE_GPGPU preset for end-to-end prototype credibility.",
        "upstream": ["gpgpu-front-end DESIGN_INTENT_IR"],
        "downstream": ["gpgpu-spec-lock consumes SYNTHESIZED_SPEC_DRAFT"],
        "inputs": ["DESIGN_INTENT_IR", "architecture_preset_library", "hard_constraint_table", "quality_target_table", "requirement_owner_table"],
        "outputs": ["ARCH_CANDIDATE_IR", "SYNTHESIZED_SPEC_DRAFT", "ARCH_SYNTHESIS_REPORT"],
        "owned": ["Requirement coverage", "Preset selection", "Parameter allocation", "Hard constraint checking", "Candidate scoring"],
        "forbidden": ["Emit SPEC_IR or GPU_STATE_IR", "Bypass gpgpu-spec-lock", "Invent topology outside shared/tables/architecture_preset_library.yaml or shared/tables/minimal_vertical_slice_preset.yaml", "Use COMMON_GPU_DEFAULT, MODEL_GUESS, UNKNOWN, or IMPLICIT_DEFAULT provenance"],
        "tables": ["shared/tables/architecture_preset_library.yaml", "shared/tables/minimal_vertical_slice_preset.yaml", "shared/tables/hard_constraint_table.yaml", "shared/tables/quality_target_table.yaml", "shared/tables/requirement_owner_table.yaml", "shared/tables/enum_table.yaml", "shared/tables/provenance_table.yaml"],
        "schemas": ["shared/schemas/design_intent_ir.schema.yaml", "shared/schemas/arch_candidate_ir.schema.yaml", "shared/schemas/synthesized_spec_draft.schema.yaml"],
        "invariants": ["ARCH_CANDIDATE_IR != SPEC_IR", "Every intent requirement has an owner or explicit non-goal", "Hard constraints pass before scoring", "Every generated parameter has allowed provenance", "MINIMAL_VERTICAL_SLICE_GPGPU includes frontend, assembler, program image, RTL simulation, and memory dump validation contracts"],
        "failures": ["REJECTED_ARCH_CANDIDATE", "UNSUPPORTED_REQUIREMENT", "HARD_CONSTRAINT_FAIL", "FORBIDDEN_PROVENANCE", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "candidate_id", "consumed_ir_hash", "produced_ir_hash", "selected_preset", "constraint_proof", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["preset_selection.md", "parameter_allocation.md", "candidate_scoring.md", "shared/schemas/arch_candidate_ir.schema.yaml", "shared/schemas/synthesized_spec_draft.schema.yaml", "shared/tables/architecture_preset_library.yaml", "shared/tables/minimal_vertical_slice_preset.yaml", "shared/tables/hard_constraint_table.yaml", "shared/tables/quality_target_table.yaml", "shared/tables/requirement_owner_table.yaml"],
        "subpasses": {
            "preset_selection.md": ("Preset Selection", "Select only MINIMAL_SIMT_CORE, MULTI_WARP_SINGLE_SM, or MINIMAL_VERTICAL_SLICE_GPGPU in v4 baseline. Use MINIMAL_VERTICAL_SLICE_GPGPU only when the intent requires compile_kernel_to_program_image, rtl_sim_smoke_test, and memory_dump_golden_check. Unsupported presets must reject or emit refinement evidence instead of being improvised."),
            "parameter_allocation.md": ("Parameter Allocation", "Allocate warp, SM, scheduler, register, shared memory, LSU, cache, and launch parameters only from the selected preset plus explicit user constraints."),
            "candidate_scoring.md": ("Candidate Scoring", "Score only candidates that passed hard constraints. Scores are evidence for closure, not design truth."),
        },
    },
    "gpgpu-spec-lock": {
        "title": "GPGPU Spec Lock",
        "description": "Use when a human spec or synthesized spec draft must become complete, unambiguous, provenance-bearing SPEC_IR with no hidden defaults or ISA source-of-truth drift.",
        "role": "This skill locks static architecture facts. It parses and validates, but it does not design missing fields. It also locks isa_source_of_truth so docs, assembler, disassembler, compiler tables, and RTL defines are derived artifacts rather than independent truth sources.",
        "upstream": ["Human complete spec", "gpgpu-architecture-synthesizer SYNTHESIZED_SPEC_DRAFT"],
        "downstream": ["gpgpu-canonical-state-engine"],
        "inputs": ["HUMAN_SPEC", "SYNTHESIZED_SPEC_DRAFT", "enum_table", "provenance_table", "spec_required_field_table"],
        "outputs": ["SPEC_IR", "SPEC_LOCK_REPORT"],
        "owned": ["ISA", "isa_source_of_truth", "warp model", "thread/block/grid model", "scheduler policy", "register file", "memory hierarchy", "CSR/DCR", "launch ABI", "config defaults", "debug/test hooks"],
        "forbidden": ["Infer missing warp size, scheduler, memory hierarchy, ISA, or cache policy", "Accept hidden defaults or forbidden provenance", "Emit GPU_STATE_IR", "Pass free-form prose downstream"],
        "tables": ["shared/tables/spec_required_field_table.yaml", "shared/tables/source_of_truth_generation_table.yaml", "shared/tables/enum_table.yaml", "shared/tables/provenance_table.yaml"],
        "schemas": ["shared/schemas/spec_ir.schema.yaml", "shared/schemas/synthesized_spec_draft.schema.yaml"],
        "invariants": ["No ambiguity", "No hidden default", "All enums resolved", "Every field has provenance", "Field order and hash are stable", "isa_source_of_truth.owner is SPEC_IR.isa and generated_artifacts are not accepted as independent truth sources"],
        "failures": ["INSUFFICIENT_SPEC", "HIDDEN_DEFAULT_REJECT", "UNKNOWN_ENUM_REJECT", "FORBIDDEN_PROVENANCE", "CONFLICTING_SPEC_FIELD", "SOURCE_OF_TRUTH_DRIFT", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "source_kind", "consumed_ir_hash", "produced_ir_hash", "locked_fields", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["spec_ir_contract.md", "canonical_serialization.md", "provenance_rules.md", "shared/schemas/spec_ir.schema.yaml", "shared/tables/spec_required_field_table.yaml", "shared/tables/source_of_truth_generation_table.yaml", "shared/tables/enum_table.yaml", "shared/tables/provenance_table.yaml"],
        "subpasses": {
            "spec_ir_contract.md": ("SPEC_IR Contract", "Lock only complete architecture facts. Required groups are ISA, isa_source_of_truth, warp model, grid/block/thread model, scheduler, register file, memory hierarchy, CSR/DCR, launch ABI, config defaults, and hooks. Docs, RTL defines, and tool opcode tables must be derived from SPEC_IR.isa."),
            "canonical_serialization.md": ("Canonical Serialization", "Serialize fields in schema order with deterministic scalar formatting. Hash the serialized SPEC_IR, not source prose."),
            "provenance_rules.md": ("Provenance Rules", "Accept USER_SPEC, USER_CONSTRAINT, DESIGN_PRESET, SOLVER_DERIVED, REPAIR_DERIVED, and EXPLICIT_DEFAULT. Reject UNKNOWN, COMMON_GPU_DEFAULT, MODEL_GUESS, and IMPLICIT_DEFAULT."),
        },
    },
    "gpgpu-canonical-state-engine": {
        "title": "GPGPU Canonical State Engine",
        "description": "Use when locked SPEC_IR must become deterministic GPU_STATE_IR or when canonical state invariants, transitions, snapshots, and FSM APIs must be checked.",
        "role": "This skill converts static spec truth into the only execution-state truth consumed by runtime, memory, implementation, and closure passes. It expands SIMT, pipeline, scoreboard, and memory stall state into trace-diffable fields.",
        "upstream": ["gpgpu-spec-lock SPEC_IR"],
        "downstream": ["gpgpu-artifact-contract-engine"],
        "inputs": ["SPEC_IR"],
        "outputs": ["GPU_STATE_IR", "STATE_CONSTRUCTION_REPORT"],
        "owned": ["Initial state construction", "State transition rule binding", "State invariant checking", "Snapshot schema generation", "Trace-diffable pc_table, exec_mask_table, warp_active, warp_halted, scheduler cursor, scoreboard, simt_stack_state, pipeline_registers, memory_stall_state, and performance counters"],
        "forbidden": ["Plan architecture", "Evaluate quality", "Select templates", "Absorb candidate-only quality estimates", "Create state fields absent from SPEC_IR", "Modify state for RTL or runtime convenience"],
        "tables": ["shared/tables/initial_state_construction_table.yaml", "shared/tables/state_transition_rule_table.yaml", "shared/tables/state_invariant_table.yaml"],
        "schemas": ["shared/schemas/spec_ir.schema.yaml", "shared/schemas/gpu_state_ir.schema.yaml"],
        "invariants": ["Active mask width equals warp width", "Resident warp slots match SPEC_IR", "Scheduler references valid resident warps", "Scoreboard dependencies reference existing registers and events", "Outstanding memory request tags are unique", "pc_table, exec_mask_table, simt_stack_state, pipeline_registers, and memory_stall_state are present in snapshots"],
        "failures": ["STATE_CONSTRUCTION_REJECT", "MISSING_TRANSITION_RULE", "STATE_INVARIANT_FAIL", "INVALID_SCHEDULER_STATE", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "initialized_fields", "invariant_results", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["gpu_state_ir_contract.md", "state_transition_rules.md", "state_invariants.md", "shared/schemas/gpu_state_ir.schema.yaml", "shared/tables/initial_state_construction_table.yaml", "shared/tables/state_transition_rule_table.yaml", "shared/tables/state_invariant_table.yaml"],
        "subpasses": {
            "gpu_state_ir_contract.md": ("GPU_STATE_IR Contract", "Populate warp_state, thread_state, pc_state, active_mask_state, scheduler_state, scoreboard_state, register_state, memory_request_state, csr_state, launch_state, pipeline_state, simt_stack_state, and fault_state. Required trace-diff fields include pc_table, exec_mask_table, warp_active, warp_halted, current_fetch_warp, next_fetch_warp, register_pending, pipeline_registers, memory_stall_state, and performance_counters."),
            "state_transition_rules.md": ("State Transition Rules", "Bind every state-changing event to a named rule_id. Unknown events or unbound rules reject before downstream mapping."),
            "state_invariants.md": ("State Invariants", "Validate invariants during init, before transition, after transition, and before snapshot emission."),
        },
    },
    "gpgpu-artifact-contract-engine": {
        "title": "GPGPU Artifact Contract Engine",
        "description": "Use when SPEC_IR and GPU_STATE_IR must be mapped to deterministic RTL, simulator, runtime, software stack, memory, config, validation, PPA contracts, and cross-artifact consistency gates.",
        "role": "This skill is the deterministic transform and config binding pass. It maps state truth to artifact contracts without making new architecture decisions and emits cross_artifact_consistency_gate plus declared_test_coverage_gate evidence.",
        "upstream": ["gpgpu-spec-lock SPEC_IR", "gpgpu-canonical-state-engine GPU_STATE_IR"],
        "downstream": ["gpgpu-runtime-validator", "gpgpu-memory-subsystem", "gpgpu-implementation-validator", "gpgpu-closure-refinement-engine"],
        "inputs": ["SPEC_IR", "GPU_STATE_IR"],
        "outputs": ["RTL_MAPPING_IR", "SIM_BEHAVIOR_IR", "RUNTIME_CONTRACT_IR", "SOFTWARE_STACK_CONTRACT_IR", "PROGRAM_IMAGE_CONTRACT_IR", "TEST_APP_CONTRACT_IR", "MEMORY_MODEL_IR", "CONFIG_BINDING_IR", "VALIDATION_PLAN_IR", "PPA_COUNTER_MAP", "ARTIFACT_CONTRACT_REPORT"],
        "owned": ["Deterministic transform", "Config parameter ownership", "Artifact mapping coverage", "Validation plan emission", "PPA counter binding", "cross_artifact_consistency_gate", "declared_test_coverage_gate", "source-of-truth artifact generation mapping"],
        "forbidden": ["Infer mappings without table entries", "Let runtime or RTL reinterpret ABI fields", "Leak debug-only fields to ABI", "Treat config as independent design truth"],
        "tables": ["shared/tables/artifact_mapping_table.yaml", "shared/tables/config_ownership_table.yaml", "shared/tables/source_of_truth_generation_table.yaml", "shared/tables/cross_artifact_consistency_table.yaml", "shared/tables/software_stack_contract_table.yaml", "shared/tables/end_to_end_smoke_test_table.yaml", "shared/tables/state_to_rtl_mapping.yaml", "shared/tables/state_to_sim_mapping.yaml", "shared/tables/state_to_runtime_mapping.yaml", "shared/tables/state_to_memory_mapping.yaml"],
        "schemas": ["shared/schemas/rtl_mapping_ir.schema.yaml", "shared/schemas/sim_behavior_ir.schema.yaml", "shared/schemas/runtime_contract_ir.schema.yaml", "shared/schemas/software_stack_contract_ir.schema.yaml", "shared/schemas/program_image_contract_ir.schema.yaml", "shared/schemas/test_app_contract_ir.schema.yaml", "shared/schemas/memory_model_ir.schema.yaml", "shared/schemas/config_binding_ir.schema.yaml", "shared/schemas/validation_plan_ir.schema.yaml"],
        "invariants": ["Every consumed state field is mapped or explicit_unused", "Every config parameter has owner and visibility", "ABI fields have one interpretation", "Missing mapping fails closed", "SPEC_IR.isa is byte-or-semantically equivalent to generated RTL/tool/doc opcode artifacts", "Declared validation tests appear in the runner and at least compile/generate"],
        "failures": ["MISSING_MAPPING_FAIL_CLOSED", "CONFIG_OWNER_MISSING", "ABI_FIELD_REINTERPRETED", "DEBUG_ONLY_LEAKS_TO_ABI", "DOC_ARTIFACT_DRIFT", "ISA_ENCODING_DRIFT", "DECLARED_TEST_NOT_RUN", "MAGIC_CONSTANT_UNBOUND", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "mapping_coverage", "config_ownership", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["deterministic_transform.md", "config_binding.md", "artifact_mapping.md", "shared/tables/artifact_mapping_table.yaml", "shared/tables/config_ownership_table.yaml", "shared/tables/source_of_truth_generation_table.yaml", "shared/tables/cross_artifact_consistency_table.yaml", "shared/tables/software_stack_contract_table.yaml", "shared/tables/end_to_end_smoke_test_table.yaml", "shared/tables/state_to_rtl_mapping.yaml", "shared/tables/state_to_sim_mapping.yaml", "shared/tables/state_to_runtime_mapping.yaml", "shared/tables/state_to_memory_mapping.yaml"],
        "subpasses": {
            "deterministic_transform.md": ("Deterministic Transform", "Apply mapping tables to SPEC_IR and GPU_STATE_IR. If a state field has no mapping, emit MISSING_MAPPING_FAIL_CLOSED."),
            "config_binding.md": ("Config Binding", "Classify config fields as hardware_private, simulator_private, hw_sw_abi, test_only, or debug_only. Validate owner and allowed consumers. Magic constants such as total_threads, block_dim, base_data_addr, base_a, base_b, base_c, dump_range, and finish_delay must be bound through CONFIG_BINDING_IR or rejected as MAGIC_CONSTANT_UNBOUND."),
            "artifact_mapping.md": ("Artifact Mapping", "Emit downstream contracts for RTL, simulator, runtime, software stack, program image, test app, memory subsystem, validation plan, and PPA counters. Validate cross_artifact_consistency_gate and declared_test_coverage_gate before closure."),
        },
    },
    "gpgpu-runtime-validator": {
        "title": "GPGPU Runtime Validator",
        "description": "Use when host runtime, software stack, CUDA-like frontend subset, assembler, program image, launch ABI, command queue, completion, fault, and synchronization behavior must be validated against locked contracts.",
        "role": "This skill validates host/runtime/launch ABI and software stack behavior. It does not design memory hierarchy or RTL memory path.",
        "upstream": ["gpgpu-artifact-contract-engine RUNTIME_CONTRACT_IR, SOFTWARE_STACK_CONTRACT_IR, PROGRAM_IMAGE_CONTRACT_IR, TEST_APP_CONTRACT_IR, and CONFIG_BINDING_IR", "gpgpu-canonical-state-engine launch_state", "gpgpu-spec-lock ABI_launch_contract"],
        "downstream": ["gpgpu-closure-refinement-engine"],
        "inputs": ["RUNTIME_CONTRACT_IR", "SOFTWARE_STACK_CONTRACT_IR", "PROGRAM_IMAGE_CONTRACT_IR", "TEST_APP_CONTRACT_IR", "CONFIG_BINDING_IR", "GPU_STATE_IR.launch_state", "SPEC_IR.ABI_launch_contract"],
        "outputs": ["RUNTIME_VALIDATION_REPORT_IR", "runtime_smoke_trace", "launch_contract_report", "software_stack_contract_report", "program_image_contract_report", "test_app_contract_report"],
        "owned": ["frontend_subset_contract", "assembler_contract", "program_image_contract", "kernel_test_app_contract", "golden_output_contract", "Program image loading", "Kernel entry", "Argument layout", "Grid/block dimensions", "Command queue", "Doorbell/start", "Completion/done", "Fault reporting", "CSR/runtime interface", "Host-device synchronization"],
        "forbidden": ["Design coalescer, load/store queue, cache hierarchy, shared memory banks, request/response tags, or memory RTL pipeline", "Reinterpret ABI fields", "Modify GPU_STATE_IR"],
        "tables": ["shared/tables/runtime_smoke_test_table.yaml", "shared/tables/software_stack_contract_table.yaml", "shared/tables/end_to_end_smoke_test_table.yaml", "shared/tables/config_ownership_table.yaml"],
        "schemas": ["shared/schemas/runtime_contract_ir.schema.yaml", "shared/schemas/software_stack_contract_ir.schema.yaml", "shared/schemas/program_image_contract_ir.schema.yaml", "shared/schemas/test_app_contract_ir.schema.yaml", "shared/schemas/config_binding_ir.schema.yaml", "shared/schemas/runtime_validation_report_ir.schema.yaml"],
        "invariants": ["Launch ABI layout matches SPEC_IR", "Grid/block dimensions fit launch_state", "Completion and fault paths are observable", "Runtime consumes only ABI-visible config", "High-level kernel compilation, assembler output, program image load, parameter binding, output memory dump, and golden checker location agree with the runtime contract"],
        "failures": ["INVALID_ARGUMENT_LAYOUT", "GRID_DIM_MISMATCH", "MISSING_COMPLETION_PATH", "FAULT_CONTRACT_FAIL", "APP_COMPILE_FAIL", "FRONTEND_RUNTIME_MAPPING_MISMATCH", "MEMORY_DUMP_CONTRACT_MISMATCH", "MAGIC_CONSTANT_UNBOUND", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "runtime_smoke_trace_hash", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["launch_contract.md", "abi_validation.md", "completion_fault_validation.md", "shared/schemas/runtime_validation_report_ir.schema.yaml", "shared/schemas/software_stack_contract_ir.schema.yaml", "shared/schemas/program_image_contract_ir.schema.yaml", "shared/schemas/test_app_contract_ir.schema.yaml", "shared/tables/runtime_smoke_test_table.yaml", "shared/tables/software_stack_contract_table.yaml", "shared/tables/end_to_end_smoke_test_table.yaml"],
        "subpasses": {
            "launch_contract.md": ("Launch Contract", "Validate CUDA-like frontend subset, app compile smoke, assembler smoke, program image layout, kernel entry, command queue, doorbell/start, grid/block dimensions, argument binding, launch resource admission, memory dump contract, and golden_output_contract."),
            "abi_validation.md": ("ABI Validation", "Check argument layout, scalar size, pointer size, alignment, ABI version, CSR/runtime interface ownership, blockIdx/threadIdx/blockDim/gridDim mapping, total_threads, block_dim, and base address bindings."),
            "completion_fault_validation.md": ("Completion and Fault Validation", "Ensure done, error, timeout, and fault-reporting paths are visible to host and closure."),
        },
    },
    "gpgpu-memory-subsystem": {
        "title": "GPGPU Memory Subsystem",
        "description": "Use when GPGPU memory subsystem contract, RTL-facing memory path, memory request lifecycle, duplicate request prevention, coalescing, LSQ, shared memory, cache/global interface, ordering, tags, and scoreboard wakeup must be defined and validated.",
        "role": "This skill defines and validates the GPGPU memory subsystem contract and RTL-facing memory path from canonical state and memory model inputs. It must make request issue, stall, response, replay, and scoreboard wakeup observable.",
        "upstream": ["gpgpu-canonical-state-engine memory_request_state, warp_state, scoreboard_state", "gpgpu-artifact-contract-engine MEMORY_MODEL_IR and RTL_MAPPING_IR.memory_interface"],
        "downstream": ["gpgpu-implementation-validator", "gpgpu-closure-refinement-engine"],
        "inputs": ["GPU_STATE_IR.memory_request_state", "GPU_STATE_IR.warp_state", "GPU_STATE_IR.scoreboard_state", "MEMORY_MODEL_IR", "RTL_MAPPING_IR.memory_interface"],
        "outputs": ["MEMORY_SUBSYSTEM_IR", "MEMORY_VALIDATION_REPORT_IR", "memory_trace", "memory_ordering_report", "memory_rtl_interface_report"],
        "owned": ["Address spaces", "Global/shared/local/constant memory", "Load/store path", "memory_request_lifecycle", "duplicate_request_prevention", "request_replay_policy", "Coalescing policy", "Lane mask handling", "Byte enables", "Load/store queue", "Outstanding request table", "Request/response tags", "Shared memory banks", "Cache/global interface", "Atomic unit", "Fence ordering", "Memory fault contract", "Scoreboard wakeup", "Backpressure"],
        "forbidden": ["Choose architecture memory hierarchy not present in SPEC_IR", "Modify scheduler policy", "Treat memory validation as runtime launch validation", "Ignore tag or lane-mask mismatches"],
        "tables": ["shared/tables/memory_address_space_table.yaml", "shared/tables/coalescing_rule_table.yaml", "shared/tables/shared_memory_bank_table.yaml", "shared/tables/memory_ordering_table.yaml", "shared/tables/memory_scoreboard_wakeup_table.yaml"],
        "schemas": ["shared/schemas/memory_model_ir.schema.yaml", "shared/schemas/memory_subsystem_ir.schema.yaml", "shared/schemas/memory_validation_report_ir.schema.yaml"],
        "invariants": ["Lane mask drives byte enable generation", "Request tags are unique until response", "Load response wakes matching scoreboard dependency", "Fences enforce declared ordering", "Bank conflicts are detected and reported", "A stalled memory instruction does not duplicate a serviced request", "stall_release_condition is tied to response_match_policy and scoreboard_wakeup_condition"],
        "failures": ["REQUEST_TAG_MISMATCH", "BANK_CONFLICT_DETECTED", "ORDERING_VIOLATION", "SCOREBOARD_WAKEUP_MISSING", "DUPLICATE_MEMORY_REQUEST", "MEMORY_STALL_RELEASE_MISSING", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "memory_trace_hash", "ordering_results", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["memory_model.md", "coalescer.md", "load_store_queue.md", "shared_memory.md", "cache_global_interface.md", "scoreboard_wakeup.md", "shared/schemas/memory_subsystem_ir.schema.yaml", "shared/tables/coalescing_rule_table.yaml", "shared/tables/memory_ordering_table.yaml"],
        "subpasses": {
            "memory_model.md": ("Memory Model", "Bind address spaces, consistency, atomic, fence, fault, cache/global interface semantics, and memory_request_lifecycle from MEMORY_MODEL_IR."),
            "coalescer.md": ("Coalescer", "Validate lane masks, address grouping, byte enables, transaction boundaries, and partial stores."),
            "load_store_queue.md": ("Load Store Queue", "Validate LSQ admission, outstanding request table, request/response tags, replay, backpressure, serviced_tracking, response_match_policy, duplicate_request_prevention, and stall_release_condition."),
            "shared_memory.md": ("Shared Memory", "Validate shared memory banks, bank conflicts, broadcast behavior, and conflict reporting."),
            "cache_global_interface.md": ("Cache Global Interface", "Validate cache request/response contract, global memory interface, atomics, faults, miss/ready handshake, request replay, and retry behavior."),
            "scoreboard_wakeup.md": ("Scoreboard Wakeup", "Validate that load responses, atomic responses, and fault responses wake or poison the correct scoreboard entries."),
        },
    },
    "gpgpu-implementation-validator": {
        "title": "GPGPU Implementation Validator",
        "description": "Use when RTL SIMT core, app-to-hex vertical slices, memory dump checks, and golden simulator traces must be validated against GPU_STATE_IR, mapping contracts, memory subsystem behavior, and validation plans.",
        "role": "This skill validates RTL and golden simulator behavior against canonical state. It merges the former RTL SIMT core and golden sim responsibilities and requires an app -> asm -> hex -> RTL sim -> memory dump path for vertical-slice prototypes.",
        "upstream": ["gpgpu-canonical-state-engine GPU_STATE_IR", "gpgpu-artifact-contract-engine RTL_MAPPING_IR, SIM_BEHAVIOR_IR, VALIDATION_PLAN_IR", "gpgpu-memory-subsystem MEMORY_SUBSYSTEM_IR"],
        "downstream": ["gpgpu-closure-refinement-engine"],
        "inputs": ["GPU_STATE_IR", "RTL_MAPPING_IR", "SIM_BEHAVIOR_IR", "MEMORY_SUBSYSTEM_IR", "VALIDATION_PLAN_IR", "SOFTWARE_STACK_CONTRACT_IR", "PROGRAM_IMAGE_CONTRACT_IR", "TEST_APP_CONTRACT_IR", "trace"],
        "outputs": ["IMPLEMENTATION_VALIDATION_REPORT_IR", "RTL_VALIDATION_REPORT", "GOLDEN_SIM_REPORT", "FIRST_DIVERGENCE_REPORT", "VERTICAL_SLICE_VALIDATION_REPORT"],
        "owned": ["RTL SIMT core validation", "Golden simulator validation", "RTL-vs-golden first divergence", "Trace event consistency", "app_compile_smoke", "assembler_smoke", "program_hex_load_smoke", "rtl_sim_smoke", "memory_dump_compare", "waveform_or_trace_required"],
        "forbidden": ["Redefine ISA", "Change GPU_STATE_IR to match RTL", "Let golden sim become a second truth source", "Ignore first divergence evidence"],
        "tables": ["shared/tables/rtl_validation_gate_table.yaml", "shared/tables/golden_sim_trace_field_table.yaml", "shared/tables/first_divergence_taxonomy.yaml", "shared/tables/end_to_end_smoke_test_table.yaml", "shared/tables/vertical_slice_validation_table.yaml"],
        "schemas": ["shared/schemas/implementation_validation_report_ir.schema.yaml", "shared/schemas/first_divergence_report_ir.schema.yaml"],
        "invariants": ["Fetch/decode/issue/execute/writeback obey mapped state", "Active mask updates match transition rules", "Scoreboard stalls and wakeups match memory subsystem contract", "Trace fields cover mandatory semantic fields", "Vertical-slice tests produce program.hex, rtl_sim_trace or waveform, memory_dump, and golden comparison evidence"],
        "failures": ["RTL_VALIDATION_FAIL", "GOLDEN_SIM_REDEFINES_ISA", "FIRST_DIVERGENCE_DETECTED", "TRACE_FIELD_MISSING", "APP_COMPILE_FAIL", "PROGRAM_HEX_LOAD_FAIL", "MEMORY_DUMP_CONTRACT_MISMATCH", "DECLARED_TEST_NOT_RUN", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "rtl_report_hash", "golden_report_hash", "first_divergence", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["rtl_simt_core_validation.md", "golden_sim_validation.md", "first_divergence.md", "shared/schemas/implementation_validation_report_ir.schema.yaml", "shared/schemas/first_divergence_report_ir.schema.yaml", "shared/tables/rtl_validation_gate_table.yaml", "shared/tables/golden_sim_trace_field_table.yaml", "shared/tables/first_divergence_taxonomy.yaml", "shared/tables/end_to_end_smoke_test_table.yaml", "shared/tables/vertical_slice_validation_table.yaml"],
        "subpasses": {
            "rtl_simt_core_validation.md": ("RTL SIMT Core Validation", "Validate fetch, decode, issue, execute, writeback, scheduler, active mask, scoreboard, register, CSR, pipeline, memory request interface events, and vertical-slice smoke tests: app_compile_smoke, assembler_smoke, program_hex_load_smoke, rtl_sim_smoke, memory_dump_compare, and waveform_or_trace_required."),
            "golden_sim_validation.md": ("Golden Simulator Validation", "Validate deterministic replay and property coverage against SIM_BEHAVIOR_IR without redefining ISA or architecture semantics."),
            "first_divergence.md": ("First Divergence", "Compare RTL and golden traces by ordered semantic events and classify the first field, rule, and owner that diverges."),
        },
    },
    "gpgpu-closure-refinement-engine": {
        "title": "GPGPU Closure Refinement Engine",
        "description": "Use when architecture candidates, locked specs, state, artifact reports, runtime/memory/implementation validation, vertical-slice evidence, PPA evidence, and trace divergences must be accepted, rejected, or routed to refinement.",
        "role": "This skill is the final acceptance, failure attribution, and refinement-request compiler pass. It classifies Vibe-derived failures such as documentation drift, declared tests not run, app compile failures, and unbound magic constants.",
        "upstream": ["gpgpu-architecture-synthesizer", "gpgpu-spec-lock", "gpgpu-canonical-state-engine", "gpgpu-artifact-contract-engine", "gpgpu-runtime-validator", "gpgpu-memory-subsystem", "gpgpu-implementation-validator"],
        "downstream": ["User-facing closure decision", "Repair owner skill for refinement loops"],
        "inputs": ["ARCH_CANDIDATE_IR", "SPEC_IR", "GPU_STATE_IR", "ARTIFACT_CONTRACT_REPORT", "RUNTIME_VALIDATION_REPORT", "MEMORY_VALIDATION_REPORT", "IMPLEMENTATION_VALIDATION_REPORT", "PPA_REPORT", "TRACE_DIVERGENCE_REPORT"],
        "outputs": ["SYNTHESIS_ACCEPTANCE_REPORT_IR", "REFINEMENT_REQUEST_IR"],
        "owned": ["Closure gate evaluation", "Failure attribution", "Refinement request generation", "Repair routing"],
        "forbidden": ["Design architecture", "Bypass failed gates", "Accept evidence-free candidates", "Directly mutate ARCH_CANDIDATE_IR, SPEC_IR, or GPU_STATE_IR"],
        "tables": ["shared/tables/closure_gate_table.yaml", "shared/tables/verdict_decision_table.yaml", "shared/tables/failure_taxonomy_table.yaml", "shared/tables/vibe_failure_taxonomy_table.yaml", "shared/tables/repair_routing_table.yaml", "shared/tables/vertical_slice_validation_table.yaml"],
        "schemas": ["shared/schemas/synthesis_acceptance_report_ir.schema.yaml", "shared/schemas/refinement_request_ir.schema.yaml"],
        "invariants": ["Verdict is one of ACCEPT, REJECT, REFINE_REQUIRED, INSUFFICIENT_EVIDENCE", "Every failed gate has owner, affected field, evidence, and repair route", "Hard correctness failures reject", "Repairable trace failures refine", "DOC_ARTIFACT_DRIFT, ISA_ENCODING_DRIFT, DECLARED_TEST_NOT_RUN, APP_COMPILE_FAIL, MAGIC_CONSTANT_UNBOUND, FRONTEND_RUNTIME_MAPPING_MISMATCH, and MEMORY_DUMP_CONTRACT_MISMATCH have explicit repair owners"],
        "failures": ["INSUFFICIENT_EVIDENCE", "HARD_CORRECTNESS_FAIL", "REPAIRABLE_TRACE_FAIL", "UNROUTED_FAILURE", "DOC_ARTIFACT_DRIFT", "ISA_ENCODING_DRIFT", "DECLARED_TEST_NOT_RUN", "APP_COMPILE_FAIL", "MAGIC_CONSTANT_UNBOUND", "FRONTEND_RUNTIME_MAPPING_MISMATCH", "MEMORY_DUMP_CONTRACT_MISMATCH", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "gate_results", "failed_fields", "missing_assets", "downstream_contract", "refinement_request"],
        "assets": ["closure_gate.md", "causal_trace_analysis.md", "refinement_request.md", "shared/schemas/synthesis_acceptance_report_ir.schema.yaml", "shared/schemas/refinement_request_ir.schema.yaml", "shared/tables/closure_gate_table.yaml", "shared/tables/verdict_decision_table.yaml", "shared/tables/failure_taxonomy_table.yaml", "shared/tables/vibe_failure_taxonomy_table.yaml", "shared/tables/repair_routing_table.yaml", "shared/tables/vertical_slice_validation_table.yaml"],
        "subpasses": {
            "closure_gate.md": ("Closure Gate", "Evaluate coverage, spec lock, state invariant, artifact mapping, cross_artifact_consistency_gate, declared_test_coverage_gate, runtime, memory, implementation, vertical-slice validation, PPA, and stability gates."),
            "causal_trace_analysis.md": ("Causal Trace Analysis", "Route metric or trace deltas to GPU_STATE_IR fields, transition rules, failed gates, and owner skills."),
            "refinement_request.md": ("Refinement Request", "Emit structured repair requests with root cause, affected state field, failed gate, repair owner skill, repair type, and evidence trace."),
        },
    },
}


SCHEMAS = {
    "mode_selection_ir.schema.yaml": """
schema: MODE_SELECTION_IR
version: v4
type: object
required: [schema_version, mode, input_kind, route_reason, next_skill, forbidden_next_skills, provenance]
properties:
  mode:
    type: enum
    values: [REPRODUCE, DESIGN, PATCH_REQUEST, TRACE_DEBUG]
  input_kind:
    type: enum
    values: [COMPLETE_SPEC, DESIGN_GOAL, PATCH, TRACE]
  next_skill:
    type: string
  forbidden_next_skills:
    type: list[string]
  provenance:
    type: list[FIELD_PROVENANCE]
failure_rules:
  ambiguous_mode: AMBIGUOUS_MODE
  architecture_field_present: FORBIDDEN_ARCHITECTURE_FIELD
""",
    "design_intent_ir.schema.yaml": """
schema: DESIGN_INTENT_IR
version: v4
type: object
required: [schema_version, intent_id, objective, non_goals, workload_profile, target_platform, hard_constraints, soft_constraints, required_features, optional_features, validation_target, prototype_kind, prototype_credibility_target, provenance]
forbidden_fields: [warp_size, sm_count, cache_policy, scheduler_policy, isa_encoding, memory_hierarchy, register_file_size, rtl_pipeline]
properties:
  objective: {type: string, min_length: 1}
  non_goals: {type: list[string]}
  workload_profile: {type: object}
  target_platform: {type: enum, values: [TEACHING, FPGA_SMALL, ASIC_PROTOTYPE, SIMULATION_ONLY]}
  hard_constraints: {type: list[constraint]}
  soft_constraints: {type: list[constraint]}
  required_features: {type: list[string]}
  optional_features: {type: list[string]}
  validation_target: {type: list[string]}
  prototype_kind: {type: enum, values: [DOCUMENT_ONLY, VERTICAL_SLICE_PROTOTYPE]}
  prototype_credibility_target:
    type: list[string]
    values: [compile_kernel_to_program_image, rtl_sim_smoke_test, memory_dump_golden_check, trace_diff_debug]
  provenance: {type: list[FIELD_PROVENANCE]}
failure_rules:
  forbidden_architecture_field: FORBIDDEN_ARCHITECTURE_FIELD
  missing_required_field: INSUFFICIENT_REQUEST
  ambiguous_objective: AMBIGUOUS_INTENT
""",
    "arch_candidate_ir.schema.yaml": """
schema: ARCH_CANDIDATE_IR
version: v4
type: object
required: [schema_version, candidate_id, source_intent_hash, selected_preset, parameter_set, requirement_coverage_matrix, constraint_proof, quality_estimate, rejected_alternatives, unresolved_risks, provenance]
properties:
  selected_preset:
    type: enum
    values: [MINIMAL_SIMT_CORE, MULTI_WARP_SINGLE_SM, MINIMAL_VERTICAL_SLICE_GPGPU]
  parameter_set:
    required: [sm_count, warp_size, max_warps_per_sm, scheduler_policy, register_file, shared_memory, memory_hierarchy, isa_profile, launch_abi]
  provenance:
    allowed: [USER_CONSTRAINT, DESIGN_PRESET, SOLVER_DERIVED, REPAIR_DERIVED]
failure_rules:
  preset_not_supported: UNSUPPORTED_REQUIREMENT
  hard_constraint_failed: HARD_CONSTRAINT_FAIL
  forbidden_provenance: FORBIDDEN_PROVENANCE
  candidate_equals_spec: ARCH_CANDIDATE_MUST_NOT_BE_SPEC
""",
    "synthesized_spec_draft.schema.yaml": """
schema: SYNTHESIZED_SPEC_DRAFT
version: v4
type: object
required: [schema_version, draft_id, source_candidate_id, spec_fields, completeness_claim, unresolved_fields, provenance]
properties:
  completeness_claim: {type: enum, values: [COMPLETE_FOR_SPEC_LOCK, INCOMPLETE_REQUIRES_REFINEMENT]}
  unresolved_fields: {type: list[string]}
failure_rules:
  unresolved_required_field: INSUFFICIENT_SPEC
  forbidden_provenance: FORBIDDEN_PROVENANCE
""",
    "spec_ir.schema.yaml": """
schema: SPEC_IR
version: v4
type: object
required: [schema_version, design_identity, source_kind, isa, isa_source_of_truth, warp_model, thread_block_grid_model, scheduler_policy, register_file, memory_hierarchy, csr_dcr, launch_abi, config_defaults, debug_test_hooks, provenance, canonical_hash]
properties:
  source_kind: {type: enum, values: [HUMAN_SPEC, SYNTHESIZED_SPEC_DRAFT]}
  isa:
    required: [profile, operation_classes, encoding_policy]
  isa_source_of_truth:
    owner: SPEC_IR.isa
    required: [owner, generated_artifacts, generation_table]
  warp_model:
    required: [width, active_mask_width, reconvergence_model]
  scheduler_policy:
    required: [policy, issue_width]
  memory_hierarchy:
    required: [address_spaces, global_memory, shared_memory, local_memory, constant_memory, cache_policy]
  launch_abi:
    required: [abi_version, argument_layout, grid_dim_fields, block_dim_fields, completion_path, fault_path]
  provenance:
    required_for: all_fields
    forbidden: [UNKNOWN, COMMON_GPU_DEFAULT, MODEL_GUESS, IMPLICIT_DEFAULT]
failure_rules:
  missing_required_field: INSUFFICIENT_SPEC
  hidden_default: HIDDEN_DEFAULT_REJECT
  unknown_enum: UNKNOWN_ENUM_REJECT
  forbidden_provenance: FORBIDDEN_PROVENANCE
  conflicting_field: CONFLICTING_SPEC_FIELD
  unstable_hash: CANONICAL_HASH_UNSTABLE
  source_of_truth_drift: SOURCE_OF_TRUTH_DRIFT
""",
    "gpu_state_ir.schema.yaml": """
schema: GPU_STATE_IR
version: v4
type: object
required: [schema_version, design_identity, source_spec_hash, warp_state, thread_state, pc_state, active_mask_state, scheduler_state, scoreboard_state, simt_stack_state, register_state, memory_request_state, csr_state, launch_state, pipeline_state, fault_state, canonical_hash]
properties:
  warp_state: {required: [resident_warps, warp_width, per_warp_status, pc_table, exec_mask_table, warp_active, warp_halted]}
  thread_state: {required: [thread_ids, block_ids, grid_ids]}
  pc_state: {required: [per_warp_pc]}
  active_mask_state: {required: [per_warp_active_mask, mask_width]}
  scheduler_state: {required: [policy, eligible_warps, selected_warp, current_fetch_warp, next_fetch_warp]}
  scoreboard_state: {required: [pending_registers, register_pending, wakeup_events]}
  simt_stack_state: {required: [entries, depth]}
  register_state: {required: [register_file_size, per_thread_registers]}
  memory_request_state: {required: [outstanding_requests, request_tags, lane_masks, serviced_tracking]}
  launch_state: {required: [grid_dim, block_dim, kernel_entry, completion, fault]}
  pipeline_state: {required: [pipeline_registers, memory_stall_state, performance_counters]}
failure_rules:
  active_mask_width_mismatch: STATE_INVARIANT_FAIL
  resident_slot_mismatch: STATE_INVARIANT_FAIL
  missing_transition_rule: MISSING_TRANSITION_RULE
  invalid_scheduler_state: INVALID_SCHEDULER_STATE
""",
    "rtl_mapping_ir.schema.yaml": """
schema: RTL_MAPPING_IR
version: v4
required: [schema_version, source_state_hash, modules, interfaces, state_field_mapping, explicit_unused]
failure_rules: {missing_mapping: MISSING_MAPPING_FAIL_CLOSED}
""",
    "sim_behavior_ir.schema.yaml": """
schema: SIM_BEHAVIOR_IR
version: v4
required: [schema_version, source_state_hash, transition_semantics, trace_fields, deterministic_replay_contract]
failure_rules: {isa_redefinition: GOLDEN_SIM_REDEFINES_ISA}
""",
    "runtime_contract_ir.schema.yaml": """
schema: RUNTIME_CONTRACT_IR
version: v4
required: [schema_version, abi_version, software_stack_contract, program_image_contract, test_app_contract, memory_dump_contract, kernel_entry, argument_layout, grid_block_contract, command_queue, doorbell, completion, fault_reporting]
failure_rules: {invalid_layout: INVALID_ARGUMENT_LAYOUT, missing_completion: MISSING_COMPLETION_PATH, app_compile_fail: APP_COMPILE_FAIL, memory_dump_mismatch: MEMORY_DUMP_CONTRACT_MISMATCH}
""",
    "software_stack_contract_ir.schema.yaml": """
schema: SOFTWARE_STACK_CONTRACT_IR
version: v4
required: [schema_version, frontend_subset_contract, assembler_contract, program_image_contract, kernel_test_app_contract, golden_output_contract]
properties:
  frontend_subset_contract: {required: [language_subset, thread_id_intrinsics, supported_control_flow, unsupported_features]}
  assembler_contract: {required: [opcode_source, symbol_policy, error_policy]}
  program_image_contract: {required: [format, entry_symbol, load_address, section_layout]}
  kernel_test_app_contract: {required: [declared_tests, runner_tests, argument_binding, data_layout]}
  golden_output_contract: {required: [checker, output_region, comparison_policy]}
failure_rules:
  app_compile_fail: APP_COMPILE_FAIL
  declared_test_not_run: DECLARED_TEST_NOT_RUN
  frontend_runtime_mapping_mismatch: FRONTEND_RUNTIME_MAPPING_MISMATCH
""",
    "program_image_contract_ir.schema.yaml": """
schema: PROGRAM_IMAGE_CONTRACT_IR
version: v4
required: [schema_version, encoding_source_hash, section_layout, entry_symbol, load_address, parameter_binding, hex_format, loader_contract]
failure_rules:
  source_drift: ISA_ENCODING_DRIFT
  load_fail: PROGRAM_HEX_LOAD_FAIL
""",
    "test_app_contract_ir.schema.yaml": """
schema: TEST_APP_CONTRACT_IR
version: v4
required: [schema_version, declared_tests, runner_binding, compile_or_generate_step, input_data_layout, output_data_layout, memory_dump_contract, golden_checker]
failure_rules:
  declared_test_not_run: DECLARED_TEST_NOT_RUN
  app_compile_fail: APP_COMPILE_FAIL
  memory_dump_mismatch: MEMORY_DUMP_CONTRACT_MISMATCH
""",
    "memory_model_ir.schema.yaml": """
schema: MEMORY_MODEL_IR
version: v4
required: [schema_version, address_spaces, coalescing_policy, ordering_policy, shared_memory_banks, cache_global_interface, atomic_contract, fence_contract, fault_contract]
failure_rules: {unsupported_space: MEMORY_ADDRESS_SPACE_UNSUPPORTED}
""",
    "config_binding_ir.schema.yaml": """
schema: CONFIG_BINDING_IR
version: v4
required: [schema_version, parameters, owners, visibility, consumers]
visibility_values: [hardware_private, simulator_private, hw_sw_abi, test_only, debug_only]
failure_rules: {missing_owner: CONFIG_OWNER_MISSING, debug_leak: DEBUG_ONLY_LEAKS_TO_ABI}
""",
    "memory_subsystem_ir.schema.yaml": """
schema: MEMORY_SUBSYSTEM_IR
version: v4
required: [schema_version, address_spaces, coalescer, load_store_queue, outstanding_request_table, memory_request_lifecycle, request_replay_policy, shared_memory, cache_global_interface, atomic_unit, fence_ordering, scoreboard_wakeup, backpressure]
properties:
  memory_request_lifecycle:
    required: [issue_condition, outstanding_tracking, replay_or_serviced_policy, response_match_policy, scoreboard_wakeup_condition, duplicate_request_prevention, stall_release_condition]
  request_replay_policy:
    required: [on_pipeline_stall, serviced_tracking, response_matching]
failure_rules: {tag_mismatch: REQUEST_TAG_MISMATCH, duplicate_request: DUPLICATE_MEMORY_REQUEST, missing_stall_release: MEMORY_STALL_RELEASE_MISSING}
""",
    "validation_plan_ir.schema.yaml": """
schema: VALIDATION_PLAN_IR
version: v4
required: [schema_version, runtime_tests, memory_tests, implementation_tests, vertical_slice_tests, closure_gates, declared_test_coverage_gate, trace_requirements]
failure_rules: {missing_required_test: VALIDATION_PLAN_INCOMPLETE, declared_test_not_run: DECLARED_TEST_NOT_RUN}
""",
    "runtime_validation_report_ir.schema.yaml": """
schema: RUNTIME_VALIDATION_REPORT_IR
version: v4
required: [schema_version, verdict, consumed_ir_hash, produced_ir_hash, launch_contract_report, runtime_smoke_trace, failed_fields]
verdict_values: [PASS, REJECT, INSUFFICIENT_EVIDENCE]
""",
    "memory_validation_report_ir.schema.yaml": """
schema: MEMORY_VALIDATION_REPORT_IR
version: v4
required: [schema_version, verdict, consumed_ir_hash, produced_ir_hash, memory_trace, memory_ordering_report, memory_rtl_interface_report, failed_fields]
verdict_values: [PASS, REJECT, REFINE_REQUIRED, INSUFFICIENT_EVIDENCE]
""",
    "implementation_validation_report_ir.schema.yaml": """
schema: IMPLEMENTATION_VALIDATION_REPORT_IR
version: v4
required: [schema_version, verdict, consumed_ir_hash, produced_ir_hash, rtl_validation_report, golden_sim_report, first_divergence_report, failed_fields]
verdict_values: [PASS, REJECT, REFINE_REQUIRED, INSUFFICIENT_EVIDENCE]
""",
    "first_divergence_report_ir.schema.yaml": """
schema: FIRST_DIVERGENCE_REPORT_IR
version: v4
required: [schema_version, divergence_id, trace_a, trace_b, first_event_index, affected_state_field, transition_rule, taxonomy, evidence]
failure_rules: {unclassified: FIRST_DIVERGENCE_UNCLASSIFIED}
""",
    "synthesis_acceptance_report_ir.schema.yaml": """
schema: SYNTHESIS_ACCEPTANCE_REPORT_IR
version: v4
type: object
required: [schema_version, verdict, consumed_ir_hash, produced_ir_hash, gate_results, failed_fields, missing_assets, downstream_contract]
properties:
  verdict:
    type: enum
    values: [ACCEPT, REJECT, REFINE_REQUIRED, INSUFFICIENT_EVIDENCE]
  gate_results:
    required: [requirement_coverage, spec_lock, state_invariants, artifact_mapping, cross_artifact_consistency_gate, declared_test_coverage_gate, runtime_validation, memory_validation, implementation_validation, vertical_slice_validation, ppa, stability]
failure_rules:
  missing_evidence: INSUFFICIENT_EVIDENCE
  hard_correctness_fail: REJECT
  repairable_trace_fail: REFINE_REQUIRED
""",
    "refinement_request_ir.schema.yaml": """
schema: REFINEMENT_REQUEST_IR
version: v4
type: object
required: [schema_version, request_id, root_cause, affected_state_field, failed_gate, repair_owner_skill, repair_type, evidence_trace, constraints]
properties:
  repair_type:
    type: enum
    values: [SPEC_FIELD_FIX, STATE_RULE_FIX, ARTIFACT_MAPPING_FIX, RUNTIME_ABI_FIX, SOFTWARE_STACK_FIX, MEMORY_CONTRACT_FIX, RTL_FIX, GOLDEN_SIM_FIX, ARCHITECTURE_REFINEMENT]
failure_rules:
  missing_owner: UNROUTED_FAILURE
  direct_state_mutation: FORBIDDEN_REPAIR_ACTION
""",
}


TABLES = {
    "enum_table.yaml": """
table: enum_table
version: v4
enums:
  mode: [REPRODUCE, DESIGN, PATCH_REQUEST, TRACE_DEBUG]
  verdict: [ACCEPT, REJECT, REFINE_REQUIRED, INSUFFICIENT_EVIDENCE]
  architecture_preset: [MINIMAL_SIMT_CORE, MULTI_WARP_SINGLE_SM, MINIMAL_VERTICAL_SLICE_GPGPU]
  scheduler_policy: [ROUND_ROBIN, SCOREBOARD_ROUND_ROBIN]
  cache_policy: [NONE, DIRECT_MAPPED_L1]
  memory_space: [global, shared, local, constant]
failure_rule: unknown enum values must emit UNKNOWN_ENUM_REJECT
""",
    "provenance_table.yaml": """
table: provenance_table
version: v4
allowed:
  human_spec: [USER_SPEC, EXPLICIT_DEFAULT]
  synthesized: [USER_CONSTRAINT, DESIGN_PRESET, SOLVER_DERIVED, REPAIR_DERIVED]
forbidden: [UNKNOWN, COMMON_GPU_DEFAULT, MODEL_GUESS, IMPLICIT_DEFAULT]
failure_rule: forbidden provenance emits FORBIDDEN_PROVENANCE
""",
    "mode_decision_table.yaml": """
table: mode_decision_table
version: v4
decisions:
  - match: complete_spec
    mode: REPRODUCE
    next_skill: gpgpu-spec-lock
  - match: vague_design_goal
    mode: DESIGN
    next_skill: gpgpu-architecture-synthesizer
    requires_subpass: Design Intent Lock
  - match: vertical_slice_prototype_goal
    mode: DESIGN
    prototype_kind: VERTICAL_SLICE_PROTOTYPE
    next_skill: gpgpu-architecture-synthesizer
    required_targets: [compile_kernel_to_program_image, rtl_sim_smoke_test, memory_dump_golden_check]
  - match: patch_against_locked_ir
    mode: PATCH_REQUEST
    next_skill: gpgpu-closure-refinement-engine
  - match: trace_or_divergence
    mode: TRACE_DEBUG
    next_skill: gpgpu-closure-refinement-engine
forbidden_outputs: [warp_size, sm_count, cache_policy, scheduler_policy, isa_encoding, memory_hierarchy, register_file_size, rtl_pipeline]
""",
    "architecture_preset_library.yaml": """
table: architecture_preset_library
version: v4
presets:
  - preset_id: MINIMAL_SIMT_CORE
    description: Single SM, single resident warp, teaching-friendly integer SIMT core.
    parameters:
      sm_count: 1
      warp_size: 8
      max_warps_per_sm: 1
      scheduler_policy: ROUND_ROBIN
      issue_width: 1
      register_file:
        registers_per_thread: 16
        integer_width_bits: 32
      shared_memory:
        bytes_per_sm: 0
        banks: 0
      memory_hierarchy:
        cache_policy: NONE
        global_interface_bits: 32
      isa_profile: RV32I_SIMT_MINIMAL
      launch_abi: SIMPLE_MMIO_DOORBELL_V1
    provenance: DESIGN_PRESET
  - preset_id: MULTI_WARP_SINGLE_SM
    description: Single SM with multiple resident warps, scoreboard wakeup, and optional direct-mapped L1.
    parameters:
      sm_count: 1
      warp_size: 8
      max_warps_per_sm: 4
      scheduler_policy: SCOREBOARD_ROUND_ROBIN
      issue_width: 1
      register_file:
        registers_per_thread: 32
        integer_width_bits: 32
      shared_memory:
        bytes_per_sm: 4096
        banks: 4
      memory_hierarchy:
        cache_policy: DIRECT_MAPPED_L1
        global_interface_bits: 64
      isa_profile: RV32I_SIMT_BASE
      launch_abi: SIMPLE_MMIO_DOORBELL_V1
    provenance: DESIGN_PRESET
  - preset_id: MINIMAL_VERTICAL_SLICE_GPGPU
    description: Small end-to-end SIMT GPU prototype with CUDA-like frontend, assembler, program image, RTL simulation, and golden memory dump check.
    parameters:
      sm_count: 4
      allowed_sm_count: [1, 4]
      warp_size: 8
      max_warps_per_sm: 4
      scheduler_policy: ROUND_ROBIN
      issue_width: 1
      pipeline: IF_ID_EX_MEM_WB
      register_file:
        registers_per_thread: 32
        integer_width_bits: 32
      divergence: SIMT_STACK_JOIN
      memory_hierarchy:
        cache_policy: DIRECT_MAPPED_L1
        global_interface_bits: 64
        load_store_path: LDW_STW_GLOBAL_ONLY_FIRST
      frontend: PYTHON_CUDA_LIKE_SUBSET
      assembler: REQUIRED
      verilator_smoke: REQUIRED
      memory_dump_golden_check: REQUIRED
      isa_profile: VERTICAL_SLICE_SIMT_BASE
      launch_abi: SIMPLE_MMIO_DOORBELL_V1
    non_goals: [coherent_cache, full_cuda, virtual_memory, atomics_initially, tensor_core, dram_controller_accuracy]
    provenance: DESIGN_PRESET
unsupported_presets: [FPGA_SMALL_GPGPU, TENSOR_EXTENDED_GPGPU]
""",
    "minimal_vertical_slice_preset.yaml": """
table: minimal_vertical_slice_preset
version: v4
preset_id: MINIMAL_VERTICAL_SLICE_GPGPU
purpose: Small end-to-end SIMT GPU prototype.
default_parameters:
  sm_count: 4
  allowed_sm_count: [1, 4]
  warp_size: 8
  warps_per_sm: 4
  registers_per_thread: 32
  pipeline: IF_ID_EX_MEM_WB
  scheduler: ROUND_ROBIN
  divergence: SIMT_STACK_JOIN
  memory: GLOBAL_LOAD_STORE_ONLY_FIRST
  frontend: PYTHON_CUDA_LIKE_SUBSET
  assembler: REQUIRED
  verilator_smoke: REQUIRED
required_vertical_slice:
  - compile_kernel_to_program_image
  - rtl_sim_smoke_test
  - memory_dump_golden_check
non_goals:
  - coherent_cache
  - full_cuda
  - virtual_memory
  - atomics_initially
  - tensor_core
  - DRAM_controller_accuracy
""",
    "hard_constraint_table.yaml": """
table: hard_constraint_table
version: v4
constraints:
  - id: WARP_WIDTH_MATCHES_ACTIVE_MASK
    expression: warp_size == active_mask_width
    on_fail: HARD_CONSTRAINT_FAIL
  - id: ISSUE_WIDTH_PORT_LIMIT
    expression: issue_width <= execution_unit_ports
    on_fail: HARD_CONSTRAINT_FAIL
  - id: MEMORY_REQUEST_WIDTH_LIMIT
    expression: memory_request_width_bits <= global_interface_bits
    on_fail: HARD_CONSTRAINT_FAIL
  - id: WARP_SIZE_SUPPORTED
    expression: warp_size in [4, 8, 16, 32]
    on_fail: HARD_CONSTRAINT_FAIL
  - id: PRESET_SUPPORTS_REQUIRED_FEATURES
    expression: required_features subset_of preset.supported_features
    on_fail: UNSUPPORTED_REQUIREMENT
""",
    "quality_target_table.yaml": """
table: quality_target_table
version: v4
targets:
  teaching_minimal: {priority: clarity, ppa_weight: low, verification_weight: high}
  fpga_small: {priority: area, ppa_weight: high, verification_weight: high}
  research_prototype: {priority: extensibility, ppa_weight: medium, verification_weight: high}
""",
    "requirement_owner_table.yaml": """
table: requirement_owner_table
version: v4
owners:
  simt_execution: gpgpu-architecture-synthesizer
  launch_abi: gpgpu-spec-lock
  canonical_state: gpgpu-canonical-state-engine
  artifact_mapping: gpgpu-artifact-contract-engine
  runtime_launch: gpgpu-runtime-validator
  memory_ordering: gpgpu-memory-subsystem
  rtl_trace: gpgpu-implementation-validator
  closure_verdict: gpgpu-closure-refinement-engine
  source_of_truth_generation: gpgpu-spec-lock
  software_stack_contract: gpgpu-runtime-validator
  vertical_slice_validation: gpgpu-implementation-validator
""",
    "spec_required_field_table.yaml": """
table: spec_required_field_table
version: v4
required_fields:
  - isa.profile
  - isa.operation_classes
  - isa_source_of_truth.owner
  - isa_source_of_truth.generated_artifacts
  - warp_model.width
  - warp_model.active_mask_width
  - warp_model.reconvergence_model
  - thread_block_grid_model.grid_dim
  - thread_block_grid_model.block_dim
  - scheduler_policy.policy
  - scheduler_policy.issue_width
  - register_file.registers_per_thread
  - memory_hierarchy.address_spaces
  - memory_hierarchy.cache_policy
  - csr_dcr.registers
  - launch_abi.argument_layout
  - launch_abi.completion_path
  - config_defaults
failure_rule: missing required fields emit INSUFFICIENT_SPEC
""",
    "initial_state_construction_table.yaml": """
table: initial_state_construction_table
version: v4
constructors:
  warp_state: from SPEC_IR.warp_model and launch_state
  thread_state: from SPEC_IR.thread_block_grid_model
  pc_state: from SPEC_IR.launch_abi.kernel_entry
  active_mask_state: from SPEC_IR.warp_model.active_mask_width
  scheduler_state: from SPEC_IR.scheduler_policy
  scoreboard_state: empty at reset
  register_state: from SPEC_IR.register_file
  memory_request_state: empty outstanding table
  simt_stack_state: empty stack per warp
  csr_state: from SPEC_IR.csr_dcr
  launch_state: from SPEC_IR.launch_abi
  pipeline_state: reset state
  fault_state: no fault
""",
    "state_transition_rule_table.yaml": """
table: state_transition_rule_table
version: v4
rules:
  - rule_id: launch_admit
    consumes: [launch_state]
    produces: [warp_state, pc_state, active_mask_state]
  - rule_id: issue_instruction
    consumes: [scheduler_state, scoreboard_state, pc_state]
    produces: [pipeline_state, scoreboard_state]
  - rule_id: branch_update_mask
    consumes: [active_mask_state, pc_state]
    produces: [active_mask_state, pc_state]
  - rule_id: memory_request_issue
    consumes: [memory_request_state, active_mask_state, scoreboard_state]
    produces: [memory_request_state, scoreboard_state]
  - rule_id: memory_response_wakeup
    consumes: [memory_request_state, scoreboard_state]
    produces: [register_state, scoreboard_state]
  - rule_id: memory_stall_release
    consumes: [memory_request_state, scoreboard_state, pipeline_state]
    produces: [pipeline_state, scoreboard_state]
failure_rule: missing rule emits MISSING_TRANSITION_RULE
""",
    "state_invariant_table.yaml": """
table: state_invariant_table
version: v4
invariants:
  - id: active_mask_width_matches_warp_width
    expression: active_mask_state.mask_width == warp_state.warp_width
  - id: resident_warp_slots_match_spec
    expression: len(warp_state.resident_warps) <= SPEC_IR.scheduler_policy.max_warps_per_sm
  - id: scheduler_references_valid_warps
    expression: scheduler_state.eligible_warps subset_of warp_state.resident_warps
  - id: memory_request_tags_unique
    expression: unique(memory_request_state.request_tags)
  - id: simt_stack_depth_within_limit
    expression: simt_stack_state.depth <= SPEC_IR.warp_model.max_simt_stack_depth
  - id: duplicate_request_prevention
    expression: no_duplicate_serviced_request(memory_request_state.serviced_tracking)
""",
    "artifact_mapping_table.yaml": """
table: artifact_mapping_table
version: v4
coverage_rule: every GPU_STATE_IR field must be mapped or explicit_unused
artifacts: [rtl, sim, runtime, memory, config, validation, ppa]
fields:
  warp_state: [rtl, sim, validation]
  thread_state: [sim, runtime, validation]
  pc_state: [rtl, sim, validation]
  active_mask_state: [rtl, sim, validation]
  scheduler_state: [rtl, sim, validation]
  scoreboard_state: [rtl, sim, memory, validation]
  simt_stack_state: [rtl, sim, validation]
  register_state: [rtl, sim, validation]
  memory_request_state: [rtl, sim, memory, validation]
  csr_state: [rtl, runtime, sim, validation]
  launch_state: [runtime, rtl, sim, validation]
  pipeline_state: [rtl, sim, validation]
  fault_state: [runtime, rtl, sim, validation]
on_missing: MISSING_MAPPING_FAIL_CLOSED
""",
    "config_ownership_table.yaml": """
table: config_ownership_table
version: v4
parameters:
  warp_size: {owner: gpgpu-spec-lock, visibility: hw_sw_abi, consumers: [runtime, rtl, sim, validation]}
  max_warps_per_sm: {owner: gpgpu-spec-lock, visibility: hardware_private, consumers: [rtl, sim, validation]}
  trace_enable: {owner: gpgpu-artifact-contract-engine, visibility: debug_only, consumers: [validation]}
  simulator_seed: {owner: gpgpu-artifact-contract-engine, visibility: simulator_private, consumers: [sim]}
  test_timeout_cycles: {owner: gpgpu-artifact-contract-engine, visibility: test_only, consumers: [validation]}
  total_threads: {owner: gpgpu-runtime-validator, visibility: hw_sw_abi, consumers: [runtime, validation]}
  block_dim: {owner: gpgpu-runtime-validator, visibility: hw_sw_abi, consumers: [runtime, validation]}
  base_data_addr: {owner: gpgpu-runtime-validator, visibility: test_only, consumers: [runtime, validation]}
  base_a: {owner: gpgpu-runtime-validator, visibility: test_only, consumers: [runtime, validation]}
  base_b: {owner: gpgpu-runtime-validator, visibility: test_only, consumers: [runtime, validation]}
  base_c: {owner: gpgpu-runtime-validator, visibility: test_only, consumers: [runtime, validation]}
  memory_dump_range: {owner: gpgpu-implementation-validator, visibility: test_only, consumers: [validation]}
  finish_delay_cycles: {owner: gpgpu-implementation-validator, visibility: test_only, consumers: [rtl, validation]}
on_missing_owner: CONFIG_OWNER_MISSING
""",
    "state_to_rtl_mapping.yaml": """
table: state_to_rtl_mapping
version: v4
mappings:
  warp_state: rtl.warp_table
  pc_state: rtl.fetch_pc_file
  active_mask_state: rtl.mask_stack
  scheduler_state: rtl.scheduler
  scoreboard_state: rtl.scoreboard
  simt_stack_state: rtl.simt_stack
  register_state: rtl.register_file
  memory_request_state: rtl.lsu_interface
  csr_state: rtl.csr_file
  launch_state: rtl.launch_controller
  pipeline_state: rtl.pipeline_regs
  fault_state: rtl.fault_unit
explicit_unused: [thread_state]
""",
    "state_to_sim_mapping.yaml": """
table: state_to_sim_mapping
version: v4
mappings:
  warp_state: sim.warps
  thread_state: sim.threads
  pc_state: sim.pc
  active_mask_state: sim.active_mask
  scheduler_state: sim.scheduler
  scoreboard_state: sim.scoreboard
  simt_stack_state: sim.simt_stack
  register_state: sim.registers
  memory_request_state: sim.memory_events
  csr_state: sim.csr
  launch_state: sim.launch
  pipeline_state: sim.pipeline_model
  fault_state: sim.faults
""",
    "state_to_runtime_mapping.yaml": """
table: state_to_runtime_mapping
version: v4
mappings:
  thread_state: runtime.grid_block_thread_ids
  launch_state: runtime.launch_descriptor
  csr_state: runtime.mmio_csr
  fault_state: runtime.fault_status
explicit_unused: [warp_state, pc_state, active_mask_state, scheduler_state, scoreboard_state, simt_stack_state, register_state, memory_request_state, pipeline_state]
""",
    "state_to_memory_mapping.yaml": """
table: state_to_memory_mapping
version: v4
mappings:
  warp_state: memory.lane_context
  active_mask_state: memory.lane_mask
  scoreboard_state: memory.scoreboard_wakeup
  memory_request_state: memory.request_table
  fault_state: memory.fault_contract
explicit_unused: [thread_state, pc_state, scheduler_state, simt_stack_state, register_state, csr_state, launch_state, pipeline_state]
""",
    "runtime_smoke_test_table.yaml": """
table: runtime_smoke_test_table
version: v4
tests:
  - valid_kernel_launch_pass
  - invalid_argument_layout_reject
  - grid_dim_mismatch_reject
  - missing_completion_path_reject
  - fault_reporting_contract_pass
  - app_compile_smoke
  - assembler_smoke
  - program_hex_load_smoke
  - memory_dump_compare
""",
    "software_stack_contract_table.yaml": """
table: software_stack_contract_table
version: v4
contracts:
  frontend_subset_contract:
    required: [threadIdx.x, blockIdx.x, blockDim.x, gridDim.x, if, for, integer_arithmetic, global_load_store]
    forbidden: [full_cuda, dynamic_parallelism, inline_asm_initially]
  assembler_contract:
    source_of_truth: SPEC_IR.isa
    required_outputs: [assembly_listing, program_hex, symbol_map]
  program_image_contract:
    required_fields: [entry_symbol, text_base, data_base, hex_word_width, loader_endianness]
  kernel_test_app_contract:
    required_fields: [compile_or_generate_step, input_data_layout, output_data_layout, runner_binding]
  golden_output_contract:
    required_fields: [checker_entrypoint, output_region, comparison_policy, tolerance_policy]
failure_rules:
  app_compile_fail: APP_COMPILE_FAIL
  mapping_mismatch: FRONTEND_RUNTIME_MAPPING_MISMATCH
  memory_dump_mismatch: MEMORY_DUMP_CONTRACT_MISMATCH
""",
    "source_of_truth_generation_table.yaml": """
table: source_of_truth_generation_table
version: v4
generation_rules:
  isa.opcodes:
    source: SPEC_IR.isa.opcodes
    derived_artifacts:
      - rtl/defines.svh
      - tools/isa.py
      - tools/assembler.py opcode table
      - tools/disassembler.py opcode table
      - docs/isa.md
    gate: byte_or_semantic_equivalence_required
  hardware_threads:
    source: SPEC_IR.thread_block_grid_model
    derived_artifacts:
      - compiler total_threads
      - runtime gridDim calculation
      - test expected output length
      - memory dump length
    gate: semantic_equivalence_required
truth_source_rules:
  - docs cannot be the truth source
  - rtl defines cannot be the truth source
  - tool opcode tables cannot be the truth source
failure_rules:
  drift: SOURCE_OF_TRUTH_DRIFT
  isa_encoding_drift: ISA_ENCODING_DRIFT
""",
    "cross_artifact_consistency_table.yaml": """
table: cross_artifact_consistency_table
version: v4
gates:
  isa_opcode_equivalence:
    source: SPEC_IR.isa
    artifacts: [tools/isa.py, rtl/defines.svh, tools/assembler.py, tools/disassembler.py, docs/isa.md]
    failure: ISA_ENCODING_DRIFT
  hardware_thread_count_equivalence:
    source: SPEC_IR.thread_block_grid_model
    artifacts: [frontend total_threads, runtime grid_dim, test_expected_length, memory_dump_range]
    failure: FRONTEND_RUNTIME_MAPPING_MISMATCH
  declared_test_coverage_gate:
    declared_sources: [README.md, VALIDATION_PLAN_IR, docs]
    runner_sources: [tests/test_suite.py, build scripts]
    required: [declared, in_runner, compile_or_generate_pass]
    failure: DECLARED_TEST_NOT_RUN
  magic_constant_binding:
    artifacts: [compiler, apps, tests, rtl_top, sim_harness]
    required_binding: CONFIG_BINDING_IR
    failure: MAGIC_CONSTANT_UNBOUND
""",
    "end_to_end_smoke_test_table.yaml": """
table: end_to_end_smoke_test_table
version: v4
ladder:
  T0_instruction_smoke:
    required_features: [fetch, decode, execute, writeback]
    expected_observable: [single_instruction_trace]
    owner_skill: [gpgpu-implementation-validator]
  T1_thread_id:
    required_features: [TID, WARPID, SMID, global_thread_id_mapping]
    expected_observable: [output_i_equals_global_id]
    owner_skill: [gpgpu-runtime-validator, gpgpu-implementation-validator]
  T2_load_store:
    required_features: [LDW, STW, global_memory_path]
    expected_observable: [memory_dump_changed_region]
    owner_skill: [gpgpu-memory-subsystem, gpgpu-implementation-validator]
  T3_loop:
    required_features: [branch, loop_counter, pc_update]
    expected_observable: [multi_iteration_trace]
    owner_skill: [gpgpu-implementation-validator]
  T4_divergence:
    required_features: [branch, active_mask, simt_stack, join]
    expected_observable: [per_lane_result_diff, reconverged_final_store]
    owner_skill: [gpgpu-canonical-state-engine, gpgpu-implementation-validator]
  T5_vector_arithmetic:
    required_features: [integer_alu, global_load_store]
    expected_observable: [vecadd_or_vecmul_matches_golden]
    owner_skill: [gpgpu-runtime-validator, gpgpu-implementation-validator]
  T6_matrix_multiply:
    required_features: [nested_loop, memory_stride, arithmetic_pipeline]
    expected_observable: [matmul_matches_golden]
    owner_skill: [gpgpu-implementation-validator]
  T7_memory_stress:
    required_features: [stall, miss, backpressure, scoreboard_wakeup]
    expected_observable: [no_duplicate_memory_request, wakeup_after_response]
    owner_skill: [gpgpu-memory-subsystem]
  T8_special_unit:
    required_features: [fp_or_extension_unit]
    expected_observable: [extension_test_declared_and_run]
    owner_skill: [gpgpu-implementation-validator, gpgpu-closure-refinement-engine]
""",
    "vertical_slice_validation_table.yaml": """
table: vertical_slice_validation_table
version: v4
tests:
  debug_gid_test:
    app: apps/debug_gid.py
    expected_feature: [TID, WARPID, SMID, global_thread_id_mapping]
    required_artifacts: [program.hex, rtl_sim_trace, memory_dump]
    pass_condition: output[i] == i
  load_store_test:
    app: apps/load_store.py
    expected_feature: [LDW, STW, memory_dump_contract]
    required_artifacts: [program.hex, rtl_sim_trace, memory_dump]
    pass_condition: loaded_values_match_input
  divergence_test:
    app: apps/divergence.py
    expected_feature: [active_mask, simt_stack, join]
    required_artifacts: [program.hex, rtl_sim_trace, memory_dump]
    pass_condition: reconverged_final_store_matches_golden
  vecmul_test:
    app: apps/vecmul.py
    expected_feature: [integer_mul, global_load_store]
    required_artifacts: [program.hex, rtl_sim_trace, memory_dump]
    pass_condition: output_matches_python_golden
required_smokes:
  - app_compile_smoke
  - assembler_smoke
  - program_hex_load_smoke
  - rtl_sim_smoke
  - memory_dump_compare
  - waveform_or_trace_required
""",
    "memory_address_space_table.yaml": """
table: memory_address_space_table
version: v4
spaces:
  global: {coalesced: true, ordered_by: fence, faultable: true}
  shared: {coalesced: false, banked: true, faultable: false}
  local: {coalesced: false, per_thread: true, faultable: true}
  constant: {coalesced: true, read_only: true, faultable: true}
""",
    "coalescing_rule_table.yaml": """
table: coalescing_rule_table
version: v4
rules:
  - id: coalesced_global_load
    address_space: global
    condition: contiguous_active_lanes_same_segment
    result: single_transaction
  - id: partial_lane_mask_store
    address_space: global
    condition: inactive_lanes_present
    result: byte_enable_from_active_mask
  - id: divergent_addresses
    address_space: global
    condition: multiple_segments
    result: split_transactions
""",
    "shared_memory_bank_table.yaml": """
table: shared_memory_bank_table
version: v4
bank_model:
  bank_count_field: MEMORY_MODEL_IR.shared_memory_banks
  bank_index: (address / word_bytes) % bank_count
  conflict_policy: detect_and_serialize
  broadcast_policy: same_address_no_conflict
""",
    "memory_ordering_table.yaml": """
table: memory_ordering_table
version: v4
rules:
  - id: fence_orders_prior_global_ops
    before: [global_load, global_store, atomic]
    after: [fence]
  - id: same_thread_program_order
    scope: thread
    ordered: true
  - id: different_warps_unordered_without_fence
    scope: warp
    ordered: false
""",
    "memory_scoreboard_wakeup_table.yaml": """
table: memory_scoreboard_wakeup_table
version: v4
wakeups:
  load_response: {matches: request_tag, action: clear_destination_register_pending}
  atomic_response: {matches: request_tag, action: write_result_and_clear_pending}
  store_ack: {matches: request_tag, action: clear_store_slot}
  memory_fault: {matches: request_tag, action: poison_destination_and_raise_fault}
request_lifecycle:
  issue_condition: instruction_valid and active_mask_nonzero and scoreboard_allows_issue
  outstanding_tracking: request_tag plus warp_id plus instruction_id
  replay_or_serviced_policy: do_not_duplicate_serviced_request
  response_match_policy: response_tag matches outstanding_request.tag
  scoreboard_wakeup_condition: matching load_or_atomic_response_valid
  duplicate_request_prevention: serviced_tracking_required_on_pipeline_stall
  stall_release_condition: response_matched or fault_recorded
""",
    "rtl_validation_gate_table.yaml": """
table: rtl_validation_gate_table
version: v4
gates:
  - fetch_decode_issue_execute_writeback
  - warp_scheduler_policy
  - active_mask_update
  - branch_reconvergence
  - scoreboard_stall_wakeup
  - register_read_write
  - csr_access
  - pipeline_stall_flush
  - memory_request_interface
""",
    "golden_sim_trace_field_table.yaml": """
table: golden_sim_trace_field_table
version: v4
mandatory_fields:
  - cycle
  - warp_id
  - pc
  - instruction
  - active_mask
  - issued
  - scoreboard_state
  - register_writes
  - memory_request
  - fault
""",
    "first_divergence_taxonomy.yaml": """
table: first_divergence_taxonomy
version: v4
classes:
  ACTIVE_MASK_DIVERGENCE: {affected_state_field: warp_state.active_mask, owner: gpgpu-implementation-validator}
  PC_DIVERGENCE: {affected_state_field: pc_state.per_warp_pc, owner: gpgpu-implementation-validator}
  SCOREBOARD_DIVERGENCE: {affected_state_field: scoreboard_state, owner: gpgpu-implementation-validator}
  MEMORY_TAG_DIVERGENCE: {affected_state_field: memory_request_state.request_tags, owner: gpgpu-memory-subsystem}
  ABI_DIVERGENCE: {affected_state_field: launch_state, owner: gpgpu-runtime-validator}
""",
    "closure_gate_table.yaml": """
table: closure_gate_table
version: v4
gates:
  - requirement_coverage
  - spec_lock
  - state_invariants
  - artifact_mapping
  - cross_artifact_consistency_gate
  - declared_test_coverage_gate
  - runtime_validation
  - memory_validation
  - implementation_validation
  - vertical_slice_validation
  - ppa
  - stability
hard_correctness_gates: [spec_lock, state_invariants, artifact_mapping, cross_artifact_consistency_gate, declared_test_coverage_gate, runtime_validation, memory_validation, implementation_validation, vertical_slice_validation]
""",
    "verdict_decision_table.yaml": """
table: verdict_decision_table
version: v4
decisions:
  - condition: all_gates_pass
    verdict: ACCEPT
  - condition: missing_required_evidence
    verdict: INSUFFICIENT_EVIDENCE
  - condition: hard_correctness_gate_failed
    verdict: REJECT
  - condition: repairable_trace_failure
    verdict: REFINE_REQUIRED
allowed_verdicts: [ACCEPT, REJECT, REFINE_REQUIRED, INSUFFICIENT_EVIDENCE]
""",
    "failure_taxonomy_table.yaml": """
table: failure_taxonomy_table
version: v4
failures:
  active_mask_divergence: {field: warp_state.active_mask, category: trace_correctness}
  missing_mapping: {field: artifact_mapping, category: contract_coverage}
  hidden_default: {field: spec_ir.provenance, category: spec_correctness}
  memory_tag_mismatch: {field: memory_request_state.request_tags, category: memory_correctness}
  invalid_argument_layout: {field: launch_state.argument_layout, category: runtime_abi}
  DOC_ARTIFACT_DRIFT: {field: docs_vs_generated_artifacts, category: source_of_truth_consistency}
  ISA_ENCODING_DRIFT: {field: SPEC_IR.isa, category: source_of_truth_consistency}
  DECLARED_TEST_NOT_RUN: {field: VALIDATION_PLAN_IR.declared_test_coverage_gate, category: validation_coverage}
  APP_COMPILE_FAIL: {field: TEST_APP_CONTRACT_IR.compile_or_generate_step, category: software_stack}
  MAGIC_CONSTANT_UNBOUND: {field: CONFIG_BINDING_IR.parameters, category: config_binding}
  FRONTEND_RUNTIME_MAPPING_MISMATCH: {field: RUNTIME_CONTRACT_IR.grid_block_contract, category: runtime_abi}
  MEMORY_DUMP_CONTRACT_MISMATCH: {field: TEST_APP_CONTRACT_IR.memory_dump_contract, category: validation_output}
""",
    "vibe_failure_taxonomy_table.yaml": """
table: vibe_failure_taxonomy_table
version: v4
failure_types:
  DOC_ARTIFACT_DRIFT:
    failed_gate: cross_artifact_consistency_gate
    repair_owner_skill: gpgpu-artifact-contract-engine
    secondary_owner_skill: gpgpu-spec-lock
  ISA_ENCODING_DRIFT:
    failed_gate: cross_artifact_consistency_gate
    repair_owner_skill: gpgpu-spec-lock
    secondary_owner_skill: gpgpu-artifact-contract-engine
  DECLARED_TEST_NOT_RUN:
    failed_gate: declared_test_coverage_gate
    repair_owner_skill: gpgpu-implementation-validator
    secondary_owner_skill: gpgpu-artifact-contract-engine
  APP_COMPILE_FAIL:
    failed_gate: declared_test_coverage_gate
    repair_owner_skill: gpgpu-runtime-validator
    secondary_owner_skill: gpgpu-artifact-contract-engine
  MAGIC_CONSTANT_UNBOUND:
    failed_gate: config_binding
    repair_owner_skill: gpgpu-artifact-contract-engine
    secondary_owner_skill: gpgpu-runtime-validator
  FRONTEND_RUNTIME_MAPPING_MISMATCH:
    failed_gate: runtime_validation
    repair_owner_skill: gpgpu-runtime-validator
    secondary_owner_skill: gpgpu-front-end
  MEMORY_DUMP_CONTRACT_MISMATCH:
    failed_gate: vertical_slice_validation
    repair_owner_skill: gpgpu-implementation-validator
    secondary_owner_skill: gpgpu-runtime-validator
example:
  failure_type: APP_COMPILE_FAIL
  failed_gate: declared_test_coverage_gate
  affected_artifact: apps/app_fp8_test.py
  root_cause: assembler_api_missing_program_id
  repair_owner_skill: gpgpu-runtime-validator
  secondary_owner_skill: gpgpu-artifact-contract-engine
""",
    "repair_routing_table.yaml": """
table: repair_routing_table
version: v4
routes:
  active_mask_divergence: {owner: gpgpu-implementation-validator, repair_type: RTL_FIX}
  missing_mapping: {owner: gpgpu-artifact-contract-engine, repair_type: ARTIFACT_MAPPING_FIX}
  hidden_default: {owner: gpgpu-spec-lock, repair_type: SPEC_FIELD_FIX}
  memory_tag_mismatch: {owner: gpgpu-memory-subsystem, repair_type: MEMORY_CONTRACT_FIX}
  invalid_argument_layout: {owner: gpgpu-runtime-validator, repair_type: RUNTIME_ABI_FIX}
  DOC_ARTIFACT_DRIFT: {owner: gpgpu-artifact-contract-engine, repair_type: ARTIFACT_MAPPING_FIX}
  ISA_ENCODING_DRIFT: {owner: gpgpu-spec-lock, repair_type: SPEC_FIELD_FIX}
  DECLARED_TEST_NOT_RUN: {owner: gpgpu-implementation-validator, repair_type: RTL_FIX}
  APP_COMPILE_FAIL: {owner: gpgpu-runtime-validator, repair_type: SOFTWARE_STACK_FIX}
  MAGIC_CONSTANT_UNBOUND: {owner: gpgpu-artifact-contract-engine, repair_type: ARTIFACT_MAPPING_FIX}
  FRONTEND_RUNTIME_MAPPING_MISMATCH: {owner: gpgpu-runtime-validator, repair_type: RUNTIME_ABI_FIX}
  MEMORY_DUMP_CONTRACT_MISMATCH: {owner: gpgpu-implementation-validator, repair_type: RTL_FIX}
""",
}


TEST_CASES = {
    "front_end": ["complete_spec_routes_to_reproduce", "vague_goal_routes_to_design_intent_lock", "vertical_slice_prototype_routes_to_design", "patch_request_routes_to_patch", "trace_failure_routes_to_trace_debug", "forbidden_architecture_field_rejected_in_intent"],
    "architecture_synthesizer": ["minimal_simt_candidate_pass", "multi_warp_single_sm_candidate_pass", "minimal_vertical_slice_candidate_pass", "unsupported_feature_reject", "hard_constraint_fail_reject", "candidate_not_spec_ir"],
    "spec_lock": ["complete_spec_pass", "isa_source_of_truth_lock_pass", "source_of_truth_drift_reject", "missing_warp_size_reject", "hidden_default_reject", "unknown_enum_reject", "forbidden_provenance_reject", "conflicting_spec_field_reject", "canonical_hash_stable"],
    "state_engine": ["minimal_simt_initial_state_pass", "trace_diffable_state_fields_pass", "active_mask_width_matches_warp_width", "resident_warp_slots_match_spec", "invalid_scheduler_state_reject", "missing_transition_rule_reject"],
    "artifact_contract": ["all_state_fields_mapped_pass", "cross_artifact_consistency_pass", "declared_test_coverage_gate_pass", "missing_mapping_fail_closed", "config_owner_missing_reject", "abi_field_reinterpreted_reject", "debug_only_leaks_to_abi_reject", "magic_constant_unbound_reject"],
    "runtime_validator": ["valid_kernel_launch_pass", "software_stack_contract_pass", "program_image_contract_pass", "invalid_argument_layout_reject", "grid_dim_mismatch_reject", "missing_completion_path_reject", "app_compile_fail_reject", "fault_reporting_contract_pass"],
    "memory_subsystem": ["coalesced_global_load_pass", "partial_lane_mask_store_pass", "shared_memory_bank_conflict_detected", "load_response_wakes_scoreboard", "memory_request_lifecycle_pass", "duplicate_memory_request_reject", "fence_ordering_pass", "request_tag_mismatch_reject"],
    "implementation_validator": ["single_warp_integer_trace_pass", "branch_active_mask_trace_pass", "scoreboard_stall_trace_pass", "vertical_slice_smoke_pass", "memory_dump_compare_pass", "declared_test_not_run_reject", "rtl_golden_first_divergence_detected", "golden_sim_redefines_isa_reject"],
    "closure_refinement": ["all_gates_pass_accept", "missing_evidence_insufficient", "hard_correctness_fail_reject", "repairable_trace_fail_refine_required", "doc_artifact_drift_reject", "declared_test_not_run_reject", "failure_routed_to_correct_owner_skill"],
}


def render_skill(name, spec):
    return f"""
---
name: {name}
description: {spec['description']}
---

# {spec['title']}

## Role

{spec['role']}

## Position in Flow

Upstream:
{bullets(spec['upstream'])}

Downstream:
{bullets(spec['downstream'])}

## Input IR

Consumes:
{bullets(spec['inputs'])}

## Output IR

Produces:
{bullets(spec['outputs'])}

## Owned Decisions

This skill owns:
{bullets(spec['owned'])}

## Forbidden Actions

This skill must not:
{bullets(spec['forbidden'])}

## Required Tables

This skill must use:
{bullets(spec['tables'])}

## Required Schemas

This skill must validate:
{bullets(spec['schemas'])}

## Required Invariants

The output must satisfy:
{bullets(spec['invariants'])}

## Failure Modes

This skill must emit:
{bullets(spec['failures'])}

## Report Schema

The report must include:
{bullets(spec['report'])}

## Concrete Assets Required

This skill is incomplete unless the following exist:
{bullets(spec['assets'])}

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
"""


def render_subpass(title, body):
    return f"""
# {title}

## Purpose

{body}

## Required Inputs

- Upstream IR named in `SKILL.md`
- Required schema assets
- Required table assets

## Output Contract

- Emit only the IR/report fields owned by the parent skill.
- Preserve consumed IR hashes.
- Record failed fields and missing assets.

## Fail Closed Rule

If a required schema row, table row, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET`. If a field is ambiguous or unsupported, reject instead of inferring.
"""


def generate_skills():
    for name, spec in SKILLS.items():
        write(ROOT / name / "SKILL.md", render_skill(name, spec))
        for filename, (title, body) in spec["subpasses"].items():
            write(ROOT / name / filename, render_subpass(title, body))


def generate_schemas():
    for filename, text in SCHEMAS.items():
        write(ROOT / "shared" / "schemas" / filename, text)


def generate_tables():
    for filename, text in TABLES.items():
        write(ROOT / "shared" / "tables" / filename, text)


def generate_tests():
    for dirname, cases in TEST_CASES.items():
        text = "suite: " + dirname + "\nversion: v4\ncases:\n"
        for case in cases:
            if "pass" in case or case == "canonical_hash_stable" or case == "fault_reporting_contract_pass" or case == "failure_routed_to_correct_owner_skill":
                expected = "PASS"
            elif "insufficient" in case:
                expected = "INSUFFICIENT_EVIDENCE"
            elif "refine" in case or "conflict_detected" in case or "divergence_detected" in case:
                expected = "REFINE_REQUIRED"
            else:
                expected = "REJECT"
            text += f"  - id: {case}\n    input: fixtures/{case}.yaml\n    expected_verdict: {expected}\n"
        text += "common_reject_rules:\n  - missing field must not be invented\n  - hidden default must be rejected\n  - forbidden inference must be rejected\n  - conflicts must fail closed\n"
        write(ROOT / "shared" / "tests" / dirname / "cases.yaml", text)


def generate_examples():
    rep = ROOT / "shared" / "examples" / "reproduce_minimal_simt"
    write(rep / "input_spec.md", """
# Minimal SIMT Complete Spec

Design identity: minimal-simt-v4
Source kind: HUMAN_SPEC

- ISA profile: RV32I_SIMT_MINIMAL
- Operation classes: integer ALU, branch, global load, global store, CSR
- Warp width: 8
- Active mask width: 8
- Reconvergence model: stackless single-path teaching model
- SM count: 1
- Max resident warps per SM: 1
- Scheduler policy: ROUND_ROBIN
- Issue width: 1
- Register file: 16 x 32-bit registers per thread
- Address spaces: global, local, constant
- Shared memory: disabled
- Cache policy: NONE
- Launch ABI: SIMPLE_MMIO_DOORBELL_V1
- Completion path: done CSR
- Fault path: fault CSR

Every field above is explicit. No hidden defaults are allowed.
""")
    write(rep / "expected_spec_ir.yaml", """
schema_version: v4
design_identity: minimal-simt-v4
source_kind: HUMAN_SPEC
isa: {profile: RV32I_SIMT_MINIMAL, operation_classes: [integer_alu, branch, global_load, global_store, csr], encoding_policy: fixed32}
isa_source_of_truth:
  owner: SPEC_IR.isa
  generated_artifacts: [rtl/defines.svh, tools/isa.py, tools/assembler.py opcode table, tools/disassembler.py opcode table, docs/isa.md]
  generation_table: shared/tables/source_of_truth_generation_table.yaml
warp_model: {width: 8, active_mask_width: 8, reconvergence_model: stackless_single_path}
thread_block_grid_model: {grid_dim: [1, 1, 1], block_dim: [8, 1, 1]}
scheduler_policy: {policy: ROUND_ROBIN, issue_width: 1, max_warps_per_sm: 1}
register_file: {registers_per_thread: 16, integer_width_bits: 32}
memory_hierarchy: {address_spaces: [global, local, constant], cache_policy: NONE, shared_memory: disabled}
csr_dcr: {registers: [start, done, fault, kernel_entry]}
launch_abi: {abi_version: SIMPLE_MMIO_DOORBELL_V1, argument_layout: flat32, completion_path: done_csr, fault_path: fault_csr}
config_defaults: {trace_enable: false}
debug_test_hooks: {trace_schema: v4_minimal}
provenance: USER_SPEC
canonical_hash: expected-stable-spec-hash
""")
    write(rep / "expected_gpu_state_ir.yaml", """
schema_version: v4
design_identity: minimal-simt-v4
source_spec_hash: expected-stable-spec-hash
warp_state:
  resident_warps: [0]
  warp_width: 8
  per_warp_status: {0: reset}
  pc_table: {0: kernel_entry}
  exec_mask_table: {0: "11111111"}
  warp_active: "00000001"
  warp_halted: "00000000"
thread_state: {thread_ids: [0,1,2,3,4,5,6,7], block_ids: [0], grid_ids: [0]}
pc_state: {per_warp_pc: {0: kernel_entry}}
active_mask_state: {mask_width: 8, per_warp_active_mask: {0: "11111111"}}
scheduler_state: {policy: ROUND_ROBIN, eligible_warps: [0], selected_warp: null, current_fetch_warp: 0, next_fetch_warp: 0}
scoreboard_state: {pending_registers: [], register_pending: {0: []}, wakeup_events: []}
simt_stack_state: {entries: [], depth: 0}
register_state: {register_file_size: 16, per_thread_registers: zeroed}
memory_request_state: {outstanding_requests: [], request_tags: [], lane_masks: [], serviced_tracking: []}
csr_state: {start: 0, done: 0, fault: 0, kernel_entry: null}
launch_state: {grid_dim: [1,1,1], block_dim: [8,1,1], kernel_entry: null, completion: pending, fault: none}
pipeline_state: {pipeline_registers: reset, memory_stall_state: none, performance_counters: zeroed}
fault_state: none
canonical_hash: expected-stable-state-hash
""")
    for filename, verdict in [
        ("expected_artifact_contract_report.yaml", "PASS"),
        ("expected_runtime_report.yaml", "PASS"),
        ("expected_memory_report.yaml", "PASS"),
        ("expected_implementation_report.yaml", "PASS"),
        ("expected_closure_report.yaml", "ACCEPT"),
    ]:
        write(rep / filename, f"schema_version: v4\nverdict: {verdict}\nconsumed_ir_hash: expected-stable-state-hash\nfailed_fields: []\nmissing_assets: []\n")

    des = ROOT / "shared" / "examples" / "design_minimal_teaching_gpgpu"
    write(des / "input_request.md", """
Design a minimal teaching GPGPU that can be simulated in RTL, runs a single integer SIMT warp, has an explicit launch ABI, and rejects hidden defaults.
""")
    write(des / "expected_design_intent_ir.yaml", """
schema_version: v4
intent_id: design-minimal-teaching-gpgpu
objective: minimal RTL-simulatable teaching GPGPU
non_goals: [multi_sm_scaling, tensor_units, production_cache_hierarchy]
workload_profile: {kernels: [integer_vector_add], control_flow: simple_branching}
target_platform: TEACHING
hard_constraints: [rtl_simulatable, explicit_launch_abi, no_hidden_defaults]
soft_constraints: [small_area, easy_trace_debug]
required_features: [simt_execution, integer_alu, global_load_store, launch_completion]
optional_features: [shared_memory]
validation_target: [single_warp_integer_trace_pass, valid_kernel_launch_pass]
prototype_kind: VERTICAL_SLICE_PROTOTYPE
prototype_credibility_target: [compile_kernel_to_program_image, rtl_sim_smoke_test, memory_dump_golden_check]
provenance: USER_CONSTRAINT
""")
    write(des / "expected_arch_candidate_ir.yaml", """
schema_version: v4
candidate_id: minimal-teaching-candidate-001
source_intent_hash: expected-design-intent-hash
selected_preset: MINIMAL_SIMT_CORE
parameter_set: {sm_count: 1, warp_size: 8, max_warps_per_sm: 1, scheduler_policy: ROUND_ROBIN, issue_width: 1}
requirement_coverage_matrix: {simt_execution: covered, launch_completion: covered, multi_sm_scaling: non_goal}
constraint_proof: {WARP_WIDTH_MATCHES_ACTIVE_MASK: pass, ISSUE_WIDTH_PORT_LIMIT: pass}
quality_estimate: {area: low, verification_effort: low}
rejected_alternatives: [MULTI_WARP_SINGLE_SM]
unresolved_risks: []
provenance: DESIGN_PRESET
""")
    write(des / "expected_synthesized_spec_draft.yaml", """
schema_version: v4
draft_id: minimal-teaching-draft-001
source_candidate_id: minimal-teaching-candidate-001
completeness_claim: COMPLETE_FOR_SPEC_LOCK
unresolved_fields: []
provenance: [USER_CONSTRAINT, DESIGN_PRESET, SOLVER_DERIVED]
""")
    write(des / "expected_spec_ir.yaml", "include: ../reproduce_minimal_simt/expected_spec_ir.yaml\nsource_kind: SYNTHESIZED_SPEC_DRAFT\n")
    write(des / "expected_gpu_state_ir.yaml", "include: ../reproduce_minimal_simt/expected_gpu_state_ir.yaml\n")
    write(des / "expected_closure_report.yaml", "schema_version: v4\nverdict: ACCEPT\ngate_results: {requirement_coverage: pass, spec_lock: pass, state_invariants: pass, artifact_mapping: pass, cross_artifact_consistency_gate: pass, declared_test_coverage_gate: pass, runtime_validation: pass, memory_validation: pass, implementation_validation: pass, vertical_slice_validation: pass, ppa: pass, stability: pass}\n")

    vibe = ROOT / "shared" / "examples" / "vibe_minimal_vertical_slice"
    write(vibe / "input_request.md", """
# Vibe-Inspired Minimal Vertical Slice

Build the smallest GPGPU prototype that can run a CUDA-like Python kernel through a compiler frontend, assembler, program.hex image, RTL simulation, memory dump, and Python golden checker.

Required credibility target:
- compile_kernel_to_program_image
- rtl_sim_smoke_test
- memory_dump_golden_check
""")
    write(vibe / "expected_design_intent_ir.yaml", """
schema_version: v4
intent_id: vibe-minimal-vertical-slice
objective: runnable end-to-end SIMT GPGPU prototype
non_goals: [full_cuda, coherent_cache, virtual_memory, atomics_initially, tensor_core, dram_controller_accuracy]
workload_profile: {kernels: [debug_gid, load_store, divergence, vecmul], control_flow: loops_and_simple_divergence}
target_platform: SIMULATION_ONLY
hard_constraints: [compile_kernel_to_program_image, rtl_sim_smoke_test, memory_dump_golden_check, no_hidden_defaults]
soft_constraints: [small_rtl, easy_trace_debug, single_repo_flow]
required_features: [cuda_like_frontend_subset, assembler, program_hex, simt_stack_join, global_load_store, memory_dump_golden_check]
optional_features: [matmul_smoke]
validation_target: [debug_gid_test, load_store_test, divergence_test, vecmul_test]
prototype_kind: VERTICAL_SLICE_PROTOTYPE
prototype_credibility_target: [compile_kernel_to_program_image, rtl_sim_smoke_test, memory_dump_golden_check]
provenance: USER_CONSTRAINT
""")
    write(vibe / "expected_arch_candidate_ir.yaml", """
schema_version: v4
candidate_id: vibe-minimal-vertical-slice-candidate-001
source_intent_hash: expected-vibe-intent-hash
selected_preset: MINIMAL_VERTICAL_SLICE_GPGPU
parameter_set:
  sm_count: 4
  warp_size: 8
  max_warps_per_sm: 4
  scheduler_policy: ROUND_ROBIN
  issue_width: 1
  pipeline: IF_ID_EX_MEM_WB
  register_file: {registers_per_thread: 32, integer_width_bits: 32}
  divergence: SIMT_STACK_JOIN
  memory_hierarchy: {cache_policy: DIRECT_MAPPED_L1, global_interface_bits: 64, load_store_path: LDW_STW_GLOBAL_ONLY_FIRST}
  frontend: PYTHON_CUDA_LIKE_SUBSET
  assembler: REQUIRED
  verilator_smoke: REQUIRED
requirement_coverage_matrix:
  compile_kernel_to_program_image: covered
  rtl_sim_smoke_test: covered
  memory_dump_golden_check: covered
  full_cuda: non_goal
constraint_proof: {WARP_WIDTH_MATCHES_ACTIVE_MASK: pass, MEMORY_REQUEST_WIDTH_LIMIT: pass, PRESET_SUPPORTS_REQUIRED_FEATURES: pass}
quality_estimate: {area: low, verification_effort: medium, end_to_end_credibility: high}
rejected_alternatives: [MINIMAL_SIMT_CORE, MULTI_WARP_SINGLE_SM]
unresolved_risks: [limited_frontend_subset, simplified_memory_model]
provenance: DESIGN_PRESET
""")
    write(vibe / "expected_spec_ir.yaml", """
schema_version: v4
design_identity: vibe-minimal-vertical-slice
source_kind: SYNTHESIZED_SPEC_DRAFT
isa:
  profile: VERTICAL_SLICE_SIMT_BASE
  operation_classes: [integer_alu, branch, join, global_load, global_store, csr, thread_id]
  encoding_policy: fixed32
  opcodes: {LDI: 0x03, MUL: 0x07, FADD: 0x08, FMUL: 0x09, WARPID: 0x14, BEQ: 0x20, BNE: 0x21, JOIN: 0x22}
isa_source_of_truth:
  owner: SPEC_IR.isa
  generated_artifacts: [rtl/defines.svh, tools/isa.py, tools/assembler.py opcode table, tools/disassembler.py opcode table, docs/isa.md]
  generation_table: shared/tables/source_of_truth_generation_table.yaml
warp_model: {width: 8, active_mask_width: 8, reconvergence_model: SIMT_STACK_JOIN, max_simt_stack_depth: 8}
thread_block_grid_model: {sm_count: 4, grid_dim: [4,1,1], block_dim: [32,1,1], total_threads: 128}
scheduler_policy: {policy: ROUND_ROBIN, issue_width: 1, max_warps_per_sm: 4}
register_file: {registers_per_thread: 32, integer_width_bits: 32}
memory_hierarchy:
  address_spaces: [global]
  global_memory: {word_bytes: 4, interface_bits: 64}
  shared_memory: disabled
  local_memory: disabled_initially
  constant_memory: disabled_initially
  cache_policy: DIRECT_MAPPED_L1
csr_dcr: {registers: [start, done, fault, kernel_entry, grid_dim, block_dim]}
launch_abi: {abi_version: SIMPLE_MMIO_DOORBELL_V1, argument_layout: flat32, grid_dim_fields: [x,y,z], block_dim_fields: [x,y,z], completion_path: done_csr, fault_path: fault_csr}
config_defaults: {total_threads: 128, block_dim: 32, base_data_addr: 1024, base_c: 2560, memory_dump_range: [2560, 3072], finish_delay_cycles: 16}
debug_test_hooks: {trace_schema: vertical_slice_v1, memory_dump: required, waveform: optional}
provenance: [USER_CONSTRAINT, DESIGN_PRESET, SOLVER_DERIVED]
canonical_hash: expected-vibe-spec-hash
""")
    write(vibe / "expected_gpu_state_ir.yaml", """
schema_version: v4
design_identity: vibe-minimal-vertical-slice
source_spec_hash: expected-vibe-spec-hash
warp_state:
  resident_warps: [0,1,2,3]
  warp_width: 8
  per_warp_status: {0: reset, 1: reset, 2: reset, 3: reset}
  pc_table: {0: kernel_entry, 1: kernel_entry, 2: kernel_entry, 3: kernel_entry}
  exec_mask_table: {0: "11111111", 1: "11111111", 2: "11111111", 3: "11111111"}
  warp_active: "1111"
  warp_halted: "0000"
thread_state: {thread_ids: range_0_127, block_ids: [0,1,2,3], grid_ids: [0]}
pc_state: {per_warp_pc: {0: kernel_entry, 1: kernel_entry, 2: kernel_entry, 3: kernel_entry}}
active_mask_state: {mask_width: 8, per_warp_active_mask: {0: "11111111", 1: "11111111", 2: "11111111", 3: "11111111"}}
scheduler_state: {policy: ROUND_ROBIN, eligible_warps: [0,1,2,3], selected_warp: null, current_fetch_warp: 0, next_fetch_warp: 1}
scoreboard_state: {pending_registers: [], register_pending: {0: [], 1: [], 2: [], 3: []}, wakeup_events: []}
simt_stack_state: {entries: [], depth: 0}
register_state: {register_file_size: 32, per_thread_registers: zeroed}
memory_request_state: {outstanding_requests: [], request_tags: [], lane_masks: [], serviced_tracking: []}
csr_state: {start: 0, done: 0, fault: 0, kernel_entry: null}
launch_state: {grid_dim: [4,1,1], block_dim: [32,1,1], kernel_entry: null, completion: pending, fault: none}
pipeline_state: {pipeline_registers: reset, memory_stall_state: none, performance_counters: zeroed}
fault_state: none
canonical_hash: expected-vibe-state-hash
""")
    write(vibe / "expected_artifact_contract_report.yaml", """
schema_version: v4
verdict: PASS
cross_artifact_consistency_gate: pass
declared_test_coverage_gate: pass
config_ownership: {total_threads: bound, block_dim: bound, base_data_addr: bound, base_c: bound, memory_dump_range: bound}
failed_fields: []
missing_assets: []
""")
    write(vibe / "expected_runtime_contract_ir.yaml", """
schema_version: v4
abi_version: SIMPLE_MMIO_DOORBELL_V1
software_stack_contract:
  frontend_subset_contract: {language_subset: PYTHON_CUDA_LIKE_SUBSET, thread_id_intrinsics: [threadIdx.x, blockIdx.x, blockDim.x, gridDim.x], supported_control_flow: [if, for], unsupported_features: [full_cuda]}
  assembler_contract: {opcode_source: SPEC_IR.isa, symbol_policy: static_labels, error_policy: fail_closed}
  program_image_contract: {format: program.hex, entry_symbol: kernel_entry, load_address: 0, section_layout: [text, data]}
  kernel_test_app_contract: {declared_tests: [debug_gid, load_store, divergence, vecmul], runner_tests: [debug_gid, load_store, divergence, vecmul], argument_binding: flat32, data_layout: explicit_base_addresses}
  golden_output_contract: {checker: python_reference, output_region: [2560, 3072], comparison_policy: exact_int32}
program_image_contract: {format: program.hex, entry_symbol: kernel_entry, load_address: 0, hex_word_width: 32}
test_app_contract: {runner_binding: tests/test_suite.py, memory_dump_contract: output_region_2560_3072, golden_checker: python_reference}
memory_dump_contract: {region: [2560, 3072], format: little_endian_words, pass_condition: exact_match}
kernel_entry: kernel_entry
argument_layout: flat32
grid_block_contract: {grid_dim: [4,1,1], block_dim: [32,1,1], total_threads: 128}
command_queue: single_launch
doorbell: start_csr
completion: done_csr
fault_reporting: fault_csr
""")
    write(vibe / "expected_memory_subsystem_ir.yaml", """
schema_version: v4
address_spaces: [global]
coalescer: {policy: contiguous_active_lanes_same_segment}
load_store_queue: {entries_per_sm: 4, issue_width: 1}
outstanding_request_table: {tag_fields: [sm_id, warp_id, instruction_id], unique_until_response: true}
memory_request_lifecycle:
  issue_condition: instruction_valid and active_mask_nonzero and scoreboard_allows_issue
  outstanding_tracking: request_tag plus warp_id plus instruction_id
  replay_or_serviced_policy: do_not_duplicate_serviced_request
  response_match_policy: response_tag matches outstanding_request.tag
  scoreboard_wakeup_condition: matching_load_response_valid
  duplicate_request_prevention: serviced_tracking_required_on_pipeline_stall
  stall_release_condition: response_matched_or_fault_recorded
request_replay_policy: {on_pipeline_stall: do_not_duplicate_serviced_request, serviced_tracking: required, response_matching: required}
shared_memory: disabled
cache_global_interface: {signals: [dmem_req, dmem_wen, dmem_addr, dmem_wdata, dmem_rdata, dmem_miss, cache_serviced, mem_ready]}
atomic_unit: disabled_initially
fence_ordering: same_thread_program_order
scoreboard_wakeup: {load_response: clear_destination_register_pending, store_ack: clear_store_slot}
backpressure: {cache_miss_stalls_pipeline: true}
""")
    write(vibe / "expected_validation_plan_ir.yaml", """
schema_version: v4
runtime_tests: [app_compile_smoke, assembler_smoke, program_hex_load_smoke]
memory_tests: [memory_request_lifecycle_pass, duplicate_memory_request_reject, memory_dump_compare_pass]
implementation_tests: [rtl_sim_smoke, branch_active_mask_trace_pass, scoreboard_stall_trace_pass]
vertical_slice_tests: [debug_gid_test, load_store_test, divergence_test, vecmul_test]
closure_gates: [cross_artifact_consistency_gate, declared_test_coverage_gate, runtime_validation, memory_validation, implementation_validation, vertical_slice_validation]
declared_test_coverage_gate: {declared_tests: [debug_gid, load_store, divergence, vecmul], runner_tests: [debug_gid, load_store, divergence, vecmul], compile_or_generate_required: true}
trace_requirements: [cycle, warp_id, pc, instruction, active_mask, memory_request, register_writes]
""")
    write(vibe / "expected_closure_report.yaml", """
schema_version: v4
verdict: ACCEPT
gate_results:
  requirement_coverage: pass
  spec_lock: pass
  state_invariants: pass
  artifact_mapping: pass
  cross_artifact_consistency_gate: pass
  declared_test_coverage_gate: pass
  runtime_validation: pass
  memory_validation: pass
  implementation_validation: pass
  vertical_slice_validation: pass
  ppa: not_required_for_vertical_slice
  stability: pass
failed_fields: []
missing_assets: []
""")

    skill_examples = {
        "front_end": "Shows mode routing and forbidden architecture fields in DESIGN_INTENT_IR.",
        "state_engine": "Shows initial GPU_STATE_IR construction and invariant rejection.",
        "runtime_validator": "Shows valid and invalid launch ABI evidence.",
        "memory_subsystem": "Shows coalescing, bank conflict, tag mismatch, and scoreboard wakeup evidence.",
        "implementation_validator": "Shows RTL/golden trace comparison and first divergence evidence.",
        "closure_refinement": "Shows gate evaluation and repair routing.",
    }
    for dirname, summary in skill_examples.items():
        write(ROOT / "shared" / "examples" / dirname / "README.md", f"# {dirname}\n\n{summary}\n")


def generate_flow_and_references():
    write(ROOT / "shared" / "flow" / "gpgpu_design_flow.md", """
# GPGPU Design Flow

This flow is an IR-centered compiler pipeline. Skills are passes. Schemas define accepted IR. Tables define decisions. Examples and tests define regression behavior.

## Reproduce Path

Input: complete `spec.md`.

```text
gpgpu-front-end
  -> MODE_SELECTION_IR: REPRODUCE
gpgpu-spec-lock
  -> SPEC_IR
gpgpu-canonical-state-engine
  -> GPU_STATE_IR
gpgpu-artifact-contract-engine
  -> RTL_MAPPING_IR / SIM_BEHAVIOR_IR / RUNTIME_CONTRACT_IR / MEMORY_MODEL_IR / CONFIG_BINDING_IR / VALIDATION_PLAN_IR
gpgpu-runtime-validator
gpgpu-memory-subsystem
gpgpu-implementation-validator
  -> validation reports
gpgpu-closure-refinement-engine
  -> ACCEPT / REJECT / REFINE_REQUIRED / INSUFFICIENT_EVIDENCE
```

Stability requirement: the same input spec must produce the same SPEC_IR hash, GPU_STATE_IR hash, artifact mapping report, and closure verdict.

## Design From Intent Path

Input: design goal.

```text
gpgpu-front-end
  -> MODE_SELECTION_IR: DESIGN
  -> DESIGN_INTENT_IR
gpgpu-architecture-synthesizer
  -> ARCH_CANDIDATE_IR
  -> SYNTHESIZED_SPEC_DRAFT
gpgpu-spec-lock
  -> SPEC_IR
```

After SPEC_IR, the path rejoins the reproduce path. The synthesizer must not skip spec-lock.

## Vertical Slice Prototype Path

Input: a request to run a minimal GPU demo end to end.

```text
CUDA-like Python kernel
  -> frontend_subset_contract
  -> assembler_contract
  -> program.hex / PROGRAM_IMAGE_CONTRACT_IR
  -> RTL sim smoke
  -> memory dump
  -> golden_output_contract
  -> closure
```

This path uses `MINIMAL_VERTICAL_SLICE_GPGPU`, `software_stack_contract_table.yaml`, `end_to_end_smoke_test_table.yaml`, and `vertical_slice_validation_table.yaml`. It must still pass `SPEC_IR -> GPU_STATE_IR -> artifact contract -> validation closure`; the runnable demo is evidence, not a second source of truth.

## Fail Closed Policy

Missing schema, missing table row, hidden default, unsupported enum, forbidden provenance, and unmapped state fields must reject or emit `INSUFFICIENT_SKILL_ASSET`. They must not be repaired by model inference.
""")
    lessons = {
        "vortex_lessons.yaml": ("VORTEX_WARP_SCHED_001", "Vortex", "warp_scheduler", "Warp scheduling policy must be represented as architectural state or explicit implementation policy."),
        "miaow_lessons.yaml": ("MIAOW_SIMT_CORE_001", "MIAOW", "simt_core", "SIMT lane mask and register behavior must be visible in validation traces."),
        "gpgpusim_lessons.yaml": ("GPGPUSIM_TRACE_001", "GPGPU-Sim", "golden_trace", "Golden simulator traces are evidence and must not redefine ISA or state semantics."),
        "rocket_lessons.yaml": ("ROCKET_CONFIG_001", "Rocket Chip", "config_binding", "Generator configuration needs explicit ownership and downstream consumer binding."),
        "xiangshan_lessons.yaml": ("XIANGSHAN_VALIDATION_001", "XiangShan", "validation_closure", "Pipeline and trace validation should route failures to fields, rules, and owners."),
    }
    index_entries = []
    for filename, (lesson_id, project, topic, principle) in lessons.items():
        write(ROOT / "shared" / "references" / filename, f"""
lessons:
  - lesson_id: {lesson_id}
    source_project: {project}
    applies_to:
      - gpgpu-canonical-state-engine
      - gpgpu-implementation-validator
    topic: {topic}
    principle: "{principle}"
    do:
      - "Bind behavior through SPEC_IR, GPU_STATE_IR, and explicit contract tables."
    do_not:
      - "Let a downstream implementation invent behavior not visible to validation."
    evidence_anchor:
      - "ref/skillref/{project.lower().replace('-', '')}.md"
""")
        index_entries.append(f"  - {filename}")
    write(ROOT / "shared" / "references" / "vibe_gpu_lessons.yaml", """
lessons:
  - lesson_id: VIBE_GPU_VERTICAL_SLICE_001
    source_project: Vibe-GPU
    applies_to:
      - gpgpu-front-end
      - gpgpu-architecture-synthesizer
      - gpgpu-runtime-validator
      - gpgpu-implementation-validator
    topic: vertical_slice_prototype
    principle: "A credible minimal GPGPU needs an end-to-end kernel -> compiler -> assembler -> program image -> RTL simulation -> memory dump -> golden checker path."
    do:
      - "Use MINIMAL_VERTICAL_SLICE_GPGPU as a runnable reference preset."
      - "Gate vertical slices with app_compile_smoke, assembler_smoke, program_hex_load_smoke, rtl_sim_smoke, and memory_dump_compare."
    do_not:
      - "Treat architecture documents alone as prototype evidence."
  - lesson_id: VIBE_GPU_DRIFT_001
    source_project: Vibe-GPU
    applies_to:
      - gpgpu-spec-lock
      - gpgpu-artifact-contract-engine
      - gpgpu-closure-refinement-engine
    topic: source_of_truth_and_test_drift
    principle: "Docs, RTL defines, ISA tools, declared tests, and actual runners drift unless SPEC_IR and validation plans own the truth."
    do:
      - "Generate or check ISA/tool/doc artifacts from SPEC_IR.isa."
      - "Reject declared tests that do not appear in the runner or cannot compile/generate."
      - "Bind magic constants through CONFIG_BINDING_IR and runtime contracts."
    do_not:
      - "Let docs/isa.md, rtl/defines.svh, or tools/isa.py independently define opcodes."
evidence_anchor:
  - ref_submodule/Vibe-GPU
  - ref_submodule/Vibe-GPU/tools/isa.py
  - ref_submodule/Vibe-GPU/rtl/defines.svh
  - ref_submodule/Vibe-GPU/tests/test_suite.py
""")
    index_entries.append("  - vibe_gpu_lessons.yaml")
    write(ROOT / "shared" / "references" / "reference_lesson_index.yaml", "lesson_files:\n" + "\n".join(index_entries) + "\n")


def generate_readme_and_summary():
    readme = """
# GPGPU Skills

This repository defines an IR-centered GPGPU design compiler flow.

## Goals

1. Reproduce a GPGPU from a complete spec.
2. Design a GPGPU from intent through candidate synthesis and closure.
3. Prevent hidden defaults, unstable outputs, and uncontrolled model inference.
4. Provide a runnable vertical-slice proof path for CUDA-like kernel -> program image -> RTL simulation -> memory dump -> golden check.

## Top-Level Skills

1. gpgpu-front-end
2. gpgpu-architecture-synthesizer
3. gpgpu-spec-lock
4. gpgpu-canonical-state-engine
5. gpgpu-artifact-contract-engine
6. gpgpu-runtime-validator
7. gpgpu-memory-subsystem
8. gpgpu-implementation-validator
9. gpgpu-closure-refinement-engine

## Flow

Intent -> Candidate -> Spec -> State -> Contract -> Validation -> Closure

Vertical-slice prototype path: CUDA-like Python kernel -> frontend -> assembler -> program.hex -> RTL simulation -> memory dump -> Python golden check.

## Shared Assets

- schemas
- tables
- examples
- tests
- flow
- references

## Legacy

The former 13 top-level GPGPU skills are preserved under `legacy/`. Their capabilities are retained as subpasses inside the 9 v4 top-level skills.
"""
    write(ROOT / "README.md", readme)
    summary = """
# Skill Summary: GPGPU Skills v4

`skill/` now defines a 9-pass GPGPU design compiler flow:

```text
User Request / Spec
  -> Front-End
  -> Architecture Candidate
  -> Spec Lock
  -> Canonical State
  -> Artifact Contract
  -> Runtime / Memory / Implementation Validation
  -> Closure / Refinement
```

## Top-Level Skills

| Skill | Responsibility |
|---|---|
| `gpgpu-front-end` | mode selection and design intent lock |
| `gpgpu-architecture-synthesizer` | DESIGN_INTENT_IR to ARCH_CANDIDATE_IR and SYNTHESIZED_SPEC_DRAFT |
| `gpgpu-spec-lock` | complete spec or draft to stable SPEC_IR |
| `gpgpu-canonical-state-engine` | SPEC_IR to GPU_STATE_IR |
| `gpgpu-artifact-contract-engine` | deterministic artifact mapping and config binding |
| `gpgpu-runtime-validator` | host/runtime/launch ABI validation |
| `gpgpu-memory-subsystem` | memory subsystem and RTL-facing memory path validation |
| `gpgpu-implementation-validator` | RTL and golden sim validation plus first divergence |
| `gpgpu-closure-refinement-engine` | acceptance, failure attribution, and refinement request generation |

## Legacy Mapping

| v4 skill | v3 source |
|---|---|
| `gpgpu-front-end` | `gpgpu-mode-controller` + `gpgpu-design-intent-lock` |
| `gpgpu-architecture-synthesizer` | retained |
| `gpgpu-spec-lock` | retained |
| `gpgpu-canonical-state-engine` | retained |
| `gpgpu-artifact-contract-engine` | `gpgpu-deterministic-transform-engine` + `gpgpu-config` |
| `gpgpu-runtime-validator` | `gpgpu-runtime` |
| `gpgpu-memory-subsystem` | `gpgpu-memory-path` |
| `gpgpu-implementation-validator` | `gpgpu-rtl-simt-core` + `gpgpu-golden-sim` |
| `gpgpu-closure-refinement-engine` | `gpgpu-synthesis-closure-engine` + `gpgpu-causal-trace-analyzer` |

## Shared Assets

`shared/schemas/` defines IR contracts. `shared/tables/` defines decisions and mappings. `shared/examples/` contains end-to-end expected outputs, including `vibe_minimal_vertical_slice`. `shared/tests/` contains per-skill regression cases plus `validate_v4_assets.py`. `shared/references/` converts project references into lesson/rule/evidence entries.

## Fail-Closed Principle

Missing schema, missing table rows, hidden defaults, unknown enums, forbidden provenance, and unmapped state fields must emit a reject verdict or `INSUFFICIENT_SKILL_ASSET`. The flow must not fill gaps with model guesses.
"""
    write(ROOT / "skill_summary.md", summary)


def main():
    generate_skills()
    generate_schemas()
    generate_tables()
    generate_tests()
    generate_examples()
    generate_flow_and_references()
    generate_readme_and_summary()


if __name__ == "__main__":
    main()
