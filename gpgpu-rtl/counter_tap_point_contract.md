# Counter Tap Point Contract

Every stable counter needs a tap point:

- producer module;
- producer event;
- counter name;
- unit;
- sampling window;
- reset behavior;
- stable/debug status;
- consumer skill.

Tap points collect evidence; power or root-cause models remain outside RTL.

## Trace DB Counter Sink

Stable counters that participate in XiangShan-style structured trace must name
their `STRUCTURED_TRACE_TABLE`, write gate, schema version, and
`TRACE_DB_MANIFEST` consumer path. Debug-only counters must be marked so they do
not contaminate performance ranking.
