#!/usr/bin/env python3
"""Validate the GPGPU skill v5 self-correcting design-system contract."""

from pathlib import Path
from typing import Dict, List

import yaml


ROOT = Path(__file__).resolve().parents[2]

TOP_LEVEL_SKILLS = [
    "gpgpu-arch",
    "gpgpu-golden",
    "gpgpu-runtime",
    "gpgpu-rtl",
    "gpgpu-simppa",
    "gpgpu-loop",
    "gpgpu-interconnect",
    "gpgpu-memory",
    "gpgpu-atomic-sync",
]

REMOVED_TOP_LEVEL_SKILLS = [
    "gpgpu-front-end",
    "gpgpu-architecture-synthesizer",
    "gpgpu-spec-lock",
    "gpgpu-canonical-state-engine",
    "gpgpu-artifact-contract-engine",
    "gpgpu-runtime-validator",
    "gpgpu-memory-subsystem",
    "gpgpu-implementation-validator",
    "gpgpu-closure-refinement-engine",
]

REMOVED_LEGACY_SKILLS = [
    "legacy/gpgpu-mode-controller",
    "legacy/gpgpu-design-intent-lock",
    "legacy/gpgpu-deterministic-transform-engine",
    "legacy/gpgpu-config",
    "legacy/gpgpu-runtime",
    "legacy/gpgpu-memory-path",
    "legacy/gpgpu-rtl-simt-core",
    "legacy/gpgpu-golden-sim",
    "legacy/gpgpu-synthesis-closure-engine",
    "legacy/gpgpu-causal-trace-analyzer",
]

REMOVED_FILES = [
    "file_descriptions.zh.md",
    "skill_5stage_compression_plan.zh.md",
    "skill_summary.md",
    "shared/tools/generate_v4_assets.py",
]

REMOVED_DIRS = [
    "examples",
    "references",
    "shared/tools",
]

ACTIVE_STALE_REFERENCE_ROOTS = [
    "shared/tables",
    "shared/references",
]

SKILL_SECTIONS = [
    "## Role",
    "## Position in Flow",
    "## Input IR",
    "## Output IR",
    "## Owned Decisions",
    "## Human and AI Output Policy",
    "## Forbidden Actions",
    "## Required Tables",
    "## Required Schemas",
    "## Required Invariants",
    "## Failure Modes",
    "## Report Schema",
    "## Concrete Assets Required",
]

NEW_SCHEMAS = [
    "config_stack_ir.schema.yaml",
    "resolved_config_ir.schema.yaml",
    "system_composition_ir.schema.yaml",
    "negotiated_interface_ir.schema.yaml",
    "adapter_contract.schema.yaml",
    "protocol_monitor_contract.schema.yaml",
    "mmio_register_map_ir.schema.yaml",
    "debug_counter_contract.schema.yaml",
    "capability_profile_ir.schema.yaml",
    "contract_fragment_ir.schema.yaml",
    "lsu_lane_format_contract.schema.yaml",
    "nonblocking_memory_tag_contract.schema.yaml",
    "coalescer_response_restore_contract.schema.yaml",
    "local_memory_bank_contract.schema.yaml",
    "l1_cache_or_global_adapter_contract.schema.yaml",
    "fabric_request_response_contract.schema.yaml",
    "l2_slice_routing_contract.schema.yaml",
    "l2_cache_slice_contract.schema.yaml",
    "mshr_replay_contract.schema.yaml",
    "cache_response_routing_contract.schema.yaml",
    "dram_controller_contract.schema.yaml",
    "memory_visibility_contract.schema.yaml",
    "atomic_execution_model.schema.yaml",
    "fence_visibility_contract.schema.yaml",
    "barrier_phase_contract.schema.yaml",
    "wsync_drain_contract.schema.yaml",
    "mode_selection_ir.schema.yaml",
    "output_mode_ir.schema.yaml",
    "artifact_manifest_ir.schema.yaml",
    "human_report_manifest_ir.schema.yaml",
    "artifact_visibility_ir.schema.yaml",
    "design_intent_ir.schema.yaml",
    "arch_ir.schema.yaml",
    "micro_constraint_estimate_ir.schema.yaml",
    "arch_generation_report_ir.schema.yaml",
    "system_contract_ir.schema.yaml",
    "golden_contract_model.schema.yaml",
    "contract_semantics_report_ir.schema.yaml",
    "toolchain_artifact_ir.schema.yaml",
    "assembly_ir.schema.yaml",
    "program_image_ir.schema.yaml",
    "runtime_launch_ir.schema.yaml",
    "loader_contract_ir.schema.yaml",
    "assembler_binding_report_ir.schema.yaml",
    "toolchain_smoke_report_ir.schema.yaml",
    "incremental_rtl_map.schema.yaml",
    "module_interface_report_ir.schema.yaml",
    "rtl_partial_sim_report_ir.schema.yaml",
    "normalized_trace_ir.schema.yaml",
    "correctness_gate_report_ir.schema.yaml",
    "first_divergence_report_ir.schema.yaml",
    "pass_evidence_report_ir.schema.yaml",
    "trace_coverage_report_ir.schema.yaml",
    "performance_metric_ir.schema.yaml",
    "regression_fingerprint_ir.schema.yaml",
    "toolchain_attribution_report_ir.schema.yaml",
    "trace_source_manifest_ir.schema.yaml",
    "stall_breakdown_ir.schema.yaml",
    "perf_attribution_graph.schema.yaml",
    "root_cause_report_ir.schema.yaml",
    "sim_perf_attribution_report_ir.schema.yaml",
    "config_parameter_classification.schema.yaml",
    "config_parameter_taxonomy.schema.yaml",
    "issue_nonissue_reason.schema.yaml",
    "simt_state.schema.yaml",
    "scoreboard_state.schema.yaml",
    "warp_memory_transaction.schema.yaml",
    "coalescer_output_trace.schema.yaml",
    "cache_request_status.schema.yaml",
    "noc_packet.schema.yaml",
    "memory_request_lifecycle.schema.yaml",
    "memory_queue_boundary.schema.yaml",
    "atomic_operation.schema.yaml",
    "fence_visibility.schema.yaml",
    "barrier_state.schema.yaml",
    "counter_manifest.schema.yaml",
    "stall_reason_matrix.schema.yaml",
    "performance_attribution_graph.schema.yaml",
    "arch_rewrite_plan.schema.yaml",
    "rewrite_decision_report_ir.schema.yaml",
    "regression_tracking_report_ir.schema.yaml",
]

NEW_TABLES = [
    "enum_table.yaml",
    "provenance_table.yaml",
    "mode_decision_table.yaml",
    "output_mode_table.yaml",
    "artifact_visibility_table.yaml",
    "report_language_policy.yaml",
    "human_report_template_table.yaml",
    "ai_artifact_retention_table.yaml",
    "architecture_preset_library.yaml",
    "hard_constraint_table.yaml",
    "quality_target_table.yaml",
    "requirement_owner_table.yaml",
    "micro_constraint_estimator_table.yaml",
    "config_ownership_table.yaml",
    "contract_semantics_binding_table.yaml",
    "golden_model_coverage_table.yaml",
    "source_of_truth_generation_table.yaml",
    "toolchain_artifact_generation_table.yaml",
    "assembly_syntax_table.yaml",
    "instruction_encoding_derivation_table.yaml",
    "program_image_format_table.yaml",
    "runtime_launch_binding_table.yaml",
    "loader_contract_table.yaml",
    "toolchain_validation_gate_table.yaml",
    "rtl_module_catalog.yaml",
    "module_interface_contract_table.yaml",
    "rtl_partial_sim_gate_table.yaml",
    "trace_normalization_table.yaml",
    "correctness_gate_decision_table.yaml",
    "trace_source_manifest_table.yaml",
    "event_type_taxonomy.yaml",
    "stall_reason_taxonomy.yaml",
    "differential_compare_table.yaml",
    "pass_evidence_gate_table.yaml",
    "performance_metric_table.yaml",
    "bottleneck_template_table.yaml",
    "toolchain_attribution_taxonomy.yaml",
    "minimal_trace_window_table.yaml",
    "report_generation_table.yaml",
    "perf_attribution_taxonomy.yaml",
    "root_cause_taxonomy.yaml",
    "verification_backend_matrix.yaml",
    "rewrite_trigger_table.yaml",
    "patch_taxonomy_table.yaml",
    "revalidation_routing_table.yaml",
    "gpgpusim_config_taxonomy_seed.md",
    "stall_reason_taxonomy.md",
]

TEST_DIRS = [
    "artifact_visibility",
    "architecture_generator",
    "capability_profile_engine",
    "system_contract_golden_engine",
    "toolchain_runtime_artifact_engine",
    "incremental_rtl_binding_engine",
    "simulation_performance_attribution_engine",
    "memory_path_contract_engine",
    "fabric_contract_engine",
    "sync_atomic_contract_engine",
    "architecture_rewrite_loop_controller",
    "gpgpusim-inspired",
]

