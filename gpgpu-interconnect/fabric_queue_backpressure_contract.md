# Fabric Queue Backpressure Contract

Fabric backpressure is observable performance state and must not be hidden in
implementation-private queues.

## Queue Contract

```yaml
fabric_queue_backpressure:
  source_sm_id:
  queue_id:
  traffic_class:
  queue_occupancy:
  almost_full:
  arbitration_wait_cycles:
  virtual_channel:
  route_id:
```

## Rules

- Queue occupancy must be trace-visible for every route with backpressure.
- Atomic/fence queues must not be collapsed into ordinary load/store queues
  without an explicit synchronization contract.
- Missing backpressure evidence is `FABRIC_QUEUE_BACKPRESSURE_MISSING`.
