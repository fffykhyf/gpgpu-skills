# Cache Coherence Model

This contract defines cross-CU cache and memory visibility.

## Cache Policy

writeback vs write-through policy must be explicit for each cache level:
- L1
- L2
- write-combining buffer if present
- uncached path if present

Required fields:
- line size
- write allocate policy
- replacement visibility caveat
- dirty state owner
- invalidation or update mechanism
- response ordering rule

## Atomic Visibility Rules

atomic visibility rules are consumed from `gpgpu-atomic-sync`. This memory skill
records how the cache hierarchy preserves or forwards atomic visibility, but it
does not independently choose the atomic serialization point.

Required fields:
- atomic path
- line lock or bypass rule
- visibility completion event
- cache invalidation or update action

## Cross-CU Coherence

cross-CU coherence must define:
- which writes become visible to other CUs
- when reads can observe another CU's writes
- how L1 private caches interact with shared L2
- whether LDS is excluded from cross-CU visibility
- how fences force visibility

## Coherence State Model

Minimal allowed states:
- `INVALID`
- `SHARED`
- `EXCLUSIVE`
- `MODIFIED`
- `BYPASS`

Simpler designs may use a subset, but must state which states are absent and
why correctness still holds.

## Failure Modes

Failures include:
- stale read across CU
- write visibility missing
- dirty writeback lost
- invalidation missing
- atomic visibility violation
- fence visibility violation