SHARED_DIRS = [
    "examples",
    "flow",
    "references",
    "schemas",
    "tables",
    "templates",
    "tests",
]

SHARED_EXAMPLE_DIRS = [
    "self_correcting_minimal_simt",
    "self_correcting_minimal_simt_core",
    "self_correcting_single_sm_warp_pipeline",
    "self_correcting_toolchain_runtime_vertical_slice",
    "self_correcting_multi_sm_memory_path",
    "self_correcting_full_memory_sync_system",
    "self_correcting_atomic_fence_barrier",
]

CAPABILITY_PROFILES = [
    "minimal_simt_core",
    "single_sm_warp_pipeline",
    "toolchain_runtime_vertical_slice",
    "multi_sm_memory_path",
    "full_memory_sync_system",
]

ADVANCED_EXAMPLE_DIRS = [
    "self_correcting_multi_sm_memory_path",
    "self_correcting_full_memory_sync_system",
    "self_correcting_atomic_fence_barrier",
]

ADVANCED_EXAMPLE_ROOT_FILES = [
    "input_request.md",
]

ADVANCED_EXAMPLE_AI_FILES = [
    "expected_arch_ir.yaml",
    "expected_contract_fragment_ir.yaml",
    "expected_system_contract_ir.yaml",
    "expected_golden_contract_model.yaml",
    "expected_incremental_rtl_map.yaml",
    "expected_normalized_trace_ir.yaml",
    "expected_root_cause_report.yaml",
    "expected_rewrite_plan.yaml",
]

EXAMPLE_ROOT = "shared/examples/self_correcting_minimal_simt"

EXAMPLE_ROOT_FILES = [
    "input_request.md",
]

EXAMPLE_LAYER_DIRS = [
    "ai",
    "human",
    "manifests",
]

EXAMPLE_AI_FILES = [
    "input_kernel.asm",
    "expected_design_intent_ir.yaml",
    "expected_arch_ir.yaml",
    "expected_micro_constraint_estimate.yaml",
    "expected_system_contract_ir.yaml",
    "expected_golden_contract_model.yaml",
    "expected_contract_semantics_report_ir.yaml",
    "expected_assembly_ir.yaml",
    "expected_toolchain_artifact_ir.yaml",
    "expected_program_image_ir.yaml",
    "expected_runtime_launch_ir.yaml",
    "expected_loader_contract_ir.yaml",
    "expected_toolchain_smoke_report.yaml",
    "expected_program.hex",
    "expected_disassembly.asm",
    "expected_memory_dump.yaml",
    "expected_incremental_rtl_map.yaml",
    "expected_module_interface_report_ir.yaml",
    "expected_rtl_partial_sim_report_ir.yaml",
    "expected_correctness_gate_report_ir.yaml",
    "expected_pass_evidence_report_ir.yaml",
    "expected_trace_coverage_report_ir.yaml",
    "expected_performance_metric_ir.yaml",
    "expected_regression_fingerprint.yaml",
    "expected_first_divergence_report.yaml",
    "expected_perf_attribution_graph.yaml",
    "expected_root_cause_report.yaml",
    "expected_arch_rewrite_plan.yaml",
    "expected_rewrite_decision_report.yaml",
    "expected_regression_tracking_report.yaml",
]

EXAMPLE_HUMAN_FILES = [
    "DESIGN_BRIEF.zh.md",
    "ARCHITECTURE_DECISION.zh.md",
    "CONTRACT_FREEZE_SUMMARY.zh.md",
    "IMPLEMENTATION_DASHBOARD.zh.md",
    "VALIDATION_DASHBOARD.zh.md",
    "DEBUG_SUMMARY.zh.md",
    "PATCH_CARD.zh.md",
    "REGRESSION_SUMMARY.zh.md",
]

EXAMPLE_MANIFEST_FILES = [
    "expected_artifact_manifest_fast.yaml",
    "expected_artifact_manifest_freeze.yaml",
    "expected_artifact_manifest_debug.yaml",
]

TEMPLATE_DIRS = [
    "ai",
    "human",
]

HUMAN_TEMPLATE_FILES = [
    "design_brief.zh.md",
    "architecture_decision.zh.md",
    "contract_freeze_summary.zh.md",
    "implementation_dashboard.zh.md",
    "validation_dashboard.zh.md",
    "debug_summary.zh.md",
    "patch_card.zh.md",
    "regression_summary.zh.md",
]

AI_TEMPLATE_FILES = [
    "artifact_manifest.en.md",
    "root_cause_report.en.md",
    "rewrite_decision_report.en.md",
]

REFERENCE_LESSONS = [
    "vortex_lessons.yaml",
    "vortex_memory_sync_lessons.yaml",
    "miaow_lessons.yaml",
    "gpgpusim_lessons.yaml",
    "rocket_lessons.yaml",
    "xiangshan_lessons.yaml",
    "vibe_gpu_lessons.yaml",
    "reference_lesson_index.yaml",
]

ROCKET_REFERENCE_SUMMARIES = [
    "README.md",
    "repo_map.md",
    "config_fragment_lessons.md",
    "diplomacy_interface_contract.md",
    "generator_verification.md",
    "mmio_runtime_debug.md",
    "soc_composition.md",
]

ROCKET_RAW_REPORTS = [
    "rocket_config_fragment_lessons.md",
    "rocket_diplomacy_to_gpgpu_interface_contract.md",
    "rocket_generator_verification_to_gpgpu.md",
    "rocket_mmio_runtime_debug_to_gpgpu.md",
    "rocket_repo_map_for_gpgpu.md",
    "rocket_soc_composition_to_gpgpu_system.md",
]

ROCKET_GENERATOR_SCHEMA_OWNERS = [
    "CONFIG_STACK_IR",
    "RESOLVED_CONFIG_IR",
    "SYSTEM_COMPOSITION_IR",
    "NEGOTIATED_INTERFACE_IR",
    "ADAPTER_CONTRACT",
    "PROTOCOL_MONITOR_CONTRACT",
    "MMIO_REGISTER_MAP_IR",
    "DEBUG_COUNTER_CONTRACT",
]

ROCKET_REQUIRED_REGRESSION_CASES = [
    "rocket_style_config_resolution",
    "negotiated_interface_width_adapter",
    "mmio_start_done_fault_smoke",
    "harness_closure_and_compile_only_config",
]

TOP_LEVEL_REQUIRED_TEXT: Dict[str, List[str]] = {
    "gpgpu-arch/SKILL.md": [
        "CONFIG_STACK_IR",
        "RESOLVED_CONFIG_IR",
        "SYSTEM_COMPOSITION_IR",
        "ARCH_IR is generated only after RESOLVED_CONFIG_IR and SYSTEM_COMPOSITION_IR",
        "config owner",
        "override order",
        "derived field",
        "consumer",
        "collateral",
        "MICRO_CONSTRAINT_ESTIMATE_IR",
        "ARCH_IR is a candidate graph",
        "must not emit system contract truth",
        "DESIGN_BRIEF.zh.md",
        "ARCHITECTURE_DECISION.zh.md",
        "ARTIFACT_MANIFEST_IR",
    ],
    "gpgpu-golden/SKILL.md": [
        "GOLDEN_CONTRACT_MODEL",
        "executable reference semantics",
        "must not define independent ISA",
        "instruction encoding truth for assembler/disassembler derivation",
        "CONTRACT_FREEZE_SUMMARY.zh.md",
        "ARTIFACT_MANIFEST_IR",
    ],
    "gpgpu-runtime/SKILL.md": [
        "MMIO_REGISTER_MAP_IR",
        "DEBUG_COUNTER_CONTRACT",
        "START/BUSY/DONE/FAULTED/ACK",
        "discovery",
        "interrupt",
        "fault",
        "TOOLCHAIN_ARTIFACT_IR",
        "PROGRAM_IMAGE_IR",
        "must not define independent ISA",
        "SOURCE_OF_TRUTH_DRIFT",
        "VALIDATION_DASHBOARD.zh.md",
        "PATCH_CARD.zh.md",
        "ARTIFACT_MANIFEST_IR",
    ],
    "gpgpu-rtl/SKILL.md": [
        "NEGOTIATED_INTERFACE_IR",
        "ADAPTER_CONTRACT",
        "PROTOCOL_MONITOR_CONTRACT",
        "raw wire binding is forbidden unless it comes from a negotiated edge",
        "harness closure",
        "unit-test start/finished/timeout",
        "protocol monitor",
        "shadow memory checker",
        "adapter fuzzer",
        "trace sink",
        "compile-only drift evidence",
        "INCREMENTAL_RTL_MAP",
        "TOOLCHAIN_ARTIFACT_IR",
        "module by module",
        "Interface Contract Checker",
        "RTL Partial Simulator",
        "IMPLEMENTATION_DASHBOARD.zh.md",
        "ARTIFACT_MANIFEST_IR",
    ],
    "gpgpu-simppa/SKILL.md": [
        "PROTOCOL_MONITOR_CONTRACT",
        "harness closure",
        "unit-test start/finished/timeout",
        "protocol monitor",
        "shadow memory checker",
        "adapter fuzzer",
        "trace sink",
        "compile-only drift evidence",
        "PERF_ATTRIBUTION_GRAPH",
        "PASS_EVIDENCE_REPORT",
        "CORRECTNESS_GATE_REPORT",
        "REGRESSION_FINGERPRINT",
        "assembler_trace",
        "cycle",
        "contract path",
        "RTL module",
        "VALIDATION_DASHBOARD.zh.md",
        "DEBUG_SUMMARY.zh.md",
        "ARTIFACT_MANIFEST_IR",
    ],
    "gpgpu-loop/SKILL.md": [
        "config drift",
        "missing negotiated edge",
        "missing adapter",
        "missing MMIO semantics",
        "dangling harness port",
        "compile-only config rot",
        "ARCH_REWRITE_PLAN",
        "Architecture Patch",
        "Contract Patch",
        "Toolchain Patch",
        "RTL Patch",
        "PATCH_CARD.zh.md",
        "REGRESSION_SUMMARY.zh.md",
        "ARTIFACT_MANIFEST_IR",
    ],
    "gpgpu-interconnect/SKILL.md": [
        "NEGOTIATED_INTERFACE_IR",
        "ADAPTER_CONTRACT",
        "PROTOCOL_MONITOR_CONTRACT",
        "raw wire binding is forbidden unless it comes from a negotiated edge",
        "width adapter",
        "fragment adapter",
        "source-id adapter",
        "atomic adapter",
        "protocol bridge adapter",
        "SM_TO_MEMORY_FABRIC_IR",
        "NOC_ROUTING_CONTRACT",
        "SM to L2 routing table",
        "request merging across SM",
        "ARTIFACT_MANIFEST_IR",
    ],
    "gpgpu-memory/SKILL.md": [
        "DRAM_CONTROLLER_CONTRACT",
        "CACHE_COHERENCE_MODEL",
        "bank-level parallelism model",
        "cross-SM coherence",
        "ARTIFACT_MANIFEST_IR",
    ],
    "gpgpu-atomic-sync/SKILL.md": [
        "ATOMIC_EXECUTION_MODEL",
        "BARRIER_FENCE_CONTRACT",
        "atomic serialization point",
        "hierarchical barrier and fence semantics",
        "ARTIFACT_MANIFEST_IR",
    ],
}

