#!/usr/bin/env python3
"""Validate the GPGPU skill v5 self-correcting design-system contract."""

from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[2]

DESCRIPTION_CATALOG = "file_descriptions.zh.md"

TOP_LEVEL_SKILLS = [
    "gpgpu-architecture-generator",
    "gpgpu-system-contract-golden-engine",
    "gpgpu-incremental-rtl-binding-engine",
    "gpgpu-simulation-performance-attribution-engine",
    "gpgpu-architecture-rewrite-loop-controller",
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
    "## Forbidden Actions",
    "## Required Tables",
    "## Required Schemas",
    "## Required Invariants",
    "## Failure Modes",
    "## Report Schema",
    "## Concrete Assets Required",
]

NEW_SCHEMAS = [
    "mode_selection_ir.schema.yaml",
    "design_intent_ir.schema.yaml",
    "arch_ir.schema.yaml",
    "micro_constraint_estimate_ir.schema.yaml",
    "arch_generation_report_ir.schema.yaml",
    "system_contract_ir.schema.yaml",
    "golden_contract_model.schema.yaml",
    "contract_semantics_report_ir.schema.yaml",
    "incremental_rtl_map.schema.yaml",
    "module_interface_report_ir.schema.yaml",
    "rtl_partial_sim_report_ir.schema.yaml",
    "normalized_trace_ir.schema.yaml",
    "perf_attribution_graph.schema.yaml",
    "root_cause_report_ir.schema.yaml",
    "sim_perf_attribution_report_ir.schema.yaml",
    "arch_rewrite_plan.schema.yaml",
    "rewrite_decision_report_ir.schema.yaml",
    "regression_tracking_report_ir.schema.yaml",
]

NEW_TABLES = [
    "enum_table.yaml",
    "provenance_table.yaml",
    "mode_decision_table.yaml",
    "architecture_preset_library.yaml",
    "hard_constraint_table.yaml",
    "quality_target_table.yaml",
    "requirement_owner_table.yaml",
    "micro_constraint_estimator_table.yaml",
    "config_ownership_table.yaml",
    "contract_semantics_binding_table.yaml",
    "golden_model_coverage_table.yaml",
    "source_of_truth_generation_table.yaml",
    "rtl_module_catalog.yaml",
    "module_interface_contract_table.yaml",
    "rtl_partial_sim_gate_table.yaml",
    "trace_normalization_table.yaml",
    "perf_attribution_taxonomy.yaml",
    "root_cause_taxonomy.yaml",
    "rewrite_trigger_table.yaml",
    "patch_taxonomy_table.yaml",
    "revalidation_routing_table.yaml",
]

TEST_DIRS = [
    "architecture_generator",
    "system_contract_golden_engine",
    "incremental_rtl_binding_engine",
    "simulation_performance_attribution_engine",
    "architecture_rewrite_loop_controller",
]

SHARED_DIRS = [
    "examples",
    "flow",
    "references",
    "schemas",
    "tables",
    "tests",
]

SHARED_EXAMPLE_DIRS = [
    "self_correcting_minimal_simt",
]

