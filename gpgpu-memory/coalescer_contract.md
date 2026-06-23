# Coalescer Contract

Input:

- per-lane address;
- active mask;
- access size;
- access type;
- byte enables;
- coalescing policy.

Output:

- ordered transactions;
- coalesced group id;
- transaction mask;
- split reason;
- amplification counter.

Do not copy NVIDIA-generation coalescing rules unless a compatibility profile
selects them.

## Structured Trace Requirements

Coalescer features must provide `COALESCER_LOG` as a
`STRUCTURED_TRACE_TABLE`, plus one `SQL_DEBUG_QUERY` for mismatch localization
and one `SQL_PERF_QUERY` for request-reduction or amplification attribution.
