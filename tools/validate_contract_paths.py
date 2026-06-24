#!/usr/bin/env python3
from __future__ import print_function

import argparse
import io
import os
import sys

import yaml


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXAMPLES_DIR = os.path.join(ROOT, "shared", "examples")

TARGET_ARTIFACTS = set(
    [
        "expected_assembly_ir.yaml",
        "expected_program_image_ir.yaml",
        "expected_golden_contract_model.yaml",
        "expected_incremental_rtl_map.yaml",
        "expected_normalized_trace_ir.yaml",
        "expected_first_divergence_report.yaml",
        "expected_root_cause_report.yaml",
        "expected_correctness_gate_report_ir.yaml",
        "expected_pass_evidence_report_ir.yaml",
        "expected_trace_coverage_report_ir.yaml",
    ]
)


def fail(message):
    print("FAIL: " + message)
    raise SystemExit(1)


def read_yaml(path):
    with io.open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def rel(path):
    return os.path.relpath(path, ROOT)


def walk_examples(base):
    for current, dirs, files in os.walk(base):
        dirs[:] = [name for name in dirs if name not in (".git", "__pycache__")]
        if os.path.basename(current) != "ai":
            continue
        yield current


def normalize_contract_path(path):
    if not isinstance(path, str):
        return None
    if path.startswith("SYSTEM_CONTRACT_IR."):
        path = path[len("SYSTEM_CONTRACT_IR.") :]
    if not path or path.startswith("hash_") or "/" in path:
        return None
    if "." not in path and path not in (
        "isa_model",
        "execution_model",
        "state_model",
        "memory_model",
        "launch_model",
        "interface_semantics_model",
        "config_contract",
        "architecture_model",
    ):
        return None
    return path


def collect_paths(value, current_key=None):
    paths = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if key_text in ("contract_path_coverage", "event_to_contract_path_map"):
                if isinstance(item, dict):
                    for nested_key, nested_value in item.items():
                        candidate = normalize_contract_path(nested_key)
                        if candidate:
                            paths.append(candidate)
                        for nested in collect_paths(nested_value, key_text):
                            paths.append(nested)
                    continue
            if key_text == "source_of_truth_map" and isinstance(item, dict):
                for nested_value in item.values():
                    candidate = normalize_contract_path(nested_value)
                    if candidate:
                        paths.append(candidate)
                continue
            if key_text == "contract_path" or key_text.endswith("_contract_path"):
                candidate = normalize_contract_path(item)
                if candidate:
                    paths.append(candidate)
                continue
            if key_text == "contract_paths" or key_text.endswith("_contract_paths"):
                for candidate_value in item if isinstance(item, list) else [item]:
                    candidate = normalize_contract_path(candidate_value)
                    if candidate:
                        paths.append(candidate)
                continue
            paths.extend(collect_paths(item, key_text))
    elif isinstance(value, list):
        for item in value:
            paths.extend(collect_paths(item, current_key))
    return paths


def resolve_path(contract, dot_path):
    current = contract
    for part in dot_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def validate_example(ai_dir):
    contract_path = os.path.join(ai_dir, "expected_system_contract_ir.yaml")
    if not os.path.isfile(contract_path):
        return [], ["%s missing expected_system_contract_ir.yaml; skipped" % rel(ai_dir)]
    contract = read_yaml(contract_path)
    errors = []
    warnings = []
    checked = 0

    for name in sorted(os.listdir(ai_dir)):
        if name not in TARGET_ARTIFACTS:
            continue
        path = os.path.join(ai_dir, name)
        if not os.path.isfile(path):
            continue
        artifact = read_yaml(path)
        paths = sorted(set(collect_paths(artifact)))
        if not paths and name in (
            "expected_correctness_gate_report_ir.yaml",
            "expected_pass_evidence_report_ir.yaml",
        ):
            warnings.append("%s has no contract path evidence" % rel(path))
        for dot_path in paths:
            checked += 1
            if not resolve_path(contract, dot_path):
                errors.append("%s unresolved contract path: %s" % (rel(path), dot_path))
    return errors, warnings, checked


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Validate contract_path references against SYSTEM_CONTRACT_IR.")
    parser.add_argument("--examples", default=EXAMPLES_DIR, help="Examples directory.")
    parser.add_argument("--report", help="Optional YAML report path.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    errors = []
    warnings = []
    checked = 0
    for ai_dir in walk_examples(os.path.abspath(args.examples)):
        result = validate_example(ai_dir)
        if len(result) == 2:
            dir_errors, dir_warnings = result
            dir_checked = 0
        else:
            dir_errors, dir_warnings, dir_checked = result
        errors.extend(dir_errors)
        warnings.extend(dir_warnings)
        checked += dir_checked

    report = {"checked_contract_paths": checked, "warnings": warnings, "errors": errors}
    if args.report:
        with io.open(args.report, "w", encoding="utf-8", newline="\n") as handle:
            yaml.safe_dump(report, handle, sort_keys=False)

    if errors:
        preview = "\n".join(errors[:40])
        if len(errors) > 40:
            preview += "\n... %d more" % (len(errors) - 40)
        fail("contract path validation found %d problem(s):\n%s" % (len(errors), preview))
    if warnings:
        print("WARN: contract path validation emitted %d warning(s)" % len(warnings))
    print("CONTRACT_PATH_PASS: checked %d contract path reference(s)" % checked)


if __name__ == "__main__":
    main()
