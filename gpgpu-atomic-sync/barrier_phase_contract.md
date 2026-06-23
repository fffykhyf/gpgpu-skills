# Barrier Phase Contract

Barrier is a participant coordination primitive. It is not a fence unless the
contract explicitly adds a memory drain or visibility rule.

```yaml
barrier_phase:
  barrier_id:
  scope: warp | sm | grid
  phase:
  participant_set:
  arrival_bitmap:
  wait_mask:
  release_bitmap:
  lsu_drain_required:
  release_cycle:
```

Rules:

- Barrier release cannot substitute for memory visibility by default.
- If barrier requires LSU drain, the drain must complete before release.
- `BARRIER_PHASE_MISMATCH` routes to `SYNC_ATOMIC_PATCH`.
