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
        "description": "Use when a user request, optional spec, optional trace, or patch request must be routed into the GPGPU compiler flow and design intent must be locked without architecture inference.",
        "role": "This skill is the entry compiler pass. It classifies the request and, for DESIGN mode, locks design intent into a bounded IR before any architecture synthesis occurs.",
        "upstream": ["User Request", "optional_spec", "optional_trace", "optional_patch_request"],
        "downstream": ["gpgpu-architecture-synthesizer for DESIGN", "gpgpu-spec-lock for REPRODUCE", "gpgpu-closure-refinement-engine for TRACE_DEBUG or PATCH_REQUEST"],
        "inputs": ["user_request", "optional_spec", "optional_trace", "optional_patch_request"],
        "outputs": ["MODE_SELECTION_IR", "DESIGN_INTENT_IR when mode is DESIGN", "FRONT_END_REPORT"],
        "owned": ["Mode classification: REPRODUCE, DESIGN, PATCH_REQUEST, TRACE_DEBUG", "Design intent fields: objective, non-goals, workload, platform, constraints, verification target", "Routing evidence and rejected routes"],
        "forbidden": ["Choose warp size, SM count, cache policy, scheduler policy, ISA encoding, memory hierarchy, register file size, or RTL pipeline", "Emit SPEC_IR, ARCH_CANDIDATE_IR, or GPU_STATE_IR", "Treat vague goals as complete specs"],
        "tables": ["shared/tables/mode_decision_table.yaml", "shared/tables/enum_table.yaml"],
        "schemas": ["shared/schemas/mode_selection_ir.schema.yaml", "shared/schemas/design_intent_ir.schema.yaml"],
        "invariants": ["Every routed request has exactly one mode", "DESIGN_INTENT_IR contains no architecture parameters", "PATCH_REQUEST and TRACE_DEBUG preserve evidence anchors"],
        "failures": ["INSUFFICIENT_REQUEST", "FORBIDDEN_ARCHITECTURE_FIELD", "AMBIGUOUS_MODE", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "selected_mode", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["mode_selection.md", "design_intent_lock.md", "shared/schemas/mode_selection_ir.schema.yaml", "shared/schemas/design_intent_ir.schema.yaml", "shared/tables/mode_decision_table.yaml", "shared/tests/front_end/cases.yaml"],
        "subpasses": {
            "mode_selection.md": ("Mode Selection", "Classify the request using shared/tables/mode_decision_table.yaml. A complete spec routes to REPRODUCE, a vague design goal routes to DESIGN, an edit against locked IR routes to PATCH_REQUEST, and trace or divergence evidence routes to TRACE_DEBUG."),
            "design_intent_lock.md": ("Design Intent Lock", "For DESIGN mode, normalize the user's goals into DESIGN_INTENT_IR. Required fields are objective, non_goals, workload_profile, target_platform, hard_constraints, soft_constraints, required_features, optional_features, validation_target, and prototype_credibility_target."),
        },
    },
    "gpgpu-architecture-synthesizer": {
        "title": "GPGPU Architecture Synthesizer",
        "description": "Use when DESIGN_INTENT_IR must be converted into a bounded architecture candidate using preset tables, hard constraints, scoring rules, and provenance.",
        "role": "This skill creates architecture candidates only. It never creates final spec truth and must route every candidate through gpgpu-spec-lock.",
        "upstream": ["gpgpu-front-end DESIGN_INTENT_IR"],
        "downstream": ["gpgpu-spec-lock consumes SYNTHESIZED_SPEC_DRAFT"],
        "inputs": ["DESIGN_INTENT_IR", "architecture_preset_library", "hard_constraint_table", "quality_target_table", "requirement_owner_table"],
        "outputs": ["ARCH_CANDIDATE_IR", "SYNTHESIZED_SPEC_DRAFT", "ARCH_SYNTHESIS_REPORT"],
        "owned": ["Requirement coverage", "Preset selection", "Parameter allocation", "Hard constraint checking", "Candidate scoring"],
        "forbidden": ["Emit SPEC_IR or GPU_STATE_IR", "Bypass gpgpu-spec-lock", "Invent topology outside shared/tables/architecture_preset_library.yaml", "Use COMMON_GPU_DEFAULT, MODEL_GUESS, UNKNOWN, or IMPLICIT_DEFAULT provenance"],
        "tables": ["shared/tables/architecture_preset_library.yaml", "shared/tables/hard_constraint_table.yaml", "shared/tables/quality_target_table.yaml", "shared/tables/requirement_owner_table.yaml", "shared/tables/enum_table.yaml", "shared/tables/provenance_table.yaml"],
        "schemas": ["shared/schemas/design_intent_ir.schema.yaml", "shared/schemas/arch_candidate_ir.schema.yaml", "shared/schemas/synthesized_spec_draft.schema.yaml"],
        "invariants": ["ARCH_CANDIDATE_IR != SPEC_IR", "Every intent requirement has an owner or explicit non-goal", "Hard constraints pass before scoring", "Every generated parameter has allowed provenance"],
        "failures": ["REJECTED_ARCH_CANDIDATE", "UNSUPPORTED_REQUIREMENT", "HARD_CONSTRAINT_FAIL", "FORBIDDEN_PROVENANCE", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "candidate_id", "consumed_ir_hash", "produced_ir_hash", "selected_preset", "constraint_proof", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["preset_selection.md", "parameter_allocation.md", "candidate_scoring.md", "shared/schemas/arch_candidate_ir.schema.yaml", "shared/schemas/synthesized_spec_draft.schema.yaml", "shared/tables/architecture_preset_library.yaml", "shared/tables/hard_constraint_table.yaml", "shared/tables/quality_target_table.yaml", "shared/tables/requirement_owner_table.yaml"],
        "subpasses": {
            "preset_selection.md": ("Preset Selection", "Select only MINIMAL_SIMT_CORE or MULTI_WARP_SINGLE_SM in v4 baseline. Unsupported presets must reject or emit refinement evidence instead of being improvised."),
            "parameter_allocation.md": ("Parameter Allocation", "Allocate warp, SM, scheduler, register, shared memory, LSU, cache, and launch parameters only from the selected preset plus explicit user constraints."),
            "candidate_scoring.md": ("Candidate Scoring", "Score only candidates that passed hard constraints. Scores are evidence for closure, not design truth."),
        },
    },
    "gpgpu-spec-lock": {
        "title": "GPGPU Spec Lock",
        "description": "Use when a human spec or synthesized spec draft must become complete, unambiguous, provenance-bearing SPEC_IR with no hidden defaults.",
        "role": "This skill locks static architecture facts. It parses and validates, but it does not design missing fields.",
        "upstream": ["Human complete spec", "gpgpu-architecture-synthesizer SYNTHESIZED_SPEC_DRAFT"],
        "downstream": ["gpgpu-canonical-state-engine"],
        "inputs": ["HUMAN_SPEC", "SYNTHESIZED_SPEC_DRAFT", "enum_table", "provenance_table", "spec_required_field_table"],
        "outputs": ["SPEC_IR", "SPEC_LOCK_REPORT"],
        "owned": ["ISA", "warp model", "thread/block/grid model", "scheduler policy", "register file", "memory hierarchy", "CSR/DCR", "launch ABI", "config defaults", "debug/test hooks"],
        "forbidden": ["Infer missing warp size, scheduler, memory hierarchy, ISA, or cache policy", "Accept hidden defaults or forbidden provenance", "Emit GPU_STATE_IR", "Pass free-form prose downstream"],
        "tables": ["shared/tables/spec_required_field_table.yaml", "shared/tables/enum_table.yaml", "shared/tables/provenance_table.yaml"],
        "schemas": ["shared/schemas/spec_ir.schema.yaml", "shared/schemas/synthesized_spec_draft.schema.yaml"],
        "invariants": ["No ambiguity", "No hidden default", "All enums resolved", "Every field has provenance", "Field order and hash are stable"],
        "failures": ["INSUFFICIENT_SPEC", "HIDDEN_DEFAULT_REJECT", "UNKNOWN_ENUM_REJECT", "FORBIDDEN_PROVENANCE", "CONFLICTING_SPEC_FIELD", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "source_kind", "consumed_ir_hash", "produced_ir_hash", "locked_fields", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["spec_ir_contract.md", "canonical_serialization.md", "provenance_rules.md", "shared/schemas/spec_ir.schema.yaml", "shared/tables/spec_required_field_table.yaml", "shared/tables/enum_table.yaml", "shared/tables/provenance_table.yaml"],
        "subpasses": {
            "spec_ir_contract.md": ("SPEC_IR Contract", "Lock only complete architecture facts. Required groups are ISA, warp model, grid/block/thread model, scheduler, register file, memory hierarchy, CSR/DCR, launch ABI, config defaults, and hooks."),
            "canonical_serialization.md": ("Canonical Serialization", "Serialize fields in schema order with deterministic scalar formatting. Hash the serialized SPEC_IR, not source prose."),
            "provenance_rules.md": ("Provenance Rules", "Accept USER_SPEC, USER_CONSTRAINT, DESIGN_PRESET, SOLVER_DERIVED, REPAIR_DERIVED, and EXPLICIT_DEFAULT. Reject UNKNOWN, COMMON_GPU_DEFAULT, MODEL_GUESS, and IMPLICIT_DEFAULT."),
        },
    },
    "gpgpu-canonical-state-engine": {
        "title": "GPGPU Canonical State Engine",
        "description": "Use when locked SPEC_IR must become deterministic GPU_STATE_IR or when canonical state invariants, transitions, snapshots, and FSM APIs must be checked.",
        "role": "This skill converts static spec truth into the only execution-state truth consumed by runtime, memory, implementation, and closure passes.",
        "upstream": ["gpgpu-spec-lock SPEC_IR"],
        "downstream": ["gpgpu-artifact-contract-engine"],
        "inputs": ["SPEC_IR"],
        "outputs": ["GPU_STATE_IR", "STATE_CONSTRUCTION_REPORT"],
        "owned": ["Initial state construction", "State transition rule binding", "State invariant checking", "Snapshot schema generation"],
        "forbidden": ["Plan architecture", "Evaluate quality", "Select templates", "Absorb candidate-only quality estimates", "Create state fields absent from SPEC_IR", "Modify state for RTL or runtime convenience"],
        "tables": ["shared/tables/initial_state_construction_table.yaml", "shared/tables/state_transition_rule_table.yaml", "shared/tables/state_invariant_table.yaml"],
        "schemas": ["shared/schemas/spec_ir.schema.yaml", "shared/schemas/gpu_state_ir.schema.yaml"],
        "invariants": ["Active mask width equals warp width", "Resident warp slots match SPEC_IR", "Scheduler references valid resident warps", "Scoreboard dependencies reference existing registers and events", "Outstanding memory request tags are unique"],
        "failures": ["STATE_CONSTRUCTION_REJECT", "MISSING_TRANSITION_RULE", "STATE_INVARIANT_FAIL", "INVALID_SCHEDULER_STATE", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "initialized_fields", "invariant_results", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["gpu_state_ir_contract.md", "state_transition_rules.md", "state_invariants.md", "shared/schemas/gpu_state_ir.schema.yaml", "shared/tables/initial_state_construction_table.yaml", "shared/tables/state_transition_rule_table.yaml", "shared/tables/state_invariant_table.yaml"],
        "subpasses": {
            "gpu_state_ir_contract.md": ("GPU_STATE_IR Contract", "Populate warp_state, thread_state, pc_state, active_mask_state, scheduler_state, scoreboard_state, register_state, memory_request_state, csr_state, launch_state, pipeline_state, and fault_state."),
            "state_transition_rules.md": ("State Transition Rules", "Bind every state-changing event to a named rule_id. Unknown events or unbound rules reject before downstream mapping."),
            "state_invariants.md": ("State Invariants", "Validate invariants during init, before transition, after transition, and before snapshot emission."),
        },
    },
    "gpgpu-artifact-contract-engine": {
        "title": "GPGPU Artifact Contract Engine",
        "description": "Use when SPEC_IR and GPU_STATE_IR must be mapped to deterministic RTL, simulator, runtime, memory, config, validation, and PPA contracts.",
        "role": "This skill is the deterministic transform and config binding pass. It maps state truth to artifact contracts without making new architecture decisions.",
        "upstream": ["gpgpu-spec-lock SPEC_IR", "gpgpu-canonical-state-engine GPU_STATE_IR"],
        "downstream": ["gpgpu-runtime-validator", "gpgpu-memory-subsystem", "gpgpu-implementation-validator", "gpgpu-closure-refinement-engine"],
        "inputs": ["SPEC_IR", "GPU_STATE_IR"],
        "outputs": ["RTL_MAPPING_IR", "SIM_BEHAVIOR_IR", "RUNTIME_CONTRACT_IR", "MEMORY_MODEL_IR", "CONFIG_BINDING_IR", "VALIDATION_PLAN_IR", "PPA_COUNTER_MAP", "ARTIFACT_CONTRACT_REPORT"],
        "owned": ["Deterministic transform", "Config parameter ownership", "Artifact mapping coverage", "Validation plan emission", "PPA counter binding"],
        "forbidden": ["Infer mappings without table entries", "Let runtime or RTL reinterpret ABI fields", "Leak debug-only fields to ABI", "Treat config as independent design truth"],
        "tables": ["shared/tables/artifact_mapping_table.yaml", "shared/tables/config_ownership_table.yaml", "shared/tables/state_to_rtl_mapping.yaml", "shared/tables/state_to_sim_mapping.yaml", "shared/tables/state_to_runtime_mapping.yaml", "shared/tables/state_to_memory_mapping.yaml"],
        "schemas": ["shared/schemas/rtl_mapping_ir.schema.yaml", "shared/schemas/sim_behavior_ir.schema.yaml", "shared/schemas/runtime_contract_ir.schema.yaml", "shared/schemas/memory_model_ir.schema.yaml", "shared/schemas/config_binding_ir.schema.yaml", "shared/schemas/validation_plan_ir.schema.yaml"],
        "invariants": ["Every consumed state field is mapped or explicit_unused", "Every config parameter has owner and visibility", "ABI fields have one interpretation", "Missing mapping fails closed"],
        "failures": ["MISSING_MAPPING_FAIL_CLOSED", "CONFIG_OWNER_MISSING", "ABI_FIELD_REINTERPRETED", "DEBUG_ONLY_LEAKS_TO_ABI", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "mapping_coverage", "config_ownership", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["deterministic_transform.md", "config_binding.md", "artifact_mapping.md", "shared/tables/artifact_mapping_table.yaml", "shared/tables/config_ownership_table.yaml", "shared/tables/state_to_rtl_mapping.yaml", "shared/tables/state_to_sim_mapping.yaml", "shared/tables/state_to_runtime_mapping.yaml", "shared/tables/state_to_memory_mapping.yaml"],
        "subpasses": {
            "deterministic_transform.md": ("Deterministic Transform", "Apply mapping tables to SPEC_IR and GPU_STATE_IR. If a state field has no mapping, emit MISSING_MAPPING_FAIL_CLOSED."),
            "config_binding.md": ("Config Binding", "Classify config fields as hardware_private, simulator_private, hw_sw_abi, test_only, or debug_only. Validate owner and allowed consumers."),
            "artifact_mapping.md": ("Artifact Mapping", "Emit downstream contracts for RTL, simulator, runtime, memory subsystem, validation plan, and PPA counters."),
        },
    },
    "gpgpu-runtime-validator": {
        "title": "GPGPU Runtime Validator",
        "description": "Use when host runtime, launch ABI, command queue, completion, fault, and synchronization behavior must be validated against locked contracts.",
        "role": "This skill validates host/runtime/launch ABI behavior. It does not design memory hierarchy or RTL memory path.",
        "upstream": ["gpgpu-artifact-contract-engine RUNTIME_CONTRACT_IR and CONFIG_BINDING_IR", "gpgpu-canonical-state-engine launch_state", "gpgpu-spec-lock ABI_launch_contract"],
        "downstream": ["gpgpu-closure-refinement-engine"],
        "inputs": ["RUNTIME_CONTRACT_IR", "CONFIG_BINDING_IR", "GPU_STATE_IR.launch_state", "SPEC_IR.ABI_launch_contract"],
        "outputs": ["RUNTIME_VALIDATION_REPORT_IR", "runtime_smoke_trace", "launch_contract_report"],
        "owned": ["Program image loading", "Kernel entry", "Argument layout", "Grid/block dimensions", "Command queue", "Doorbell/start", "Completion/done", "Fault reporting", "CSR/runtime interface", "Host-device synchronization"],
        "forbidden": ["Design coalescer, load/store queue, cache hierarchy, shared memory banks, request/response tags, or memory RTL pipeline", "Reinterpret ABI fields", "Modify GPU_STATE_IR"],
        "tables": ["shared/tables/runtime_smoke_test_table.yaml", "shared/tables/config_ownership_table.yaml"],
        "schemas": ["shared/schemas/runtime_contract_ir.schema.yaml", "shared/schemas/config_binding_ir.schema.yaml", "shared/schemas/runtime_validation_report_ir.schema.yaml"],
        "invariants": ["Launch ABI layout matches SPEC_IR", "Grid/block dimensions fit launch_state", "Completion and fault paths are observable", "Runtime consumes only ABI-visible config"],
        "failures": ["INVALID_ARGUMENT_LAYOUT", "GRID_DIM_MISMATCH", "MISSING_COMPLETION_PATH", "FAULT_CONTRACT_FAIL", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "runtime_smoke_trace_hash", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["launch_contract.md", "abi_validation.md", "completion_fault_validation.md", "shared/schemas/runtime_validation_report_ir.schema.yaml", "shared/tables/runtime_smoke_test_table.yaml"],
        "subpasses": {
            "launch_contract.md": ("Launch Contract", "Validate program image, kernel entry, command queue, doorbell/start, grid/block dimensions, and launch resource admission."),
            "abi_validation.md": ("ABI Validation", "Check argument layout, scalar size, pointer size, alignment, ABI version, and CSR/runtime interface ownership."),
            "completion_fault_validation.md": ("Completion and Fault Validation", "Ensure done, error, timeout, and fault-reporting paths are visible to host and closure."),
        },
    },
    "gpgpu-memory-subsystem": {
        "title": "GPGPU Memory Subsystem",
        "description": "Use when GPGPU memory subsystem contract, RTL-facing memory path, coalescing, LSQ, shared memory, cache/global interface, ordering, tags, and scoreboard wakeup must be defined and validated.",
        "role": "This skill defines and validates the GPGPU memory subsystem contract and RTL-facing memory path from canonical state and memory model inputs.",
        "upstream": ["gpgpu-canonical-state-engine memory_request_state, warp_state, scoreboard_state", "gpgpu-artifact-contract-engine MEMORY_MODEL_IR and RTL_MAPPING_IR.memory_interface"],
        "downstream": ["gpgpu-implementation-validator", "gpgpu-closure-refinement-engine"],
        "inputs": ["GPU_STATE_IR.memory_request_state", "GPU_STATE_IR.warp_state", "GPU_STATE_IR.scoreboard_state", "MEMORY_MODEL_IR", "RTL_MAPPING_IR.memory_interface"],
        "outputs": ["MEMORY_SUBSYSTEM_IR", "MEMORY_VALIDATION_REPORT_IR", "memory_trace", "memory_ordering_report", "memory_rtl_interface_report"],
        "owned": ["Address spaces", "Global/shared/local/constant memory", "Load/store path", "Coalescing policy", "Lane mask handling", "Byte enables", "Load/store queue", "Outstanding request table", "Request/response tags", "Shared memory banks", "Cache/global interface", "Atomic unit", "Fence ordering", "Memory fault contract", "Scoreboard wakeup", "Backpressure"],
        "forbidden": ["Choose architecture memory hierarchy not present in SPEC_IR", "Modify scheduler policy", "Treat memory validation as runtime launch validation", "Ignore tag or lane-mask mismatches"],
        "tables": ["shared/tables/memory_address_space_table.yaml", "shared/tables/coalescing_rule_table.yaml", "shared/tables/shared_memory_bank_table.yaml", "shared/tables/memory_ordering_table.yaml", "shared/tables/memory_scoreboard_wakeup_table.yaml"],
        "schemas": ["shared/schemas/memory_model_ir.schema.yaml", "shared/schemas/memory_subsystem_ir.schema.yaml", "shared/schemas/memory_validation_report_ir.schema.yaml"],
        "invariants": ["Lane mask drives byte enable generation", "Request tags are unique until response", "Load response wakes matching scoreboard dependency", "Fences enforce declared ordering", "Bank conflicts are detected and reported"],
        "failures": ["REQUEST_TAG_MISMATCH", "BANK_CONFLICT_DETECTED", "ORDERING_VIOLATION", "SCOREBOARD_WAKEUP_MISSING", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "memory_trace_hash", "ordering_results", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["memory_model.md", "coalescer.md", "load_store_queue.md", "shared_memory.md", "cache_global_interface.md", "scoreboard_wakeup.md", "shared/schemas/memory_subsystem_ir.schema.yaml", "shared/tables/coalescing_rule_table.yaml", "shared/tables/memory_ordering_table.yaml"],
        "subpasses": {
            "memory_model.md": ("Memory Model", "Bind address spaces, consistency, atomic, fence, fault, and cache/global interface semantics from MEMORY_MODEL_IR."),
            "coalescer.md": ("Coalescer", "Validate lane masks, address grouping, byte enables, transaction boundaries, and partial stores."),
            "load_store_queue.md": ("Load Store Queue", "Validate LSQ admission, outstanding request table, request/response tags, replay, and backpressure."),
            "shared_memory.md": ("Shared Memory", "Validate shared memory banks, bank conflicts, broadcast behavior, and conflict reporting."),
            "cache_global_interface.md": ("Cache Global Interface", "Validate cache request/response contract, global memory interface, atomics, faults, and retry behavior."),
            "scoreboard_wakeup.md": ("Scoreboard Wakeup", "Validate that load responses, atomic responses, and fault responses wake or poison the correct scoreboard entries."),
        },
    },
    "gpgpu-implementation-validator": {
        "title": "GPGPU Implementation Validator",
        "description": "Use when RTL SIMT core and golden simulator traces must be validated against GPU_STATE_IR, mapping contracts, memory subsystem behavior, and validation plans.",
        "role": "This skill validates RTL and golden simulator behavior against canonical state. It merges the former RTL SIMT core and golden sim responsibilities.",
        "upstream": ["gpgpu-canonical-state-engine GPU_STATE_IR", "gpgpu-artifact-contract-engine RTL_MAPPING_IR, SIM_BEHAVIOR_IR, VALIDATION_PLAN_IR", "gpgpu-memory-subsystem MEMORY_SUBSYSTEM_IR"],
        "downstream": ["gpgpu-closure-refinement-engine"],
        "inputs": ["GPU_STATE_IR", "RTL_MAPPING_IR", "SIM_BEHAVIOR_IR", "MEMORY_SUBSYSTEM_IR", "VALIDATION_PLAN_IR", "trace"],
        "outputs": ["IMPLEMENTATION_VALIDATION_REPORT_IR", "RTL_VALIDATION_REPORT", "GOLDEN_SIM_REPORT", "FIRST_DIVERGENCE_REPORT"],
        "owned": ["RTL SIMT core validation", "Golden simulator validation", "RTL-vs-golden first divergence", "Trace event consistency"],
        "forbidden": ["Redefine ISA", "Change GPU_STATE_IR to match RTL", "Let golden sim become a second truth source", "Ignore first divergence evidence"],
        "tables": ["shared/tables/rtl_validation_gate_table.yaml", "shared/tables/golden_sim_trace_field_table.yaml", "shared/tables/first_divergence_taxonomy.yaml"],
        "schemas": ["shared/schemas/implementation_validation_report_ir.schema.yaml", "shared/schemas/first_divergence_report_ir.schema.yaml"],
        "invariants": ["Fetch/decode/issue/execute/writeback obey mapped state", "Active mask updates match transition rules", "Scoreboard stalls and wakeups match memory subsystem contract", "Trace fields cover mandatory semantic fields"],
        "failures": ["RTL_VALIDATION_FAIL", "GOLDEN_SIM_REDEFINES_ISA", "FIRST_DIVERGENCE_DETECTED", "TRACE_FIELD_MISSING", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "rtl_report_hash", "golden_report_hash", "first_divergence", "failed_fields", "missing_assets", "downstream_contract"],
        "assets": ["rtl_simt_core_validation.md", "golden_sim_validation.md", "first_divergence.md", "shared/schemas/implementation_validation_report_ir.schema.yaml", "shared/schemas/first_divergence_report_ir.schema.yaml", "shared/tables/rtl_validation_gate_table.yaml", "shared/tables/golden_sim_trace_field_table.yaml", "shared/tables/first_divergence_taxonomy.yaml"],
        "subpasses": {
            "rtl_simt_core_validation.md": ("RTL SIMT Core Validation", "Validate fetch, decode, issue, execute, writeback, scheduler, active mask, scoreboard, register, CSR, pipeline, and memory request interface events."),
            "golden_sim_validation.md": ("Golden Simulator Validation", "Validate deterministic replay and property coverage against SIM_BEHAVIOR_IR without redefining ISA or architecture semantics."),
            "first_divergence.md": ("First Divergence", "Compare RTL and golden traces by ordered semantic events and classify the first field, rule, and owner that diverges."),
        },
    },
    "gpgpu-closure-refinement-engine": {
        "title": "GPGPU Closure Refinement Engine",
        "description": "Use when architecture candidates, locked specs, state, artifact reports, runtime/memory/implementation validation, PPA evidence, and trace divergences must be accepted, rejected, or routed to refinement.",
        "role": "This skill is the final acceptance, failure attribution, and refinement-request compiler pass.",
        "upstream": ["gpgpu-architecture-synthesizer", "gpgpu-spec-lock", "gpgpu-canonical-state-engine", "gpgpu-artifact-contract-engine", "gpgpu-runtime-validator", "gpgpu-memory-subsystem", "gpgpu-implementation-validator"],
        "downstream": ["User-facing closure decision", "Repair owner skill for refinement loops"],
        "inputs": ["ARCH_CANDIDATE_IR", "SPEC_IR", "GPU_STATE_IR", "ARTIFACT_CONTRACT_REPORT", "RUNTIME_VALIDATION_REPORT", "MEMORY_VALIDATION_REPORT", "IMPLEMENTATION_VALIDATION_REPORT", "PPA_REPORT", "TRACE_DIVERGENCE_REPORT"],
        "outputs": ["SYNTHESIS_ACCEPTANCE_REPORT_IR", "REFINEMENT_REQUEST_IR"],
        "owned": ["Closure gate evaluation", "Failure attribution", "Refinement request generation", "Repair routing"],
        "forbidden": ["Design architecture", "Bypass failed gates", "Accept evidence-free candidates", "Directly mutate ARCH_CANDIDATE_IR, SPEC_IR, or GPU_STATE_IR"],
        "tables": ["shared/tables/closure_gate_table.yaml", "shared/tables/verdict_decision_table.yaml", "shared/tables/failure_taxonomy_table.yaml", "shared/tables/repair_routing_table.yaml"],
        "schemas": ["shared/schemas/synthesis_acceptance_report_ir.schema.yaml", "shared/schemas/refinement_request_ir.schema.yaml"],
        "invariants": ["Verdict is one of ACCEPT, REJECT, REFINE_REQUIRED, INSUFFICIENT_EVIDENCE", "Every failed gate has owner, affected field, evidence, and repair route", "Hard correctness failures reject", "Repairable trace failures refine"],
        "failures": ["INSUFFICIENT_EVIDENCE", "HARD_CORRECTNESS_FAIL", "REPAIRABLE_TRACE_FAIL", "UNROUTED_FAILURE", "INSUFFICIENT_SKILL_ASSET"],
        "report": ["verdict", "consumed_ir_hash", "produced_ir_hash", "gate_results", "failed_fields", "missing_assets", "downstream_contract", "refinement_request"],
        "assets": ["closure_gate.md", "causal_trace_analysis.md", "refinement_request.md", "shared/schemas/synthesis_acceptance_report_ir.schema.yaml", "shared/schemas/refinement_request_ir.schema.yaml", "shared/tables/closure_gate_table.yaml", "shared/tables/verdict_decision_table.yaml", "shared/tables/failure_taxonomy_table.yaml", "shared/tables/repair_routing_table.yaml"],
        "subpasses": {
            "closure_gate.md": ("Closure Gate", "Evaluate coverage, spec lock, state invariant, artifact mapping, runtime, memory, implementation, PPA, and stability gates."),
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
required: [schema_version, intent_id, objective, non_goals, workload_profile, target_platform, hard_constraints, soft_constraints, required_features, optional_features, validation_target, prototype_credibility_target, provenance]
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
  prototype_credibility_target: {type: enum, values: [TOY, TEACHING_RTL, RESEARCH_PROTOTYPE, SYNTHESIS_READY]}
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
    values: [MINIMAL_SIMT_CORE, MULTI_WARP_SINGLE_SM]
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
required: [schema_version, design_identity, source_kind, isa, warp_model, thread_block_grid_model, scheduler_policy, register_file, memory_hierarchy, csr_dcr, launch_abi, config_defaults, debug_test_hooks, provenance, canonical_hash]
properties:
  source_kind: {type: enum, values: [HUMAN_SPEC, SYNTHESIZED_SPEC_DRAFT]}
  isa:
    required: [profile, operation_classes, encoding_policy]
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
""",
    "gpu_state_ir.schema.yaml": """
schema: GPU_STATE_IR
version: v4
type: object
required: [schema_version, design_identity, source_spec_hash, warp_state, thread_state, pc_state, active_mask_state, scheduler_state, scoreboard_state, register_state, memory_request_state, csr_state, launch_state, pipeline_state, fault_state, canonical_hash]
properties:
  warp_state: {required: [resident_warps, warp_width, per_warp_status]}
  thread_state: {required: [thread_ids, block_ids, grid_ids]}
  pc_state: {required: [per_warp_pc]}
  active_mask_state: {required: [per_warp_active_mask, mask_width]}
  scheduler_state: {required: [policy, eligible_warps, selected_warp]}
  scoreboard_state: {required: [pending_registers, wakeup_events]}
  register_state: {required: [register_file_size, per_thread_registers]}
  memory_request_state: {required: [outstanding_requests, request_tags, lane_masks]}
  launch_state: {required: [grid_dim, block_dim, kernel_entry, completion, fault]}
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
required: [schema_version, abi_version, program_image, kernel_entry, argument_layout, grid_block_contract, command_queue, doorbell, completion, fault_reporting]
failure_rules: {invalid_layout: INVALID_ARGUMENT_LAYOUT, missing_completion: MISSING_COMPLETION_PATH}
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
required: [schema_version, address_spaces, coalescer, load_store_queue, outstanding_request_table, shared_memory, cache_global_interface, atomic_unit, fence_ordering, scoreboard_wakeup, backpressure]
failure_rules: {tag_mismatch: REQUEST_TAG_MISMATCH}
""",
    "validation_plan_ir.schema.yaml": """
schema: VALIDATION_PLAN_IR
version: v4
required: [schema_version, runtime_tests, memory_tests, implementation_tests, closure_gates, trace_requirements]
failure_rules: {missing_required_test: VALIDATION_PLAN_INCOMPLETE}
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
    required: [requirement_coverage, spec_lock, state_invariants, artifact_mapping, runtime_validation, memory_validation, implementation_validation, ppa, stability]
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
    values: [SPEC_FIELD_FIX, STATE_RULE_FIX, ARTIFACT_MAPPING_FIX, RUNTIME_ABI_FIX, MEMORY_CONTRACT_FIX, RTL_FIX, GOLDEN_SIM_FIX, ARCHITECTURE_REFINEMENT]
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
  architecture_preset: [MINIMAL_SIMT_CORE, MULTI_WARP_SINGLE_SM]
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
unsupported_presets: [MULTI_SM_GPGPU, FPGA_SMALL_GPGPU, TENSOR_EXTENDED_GPGPU]
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
""",
    "spec_required_field_table.yaml": """
table: spec_required_field_table
version: v4
required_fields:
  - isa.profile
  - isa.operation_classes
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
explicit_unused: [warp_state, pc_state, active_mask_state, scheduler_state, scoreboard_state, register_state, memory_request_state, pipeline_state]
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
explicit_unused: [thread_state, pc_state, scheduler_state, register_state, csr_state, launch_state, pipeline_state]
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
  - runtime_validation
  - memory_validation
  - implementation_validation
  - ppa
  - stability
hard_correctness_gates: [spec_lock, state_invariants, artifact_mapping, runtime_validation, memory_validation, implementation_validation]
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
""",
}


TEST_CASES = {
    "front_end": ["complete_spec_routes_to_reproduce", "vague_goal_routes_to_design_intent_lock", "patch_request_routes_to_patch", "trace_failure_routes_to_trace_debug", "forbidden_architecture_field_rejected_in_intent"],
    "architecture_synthesizer": ["minimal_simt_candidate_pass", "multi_warp_single_sm_candidate_pass", "unsupported_feature_reject", "hard_constraint_fail_reject", "candidate_not_spec_ir"],
    "spec_lock": ["complete_spec_pass", "missing_warp_size_reject", "hidden_default_reject", "unknown_enum_reject", "forbidden_provenance_reject", "conflicting_spec_field_reject", "canonical_hash_stable"],
    "state_engine": ["minimal_simt_initial_state_pass", "active_mask_width_matches_warp_width", "resident_warp_slots_match_spec", "invalid_scheduler_state_reject", "missing_transition_rule_reject"],
    "artifact_contract": ["all_state_fields_mapped_pass", "missing_mapping_fail_closed", "config_owner_missing_reject", "abi_field_reinterpreted_reject", "debug_only_leaks_to_abi_reject"],
    "runtime_validator": ["valid_kernel_launch_pass", "invalid_argument_layout_reject", "grid_dim_mismatch_reject", "missing_completion_path_reject", "fault_reporting_contract_pass"],
    "memory_subsystem": ["coalesced_global_load_pass", "partial_lane_mask_store_pass", "shared_memory_bank_conflict_detected", "load_response_wakes_scoreboard", "fence_ordering_pass", "request_tag_mismatch_reject"],
    "implementation_validator": ["single_warp_integer_trace_pass", "branch_active_mask_trace_pass", "scoreboard_stall_trace_pass", "rtl_golden_first_divergence_detected", "golden_sim_redefines_isa_reject"],
    "closure_refinement": ["all_gates_pass_accept", "missing_evidence_insufficient", "hard_correctness_fail_reject", "repairable_trace_fail_refine_required", "failure_routed_to_correct_owner_skill"],
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
warp_state: {resident_warps: [0], warp_width: 8, per_warp_status: {0: reset}}
thread_state: {thread_ids: [0,1,2,3,4,5,6,7], block_ids: [0], grid_ids: [0]}
pc_state: {per_warp_pc: {0: kernel_entry}}
active_mask_state: {mask_width: 8, per_warp_active_mask: {0: "11111111"}}
scheduler_state: {policy: ROUND_ROBIN, eligible_warps: [0], selected_warp: null}
scoreboard_state: {pending_registers: [], wakeup_events: []}
register_state: {register_file_size: 16, per_thread_registers: zeroed}
memory_request_state: {outstanding_requests: [], request_tags: [], lane_masks: []}
csr_state: {start: 0, done: 0, fault: 0, kernel_entry: null}
launch_state: {grid_dim: [1,1,1], block_dim: [8,1,1], kernel_entry: null, completion: pending, fault: none}
pipeline_state: reset
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
prototype_credibility_target: TEACHING_RTL
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
    write(des / "expected_closure_report.yaml", "schema_version: v4\nverdict: ACCEPT\ngate_results: {requirement_coverage: pass, spec_lock: pass, state_invariants: pass, artifact_mapping: pass, runtime_validation: pass, memory_validation: pass, implementation_validation: pass, ppa: pass, stability: pass}\n")

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
    write(ROOT / "shared" / "references" / "reference_lesson_index.yaml", "lesson_files:\n" + "\n".join(index_entries) + "\n")


def generate_readme_and_summary():
    readme = """
# GPGPU Skills

This repository defines an IR-centered GPGPU design compiler flow.

## Goals

1. Reproduce a GPGPU from a complete spec.
2. Design a GPGPU from intent through candidate synthesis and closure.
3. Prevent hidden defaults, unstable outputs, and uncontrolled model inference.

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

`shared/schemas/` defines IR contracts. `shared/tables/` defines decisions and mappings. `shared/examples/` contains end-to-end expected outputs. `shared/tests/` contains per-skill regression cases plus `validate_v4_assets.py`. `shared/references/` converts project references into lesson/rule/evidence entries.

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
