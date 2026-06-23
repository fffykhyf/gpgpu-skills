# Local Memory Bank Contract

Shared memory and local memory are SM-local unless the frozen system contract
states otherwise.

```yaml
local_memory_bank:
  sm_id:
  bank_count:
  bank_mapping_function:
  conflict_policy:
  read_during_write_policy:
  response_hold_register:
  backpressure_behavior:
  barrier_visibility_rule:
```

Required tests:

- shared memory bank conflict;
- same-bank multi-lane access;
- response held under downstream backpressure;
- barrier after shared memory access waits for required visibility.
