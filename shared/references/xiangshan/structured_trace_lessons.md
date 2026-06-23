# Structured Trace Lessons

XiangShan ChiselDB teaches that high-cardinality debug and performance events
should be recorded as structured trace tables with queries, not only as VCD or
printf output.

GPGPU abstraction:

- `STRUCTURED_TRACE_TABLE` defines table name, schema version, common fields,
  producer, write gate, retention, and consumer skill.
- `TRACE_DB_MANIFEST` lists tables, schema versions, config hash, workload,
  producer build, and storage path.
- `SQL_DEBUG_QUERY` gives feature-specific root-cause queries.
- `SQL_PERF_QUERY` gives feature-specific attribution queries.

Required table families include warp issue/commit, scoreboard, memory
transaction, coalescer, cache access, MSHR, NoC packet, barrier, fence, atomic,
runtime launch, fault, and counter snapshot logs.

Rule: every memory, scheduling, sync, atomic, or performance feature must
provide at least one debug query and one performance attribution query.