MIGRATED_REQUIRED_TEXT: Dict[str, List[str]] = {
    "gpgpu-arch/legacy_request_and_candidate_constraints.md": [
        "gpgpu-front-end",
        "gpgpu-architecture-synthesizer",
        "DESIGN_INTENT_IR",
        "ARCH_IR",
        "MICRO_CONSTRAINT_ESTIMATE_IR",
    ],
    "gpgpu-golden/contract_truth_and_state_model.md": [
        "gpgpu-spec-lock",
        "gpgpu-canonical-state-engine",
        "SYSTEM_CONTRACT_IR",
        "GOLDEN_CONTRACT_MODEL",
        "pc_table",
    ],
    "gpgpu-rtl/module_binding_rules.md": [
        "gpgpu-artifact-contract-engine",
        "gpgpu-memory-subsystem",
        "INCREMENTAL_RTL_MAP",
        "load/store queue",
        "Interface Contract Checker",
    ],
    "gpgpu-simppa/legacy_validation_and_trace_constraints.md": [
        "gpgpu-runtime-validator",
        "gpgpu-implementation-validator",
        "NORMALIZED_TRACE_IR",
        "PERF_ATTRIBUTION_GRAPH",
        "pass evidence",
        "first divergence",
    ],
    "gpgpu-loop/legacy_closure_repair_constraints.md": [
        "gpgpu-closure-refinement-engine",
        "ARCH_REWRITE_PLAN",
        "Architecture Patch",
        "Contract Patch",
        "RTL Patch",
    ],
}

REFERENCE_FILES = [
    "gpgpu-arch/legacy_request_and_candidate_constraints.md",
    "gpgpu-arch/capability_profile_and_preset.md",
    "gpgpu-arch/warp_state_contract.md",
    "gpgpu-arch/sm_hierarchy_model.md",
    "gpgpu-arch/imported_evidence_classification.md",
    "gpgpu-arch/sm_issue_gate_contract_gpgpusim.md",
    "gpgpu-arch/non_issue_reason_taxonomy.md",
    "gpgpu-arch/scheduler_visible_state_contract.md",
    "gpgpu-arch/simulator_only_exclusion_rules.md",
    "gpgpu-arch/architecture_performance_attribution_rules.md",
    "gpgpu-golden/contract_truth_and_state_model.md",
    "gpgpu-golden/executable_semantics_rules.md",
    "gpgpu-golden/golden_model_coverage_and_report.md",
    "gpgpu-runtime/isa_table_derivation.md",
    "gpgpu-runtime/assembly_ir_rules.md",
    "gpgpu-runtime/assembler_disassembler_roundtrip.md",
    "gpgpu-runtime/program_image_and_loader_contract.md",
    "gpgpu-runtime/runtime_launch_artifact_rules.md",
    "gpgpu-runtime/toolchain_smoke_gates.md",
    "gpgpu-runtime/memory_coalescing_contract.md",
    "gpgpu-runtime/lsu_instruction_bundle.md",
    "gpgpu-rtl/module_binding_rules.md",
    "gpgpu-rtl/interface_binding_and_checker.md",
    "gpgpu-rtl/partial_simulation_gates.md",
    "gpgpu-rtl/rtl_module_catalog.md",
    "gpgpu-rtl/warp_exec_model.md",
    "gpgpu-rtl/sm_instance_layout.md",
    "gpgpu-simppa/trace_ingestion_and_normalization.md",
    "gpgpu-simppa/correctness_gate_and_mode_selection.md",
    "gpgpu-simppa/differential_correctness_engine.md",
    "gpgpu-simppa/pass_evidence_engine.md",
    "gpgpu-simppa/performance_metric_extractor.md",
    "gpgpu-simppa/bottleneck_graph_builder.md",
    "gpgpu-simppa/root_cause_engine.md",
    "gpgpu-simppa/minimal_trace_window_rules.md",
    "gpgpu-simppa/toolchain_trace_attribution.md",
    "gpgpu-simppa/report_generation_rules.md",
    "gpgpu-simppa/legacy_validation_and_trace_constraints.md",
    "gpgpu-simppa/multi_sm_trace_model.md",
    "gpgpu-simppa/warp_trace_diff.md",
    "gpgpu-loop/rewrite_trigger.md",
    "gpgpu-loop/patch_taxonomy.md",
    "gpgpu-loop/regression_tracking.md",
    "gpgpu-loop/revalidation_routing.md",
    "gpgpu-loop/legacy_closure_repair_constraints.md",
    "gpgpu-interconnect/noc_routing_contract.md",
    "gpgpu-interconnect/sm_to_memory_fabric.md",
    "gpgpu-interconnect/fabric_request_response_contract.md",
    "gpgpu-interconnect/l2_slice_routing_contract.md",
    "gpgpu-interconnect/response_demux_contract.md",
    "gpgpu-interconnect/fabric_queue_backpressure_contract.md",
    "gpgpu-memory/dram_controller_contract.md",
    "gpgpu-memory/cache_coherence_model.md",
    "gpgpu-memory/l1_coalescer_cache_contract.md",
    "gpgpu-memory/mshr_deadlock_guard.md",
    "gpgpu-memory/memory_response_routing.md",
    "gpgpu-memory/lsu_lane_format_contract.md",
    "gpgpu-memory/nonblocking_memory_tag_contract.md",
    "gpgpu-memory/coalescer_response_restore_contract.md",
    "gpgpu-memory/local_memory_bank_contract.md",
    "gpgpu-memory/l1_cache_or_global_adapter_contract.md",
    "gpgpu-memory/l2_cache_slice_contract.md",
    "gpgpu-memory/mshr_replay_contract.md",
    "gpgpu-memory/cache_response_routing_contract.md",
    "gpgpu-memory/memory_visibility_contract.md",
    "gpgpu-atomic-sync/atomic_execution_model.md",
    "gpgpu-atomic-sync/barrier_fence_contract.md",
    "gpgpu-atomic-sync/atomic_serialization_contract.md",
    "gpgpu-atomic-sync/fence_visibility_contract.md",
    "gpgpu-atomic-sync/barrier_phase_contract.md",
    "gpgpu-atomic-sync/wsync_drain_contract.md",
    "gpgpu-golden/contract_fragment_freeze_rules.md",
    "gpgpu-golden/memory_path_executable_semantics.md",
    "gpgpu-golden/sync_atomic_executable_semantics.md",
    "gpgpu-golden/module_twin_model_rules.md",
    "gpgpu-golden/functional_timing_boundary.md",
    "gpgpu-golden/simt_golden_trace_spec.md",
    "gpgpu-golden/memory_transaction_golden_spec.md",
    "gpgpu-golden/atomic_fence_barrier_golden_spec.md",
    "gpgpu-golden/compatibility_profile_contract.md",
    "gpgpu-runtime/launch_descriptor_contract.md",
    "gpgpu-runtime/argument_layout_contract.md",
    "gpgpu-runtime/coalescer_input_trace_generation.md",
    "gpgpu-runtime/compatibility_mapping_rules.md",
    "gpgpu-rtl/rtl_contract_extraction_from_simulator_evidence.md",
    "gpgpu-rtl/observable_trace_contract.md",
    "gpgpu-rtl/counter_tap_point_contract.md",
    "gpgpu-rtl/hardware_rewritten_mechanism_checklist.md",
    "gpgpu-rtl/simulator_artifact_rejection_checklist.md",
    "gpgpu-simppa/counter_manifest_contract.md",
    "gpgpu-simppa/producer_audit.md",
    "gpgpu-simppa/stall_reason_matrix.md",
    "gpgpu-simppa/memory_attribution_matrix.md",
    "gpgpu-simppa/queue_boundary_attribution.md",
    "gpgpu-simppa/power_energy_provenance.md",
    "gpgpu-simppa/root_cause_evidence_rule.md",
    "gpgpu-loop/counter_gated_regression.md",
    "gpgpu-loop/attribution_driven_rewrite_trigger.md",
    "gpgpu-loop/patch_routing_rule.md",
    "gpgpu-loop/config_drift_guard.md",
    "gpgpu-loop/simulator_artifact_guard.md",
    "gpgpu-memory/warp_memory_transaction_contract.md",
    "gpgpu-memory/coalescer_contract.md",
    "gpgpu-memory/shared_memory_bank_conflict_contract.md",
    "gpgpu-memory/l1_cache_status_contract.md",
    "gpgpu-memory/mshr_reservation_fail_contract.md",
    "gpgpu-memory/memory_return_scoreboard_release_contract.md",
    "gpgpu-interconnect/packet_contract.md",
    "gpgpu-interconnect/icnt_backpressure_contract.md",
    "gpgpu-interconnect/l2_subpartition_queue_contract.md",
    "gpgpu-interconnect/dram_scheduler_boundary_contract.md",
    "gpgpu-interconnect/address_mapping_evidence_contract.md",
    "gpgpu-interconnect/return_path_contract.md",
    "gpgpu-atomic-sync/atomic_operation_contract.md",
    "gpgpu-atomic-sync/fence_scope_visibility_contract.md",
    "gpgpu-atomic-sync/cta_barrier_contract.md",
    "gpgpu-atomic-sync/memory_ordering_litmus_tests.md",
    "gpgpu-atomic-sync/synchronization_stall_attribution.md",
]

