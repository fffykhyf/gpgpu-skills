# Interface Binding And Checker

The interface checker prevents incompatible RTL modules from being assembled
into a full design. Interfaces are checked as `INTERFACE_BINDING_IR`, not loose
signal maps.

## INTERFACE_BINDING_IR

Each interface binding must define:

- `interface_id`
- `producer_module`
- `consumer_module`
- `protocol`
  - `type`: `VALID_READY`, `REQ_RSP_TAGGED`, `CSR_MMIO`, or `STREAM`
- `payload`
  - `fields`
    - `name`
    - `width`
    - `signedness`
    - `semantic_path`
- `handshake`
  - `accepted_when`
  - `stall_rule`
  - `payload_stability_when_stalled`
- `ordering`
  - `in_order`
  - `tag_unique_until_response`
- `latency`
  - `min`
  - `max`
- `reset`
  - `valid_reset`
  - `ready_reset`
- `trace_tap`
  - `fire_event`
  - `payload_fields`
- `adapter`
  - `allowed`
  - `adapter_module`

## Required Checks

- producer and consumer payload fields match in name, width, signedness, and
  semantic path
- handshake protocol matches or is bridged by an explicit adapter module
- accepted transaction rule is declared
- stalled payload stability is declared and checked
- request tags are unique until response when `REQ_RSP_TAGGED` is used
- same-tag response ordering is declared
- latency bounds are compatible with pipeline boundaries
- reset values preserve legal contract state
- trace taps cover fire event and payload fields
- fault and completion propagation is declared
- CSR visibility and runtime handoff are declared for `CSR_MMIO`
- no combinational ready loop exists

## Adapter Rule

An adapter is allowed only when `adapter.allowed = true` and
`adapter.adapter_module` names a catalog module with its own template, contract
paths, partial simulation cases, and timing feedback. Silent protocol coercion
is forbidden.

## Failure Modes

- `INTERFACE_PROTOCOL_MISMATCH`
- `LATENCY_INCOMPATIBLE`
- `PIPELINE_BOUNDARY_FAIL`
- `SIGNAL_WIDTH_MISMATCH`
- `BACKPRESSURE_DROP_OR_DUPLICATE`
- `TAG_REUSE_BEFORE_RESPONSE`
- `PAYLOAD_STABILITY_FAIL`
- `COMBINATIONAL_READY_LOOP`
- `FAULT_COMPLETION_PATH_UNBOUND`
