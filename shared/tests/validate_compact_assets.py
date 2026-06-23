#!/usr/bin/env python
from __future__ import print_function

import io
import os
import re
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SKILL = os.path.join(ROOT, "skill")

ACTIVE = [
    "gpgpu-architecture",
    "gpgpu-contract",
    "gpgpu-toolchain-runtime",
    "gpgpu-rtl",
    "gpgpu-validation",
    "gpgpu-loop",
]

OLD = [
    "gpgpu-" + "arch",
    "gpgpu-" + "golden",
    "gpgpu-" + "runtime",
    "gpgpu-" + "simppa",
    "gpgpu-" + "memory",
    "gpgpu-" + "interconnect",
    "gpgpu-" + "atomic-sync",
]

REQUIRED_FILES = [
    "gpgpu-architecture/architecture_core.md",
    "gpgpu-architecture/capability_profiles.md",
    "gpgpu-contract/system_contract_core.md",
    "gpgpu-contract/golden_semantics.md",
    "gpgpu-contract/packs/memory_path.md",
    "gpgpu-contract/packs/interconnect.md",
    "gpgpu-contract/packs/atomic_sync.md",
    "gpgpu-toolchain-runtime/toolchain_runtime_core.md",
    "gpgpu-rtl/rtl_binding_core.md",
    "gpgpu-validation/validation_core.md",
    "gpgpu-validation/debug_attribution_pack.md",
    "gpgpu-validation/performance_pack.md",
    "gpgpu-loop/rewrite_loop_core.md",
]

PACK_TOKENS = {
    "gpgpu-contract/packs/memory_path.md": [
        "MEMORY_BUNDLE",
        "coalescer",
        "response restore",
        "nonblocking_memory_tag",
        "local_memory_bank",
        "l1_cache_or_global_adapter",
        "l2_cache_slice",
        "mshr",
        "dram_controller",
        "memory_visibility",
        "scoreboard release",
    ],
    "gpgpu-contract/packs/interconnect.md": [
        "source_sm_id",
        "request_tag",
        "traffic_class",
        "target_l2_slice_id",
        "NoC",
        "SM to L2",
        "backpressure",
        "response demux",
        "return path",
    ],
    "gpgpu-contract/packs/atomic_sync.md": [
        "atomic",
        "serialization_point",
        "barrier_phase",
        "arrival_bitmap",
        "release_bitmap",
        "fence_visibility",
        "WSYNC",
        "memory ordering",
    ],
}

FORBIDDEN = [
    "L3" + "/L4 upgrade",
    "L3" + " designs",
    "L4" + " designs",
    "L3" + " contract layer",
    "L4" + " system memory",
]

REQUIRED_SKILL_TEXT = {
    "gpgpu-contract/SKILL.md": ["SYSTEM_CONTRACT_IR", "GOLDEN_CONTRACT_MODEL"],
    "gpgpu-toolchain-runtime/SKILL.md": [
        "assembler",
        "disassembler",
        "program image",
        "loader",
        "START/BUSY/DONE/FAULTED/ACK",
    ],
    "gpgpu-rtl/SKILL.md": [
        "INCREMENTAL_RTL_MAP",
        "negotiated interface",
        "partial sim",
        "trace",
    ],
    "gpgpu-validation/SKILL.md": [
        "PASS_EVIDENCE",
        "REGRESSION_FINGERPRINT",
        "FIRST_DIVERGENCE",
        "ROOT_CAUSE",
    ],
    "gpgpu-loop/SKILL.md": ["Patch", "revalidation", "config drift"],
}


def fail(message):
    print("FAIL: " + message)
    raise SystemExit(1)


def path(*parts):
    return os.path.join(*parts)


def rel(p):
    return os.path.relpath(p, ROOT)