CAPABILITY_REQUIRED_TEXT: Dict[str, List[str]] = {
    "gpgpu-arch/capability_profile_and_preset.md": [
        "minimal_simt_core",
        "single_sm_warp_pipeline",
        "toolchain_runtime_vertical_slice",
        "multi_sm_memory_path",
        "full_memory_sync_system",
        "capability_profile",
    ],
    "gpgpu-arch/warp_state_contract.md": [
        "ACTIVE",
        "PENDING",
        "STALLED",
        "WAITING_MEMORY",
        "DIVERGED",
        "RECONVERGING",
        "RETIRED",
        "EXEC mask evolution rules",
        "branch divergence model",
        "reconvergence stack",
    ],
    "gpgpu-arch/sm_hierarchy_model.md": [
        "SM is the canonical execution island",
        "Warp pool",
        "SIMD lanes",
        "LDS",
        "LSU",
        "Issue Arbiter",
        "no shared execution state across SM",
    ],
    "gpgpu-rtl/warp_exec_model.md": [
        "Execution Granularity",
        "warp = 32/64 threads",
        "VGPR bank",
        "SGPR bank",
        "EXEC mask register",
        "VCC/SCC flags",
        "EXEC-mask driven SIMD gating",
        "per-warp context switching",
        "scoreboard interaction with EXEC mask",
    ],
    "gpgpu-rtl/sm_instance_layout.md": [
        "SM contains",
        "N SIMD lanes",
        "Warp pool",
        "LSU front-end",
        "LDS SRAM",
        "SM_ID routing rule",
        "warp dispatch mapping",
        "no cross-SM dependency",
    ],
    "gpgpu-runtime/memory_coalescing_contract.md": [
        "Coalescing Rules",
        "lanes with contiguous addresses",
        "aligned accesses",
        "bank conflict",
        "divergence",
        "warp memory bundle formation BEFORE issue",
        "not per-instruction LSQ only",
    ],
    "gpgpu-runtime/lsu_instruction_bundle.md": [
        "MEMORY_BUNDLE",
        "address vector",
        "lane mask",
        "access type",
        "decode stage emits MEMORY_BUNDLE",
    ],
    "gpgpu-simppa/multi_sm_trace_model.md": [
        "SM-level trace partitioning",
        "warp interleaving model",
        "memory ordering per SM",
        "multi-SM independence",
    ],
    "gpgpu-simppa/warp_trace_diff.md": [
        "EXEC mask diff",
        "warp state diff",
        "divergence path diff",
        "instruction trace diff is insufficient",
    ],
    "gpgpu-interconnect/fabric_request_response_contract.md": [
        "source_sm_id",
        "request_tag",
        "traffic_class",
        "target_l2_slice_id",
        "source_request_tag",
        "final_eop",
    ],
    "gpgpu-interconnect/l2_slice_routing_contract.md": [
        "SM to L2 routing table",
        "arbitration policy",
        "latency model",
        "congestion model",
        "memory request queue per SM",
    ],
    "gpgpu-memory/lsu_lane_format_contract.md": [
        "lsu_lane_request",
        "per_lane_addr",
        "byte_enable",
        "store_data_shifted",
        "load_format_rule",
    ],
    "gpgpu-memory/nonblocking_memory_tag_contract.md": [
        "nonblocking_memory_tag",
        "allocated_on: accepted_load_or_atomic_request",
        "released_on: final_core_visible_response_eop",
        "response_restore_context",
    ],
    "gpgpu-memory/coalescer_response_restore_contract.md": [
        "coalescer correctness = request merge correctness + response restore correctness",
        "COALESCER_RESPONSE_SHAPE_MISMATCH",
        "final_eop",
    ],
    "gpgpu-memory/local_memory_bank_contract.md": [
        "local_memory_bank",
        "bank_mapping_function",
        "read_during_write_policy",
        "response_hold_register",
    ],
    "gpgpu-memory/l2_cache_slice_contract.md": [
        "l2_cache_slice",
        "mshr_id",
        "response_demux_target",
    ],
    "gpgpu-memory/mshr_replay_contract.md": [
        "mshr_replay_contract",
        "fill_completion_event",
        "mshr_deadlock_guard",
    ],
    "gpgpu-atomic-sync/atomic_serialization_contract.md": [
        "serialization_point",
        "serialization_sequence",
        "visibility_event",
        "response_to_warp",
    ],
    "gpgpu-atomic-sync/fence_visibility_contract.md": [
        "fence_visibility",
        "drain_begin_event",
        "drain_end_event",
        "completion_condition",
    ],
    "gpgpu-atomic-sync/barrier_phase_contract.md": [
        "barrier_phase",
        "arrival_bitmap",
        "release_bitmap",
        "lsu_drain_required",
    ],
    "gpgpu-atomic-sync/wsync_drain_contract.md": [
        "WSYNC is prior-work drain",
        "prior_work_count",
        "pending_memory_ops",
        "release_event",
    ],
    "gpgpu-golden/contract_fragment_freeze_rules.md": [
        "contract_fragment_ir",
        "SYSTEM_CONTRACT_IR",
        "executable golden model",
        "only from SYSTEM_CONTRACT_IR",
    ],
}

FORBIDDEN_CAPABILITY_PHRASES = [
    "L3 contract layer",
    "L4 system memory",
    "L3/L4 upgrade",
    "L3 designs",
    "L4 designs",
]

ALLOWED_CACHE_PHRASES = [
    "L1 cache",
    "L2 cache",
    "SM to L2 routing",
    "L2 cache slice",
    "L2 slice",
    "L1/global adapter",
]


def require(path: Path, failures: List[str]) -> None:
    if not path.exists():
        failures.append(f"missing: {path.relative_to(ROOT)}")


def require_nonempty(path: Path, failures: List[str]) -> None:
    require(path, failures)
    if path.exists() and not path.read_text(encoding="utf-8").strip():
        failures.append(f"empty: {path.relative_to(ROOT)}")


def require_text(path: Path, needles: List[str], failures: List[str]) -> None:
    require(path, failures)
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            failures.append(f"missing text {needle!r} in {path.relative_to(ROOT)}")


