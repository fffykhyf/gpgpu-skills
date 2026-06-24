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


def fail(message):
    print("FAIL: " + message, file=sys.stderr)
    raise SystemExit(1)


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
    suffix = os.path.splitext(path)[1].lower()
    if suffix == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def strip_volatile(value, volatile_fields):
    if isinstance(value, dict):
        stripped = {}
        for key in sorted(value.keys()):
            if key in volatile_fields:
                continue
            stripped[key] = strip_volatile(value[key], volatile_fields)
        return stripped
    if isinstance(value, list):
        return [strip_volatile(item, volatile_fields) for item in value]
    return value


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_hash(value):
    encoded = canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Canonicalize YAML/JSON IR.")
    parser.add_argument("--input", required=True, help="Input YAML or JSON file.")
    parser.add_argument("--output", help="Output canonical JSON file.")
    parser.add_argument("--hash", action="store_true", help="Print canonical sha256 hash.")
    parser.add_argument(
        "--keep-volatile",
        action="store_true",
        help="Keep volatile fields instead of stripping the default volatile field set.",
    )
    parser.add_argument(
        "--volatile-field",
        action="append",
        default=[],
        help="Additional volatile field to strip. Can be repeated.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    if not os.path.isfile(args.input):
        fail("input file not found: %s" % args.input)

    value = load_ir(args.input)
    volatile_fields = set(DEFAULT_VOLATILE_FIELDS)
    volatile_fields.update(args.volatile_field)
    if not args.keep_volatile:
        value = strip_volatile(value, volatile_fields)

    canonical = canonical_json(value)
    if args.output:
        write_text(args.output, canonical + "\n")
    if args.hash:
        print(canonical_hash(value))
    if not args.output and not args.hash:
        print(canonical)


if __name__ == "__main__":
    main()
