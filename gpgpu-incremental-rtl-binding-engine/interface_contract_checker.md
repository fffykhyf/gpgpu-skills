# Interface Contract Checker

The interface checker prevents incompatible RTL modules from being assembled into a full design.

## Required Checks

Each interface must define:

- `signal_width`
- `direction`
- `valid_ready_or_req_resp`
- `latency_min`
- `latency_max`
- `reset_value`
- `backpressure_rule`
- `trace_tap`

## Compatibility Rules

- Producer and consumer widths must match.
- Handshake protocol must be identical or bridged by an explicit adapter module.
- Latency bounds must not contradict pipeline boundary rules.
- Reset values must preserve legal contract state.
- Backpressure must not drop requests or duplicate serviced requests.

## Failure Modes

- `INTERFACE_PROTOCOL_MISMATCH`
- `LATENCY_INCOMPATIBLE`
- `PIPELINE_BOUNDARY_FAIL`
- `SIGNAL_WIDTH_MISMATCH`