def require_exact_file_names(path: Path, allowed_names: List[str], failures: List[str]) -> None:
    require(path, failures)
    if not path.exists():
        return
    allowed = set(allowed_names)
    actual = {child.name for child in path.iterdir() if child.is_file()}
    for name in sorted(actual - allowed):
        failures.append(f"unexpected file in {path.relative_to(ROOT)}: {name}")


def require_exact_dir_names(path: Path, allowed_names: List[str], failures: List[str]) -> None:
    require(path, failures)
    if not path.exists():
        return
    allowed = set(allowed_names)
    actual = {child.name for child in path.iterdir() if child.is_dir() and child.name != "__pycache__"}
    for name in sorted(actual - allowed):
        failures.append(f"unexpected directory in {path.relative_to(ROOT)}: {name}")


def load_yaml(rel_path: str, failures: List[str]):
    path = ROOT / rel_path
    require(path, failures)
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        failures.append(f"invalid yaml in {rel_path}: {exc}")
        return {}


def require_shared_yaml_parse(failures: List[str]) -> None:
    for path in sorted((ROOT / "shared").rglob("*.yaml")):
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            failures.append(f"invalid yaml in {path.relative_to(ROOT)}: {exc}")


def require_rocket_reference_assets(failures: List[str]) -> None:
    rocket_root = ROOT / "shared" / "references" / "rocket"
    raw_root = rocket_root / "raw"
    for filename in ROCKET_REFERENCE_SUMMARIES:
        require_nonempty(rocket_root / filename, failures)
    for filename in ROCKET_RAW_REPORTS:
        require_nonempty(raw_root / filename, failures)


def require_rocket_lessons(failures: List[str]) -> None:
    lessons_yaml = load_yaml("shared/references/rocket_lessons.yaml", failures)
    lesson_entries = lessons_yaml.get("lessons") or []
    if not lesson_entries:
        failures.append("rocket_lessons.yaml must define at least one lesson")
        return

    required_fields = ["applies_to", "do", "do_not", "evidence_anchor"]
    lesson_ids = set()
    for entry in lesson_entries:
        lesson_id = entry.get("lesson_id")
        if not lesson_id:
            failures.append("rocket_lessons.yaml lesson missing lesson_id")
            continue
        if lesson_id in lesson_ids:
            failures.append(f"rocket_lessons.yaml duplicate lesson_id {lesson_id!r}")
        lesson_ids.add(lesson_id)
        for field in required_fields:
            value = entry.get(field)
            if not value:
                failures.append(
                    f"rocket lesson {lesson_id!r} missing required field {field!r}"
                )

    for lesson_id in [
        "ROCKET_CONFIG_FRAGMENT_STACK",
        "ROCKET_RESOLVED_CONFIG_COLLATERAL",
        "ROCKET_SYSTEM_COMPOSITION_ROOT",
        "ROCKET_NEGOTIATED_INTERFACE_EDGE",
        "ROCKET_INTERFACE_ADAPTER_CONTRACT",
        "ROCKET_PROTOCOL_MONITOR_CONTRACT",
        "ROCKET_MMIO_REGISTER_MAP",
        "ROCKET_DEBUG_COUNTER_CONTRACT",
        "ROCKET_HARNESS_CLOSURE_GATE",
        "ROCKET_COMPILE_ONLY_DRIFT_GATE",
    ]:
        if lesson_id not in lesson_ids:
            failures.append(f"rocket_lessons.yaml missing lesson_id {lesson_id!r}")


def require_rocket_regression_cases(failures: List[str]) -> None:
    discovered = set()
    for cases_path in sorted((ROOT / "shared" / "tests").glob("*/cases.yaml")):
        cases_yaml = load_yaml(str(cases_path.relative_to(ROOT)), failures)
        for case in cases_yaml.get("cases") or []:
            case_id = case.get("case_id")
            if case_id:
                discovered.add(case_id)

    for case_id in ROCKET_REQUIRED_REGRESSION_CASES:
        if case_id not in discovered:
            failures.append(f"missing Rocket regression case {case_id!r}")


def require_rocket_schema_owner_references(failures: List[str]) -> None:
    skill_text = "\n".join(
        (ROOT / skill / "SKILL.md").read_text(encoding="utf-8")
        for skill in TOP_LEVEL_SKILLS
        if (ROOT / skill / "SKILL.md").exists()
    )
    for schema_owner in ROCKET_GENERATOR_SCHEMA_OWNERS:
        if schema_owner not in skill_text:
            failures.append(
                f"new Rocket-derived schema {schema_owner!r} is not referenced by an owner skill"
            )


def require_all_present(required_fields: List[str], data: dict, rel_path: str, failures: List[str]) -> None:
    for field in required_fields:
        if field not in data:
            failures.append(f"{rel_path} missing schema required field {field!r}")


def require_visibility_policy(failures: List[str]) -> None:
    output_modes = load_yaml("shared/tables/output_mode_table.yaml", failures)
    modes = output_modes.get("modes") or {}
    expected_modes = {"FAST_ITERATION", "CONTRACT_FREEZE", "DEBUG_REGRESSION"}
    if set(modes.keys()) != expected_modes:
        failures.append("output_mode_table.yaml must define exactly FAST_ITERATION, CONTRACT_FREEZE, DEBUG_REGRESSION")

    expected_max = {
        "FAST_ITERATION": 5,
        "CONTRACT_FREEZE": 4,
        "DEBUG_REGRESSION": 4,
    }
    for mode, max_reports in expected_max.items():
        mode_rule = modes.get(mode) or {}
        if mode_rule.get("max_human_visible_reports") != max_reports:
            failures.append(f"{mode} max_human_visible_reports must be {max_reports}")
        human_visible = mode_rule.get("human_visible") or []
        failure_human_visible = mode_rule.get("failure_human_visible") or []
        if len(human_visible) > max_reports:
            failures.append(f"{mode} exposes too many default human reports")
        if len(human_visible) + len(failure_human_visible) > max_reports:
            failures.append(f"{mode} exposes too many human reports including failure reports")
        for report in human_visible + failure_human_visible:
            if not report.endswith(".zh.md"):
                failures.append(f"{mode} human report must use .zh.md suffix: {report}")
        for artifact in mode_rule.get("ai_required") or []:
            if artifact.endswith(".zh.md"):
                failures.append(f"{mode} ai_required must not contain human report {artifact}")

    language_policy = load_yaml("shared/tables/report_language_policy.yaml", failures)
    if (language_policy.get("human_reports") or {}).get("language") != "zh-CN":
        failures.append("human_reports language must be zh-CN")
    if (language_policy.get("ai_artifacts") or {}).get("language") != "en-US":
        failures.append("ai_artifacts language must be en-US")

    visibility_table = load_yaml("shared/tables/artifact_visibility_table.yaml", failures)
    classes = visibility_table.get("visibility_classes") or {}
    expected_classes = {
        "HUMAN_REQUIRED": ("zh-CN", True),
        "HUMAN_OPTIONAL": ("zh-CN", False),
        "AI_REQUIRED": ("en-US", False),
        "DEBUG_ONLY": ("en-US", False),
        "INTERNAL_CACHE": ("en-US", False),
    }
    for class_name, (language, default_show) in expected_classes.items():
        rule = classes.get(class_name) or {}
        if rule.get("language") != language:
            failures.append(f"{class_name} language must be {language}")
        if rule.get("default_show_to_human") != default_show:
            failures.append(f"{class_name} default_show_to_human must be {default_show}")


def require_templates(failures: List[str]) -> None:
    require_exact_dir_names(ROOT / "shared" / "templates", TEMPLATE_DIRS, failures)
    require_exact_dir_names(ROOT / "shared" / "templates" / "human", ["zh"], failures)
    require_exact_dir_names(ROOT / "shared" / "templates" / "ai", ["en"], failures)
    require_exact_file_names(ROOT / "shared" / "templates" / "human" / "zh", HUMAN_TEMPLATE_FILES, failures)
    require_exact_file_names(ROOT / "shared" / "templates" / "ai" / "en", AI_TEMPLATE_FILES, failures)

    template_table = load_yaml("shared/tables/human_report_template_table.yaml", failures)
    templates = template_table.get("templates") or {}
    for report_type, rule in templates.items():
        path = ROOT / rule.get("path", "")
        require_nonempty(path, failures)
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for section in rule.get("required_sections") or []:
            if f"## {section}" not in text:
                failures.append(f"{rule.get('path')} missing required section {section!r}")
        if not rule.get("source_ai_artifacts"):
            failures.append(f"human report template {report_type} missing source_ai_artifacts")


