#!/usr/bin/env python3
from __future__ import print_function

import argparse
import io
import os
import re
import sys

import yaml


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TESTS_DIR = os.path.join(ROOT, "shared", "tests")
TABLES_DIR = os.path.join(ROOT, "shared", "tables")

ALLOWED_GATES = set(
    [
        "schema_valid",
        "contract_paths_resolvable",
        "canonical_hash_present",
        "canonical_hash_verified",
        "producer_skill_valid",
        "consumer_skill_valid",
        "failure_mode_known",
        "patch_route_known",
        "required_revalidation_known",
        "forbidden_outputs_absent",
        "pass_evidence_present",
        "regression_fingerprint_present",
        "correctness_gate_present",
        "yosys_profile_known",
        "backend_claim_boundary_checked",
    ]
)


def fail(message):
    print("FAIL: " + message)
    raise SystemExit(1)


def read_text(path):
    with io.open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def read_yaml(path):
    return yaml.safe_load(read_text(path))


def rel(path):
    return os.path.relpath(path, ROOT)


def walk_case_files(base):
    for current, dirs, files in os.walk(base):
        dirs[:] = [name for name in dirs if name not in (".git", "__pycache__")]
        for name in sorted(files):
            if name == "cases.yaml":
                yield os.path.join(current, name)


def collect_known_failure_modes():
    known = set()
    token_re = re.compile(r"\b[A-Za-z][A-Za-z0-9_]*\b")
    for current, dirs, files in os.walk(os.path.join(ROOT, "shared")):
        dirs[:] = [name for name in dirs if name not in (".git", "__pycache__")]
        for name in files:
            if not (name.endswith(".yaml") or name.endswith(".md")):
                continue
            text = read_text(os.path.join(current, name))
            if "failure_mode" not in text and "root_causes" not in text and "subclasses" not in text:
                continue
            for token in token_re.findall(text):
                if "_" in token:
                    known.add(token)
                    known.add(token.lower())
    return known


def collect_patch_routes():
    routes = set(["none"])
    for filename in ("revalidation_routing_table.yaml", "rewrite_rules.yaml"):
        path = os.path.join(TABLES_DIR, filename)
        if not os.path.isfile(path):
            continue
        data = read_yaml(path) or {}
        if isinstance(data.get("routes"), dict):
            routes.update(data["routes"].keys())
        if isinstance(data.get("failure_routes"), dict):
            routes.update(data["failure_routes"].keys())
        if isinstance(data.get("rewrite_rules"), dict):
            routes.update(data["rewrite_rules"].keys())
    return routes


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def input_artifacts(case):
    if "input" in case and isinstance(case["input"], dict):
        return case["input"].get("artifacts") or []
    return case.get("input_artifacts") or []


def expected_outputs(case):
    if "expected" in case and isinstance(case["expected"], dict):
        return case["expected"].get("outputs") or []
    return case.get("expected_outputs") or []


def failure_mode(case):
    if "expected" in case and isinstance(case["expected"], dict):
        return case["expected"].get("failure_mode")
    return case.get("expected_failure_mode")


def artifact_path(artifact):
    if isinstance(artifact, dict):
        return artifact.get("path")
    if isinstance(artifact, str) and "/" in artifact:
        return artifact
    return None


def output_name(output):
    if isinstance(output, dict):
        return output.get("artifact_name")
    return output


def patch_route(case):
    route = case.get("patch_route")
    if route is None:
        return "none"
    if isinstance(route, dict):
        return route.get("expected", "none")
    return route


def validate_case(path, case, case_ids, known_failure_modes, known_routes, errors, warnings):
    case_id = case.get("case_id")
    if not case_id:
        errors.append("%s has case without case_id" % rel(path))
        return
    if case_id in case_ids:
        errors.append("%s duplicates case_id %s" % (rel(path), case_id))
    case_ids.add(case_id)

    inputs = input_artifacts(case)
    new_input_shape = isinstance(case.get("input"), dict) and "artifacts" in case.get("input", {})
    if not inputs and new_input_shape:
        errors.append("%s:%s missing input artifacts" % (rel(path), case_id))
    elif not inputs:
        warnings.append("%s:%s has legacy case without input artifacts" % (rel(path), case_id))
    for artifact in inputs:
        p = artifact_path(artifact)
        if p and not os.path.isfile(os.path.join(ROOT, p)):
            errors.append("%s:%s input artifact missing: %s" % (rel(path), case_id, p))

    outputs = expected_outputs(case)
    output_names = [output_name(output) for output in outputs if output_name(output)]
    new_expected_shape = isinstance(case.get("expected"), dict) and "outputs" in case.get("expected", {})
    if not output_names and new_expected_shape:
        errors.append("%s:%s missing expected outputs" % (rel(path), case_id))
    elif not output_names:
        warnings.append("%s:%s has legacy case without expected outputs" % (rel(path), case_id))
    for output in outputs:
        p = artifact_path(output)
        if p and not os.path.isfile(os.path.join(ROOT, p)):
            errors.append("%s:%s expected output missing: %s" % (rel(path), case_id, p))

    forbidden = set(as_list(case.get("forbidden_outputs")))
    conflicts = sorted(forbidden & set(output_names))
    if conflicts:
        errors.append("%s:%s forbidden output also expected: %s" % (rel(path), case_id, ", ".join(conflicts)))

    mode = failure_mode(case)
    if mode not in (None, "null") and mode not in known_failure_modes:
        errors.append("%s:%s unknown failure_mode %s" % (rel(path), case_id, mode))

    for gate in as_list(case.get("required_gates")):
        if gate not in ALLOWED_GATES:
            errors.append("%s:%s unknown required_gate %s" % (rel(path), case_id, gate))

    route = patch_route(case)
    if route not in known_routes:
        errors.append("%s:%s unknown patch_route %s" % (rel(path), case_id, route))

    if "input_artifacts" in case or "expected_outputs" in case or "expected_failure_mode" in case:
        warnings.append("%s:%s uses legacy case field names" % (rel(path), case_id))


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Validate structured and legacy case gates.")
    parser.add_argument("--tests", default=TESTS_DIR, help="Tests directory.")
    parser.add_argument("--report", help="Optional machine-readable YAML report path.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    case_ids = set()
    errors = []
    warnings = []
    checked = 0
    known_failure_modes = collect_known_failure_modes()
    known_routes = collect_patch_routes()

    for path in walk_case_files(os.path.abspath(args.tests)):
        data = read_yaml(path) or {}
        cases = data.get("cases")
        if not isinstance(cases, list):
            errors.append("%s missing cases list" % rel(path))
            continue
        for case in cases:
            checked += 1
            validate_case(path, case, case_ids, known_failure_modes, known_routes, errors, warnings)

    report = {"checked_cases": checked, "warnings": warnings, "errors": errors}
    if args.report:
        with io.open(args.report, "w", encoding="utf-8", newline="\n") as handle:
            yaml.safe_dump(report, handle, sort_keys=False)

    if errors:
        preview = "\n".join(errors[:40])
        if len(errors) > 40:
            preview += "\n... %d more" % (len(errors) - 40)
        fail("case validation found %d problem(s):\n%s" % (len(errors), preview))

    if warnings:
        print("WARN: case validation emitted %d warning(s)" % len(warnings))
    print("CASE_GATE_PASS: checked %d case(s)" % checked)


if __name__ == "__main__":
    main()
