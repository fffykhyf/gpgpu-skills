#!/usr/bin/env python3
from __future__ import print_function

import argparse
import hashlib
import io
import json
import os
import sys

import yaml


DEFAULT_VOLATILE_FIELDS = set(
    [
        "generated_at",
        "local_absolute_path",
        "tool_wall_time_sec",
        "yosys_version_banner_raw",
        "simulator_wall_time_sec",
    ]
)

SUPPORTED_SUFFIXES = (".yaml", ".yml", ".json")


def fail(message):
    print("FAIL: " + message, file=sys.stderr)
    raise SystemExit(1)


def read_bytes(path):
    with open(path, "rb") as handle:
        return handle.read()


def read_text(path):
    with io.open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_text(path, text):
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def load_ir(path):
    text = read_text(path)
    if path.lower().endswith(".json"):
        return json.loads(text)
    return yaml.safe_load(text)


def strip_volatile(value, volatile_fields):
    if isinstance(value, dict):
        result = {}
        for key in sorted(value.keys()):
            if key in volatile_fields:
                continue
            result[key] = strip_volatile(value[key], volatile_fields)
        return result
    if isinstance(value, list):
        return [strip_volatile(item, volatile_fields) for item in value]
    return value


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def iter_artifacts(root):
    artifacts = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in (".git", "__pycache__")]
        for name in sorted(files):
            if not name.lower().endswith(SUPPORTED_SUFFIXES):
                continue
            path = os.path.join(current, name)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            artifacts.append((rel, path))
    return sorted(artifacts)


def artifact_hashes(root, policy, volatile_fields):
    hashes = {}
    for rel, path in iter_artifacts(root):
        if policy == "byte_identical":
            hashes[rel] = sha256_bytes(read_bytes(path))
            continue
        value = load_ir(path)
        if policy == "semantic_identical_excluding_volatile":
            value = strip_volatile(value, volatile_fields)
        hashes[rel] = sha256_text(canonical_json(value))
    return hashes


def artifact_name(relpath):
    base = os.path.basename(relpath)
    stem = os.path.splitext(base)[0]
    if stem.startswith("expected_"):
        stem = stem[len("expected_") :]
    return stem.upper()


def short_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def build_manifest(run_a, run_b, policy, volatile_fields, hashes_a, hashes_b):
    paths_a = set(hashes_a.keys())
    paths_b = set(hashes_b.keys())
    common = sorted(paths_a & paths_b)
    missing_in_a = sorted(paths_b - paths_a)
    missing_in_b = sorted(paths_a - paths_b)
    different = [path for path in common if hashes_a[path] != hashes_b[path]]

    if missing_in_a or missing_in_b or different:
        verdict = "DETERMINISTIC_FAIL"
    elif not common:
        verdict = "DETERMINISTIC_INSUFFICIENT_EVIDENCE"
    else:
        verdict = "DETERMINISTIC_PASS"

    artifact_hashes = []
    for rel in common:
        artifact_hashes.append(
            {
                "artifact_name": artifact_name(rel),
                "artifact_path": rel,
                "producer_skill": "unknown",
                "canonical_hash": hashes_a[rel],
                "comparison_policy": policy,
                "volatile_fields": sorted(volatile_fields) if policy != "byte_identical" else [],
            }
        )

    manifest_basis = "%s|%s|%s" % (os.path.abspath(run_a), os.path.abspath(run_b), policy)
    return {
        "manifest_id": "determinism_diff_" + short_hash(manifest_basis),
        "canonicalization_version": "canonical_generation_rules_v1",
        "input_spec_ref": "run_directory_pair",
        "input_spec_hash": sha256_text(os.path.abspath(run_a)),
        "normalized_spec_hash": sha256_text(os.path.abspath(run_b)),
        "generation_plan_hash": sha256_text(policy),
        "artifact_hashes": artifact_hashes,
        "volatile_fields": sorted(volatile_fields) if policy != "byte_identical" else [],
        "comparison_policy": {
            "mode": policy,
            "excluded_fields": sorted(volatile_fields) if policy != "byte_identical" else [],
            "ordered_list_policy": {},
            "set_like_list_policy": {},
        },
        "determinism_verdict": verdict,
        "mismatch_summary": {
            "missing_in_run_a": missing_in_a,
            "missing_in_run_b": missing_in_b,
            "different_hashes": different,
        },
        "run_a_ref": run_a,
        "run_b_ref": run_b,
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Compare two generated artifact directories.")
    parser.add_argument("--run-a", required=True, help="First run artifact directory.")
    parser.add_argument("--run-b", required=True, help="Second run artifact directory.")
    parser.add_argument(
        "--policy",
        default="semantic_identical_excluding_volatile",
        choices=["byte_identical", "semantic_identical_excluding_volatile", "hash_identical"],
        help="Comparison policy.",
    )
    parser.add_argument("--manifest-out", help="Optional output manifest YAML path.")
    parser.add_argument(
        "--volatile-field",
        action="append",
        default=[],
        help="Additional volatile field to strip. Can be repeated.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    if not os.path.isdir(args.run_a):
        fail("run-a directory not found: %s" % args.run_a)
    if not os.path.isdir(args.run_b):
        fail("run-b directory not found: %s" % args.run_b)

    volatile_fields = set(DEFAULT_VOLATILE_FIELDS)
    volatile_fields.update(args.volatile_field)
    hashes_a = artifact_hashes(args.run_a, args.policy, volatile_fields)
    hashes_b = artifact_hashes(args.run_b, args.policy, volatile_fields)
    manifest = build_manifest(args.run_a, args.run_b, args.policy, volatile_fields, hashes_a, hashes_b)
    text = yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True)
    if args.manifest_out:
        write_text(args.manifest_out, text)
    else:
        print(text.rstrip())

    print(manifest["determinism_verdict"])
    if manifest["determinism_verdict"] == "DETERMINISTIC_FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