def read(p):
    with io.open(p, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def is_file(p):
    return os.path.isfile(p)


def is_dir(p):
    return os.path.isdir(p)


def list_dir_names(p):
    if not is_dir(p):
        return []
    return sorted(os.listdir(p))


def walk_files(base):
    for current, dirs, files in os.walk(base):
        for name in files:
            yield os.path.join(current, name)


def walk_dirs(base):
    for current, dirs, files in os.walk(base):
        for name in dirs:
            yield os.path.join(current, name)


def assert_contains(p, tokens):
    text = read(p)
    lowered = text.lower()
    for token in tokens:
        if token.lower() not in lowered:
            fail("%s missing token: %s" % (rel(p), token))


def parse_lesson_entries(text):
    entries = []
    current = None
    for line in text.splitlines():
        if line.startswith("- lesson_id:"):
            current = {"lesson_id": True}
            entries.append(current)
            continue
        if current is None:
            continue
        match = re.match(r"\s{2}([A-Za-z_]+):", line)
        if match:
            current[match.group(1)] = True
    return entries


def main():
    active_dirs = sorted(
        name
        for name in list_dir_names(SKILL)
        if is_dir(path(SKILL, name)) and name.startswith("gpgpu-")
    )
    if active_dirs != sorted(ACTIVE):
        fail("active design skill dirs mismatch: %r" % active_dirs)

    for old in OLD:
        if is_dir(path(SKILL, old)):
            fail("old top-level skill dir still exists: " + old)

    for skill in ACTIVE:
        skill_md = path(SKILL, skill, "SKILL.md")
        if not is_file(skill_md):
            fail("missing %s/SKILL.md" % skill)
        if len(read(skill_md).splitlines()) > 250:
            fail("%s/SKILL.md exceeds 250 lines" % skill)

    for required in REQUIRED_FILES:
        if not is_file(path(SKILL, required)):
            fail("missing required compact file: " + required)

    for required, tokens in PACK_TOKENS.items():
        assert_contains(path(SKILL, required), tokens)

    references = path(SKILL, "shared", "references")
    for directory in walk_dirs(references):
        if os.path.basename(directory) == "raw":
            fail("raw reference directory remains under skill/shared/references")

    lessons = path(references, "reference_lessons.yaml")
    if not is_file(lessons):
        fail("missing reference_lessons.yaml")
    required_fields = set(
        [
            "lesson_id",
            "source",
            "applies_to",
            "use_for",
            "do",
            "do_not",
            "acceptance_gate",
            "source_anchor",
        ]
    )
    entries = parse_lesson_entries(read(lessons))
    if not entries:
        fail("reference_lessons.yaml has no lessons")
    for idx, entry in enumerate(entries, 1):
        missing = sorted(required_fields - set(entry.keys()))
        if missing:
            fail("reference_lessons.yaml lesson %d missing %r" % (idx, missing))

    schema_dir = path(SKILL, "shared", "schemas")
    schema_count = len([name for name in list_dir_names(schema_dir) if is_file(path(schema_dir, name))])
    if schema_count > 35:
        fail("active schema count %d exceeds 35" % schema_count)

    table_dir = path(SKILL, "shared", "tables")
    table_count = len([name for name in list_dir_names(table_dir) if is_file(path(table_dir, name))])
    if table_count > 15:
        fail("active table count %d exceeds 15" % table_count)

    example_dir = path(SKILL, "shared", "examples")
    examples = sorted(name for name in list_dir_names(example_dir) if is_dir(path(example_dir, name)))
    if examples != ["full_memory_sync_litmus", "minimal_simt"]:
        fail("active examples mismatch: %r" % examples)

    for required in [
        "shared/schemas/run_state.schema.yaml",
        "shared/core/artifact_policy.yaml",
        "shared/templates/ai/en/run_state.en.md",
    ]:
        assert_contains(path(SKILL, required), ["RUN_STATE"])

    text_suffixes = (".md", ".yaml", ".yml", ".py")
    for current in walk_files(SKILL):
        if not current.endswith(text_suffixes):
            continue
        text = read(current)
        for phrase in FORBIDDEN:
            if phrase in text:
                fail("forbidden phrase %r found in %s" % (phrase, rel(current)))

    for required, tokens in REQUIRED_SKILL_TEXT.items():
        assert_contains(path(SKILL, required), tokens)

    print("PASS: compact GPGPU skill assets validated")


if __name__ == "__main__":
    main()
