#!/usr/bin/env python3
"""Validate the GPGPU skill v4 repository contract."""

from pathlib import Path
from typing import List

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
    "hard_constraint_table.yaml",
    "quality_target_table.yaml",
    "requirement_owner_table.yaml",
    "spec_required_field_table.yaml",
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
]

REFERENCE_LESSONS = [
    "vortex_lessons.yaml",
    "miaow_lessons.yaml",
    "gpgpusim_lessons.yaml",
    "rocket_lessons.yaml",
    "xiangshan_lessons.yaml",
    "reference_lesson_index.yaml",
]


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

    require_text(
        ROOT / "shared" / "flow" / "gpgpu_design_flow.md",
        ["## Reproduce Path", "## Design From Intent Path"],
        failures,
    )

    for lesson in REFERENCE_LESSONS:
        require(ROOT / "shared" / "references" / lesson, failures)

    require_text(
        ROOT / "README.md",
        ["# GPGPU Skills", "Intent -> Candidate -> Spec -> State -> Contract -> Validation -> Closure"],
        failures,
    )

    if failures:
        print("GPGPU skill v4 asset contract failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("GPGPU skill v4 asset contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
