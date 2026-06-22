#!/usr/bin/env python3
"""Validate the GPGPU skill v4 repository contract."""

from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[2]

TOP_LEVEL_SKILLS = [
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

LEGACY_SKILLS = [
    "gpgpu-mode-controller",
    "gpgpu-design-intent-lock",
    "gpgpu-deterministic-transform-engine",
    "gpgpu-config",
    "gpgpu-runtime",
    "gpgpu-memory-path",
    "gpgpu-rtl-simt-core",
    "gpgpu-golden-sim",
    "gpgpu-synthesis-closure-engine",
    "gpgpu-causal-trace-analyzer",
]

SKILL_SECTIONS = [
    "## Role",
    "## Position in Flow",
    "## Input IR",
    "## Output IR",
    "## Owned Decisions",
    "## Forbidden Actions",
    "## Required Tables",
    "## Required Schemas",
    "## Required Invariants",
    "## Failure Modes",
    "## Report Schema",
    "## Concrete Assets Required",
]

SCHEMAS = [
    "mode_selection_ir.schema.yaml",
    "design_intent_ir.schema.yaml",
    "arch_candidate_ir.schema.yaml",
    "synthesized_spec_draft.schema.yaml",
    "spec_ir.schema.yaml",
    "gpu_state_ir.schema.yaml",
    "rtl_mapping_ir.schema.yaml",
    "sim_behavior_ir.schema.yaml",
    "runtime_contract_ir.schema.yaml",
    "software_stack_contract_ir.schema.yaml",
    "program_image_contract_ir.schema.yaml",
    "test_app_contract_ir.schema.yaml",
    "memory_model_ir.schema.yaml",
    "config_binding_ir.schema.yaml",
    "memory_subsystem_ir.schema.yaml",
    "validation_plan_ir.schema.yaml",
    "runtime_validation_report_ir.schema.yaml",
    "memory_validation_report_ir.schema.yaml",
    "implementation_validation_report_ir.schema.yaml",
    "first_divergence_report_ir.schema.yaml",
    "synthesis_acceptance_report_ir.schema.yaml",
    "refinement_request_ir.schema.yaml",
]

TABLES = [
    "enum_table.yaml",
    "provenance_table.yaml",
    "mode_decision_table.yaml",
    "architecture_preset_library.yaml",
    "minimal_vertical_slice_preset.yaml",
    "hard_constraint_table.yaml",
    "quality_target_table.yaml",
    "requirement_owner_table.yaml",
    "spec_required_field_table.yaml",
    "source_of_truth_generation_table.yaml",
    "cross_artifact_consistency_table.yaml",
    "software_stack_contract_table.yaml",
    "end_to_end_smoke_test_table.yaml",
    "vertical_slice_validation_table.yaml",
    "initial_state_construction_table.yaml",
    "state_transition_rule_table.yaml",
    "state_invariant_table.yaml",
    "artifact_mapping_table.yaml",
    "config_ownership_table.yaml",
    "state_to_rtl_mapping.yaml",
    "state_to_sim_mapping.yaml",
    "state_to_runtime_mapping.yaml",
    "state_to_memory_mapping.yaml",
    "runtime_smoke_test_table.yaml",
    "memory_address_space_table.yaml",
    "coalescing_rule_table.yaml",
    "shared_memory_bank_table.yaml",
    "memory_ordering_table.yaml",
    "memory_scoreboard_wakeup_table.yaml",
    "rtl_validation_gate_table.yaml",
    "golden_sim_trace_field_table.yaml",
    "first_divergence_taxonomy.yaml",
    "closure_gate_table.yaml",
    "verdict_decision_table.yaml",
    "failure_taxonomy_table.yaml",
    "vibe_failure_taxonomy_table.yaml",
    "repair_routing_table.yaml",
]

TEST_DIRS = [
    "front_end",
    "architecture_synthesizer",
    "spec_lock",
    "state_engine",
    "artifact_contract",
    "runtime_validator",
    "memory_subsystem",
    "implementation_validator",
    "closure_refinement",
]

EXAMPLE_DIRS = [
    "reproduce_minimal_simt",
    "design_minimal_teaching_gpgpu",
    "vibe_minimal_vertical_slice",
]

REFERENCE_LESSONS = [
    "vortex_lessons.yaml",
    "miaow_lessons.yaml",
    "gpgpusim_lessons.yaml",
    "rocket_lessons.yaml",
    "xiangshan_lessons.yaml",
    "vibe_gpu_lessons.yaml",
    "reference_lesson_index.yaml",
]

VIBE_EXAMPLE_FILES = [
    "input_request.md",
    "expected_design_intent_ir.yaml",
    "expected_arch_candidate_ir.yaml",
    "expected_spec_ir.yaml",
    "expected_gpu_state_ir.yaml",
    "expected_artifact_contract_report.yaml",
    "expected_runtime_contract_ir.yaml",
    "expected_memory_subsystem_ir.yaml",
    "expected_validation_plan_ir.yaml",
    "expected_closure_report.yaml",
]

VIBE_REQUIRED_TEXT: Dict[str, List[str]] = {
    "gpgpu-front-end/SKILL.md": [
        "VERTICAL_SLICE_PROTOTYPE",
        "compile_kernel_to_program_image",
    ],
    "gpgpu-architecture-synthesizer/SKILL.md": [
        "MINIMAL_VERTICAL_SLICE_GPGPU",
        "shared/tables/minimal_vertical_slice_preset.yaml",
    ],
    "gpgpu-spec-lock/SKILL.md": [
        "isa_source_of_truth",
        "shared/tables/source_of_truth_generation_table.yaml",
    ],
    "gpgpu-canonical-state-engine/SKILL.md": [
        "pc_table",
        "simt_stack_state",
        "memory_stall_state",
    ],
    "gpgpu-artifact-contract-engine/SKILL.md": [
        "cross_artifact_consistency_gate",
        "declared_test_coverage_gate",
    ],
    "gpgpu-runtime-validator/SKILL.md": [
        "frontend_subset_contract",
        "program_image_contract",
        "golden_output_contract",
    ],
    "gpgpu-memory-subsystem/SKILL.md": [
        "memory_request_lifecycle",
        "duplicate_request_prevention",
    ],
    "gpgpu-implementation-validator/SKILL.md": [
        "app_compile_smoke",
        "memory_dump_compare",
    ],
    "gpgpu-closure-refinement-engine/SKILL.md": [
        "DOC_ARTIFACT_DRIFT",
        "DECLARED_TEST_NOT_RUN",
        "MAGIC_CONSTANT_UNBOUND",
    ],
    "shared/schemas/spec_ir.schema.yaml": ["isa_source_of_truth"],
    "shared/schemas/gpu_state_ir.schema.yaml": [
        "pc_table",
        "exec_mask_table",
        "simt_stack_state",
        "pipeline_registers",
        "memory_stall_state",
    ],
    "shared/schemas/runtime_contract_ir.schema.yaml": [
        "software_stack_contract",
        "program_image_contract",
        "test_app_contract",
    ],
    "shared/schemas/memory_subsystem_ir.schema.yaml": [
        "memory_request_lifecycle",
        "duplicate_request_prevention",
    ],
    "shared/schemas/validation_plan_ir.schema.yaml": [
        "declared_test_coverage_gate",
        "vertical_slice_tests",
    ],
    "shared/tables/architecture_preset_library.yaml": [
        "MINIMAL_VERTICAL_SLICE_GPGPU",
    ],
    "shared/tables/closure_gate_table.yaml": [
        "declared_test_coverage_gate",
        "cross_artifact_consistency_gate",
    ],
    "shared/tables/failure_taxonomy_table.yaml": [
        "DOC_ARTIFACT_DRIFT",
        "APP_COMPILE_FAIL",
        "FRONTEND_RUNTIME_MAPPING_MISMATCH",
    ],
}


def require(path: Path, failures: List[str]) -> None:
    if not path.exists():
        failures.append(f"missing: {path.relative_to(ROOT)}")


def require_text(path: Path, needles: List[str], failures: List[str]) -> None:
    require(path, failures)
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            failures.append(f"missing text {needle!r} in {path.relative_to(ROOT)}")


def main() -> int:
    failures: List[str] = []

    for skill in TOP_LEVEL_SKILLS:
        skill_dir = ROOT / skill
        require(skill_dir, failures)
        require_text(skill_dir / "SKILL.md", SKILL_SECTIONS, failures)

    for skill in LEGACY_SKILLS:
        require(ROOT / "legacy" / skill / "SKILL.md", failures)
        if (ROOT / skill).exists():
            failures.append(f"legacy skill still top-level: {skill}")

    for schema in SCHEMAS:
        require(ROOT / "shared" / "schemas" / schema, failures)

    for table in TABLES:
        require(ROOT / "shared" / "tables" / table, failures)

    for test_dir in TEST_DIRS:
        path = ROOT / "shared" / "tests" / test_dir
        require(path, failures)
        if path.exists() and not list(path.iterdir()):
            failures.append(f"empty test directory: {path.relative_to(ROOT)}")

    for example_dir in EXAMPLE_DIRS:
        path = ROOT / "shared" / "examples" / example_dir
        require(path, failures)
        if path.exists() and not list(path.iterdir()):
            failures.append(f"empty example directory: {path.relative_to(ROOT)}")

    for filename in VIBE_EXAMPLE_FILES:
        require(ROOT / "shared" / "examples" / "vibe_minimal_vertical_slice" / filename, failures)

    require_text(
        ROOT / "shared" / "flow" / "gpgpu_design_flow.md",
        ["## Reproduce Path", "## Design From Intent Path", "## Vertical Slice Prototype Path"],
        failures,
    )

    for lesson in REFERENCE_LESSONS:
        require(ROOT / "shared" / "references" / lesson, failures)

    require_text(
        ROOT / "README.md",
        [
            "# GPGPU Skills",
            "Intent -> Candidate -> Spec -> State -> Contract -> Validation -> Closure",
            "Vertical-slice prototype path",
        ],
        failures,
    )

    for rel_path, needles in VIBE_REQUIRED_TEXT.items():
        require_text(ROOT / rel_path, needles, failures)

    if failures:
        print("GPGPU skill v4 asset contract failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("GPGPU skill v4 asset contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
