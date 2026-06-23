# Root Cause Engine

The root cause engine classifies correctness and performance failures from `PERF_ATTRIBUTION_GRAPH`.

## Root Cause Classes

- `CONTRACT_VIOLATION`
- `RTL_STRUCTURAL_ISSUE`
- `MEMORY_IMBALANCE`
- `SCHEDULING_INEFFICIENCY`
- `INTERFACE_PROTOCOL_MISMATCH`
- `GOLDEN_MODEL_MISMATCH`
- `INSUFFICIENT_TRACE_EVIDENCE`

## Required Output

- `root_cause_class`
- `minimal_trace_window`
- `contract_paths`
- `rtl_module_paths`
- `evidence_hashes`
- `confidence`
- `rewrite_candidate`

## Ranking Rule

Prefer the earliest deterministic failure in the causal graph. If multiple causes cannot be ranked from evidence, emit `ROOT_CAUSE_AMBIGUOUS`.