def require_layered_example(failures: List[str]) -> None:
    example_root = ROOT / EXAMPLE_ROOT
    require_exact_file_names(example_root, EXAMPLE_ROOT_FILES, failures)
    require_exact_dir_names(example_root, EXAMPLE_LAYER_DIRS, failures)
    require_exact_file_names(example_root / "ai", EXAMPLE_AI_FILES, failures)
    require_exact_file_names(example_root / "human", EXAMPLE_HUMAN_FILES, failures)
    require_exact_file_names(example_root / "manifests", EXAMPLE_MANIFEST_FILES, failures)

    for filename in EXAMPLE_ROOT_FILES:
        require_nonempty(example_root / filename, failures)
    for filename in EXAMPLE_AI_FILES:
        require_nonempty(example_root / "ai" / filename, failures)
    for filename in EXAMPLE_HUMAN_FILES:
        path = example_root / "human" / filename
        require_text(path, ["# ", "Source AI artifacts:"], failures)
        if not filename.endswith(".zh.md"):
            failures.append(f"human example must use .zh.md suffix: {filename}")
    for filename in EXAMPLE_MANIFEST_FILES:
        require_nonempty(example_root / "manifests" / filename, failures)


def require_capability_examples(failures: List[str]) -> None:
    for example_dir in ADVANCED_EXAMPLE_DIRS:
        example_root = ROOT / "shared" / "examples" / example_dir
        require_exact_file_names(example_root, ADVANCED_EXAMPLE_ROOT_FILES, failures)
        require_exact_dir_names(example_root, ["ai"], failures)
        require_exact_file_names(example_root / "ai", ADVANCED_EXAMPLE_AI_FILES, failures)
        for filename in ADVANCED_EXAMPLE_ROOT_FILES:
            require_nonempty(example_root / filename, failures)
        for filename in ADVANCED_EXAMPLE_AI_FILES:
            require_nonempty(example_root / "ai" / filename, failures)


def require_manifest_consistency(failures: List[str]) -> None:
    output_modes = load_yaml("shared/tables/output_mode_table.yaml", failures)
    mode_rules = output_modes.get("modes") or {}
    allowed_visibilities = {"HUMAN_REQUIRED", "HUMAN_OPTIONAL", "AI_REQUIRED", "DEBUG_ONLY", "INTERNAL_CACHE"}

    for filename in EXAMPLE_MANIFEST_FILES:
        rel_path = f"{EXAMPLE_ROOT}/manifests/{filename}"
        manifest = load_yaml(rel_path, failures)
        output_mode = manifest.get("output_mode")
        if output_mode not in mode_rules:
            failures.append(f"{rel_path} has unknown output_mode {output_mode!r}")
            continue

        ai_artifacts = manifest.get("ai_artifacts") or []
        human_reports = manifest.get("human_reports") or []
        max_reports = (mode_rules.get(output_mode) or {}).get("max_human_visible_reports")
        if max_reports is not None and len(human_reports) > max_reports:
            failures.append(f"{rel_path} exposes {len(human_reports)} human reports, max is {max_reports}")

        ai_names = set()
        for artifact in ai_artifacts:
            name = artifact.get("artifact_name")
            ai_names.add(name)
            if artifact.get("language") != "en-US":
                failures.append(f"{rel_path} AI artifact {name!r} must use language en-US")
            if artifact.get("visibility") not in allowed_visibilities - {"HUMAN_REQUIRED", "HUMAN_OPTIONAL"}:
                failures.append(f"{rel_path} AI artifact {name!r} has invalid visibility {artifact.get('visibility')!r}")
            if not artifact.get("producer_skill"):
                failures.append(f"{rel_path} AI artifact {name!r} missing producer_skill")
            if not artifact.get("content_hash"):
                failures.append(f"{rel_path} AI artifact {name!r} missing content_hash")
            artifact_path = ROOT / str(artifact.get("path", ""))
            require(artifact_path, failures)
            if artifact_path.exists() and artifact_path.suffix == ".md" and not artifact_path.name.endswith(".en.md"):
                failures.append(f"{rel_path} AI markdown artifact must use .en.md suffix: {artifact_path.relative_to(ROOT)}")

        for report in human_reports:
            report_name = report.get("report_name")
            if report.get("language") != "zh-CN":
                failures.append(f"{rel_path} human report {report_name!r} must use language zh-CN")
            if report.get("visibility") not in {"HUMAN_REQUIRED", "HUMAN_OPTIONAL"}:
                failures.append(f"{rel_path} human report {report_name!r} has invalid visibility {report.get('visibility')!r}")
            source_artifacts = report.get("source_artifacts") or []
            if not source_artifacts:
                failures.append(f"{rel_path} human report {report_name!r} missing source_artifacts")
            for source in source_artifacts:
                if source not in ai_names:
                    failures.append(f"{rel_path} human report {report_name!r} references missing AI artifact {source!r}")
            report_path = ROOT / str(report.get("path", ""))
            require(report_path, failures)
            if report_path.exists() and not report_path.name.endswith(".zh.md"):
                failures.append(f"{rel_path} human report must use .zh.md suffix: {report_path.relative_to(ROOT)}")


