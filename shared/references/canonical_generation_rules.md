# Canonical Generation Rules

All generated IR and derived artifacts must be deterministic before hash
calculation, comparison, validation, or rewrite routing.

## 1. Canonical Input Normalization

Normalize input specs to UTF-8 text and structured IR before derivation. Remove
comments, trailing whitespace, random UUIDs, timestamps, absolute local paths,
tool wall time, simulator wall time, and raw tool banners from hash inputs.

## 2. Canonical YAML / JSON Serialization

Hash inputs must be serialized as canonical JSON:

- UTF-8
- sorted object keys
- no comments
- no trailing whitespace
- no implicit YAML anchors
- no timestamp
- no random UUID
- no absolute local path

YAML may remain the human-edited interchange format, but comparison hashes are
computed from canonical JSON.

## 3. Stable ID Generation

IDs must not depend on generation order, timestamps, UUID4, random suffixes, or
local filesystem state.

Use:

```text
<artifact_kind>_<canonical_slug>_<short_hash>
```

Examples:

```text
arch_ir_minimal_simt_core_a13f29c0
module_warp_scheduler_7d31a912
trace_event_issue_warp0_pc00000004_91ab22e0
```

## 4. Stable Module / Signal / File Naming

Generated names must be derived from contract paths, module roles, and canonical
profile names.

```text
module name = gpgpu_<subsystem>_<pattern>_<width/profile optional>
signal name = <role>_<payload>_<direction>
file name = <module_name>.sv
testbench name = tb_<module_name>.sv
assertion module = assert_<module_name>.sv
```

Forbidden generated names include `tmp`, `foo`, `new_signal`,
`generated_signal_1`, `wire_123`, and `my_module`.

## 5. Artifact Hash Calculation

Artifact hashes use:

```text
sha256:<64 lowercase hex chars>
```

The hash object is `canonical_json_without_volatile_fields`.

## 6. Volatile Field Policy

Volatile data must be isolated under `volatile_fields` or removed before
canonical hash comparison.

Default volatile fields:

```yaml
volatile_fields:
  - generated_at
  - local_absolute_path
  - tool_wall_time_sec
  - yosys_version_banner_raw
  - simulator_wall_time_sec
```

## 7. Deterministic List Ordering

Ordered lists preserve semantic order:

- instruction stream
- trace events
- pipeline stages
- priority rules
- rewrite steps

Set-like lists sort by canonical string:

- enabled_subsystems
- required_features
- warnings
- rejected_alternatives
- source artifact refs

Do not sort a list unless its schema or artifact policy declares it set-like.

## 8. Deterministic Failure Handling

Failure routing must use stable enum values, stable contract paths, and stable
rewrite route selection. Do not route based on log order, dictionary iteration
order, local path order, or nondeterministic tool output order.

## 9. RTL-Specific Deterministic Naming

RTL modules, assertions, testbenches, and generated file paths must be derived
from module role, contract path, interface protocol, and capability profile.
Assertion names use:

```text
assert_<module_name>_<property_name>
```

## 10. Comparison Modes

```yaml
comparison_policy:
  byte_identical:
    volatile_fields_allowed: false

  semantic_identical_excluding_volatile:
    volatile_fields_allowed: true
    compare_hash: canonical_hash

  hash_identical:
    volatile_fields_allowed: false
    compare_hash: canonical_hash

  evidence_equivalent:
    volatile_fields_allowed: true
    compare_required_fields_only: true
```

P0 determinism CI should use
`semantic_identical_excluding_volatile` first and upgrade to `byte_identical`
only when all generators emit stable bytes.