EXAMPLE_FILES = [
    "input_request.md",
    "expected_arch_ir.yaml",
    "expected_micro_constraint_estimate.yaml",
    "expected_system_contract_ir.yaml",
    "expected_golden_contract_model.yaml",
    "expected_incremental_rtl_map.yaml",
    "expected_perf_attribution_graph.yaml",
    "expected_arch_rewrite_plan.yaml",
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

TOP_LEVEL_REQUIRED_TEXT: Dict[str, List[str]] = {
    "gpgpu-architecture-generator/SKILL.md": [
        "MICRO_CONSTRAINT_ESTIMATE_IR",
        "ARCH_IR is a candidate graph",
        "must not emit system contract truth",
    ],
    "gpgpu-system-contract-golden-engine/SKILL.md": [
        "GOLDEN_CONTRACT_MODEL",
        "executable reference semantics",
        "must not define independent ISA",
    ],
    "gpgpu-incremental-rtl-binding-engine/SKILL.md": [
        "INCREMENTAL_RTL_MAP",
        "module by module",
        "Interface Contract Checker",
        "RTL Partial Simulator",
    ],
    "gpgpu-simulation-performance-attribution-engine/SKILL.md": [
        "PERF_ATTRIBUTION_GRAPH",
        "cycle",
        "contract path",
        "RTL module",
    ],
    "gpgpu-architecture-rewrite-loop-controller/SKILL.md": [
        "ARCH_REWRITE_PLAN",
        "Architecture Patch",
        "Contract Patch",
        "RTL Patch",
    ],
}

MIGRATED_REQUIRED_TEXT: Dict[str, List[str]] = {
    "gpgpu-architecture-generator/legacy_request_and_candidate_constraints.md": [
        "gpgpu-front-end",
        "gpgpu-architecture-synthesizer",
        "DESIGN_INTENT_IR",
        "ARCH_IR",
        "MICRO_CONSTRAINT_ESTIMATE_IR",
    ],
    "gpgpu-system-contract-golden-engine/contract_truth_and_state_model.md": [
        "gpgpu-spec-lock",
        "gpgpu-canonical-state-engine",
        "SYSTEM_CONTRACT_IR",
        "GOLDEN_CONTRACT_MODEL",
        "pc_table",
    ],
    "gpgpu-incremental-rtl-binding-engine/module_binding_rules.md": [
        "gpgpu-artifact-contract-engine",
        "gpgpu-memory-subsystem",
        "INCREMENTAL_RTL_MAP",
        "load/store queue",
        "Interface Contract Checker",
    ],
    "gpgpu-simulation-performance-attribution-engine/legacy_validation_and_trace_constraints.md": [
        "gpgpu-runtime-validator",
        "gpgpu-implementation-validator",
        "NORMALIZED_TRACE_IR",
        "PERF_ATTRIBUTION_GRAPH",
        "first divergence",
    ],
    "gpgpu-architecture-rewrite-loop-controller/legacy_closure_repair_constraints.md": [
        "gpgpu-closure-refinement-engine",
        "ARCH_REWRITE_PLAN",
        "Architecture Patch",
        "Contract Patch",
        "RTL Patch",
    ],
}

REFERENCE_FILES = [
    "gpgpu-architecture-generator/legacy_request_and_candidate_constraints.md",
    "gpgpu-system-contract-golden-engine/contract_truth_and_state_model.md",
    "gpgpu-system-contract-golden-engine/executable_semantics_rules.md",
    "gpgpu-system-contract-golden-engine/golden_model_coverage_and_report.md",
    "gpgpu-incremental-rtl-binding-engine/module_binding_rules.md",
    "gpgpu-incremental-rtl-binding-engine/interface_binding_and_checker.md",
    "gpgpu-incremental-rtl-binding-engine/partial_simulation_gates.md",
    "gpgpu-incremental-rtl-binding-engine/rtl_module_catalog.md",
    "gpgpu-simulation-performance-attribution-engine/trace_normalizer.md",
    "gpgpu-simulation-performance-attribution-engine/bottleneck_graph_builder.md",
    "gpgpu-simulation-performance-attribution-engine/root_cause_engine.md",
    "gpgpu-simulation-performance-attribution-engine/legacy_validation_and_trace_constraints.md",
    "gpgpu-architecture-rewrite-loop-controller/rewrite_trigger.md",
    "gpgpu-architecture-rewrite-loop-controller/patch_taxonomy.md",
    "gpgpu-architecture-rewrite-loop-controller/regression_tracking.md",
    "gpgpu-architecture-rewrite-loop-controller/revalidation_routing.md",
    "gpgpu-architecture-rewrite-loop-controller/legacy_closure_repair_constraints.md",
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
    actual = {child.name for child in path.iterdir() if child.is_dir()}
    for name in sorted(actual - allowed):
        failures.append(f"unexpected directory in {path.relative_to(ROOT)}: {name}")


def iter_documented_files() -> List[str]:
    files: List[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        files.append(path.relative_to(ROOT).as_posix())
    return sorted(files)


def require_file_description_catalog(failures: List[str]) -> None:
    catalog_path = ROOT / DESCRIPTION_CATALOG
    require_text(
        catalog_path,
        [
            "# Skill 文件中文说明索引",
            "## 覆盖规则",
            "内容说明：",
            "具体例子：",
        ],
        failures,
    )
    if not catalog_path.exists():
        return

    text = catalog_path.read_text(encoding="utf-8")
    for rel_path in iter_documented_files():
        heading = f"### `{rel_path}`"
        if heading not in text:
            failures.append(f"missing file description entry: {rel_path}")
            continue
        start = text.index(heading)
        next_heading = text.find("\n### `", start + len(heading))
        section = text[start:] if next_heading == -1 else text[start:next_heading]
        if "内容说明：" not in section:
            failures.append(f"missing content explanation in file description: {rel_path}")
        if "具体例子：" not in section:
            failures.append(f"missing concrete example in file description: {rel_path}")


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

    for filename in EXAMPLE_FILES:
        require_nonempty(ROOT / "shared" / "examples" / "self_correcting_minimal_simt" / filename, failures)

    for rel_path in REFERENCE_FILES:
        require_nonempty(ROOT / rel_path, failures)

    require_file_description_catalog(failures)

    for lesson in REFERENCE_LESSONS:
        require(ROOT / "shared" / "references" / lesson, failures)

    require_text(
        ROOT / "README.md",
        [
            "self-correcting GPGPU design system",
            "GOLDEN_CONTRACT_MODEL",
            "INCREMENTAL_RTL_MAP",
            "PERF_ATTRIBUTION_GRAPH",
            "ARCH_REWRITE_PLAN",
            "former 9-stage top-level GPGPU skills and the old `legacy/` skill archive have been deleted",
        ],
        failures,
    )

    require_text(
        ROOT / "shared" / "flow" / "gpgpu_design_flow.md",
        [
            "Architecture Generator",
            "System Contract + Golden Semantics Engine",
            "Incremental RTL Binding Engine",
            "Simulation + Performance Attribution Engine",
            "Architecture Rewrite Loop Controller",
            "Legacy v4 top-level skills and the old `legacy/` skill archive are not active wrappers",
        ],
        failures,
    )

    require_text(
        ROOT / "skill_5stage_compression_plan.zh.md",
        [
            "Executable Golden Model",
            "INCREMENTAL_RTL_MAP",
            "PERF_ATTRIBUTION_GRAPH",
            "ARCH_REWRITE_PLAN",
        ],
        failures,
    )

    require_text(
        ROOT / "skill_summary.md",
        [
            "# GPGPU Skill v5 总结",
            "五个核心 skill",
            "file_descriptions.zh.md",
            "self-correcting GPGPU design system",
        ],
        failures,
    )

    for rel_path, needles in TOP_LEVEL_REQUIRED_TEXT.items():
        require_text(ROOT / rel_path, needles, failures)

    for rel_path, needles in MIGRATED_REQUIRED_TEXT.items():
        require_text(ROOT / rel_path, needles, failures)

    if failures:
        print("GPGPU skill v5 self-correcting asset contract failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("GPGPU skill v5 self-correcting asset contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
