# Producer Audit

Audit every counter before use:

1. Find the producer event path.
2. Confirm update/reset/sample window.
3. Classify status.
4. Reject parser-only variables for stable gates.
5. Mark defined-only counters as evidence gaps.

Visualizer names are not stable metrics without producer proof.

## Structured Trace Producer Audit

For each `STRUCTURED_TRACE_TABLE`, audit table producer module, producer event,
write gate, schema version, sample window, and consumer skill. A table without
producer proof can support exploratory debug only; it cannot close
`SQL_PERF_QUERY` attribution or weighted performance gates.
