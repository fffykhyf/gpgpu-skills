# Rocket Interface Negotiation Summary

Raw report: `raw/rocket_diplomacy_to_gpgpu_interface_contract.md`

Rocket diplomacy is a reference for capability negotiation. It is not a
requirement to use TileLink. The transferable rule is that interfaces are
declared as endpoints, negotiated into edges, adapted explicitly when needed,
and monitored from negotiated facts.

Rules for GPGPU skills:
- Emit `NEGOTIATED_INTERFACE_IR` before binding RTL wires across SM, L1, NoC,
  L2, DRAM, host, runtime, or debug boundaries.
- Raw wire binding is forbidden unless it comes from a negotiated edge.
- The edge derives address width, data width, source/sink ID width, size width,
  beat bytes, max transfer, masks, beat counts, legality, ordering scope, error
  policy, and response shape.
- Width, fragment, source-id, atomic, buffer, and protocol bridge adapters are
  explicit `ADAPTER_CONTRACT` records.
- Adapters document translated fields, preconditions, state, monitors, and
  failure modes. They are not signal-renaming wrappers.
- Protocol monitors are generated from `NEGOTIATED_INTERFACE_IR`, not local
  constants.

Required failure behavior:
- Overlapping source IDs or address sets fail before RTL binding.
- Width or transfer-size mismatch without an adapter fails before RTL binding.
- Atomics are exposed only when the path natively supports them or an atomic
  adapter passes its structural preconditions.
- Protocol bridges document ID, burst, error, and ordering translation.
