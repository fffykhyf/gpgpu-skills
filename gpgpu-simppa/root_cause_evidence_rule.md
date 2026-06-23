# Root Cause Evidence Rule

Every root cause must include:

- symptom counter;
- exclusion counter;
- queue or stage owner;
- possible fix target;
- confidence;
- contract path or explicit evidence gap.

If any field is missing, emit `INSUFFICIENT_TRACE_EVIDENCE` or route to
`COUNTER_SCHEMA_PATCH` / `TEST_EVIDENCE_PATCH`.

