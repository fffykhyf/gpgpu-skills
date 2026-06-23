# Rocket Config Fragment Lessons Summary

Raw report: `raw/rocket_config_fragment_lessons.md`

Rocket config fragments show how a generator can compose product, debug, test,
and harness variants without forking RTL. The reusable abstraction is the
ordered config stack, not the Rocket core.

Rules for GPGPU skills:
- Emit `CONFIG_STACK_IR` before resolving architecture candidates.
- Emit `RESOLVED_CONFIG_IR` with every raw key, final value, owner skill, source
  fragment, consumers, derived fields, invariants, and collateral.
- Highest-priority overrides appear first; base defaults appear last.
- A fragment that changes one field of a structured record must transform the
  prior value instead of replacing unrelated fields.
- Global geometry such as cache-line bytes, beat bytes, source-id bits, bank
  counts, queue depths, and address ranges has one owner and explicit consumers.
- Builder-like options must declare extra ports, decode space, MMIO blocks,
  harness effects, trace effects, and tests.
- Validation invariants live beside the owning field and are generator-time
  checks, not late simulation surprises.

Anti-patterns:
- Anonymous nested maps with no owner.
- Multiple fragments silently owning the same leaf field.
- Runtime/debug/test side files that shadow generator truth.
- Local modules inventing widths, addresses, IDs, or queue depths.
