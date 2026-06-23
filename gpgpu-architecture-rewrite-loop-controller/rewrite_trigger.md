# Rewrite Trigger

Rewrite triggers map root causes to patch classes and revalidation routes.

## Trigger Mapping

| Root cause | Patch options |
|---|---|
| `MEMORY_IMBALANCE` | Architecture Patch or RTL Patch |
| `SCHEDULING_INEFFICIENCY` | Architecture Patch or Contract Patch |
| `RTL_STRUCTURAL_ISSUE` | RTL Patch |
| `CONTRACT_VIOLATION` | Contract Patch |
| `INTERFACE_PROTOCOL_MISMATCH` | RTL Patch |
| `GOLDEN_MODEL_MISMATCH` | Contract Patch or Golden Semantics Bug |

## Gate

Do not trigger a patch without `PERF_ATTRIBUTION_GRAPH` evidence and a `ROOT_CAUSE_REPORT`.
