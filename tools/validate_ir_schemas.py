#!/usr/bin/env python3
from __future__ import print_function

import argparse
import io
import os
import re
import sys

import yaml


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCHEMA_DIR = os.path.join(ROOT, "shared", "schemas")
EXAMPLES_DIR = os.path.join(ROOT, "shared", "examples")

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

ENFORCED_SCHEMA_FILES = [
    "arch_ir.schema.yaml",
    "system_contract_ir.schema.yaml",
    "golden_contract_model.schema.yaml",
    "assembly_ir.schema.yaml",
    "program_image_ir.schema.yaml",
    "runtime_launch_ir.schema.yaml",
    "loader_contract_ir.schema.yaml",
    "incremental_rtl_map.schema.yaml",
    "normalized_trace_ir.schema.yaml",
    "correctness_gate_report_ir.schema.yaml",
    "pass_evidence_report_ir.schema.yaml",
    "regression_fingerprint_ir.schema.yaml",
    "yosys_flow_ir.schema.yaml",
    "yosys_evidence_bundle_ir.schema.yaml",
    "determinism_manifest_ir.schema.yaml",
]

EXAMPLE_ALIASES = {
    "artifact_manifest_ir": ["expected_artifact_manifest_fast.yaml"],
    "regression_fingerprint_ir": ["expected_regression_fingerprint.yaml"],
}


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


def schema_name(schema):
    return str(schema.get("schema", "")).lower()


def expected_names_for_schema(name):
    names = ["expected_%s.yaml" % name]
    if name.endswith("_ir"):
        names.append("expected_%s.yaml" % name[:-3])
    names.extend(EXAMPLE_ALIASES.get(name, []))
    return names


def find_examples(name, include_all_examples):
    expected = set(expected_names_for_schema(name))
    matches = []
    for path in walk_yaml(EXAMPLES_DIR):
        if not include_all_examples and "/minimal_simt/" not in path.replace(os.sep, "/"):
            continue
        if os.path.basename(path) in expected:
            matches.append(path)
    return sorted(matches)


def is_type(value, type_name):
    if type_name in ("string", "enum"):
        return isinstance(value, str)
    if type_name in ("bool", "boolean"):
        return isinstance(value, bool)
    if type_name in ("int", "integer"):
        return isinstance(value, int) and not isinstance(value, bool)
    if type_name in ("number", "float"):
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if type_name in ("list", "array"):
        return isinstance(value, list)
    if type_name in ("map", "object"):
        return isinstance(value, dict)
    return True


def type_label(value):
    if isinstance(value, dict):
        return "map"
    if isinstance(value, list):
        return "list"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "number"
    if value is None:
        return "null"
    return type(value).__name__


def schema_type(prop_schema):
    if isinstance(prop_schema, str):
        return prop_schema
    if isinstance(prop_schema, dict):
        return prop_schema.get("type")
    return None


def enum_values(schema, field_name, prop_schema):
    if isinstance(prop_schema, dict) and isinstance(prop_schema.get("enum"), list):
        return prop_schema.get("enum")
    if prop_schema == "enum":
        keys = [field_name + "s", field_name + "_values"]
        if "mode" in field_name:
            keys.extend(["modes", "verdicts"])
        elif "verdict" in field_name:
            keys.extend(["verdicts", "modes"])
        else:
            keys.extend(["verdicts", "modes"])
        for key in keys:
            values = schema.get(key)
            if isinstance(values, list):
                return values
    return None


def validate_value(value, prop_schema, schema, definitions, path, errors, warnings):
    if value is None:
        return
    expected = schema_type(prop_schema)
    if expected and not is_type(value, expected):
        errors.append("%s expected %s, got %s" % (path, expected, type_label(value)))
        return

    if isinstance(prop_schema, dict):
        if prop_schema.get("hash_format") == "sha256_canonical_json":
            if isinstance(value, str) and value.startswith("hash_"):
                warnings.append("%s uses legacy symbolic hash %s" % (path, value))
            elif isinstance(value, str) and not SHA256_RE.match(value):
                warnings.append("%s is not canonical sha256 format: %s" % (path, value))

        if expected in ("object", "map") and isinstance(value, dict):
            validate_object(value, prop_schema, definitions, path, errors, warnings)

        if expected in ("list", "array") and isinstance(value, list):
            item_schema = prop_schema.get("items") or prop_schema.get("item_schema")
            if isinstance(item_schema, str) and item_schema in definitions:
                item_schema = definitions[item_schema]
            if isinstance(item_schema, dict):
                for idx, item in enumerate(value):
                    validate_value(item, item_schema, schema, definitions, "%s[%d]" % (path, idx), errors, warnings)


def validate_object(obj, schema, definitions, path, errors, warnings):
    required = schema.get("required") or []
    for field in required:
        if field not in obj:
            errors.append("%s missing required field %s" % (path, field))

    properties = schema.get("properties") or {}
    for field, prop_schema in properties.items():
        if field not in obj:
            continue
        value = obj[field]
        values = enum_values(schema, field, prop_schema)
        if values is not None and value not in values:
            errors.append("%s.%s has unknown enum value %r" % (path, field, value))
        validate_value(value, prop_schema, schema, definitions, "%s.%s" % (path, field), errors, warnings)


def validate_example(schema_path, example_path):
    schema = read_yaml(schema_path)
    value = read_yaml(example_path)
    errors = []
    warnings = []
    definitions = schema.get("definitions") or {}
    validate_object(value, schema, definitions, rel(example_path), errors, warnings)
    return errors, warnings


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Validate expected IR YAML against compact schema dialect.")
    parser.add_argument("--examples", default=EXAMPLES_DIR, help="Examples directory.")
    parser.add_argument("--schemas", default=SCHEMA_DIR, help="Schema directory.")
    parser.add_argument("--report", help="Optional machine-readable YAML report path.")
    parser.add_argument(
        "--include-all-examples",
        action="store_true",
        help="Strictly validate all matching examples instead of the current minimal_simt gate set.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    global SCHEMA_DIR, EXAMPLES_DIR
    SCHEMA_DIR = os.path.abspath(args.schemas)
    EXAMPLES_DIR = os.path.abspath(args.examples)

    all_errors = []
    all_warnings = []
    checked = 0
    skipped = []

    for filename in ENFORCED_SCHEMA_FILES:
        schema_path = os.path.join(SCHEMA_DIR, filename)
        if not os.path.isfile(schema_path):
            all_errors.append("missing enforced schema %s" % filename)
            continue
        schema = read_yaml(schema_path)
        name = schema_name(schema)
        examples = find_examples(name, args.include_all_examples)
        if not examples:
            skipped.append(name)
            continue
        for example in examples:
            errors, warnings = validate_example(schema_path, example)
            checked += 1
            all_errors.extend(errors)
            all_warnings.extend(warnings)

    report = {
        "checked_examples": checked,
        "skipped_schemas_without_examples": skipped,
        "warnings": all_warnings,
        "errors": all_errors,
    }
    if args.report:
        with io.open(args.report, "w", encoding="utf-8", newline="\n") as handle:
            yaml.safe_dump(report, handle, sort_keys=False)

    if all_errors:
        preview = "\n".join(all_errors[:40])
        if len(all_errors) > 40:
            preview += "\n... %d more" % (len(all_errors) - 40)
        fail("schema validation found %d problem(s):\n%s" % (len(all_errors), preview))

    if all_warnings:
        print("WARN: schema validation emitted %d warning(s)" % len(all_warnings))
    print("SCHEMA_VALIDATION_PASS: checked %d expected artifact(s)" % checked)


if __name__ == "__main__":
    main()
