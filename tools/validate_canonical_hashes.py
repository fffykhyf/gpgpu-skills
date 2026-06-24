#!/usr/bin/env python3
from __future__ import print_function

import argparse
import hashlib
import io
import json
import os
import re
import sys

import yaml


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXAMPLES_DIR = os.path.join(ROOT, "shared", "examples")

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
HASH_FIELD_NAMES = set(["canonical_hash", "content_hash"])


def fail(message):
    print("FAIL: " + message)
    raise SystemExit(1)


def read_yaml(path):
    with io.open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def rel(path):
    return os.path.relpath(path, ROOT)


def walk_yaml(base):
    for current, dirs, files in os.walk(base):
        dirs[:] = [name for name in dirs if name not in (".git", "__pycache__")]
        for name in sorted(files):
            if name.endswith(".yaml") or name.endswith(".yml"):
                yield os.path.join(current, name)


def collect_hash_fields(value, path="$"):
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            next_path = "%s.%s" % (path, key_text)
            if isinstance(item, str) and (key_text in HASH_FIELD_NAMES or key_text.endswith("_hash")):
                found.append((next_path, item))
            found.extend(collect_hash_fields(item, next_path))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            found.extend(collect_hash_fields(item, "%s[%d]" % (path, idx)))
    return found


def strip_hash_fields(value):
    if isinstance(value, dict):
        result = {}
        for key in sorted(value.keys()):
            key_text = str(key)
            if key_text in HASH_FIELD_NAMES or key_text.endswith("_hash"):
                continue
            result[key] = strip_hash_fields(value[key])
        return result
    if isinstance(value, list):
        return [strip_hash_fields(item) for item in value]
    return value


def canonical_hash_without_hash_fields(value):
    stripped = strip_hash_fields(value)
    encoded = json.dumps(stripped, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def validate_file(path, mode):
    value = read_yaml(path)
    errors = []
    warnings = []
    checked = 0
    for field_path, hash_value in collect_hash_fields(value):
        checked += 1
        if SHA256_RE.match(hash_value):
            continue
        if hash_value.startswith("hash_"):
            if mode == "strict":
                errors.append("%s %s uses legacy symbolic hash %s" % (rel(path), field_path, hash_value))
            else:
                warnings.append("SYMBOLIC_HASH_LEGACY_WARNING %s %s=%s" % (rel(path), field_path, hash_value))
            continue
        errors.append("%s %s has invalid hash format %s" % (rel(path), field_path, hash_value))

    if mode == "strict":
        declared = value.get("canonical_hash") if isinstance(value, dict) else None
        if declared and SHA256_RE.match(declared):
            actual = canonical_hash_without_hash_fields(value)
            if declared != actual:
                errors.append("%s canonical_hash mismatch declared=%s actual=%s" % (rel(path), declared, actual))

    return errors, warnings, checked


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Validate canonical hash fields.")
    parser.add_argument("--examples", default=EXAMPLES_DIR, help="Examples directory.")
    parser.add_argument(
        "--mode",
        default="legacy-compatible",
        choices=["legacy-compatible", "strict"],
        help="legacy-compatible warns on hash_*; strict fails unless sha256 hashes are present.",
    )
    parser.add_argument("--report", help="Optional YAML report path.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    errors = []
    warnings = []
    checked = 0
    for path in walk_yaml(os.path.abspath(args.examples)):
        file_errors, file_warnings, file_checked = validate_file(path, args.mode)
        errors.extend(file_errors)
        warnings.extend(file_warnings)
        checked += file_checked

    report = {"checked_hash_fields": checked, "mode": args.mode, "warnings": warnings, "errors": errors}
    if args.report:
        with io.open(args.report, "w", encoding="utf-8", newline="\n") as handle:
            yaml.safe_dump(report, handle, sort_keys=False)

    if errors:
        preview = "\n".join(errors[:40])
        if len(errors) > 40:
            preview += "\n... %d more" % (len(errors) - 40)
        fail("canonical hash validation found %d problem(s):\n%s" % (len(errors), preview))

    if warnings:
        print("WARN: canonical hash validation emitted %d warning(s)" % len(warnings))
    if args.mode == "legacy-compatible":
        print("CANONICAL_HASH_LEGACY_COMPATIBLE_PASS: checked %d hash field(s)" % checked)
    else:
        print("CANONICAL_HASH_STRICT_PASS: checked %d hash field(s)" % checked)


if __name__ == "__main__":
    main()