def require_asset_semantics(failures: List[str]) -> None:
    root_cause_taxonomy = load_yaml("shared/tables/root_cause_taxonomy.yaml", failures)
    root_causes = set((root_cause_taxonomy.get("root_causes") or {}).keys())

    rewrite_trigger_table = load_yaml("shared/tables/rewrite_trigger_table.yaml", failures)
    rewrite_triggers = set((rewrite_trigger_table.get("triggers") or {}).keys())

    patch_taxonomy = load_yaml("shared/tables/patch_taxonomy_table.yaml", failures)
    patch_classes = patch_taxonomy.get("patch_classes") or {}
    patch_types = set(patch_classes.keys())

    root_cause_schema = load_yaml("shared/schemas/root_cause_report_ir.schema.yaml", failures)
    schema_root_causes = set(root_cause_schema.get("classes") or [])
    if schema_root_causes and schema_root_causes != root_causes:
        failures.append(
            "root_cause_report_ir.schema.yaml classes must match root_cause_taxonomy.yaml"
        )

    for root_cause in sorted(rewrite_triggers - root_causes):
        failures.append(f"rewrite trigger has unknown root cause {root_cause!r}")

    for root_cause, rule in (rewrite_trigger_table.get("triggers") or {}).items():
        for patch_type in rule.get("patch_options") or []:
            if patch_type not in patch_types:
                failures.append(
                    f"rewrite trigger {root_cause!r} references unknown patch type {patch_type!r}"
                )

    for root_cause, rule in (root_cause_taxonomy.get("root_causes") or {}).items():
        patch_type = rule.get("rewrite_candidate")
        if patch_type and patch_type not in patch_types:
            failures.append(
                f"root cause {root_cause!r} references unknown rewrite_candidate {patch_type!r}"
            )

    perf_graph = load_yaml(
        "shared/examples/self_correcting_minimal_simt/ai/expected_perf_attribution_graph.yaml",
        failures,
    )
    perf_graph_schema = load_yaml("shared/schemas/perf_attribution_graph.schema.yaml", failures)
    require_all_present(
        perf_graph_schema.get("required") or [],
        perf_graph,
        "shared/examples/self_correcting_minimal_simt/ai/expected_perf_attribution_graph.yaml",
        failures,
    )
    graph_root_cause = (
        (perf_graph.get("bottleneck_summary") or {}).get("root_cause_class")
    )
    graph_root_subclass = (
        (perf_graph.get("bottleneck_summary") or {}).get("root_cause_subclass")
    )
    if graph_root_cause and graph_root_cause not in root_causes:
        failures.append(
            "expected_perf_attribution_graph.yaml uses unknown root_cause_class "
            f"{graph_root_cause!r}"
        )
    if graph_root_cause and graph_root_subclass:
        subclasses = (
            (root_cause_taxonomy.get("root_causes") or {})
            .get(graph_root_cause, {})
            .get("subclasses")
            or []
        )
        if graph_root_subclass not in subclasses:
            failures.append(
                "expected_perf_attribution_graph.yaml uses unknown root_cause_subclass "
                f"{graph_root_cause}/{graph_root_subclass}"
            )

    rewrite_plan = load_yaml(
        "shared/examples/self_correcting_minimal_simt/ai/expected_arch_rewrite_plan.yaml",
        failures,
    )
    arch_rewrite_schema = load_yaml("shared/schemas/arch_rewrite_plan.schema.yaml", failures)
    require_all_present(
        arch_rewrite_schema.get("required") or [],
        rewrite_plan,
        "shared/examples/self_correcting_minimal_simt/ai/expected_arch_rewrite_plan.yaml",
        failures,
    )
    trigger_root_cause = rewrite_plan.get("trigger_root_cause")
    trigger_root_subclass = rewrite_plan.get("trigger_root_cause_subclass")
    if trigger_root_cause and trigger_root_cause not in root_causes:
        failures.append(
            "expected_arch_rewrite_plan.yaml uses unknown trigger_root_cause "
            f"{trigger_root_cause!r}"
        )
    if trigger_root_cause and trigger_root_cause not in rewrite_triggers:
        failures.append(
            "expected_arch_rewrite_plan.yaml trigger_root_cause has no rewrite trigger "
            f"{trigger_root_cause!r}"
        )
    if trigger_root_cause and trigger_root_subclass:
        subclasses = (
            (root_cause_taxonomy.get("root_causes") or {})
            .get(trigger_root_cause, {})
            .get("subclasses")
            or []
        )
        if trigger_root_subclass not in subclasses:
            failures.append(
                "expected_arch_rewrite_plan.yaml uses unknown trigger_root_cause_subclass "
                f"{trigger_root_cause}/{trigger_root_subclass}"
            )
    plan_patch_type = rewrite_plan.get("patch_type")
    if plan_patch_type and plan_patch_type not in patch_types:
        failures.append(
            f"expected_arch_rewrite_plan.yaml uses unknown patch_type {plan_patch_type!r}"
        )

    stale_root_cause = "MEMORY_IMBALANCE"
    stale_scan_paths = [
        "shared/examples/self_correcting_minimal_simt/ai/expected_perf_attribution_graph.yaml",
        "shared/examples/self_correcting_minimal_simt/ai/expected_arch_rewrite_plan.yaml",
        "shared/tests/architecture_rewrite_loop_controller/cases.yaml",
    ]
    for rel_path in stale_scan_paths:
        path = ROOT / rel_path
        if path.exists() and stale_root_cause in path.read_text(encoding="utf-8"):
            failures.append(f"stale root cause {stale_root_cause!r} in {rel_path}")

    toolchain_examples = set((patch_classes.get("TOOLCHAIN_PATCH") or {}).get("examples") or [])
    runtime_forbidden = {
        "runtime_arg_encoding_fix",
        "runtime_arg_buffer_fix",
        "csr_launch_sequence_fix",
        "completion_fault_observation_fix",
    }
    for example in sorted(toolchain_examples & runtime_forbidden):
        failures.append(
            "TOOLCHAIN_PATCH example crosses runtime boundary: "
            f"{example}"
        )

    runtime_patch = patch_classes.get("RUNTIME_PATCH") or {}
    runtime_examples = set(runtime_patch.get("examples") or [])
    for required_example in [
        "runtime_arg_buffer_fix",
        "csr_launch_sequence_fix",
        "completion_fault_observation_fix",
    ]:
        if required_example not in runtime_examples:
            failures.append(f"RUNTIME_PATCH missing example {required_example!r}")

    runtime_trigger = (rewrite_trigger_table.get("triggers") or {}).get(
        "RUNTIME_LAUNCH_ROOT_CAUSE"
    ) or {}
    if runtime_trigger.get("patch_options") != ["RUNTIME_PATCH"]:
        failures.append(
            "RUNTIME_LAUNCH_ROOT_CAUSE must route only to RUNTIME_PATCH"
        )

    revalidation_routing = load_yaml("shared/tables/revalidation_routing_table.yaml", failures)
    toolchain_route = (
        (revalidation_routing.get("routes") or {}).get("TOOLCHAIN_PATCH") or {}
    )
    if "runtime_launch_smoke" in (toolchain_route.get("required_gates") or []):
        failures.append("TOOLCHAIN_PATCH route must not require runtime_launch_smoke")
    toolchain_root_route = (
        (revalidation_routing.get("root_cause_to_patch_route") or {})
        .get("TOOLCHAIN_ROOT_CAUSE")
        or {}
    )
    if "runtime_launch_smoke" in (toolchain_root_route.get("revalidation") or []):
        failures.append(
            "TOOLCHAIN_ROOT_CAUSE route must not require runtime_launch_smoke"
        )
    if plan_patch_type:
        patch_route = (revalidation_routing.get("routes") or {}).get(plan_patch_type) or {}
        route_gates = set(patch_route.get("required_gates") or [])
        for gate in rewrite_plan.get("required_revalidation_gates") or []:
            if gate not in route_gates:
                failures.append(
                    "expected_arch_rewrite_plan.yaml required_revalidation_gates "
                    f"contains gate not in {plan_patch_type} route: {gate!r}"
                )

    root_cause_subclasses = {
        subclass
        for rule in (root_cause_taxonomy.get("root_causes") or {}).values()
        for subclass in (rule.get("subclasses") or [])
    }
    for root_cause, route in (revalidation_routing.get("root_cause_to_patch_route") or {}).items():
        if root_cause not in root_causes and root_cause not in root_cause_subclasses:
            failures.append(
                f"revalidation route has unknown root cause {root_cause!r}"
            )
        patch_type = route.get("patch_type")
        if patch_type and patch_type not in patch_types:
            failures.append(
                f"revalidation route {root_cause!r} references unknown patch type {patch_type!r}"
            )

    perf_arch_requires = (
        (root_cause_taxonomy.get("root_causes") or {})
        .get("PERFORMANCE_ARCH_ROOT_CAUSE", {})
        .get("requires")
        or []
    )
    for required_evidence in [
        "performance_metric_ref",
        "perf_attribution_graph_ref",
        "contract_paths",
        "rtl_module_paths",
        "bottleneck_cycle_window",
        "counter_evidence",
        "alternative_patch_rejection",
    ]:
        if required_evidence not in perf_arch_requires:
            failures.append(
                "PERFORMANCE_ARCH_ROOT_CAUSE missing required evidence "
                f"{required_evidence!r}"
            )

    arch_required = set(arch_rewrite_schema.get("required") or [])
    if "rejected_alternatives" not in arch_required:
        failures.append("arch_rewrite_plan.schema.yaml must require rejected_alternatives")
    if "rejected_alternatives" not in rewrite_plan:
        failures.append("expected_arch_rewrite_plan.yaml missing rejected_alternatives")

    regression_schema = load_yaml(
        "shared/schemas/regression_tracking_report_ir.schema.yaml",
        failures,
    )
    regression_required = set(regression_schema.get("required") or [])
    for field in [
        "same_patch_attempt_count",
        "last_patch_type",
        "last_owner_module",
        "worsened_gates",
        "rollback_required",
        "escalation_policy",
    ]:
        if field not in regression_required:
            failures.append(
                "regression_tracking_report_ir.schema.yaml missing required field "
                f"{field!r}"
            )

    if "PASS_EVIDENCE_PATCH" not in patch_classes:
        failures.append("PASS_EVIDENCE_PATCH must remain in patch taxonomy")

    expected_root_causes = {
        "MEMORY_PATH_ROOT_CAUSE",
        "FABRIC_ROOT_CAUSE",
        "CACHE_MSHR_ROOT_CAUSE",
        "DRAM_ROOT_CAUSE",
        "SYNC_ATOMIC_ROOT_CAUSE",
    }
    for root_cause in sorted(expected_root_causes - root_causes):
        failures.append(f"missing advanced root cause class {root_cause!r}")

    expected_patch_types = {
        "MEMORY_PATH_PATCH": "gpgpu-memory",
        "FABRIC_PATCH": "gpgpu-interconnect",
        "SYNC_ATOMIC_PATCH": "gpgpu-atomic-sync",
        "GOLDEN_SEMANTICS_PATCH": "gpgpu-golden",
        "RTL_BINDING_PATCH": "gpgpu-rtl",
    }
    for patch_type, owner in expected_patch_types.items():
        patch_rule = patch_classes.get(patch_type) or {}
        if patch_type not in patch_classes:
            failures.append(f"missing patch type {patch_type!r}")
        elif patch_rule.get("owner") != owner:
            failures.append(f"{patch_type} owner must be {owner}")

    expected_routes = {
        "COALESCER_RESPONSE_SHAPE_MISMATCH": "MEMORY_PATH_PATCH",
        "L2_SLICE_ROUTE_MISMATCH": "FABRIC_PATCH",
        "MSHR_REPLAY_MISMATCH": "MEMORY_PATH_PATCH",
        "ATOMIC_SERIALIZATION_MISMATCH": "SYNC_ATOMIC_PATCH",
        "FENCE_DRAIN_INCOMPLETE": "SYNC_ATOMIC_PATCH",
    }
    root_routes = revalidation_routing.get("root_cause_to_patch_route") or {}
    for route_name, patch_type in expected_routes.items():
        route = root_routes.get(route_name) or {}
        if route.get("patch_type") != patch_type:
            failures.append(f"{route_name} must route to {patch_type}")

    normalized_trace = load_yaml("shared/schemas/normalized_trace_ir.schema.yaml", failures)
    event_optional = set(((normalized_trace.get("event_schema") or {}).get("optional")) or [])
    for field in [
        "instruction_uuid",
        "coalesced_tag",
        "restored_lane_mask",
        "final_eop",
        "l1_cache_id",
        "l2_slice_id",
        "cache_bank_id",
        "mshr_id",
        "fabric_route_id",
        "virtual_channel",
        "dram_channel_id",
        "dram_bank_id",
        "dram_row_id",
        "queue_occupancy",
        "arbitration_wait_cycles",
        "serialization_point",
        "serialization_sequence",
        "fence_scope",
        "visibility_event",
        "barrier_id",
        "barrier_phase",
        "arrival_bitmap",
        "release_bitmap",
    ]:
        if field not in event_optional:
            failures.append(f"normalized_trace_ir.schema.yaml missing trace field {field!r}")

    event_dictionary = set(normalized_trace.get("event_types") or [])
    for event_type in [
        "lsu_lane_format",
        "memory_tag_allocate",
        "memory_tag_release",
        "coalescer_merge",
        "coalescer_restore",
        "l1_cache_hit",
        "l1_cache_miss",
        "l2_slice_route",
        "l2_cache_hit",
        "l2_cache_miss",
        "mshr_allocate",
        "mshr_replay",
        "dram_schedule",
        "dram_bank_conflict",
        "atomic_serialize",
        "atomic_visibility",
        "fence_drain_begin",
        "fence_drain_end",
        "barrier_arrive",
        "barrier_release",
        "wsync_drain_begin",
        "wsync_drain_end",
    ]:
        if event_type not in event_dictionary:
            failures.append(f"normalized_trace_ir.schema.yaml missing event_type {event_type!r}")


def require_capability_profile_contracts(failures: List[str]) -> None:
    for rel_path, needles in CAPABILITY_REQUIRED_TEXT.items():
        require_text(ROOT / rel_path, needles, failures)

    require_text(
        ROOT / "README.md",
        [
            "SM-centric warp execution contract model",
            "minimal_simt_core",
            "single_sm_warp_pipeline",
            "toolchain_runtime_vertical_slice",
            "multi_sm_memory_path",
            "full_memory_sync_system",
        ],
        failures,
    )

    require_text(
        ROOT / "shared" / "flow" / "gpgpu_design_flow.md",
        [
            "SM-centric warp execution contract model",
            "capability_profile",
            "contract_fragment_ir",
            "multi_sm_memory_path capability",
            "full_memory_sync_system capability",
        ],
        failures,
    )

    for rel_path in [
        "shared/examples/self_correcting_minimal_simt/ai/expected_arch_ir.yaml",
        "shared/examples/self_correcting_minimal_simt/ai/expected_incremental_rtl_map.yaml",
        "shared/examples/self_correcting_minimal_simt/ai/expected_perf_attribution_graph.yaml",
    ]:
        require_text(ROOT / rel_path, ["sm", "warp"], failures)

    require_text(
        ROOT / "shared" / "tables" / "architecture_preset_library.yaml",
        [
            "MINIMAL_SIMT_CORE",
            "SINGLE_SM_WARP_PIPELINE",
            "TOOLCHAIN_RUNTIME_VERTICAL_SLICE",
            "MULTI_SM_MEMORY_PATH",
            "FULL_MEMORY_SYNC_SYSTEM",
            "capability_profile",
        ],
        failures,
    )

    capability_schema = load_yaml("shared/schemas/capability_profile_ir.schema.yaml", failures)
    capability_required = set(capability_schema.get("required") or [])
    for field in ["name", "enabled_subsystems", "preset_id", "provenance"]:
        if field not in capability_required:
            failures.append(f"capability_profile_ir.schema.yaml missing required field {field!r}")

    contract_fragment_schema = load_yaml("shared/schemas/contract_fragment_ir.schema.yaml", failures)
    fragment_required = set(contract_fragment_schema.get("required") or [])
    for field in ["fragment_id", "owner_skill", "capability_profile", "contract_paths", "provenance"]:
        if field not in fragment_required:
            failures.append(f"contract_fragment_ir.schema.yaml missing required field {field!r}")

    for rel_path in [
        "shared/schemas/arch_ir.schema.yaml",
        "shared/schemas/system_contract_ir.schema.yaml",
        "shared/schemas/golden_contract_model.schema.yaml",
        "shared/schemas/arch_rewrite_plan.schema.yaml",
    ]:
        require_text(ROOT / rel_path, ["capability_profile"], failures)

    require_text(ROOT / "shared/schemas/correctness_gate_report_ir.schema.yaml", ["comparison_scope"], failures)
    require_text(ROOT / "shared/tables/correctness_gate_decision_table.yaml", ["comparison_scope"], failures)
    require_text(ROOT / "shared/schemas/performance_metric_ir.schema.yaml", ["metric_groups"], failures)


def require_no_forbidden_capability_terms(failures: List[str]) -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix not in {".md", ".yaml"}:
            continue
        rel_path = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN_CAPABILITY_PHRASES:
            if phrase in text:
                failures.append(f"forbidden capability phrase {phrase!r} in {rel_path}")

    all_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and path.suffix in {".md", ".yaml"}
    )
    for profile in CAPABILITY_PROFILES:
        if profile not in all_text:
            failures.append(f"capability profile {profile!r} is not documented")


def main() -> int:
    failures: List[str] = []

    for skill in TOP_LEVEL_SKILLS:
        skill_dir = ROOT / skill
        require(skill_dir, failures)
        require_text(skill_dir / "SKILL.md", SKILL_SECTIONS, failures)

    for skill in REMOVED_TOP_LEVEL_SKILLS:
        if (ROOT / skill).exists():
            failures.append(f"removed top-level skill still present: {skill}")

    for skill in REMOVED_LEGACY_SKILLS:
        if (ROOT / skill).exists():
            failures.append(f"removed legacy skill still present: {skill}")

    for rel_path in REMOVED_FILES:
        if (ROOT / rel_path).exists():
            failures.append(f"removed v4 asset generator still present: {rel_path}")

    for rel_path in REMOVED_DIRS:
        if (ROOT / rel_path).exists():
            failures.append(f"removed legacy asset directory still present: {rel_path}")

    for rel_root in ACTIVE_STALE_REFERENCE_ROOTS:
        scan_root = ROOT / rel_root
        if not scan_root.exists():
            continue
        for path in scan_root.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for old_skill in REMOVED_TOP_LEVEL_SKILLS:
                if old_skill in text:
                    failures.append(
                        "stale active old-skill reference "
                        f"{old_skill!r} in {path.relative_to(ROOT)}"
                    )

    for schema in NEW_SCHEMAS:
        require_text(ROOT / "shared" / "schemas" / schema, ["required:"], failures)

    for table in NEW_TABLES:
        require_nonempty(ROOT / "shared" / "tables" / table, failures)

    require_exact_dir_names(ROOT / "shared", SHARED_DIRS, failures)
    require_exact_file_names(ROOT / "shared" / "schemas", NEW_SCHEMAS, failures)
    require_exact_file_names(ROOT / "shared" / "tables", NEW_TABLES, failures)
    require_exact_dir_names(ROOT / "shared" / "tests", TEST_DIRS, failures)
    require_exact_dir_names(ROOT / "shared" / "examples", SHARED_EXAMPLE_DIRS, failures)

    for test_dir in TEST_DIRS:
        path = ROOT / "shared" / "tests" / test_dir / "cases.yaml"
        require_text(path, ["case_id:", "expected_outputs:", "required_evidence:"], failures)

    require_visibility_policy(failures)
    require_templates(failures)
    require_layered_example(failures)
    require_capability_examples(failures)
    require_manifest_consistency(failures)

    for rel_path in REFERENCE_FILES:
        require_nonempty(ROOT / rel_path, failures)

    for lesson in REFERENCE_LESSONS:
        require(ROOT / "shared" / "references" / lesson, failures)

    require_shared_yaml_parse(failures)
    require_rocket_reference_assets(failures)
    require_rocket_lessons(failures)
    require_rocket_regression_cases(failures)
    require_rocket_schema_owner_references(failures)

    require_text(
        ROOT / "README.md",
        [
            "self-correcting GPGPU design system",
            "GOLDEN_CONTRACT_MODEL",
            "TOOLCHAIN_ARTIFACT_IR",
            "INCREMENTAL_RTL_MAP",
            "PERF_ATTRIBUTION_GRAPH",
            "ARCH_REWRITE_PLAN",
            "Human-facing reports are written in Chinese",
            "AI-facing artifacts are written in English",
            "Default output mode is `FAST_ITERATION`",
            "former 9-stage top-level GPGPU skills and the old `legacy/` skill archive have been deleted",
        ],
        failures,
    )

    require_text(
        ROOT / "shared" / "flow" / "gpgpu_design_flow.md",
        [
            "Architecture Generator",
            "System Contract + Golden Semantics Engine",
            "Toolchain + Runtime Artifact Engine",
            "Incremental RTL Binding Engine",
            "Simulation + Performance Attribution Engine",
            "Architecture Rewrite Loop Controller",
            "Artifact Visibility Policy",
            "FAST_ITERATION",
            "CONTRACT_FREEZE",
            "DEBUG_REGRESSION",
            "Legacy v4 top-level skills and the old `legacy/` skill archive are not active wrappers",
        ],
        failures,
    )

    for rel_path, needles in TOP_LEVEL_REQUIRED_TEXT.items():
        require_text(ROOT / rel_path, needles, failures)

    for rel_path, needles in MIGRATED_REQUIRED_TEXT.items():
        require_text(ROOT / rel_path, needles, failures)

    require_asset_semantics(failures)
    require_capability_profile_contracts(failures)
    require_no_forbidden_capability_terms(failures)

    if failures:
        print("GPGPU skill v5 self-correcting asset contract failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("GPGPU skill v5 self-correcting asset contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
