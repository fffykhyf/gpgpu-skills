# Rocket SoC Composition Summary

Raw report: `raw/rocket_soc_composition_to_gpgpu_system.md`

Rocket composition is a reference for a system generator root and narrow-waist
attachment APIs. It is not a reference for GPU execution pipelines.

Rules for GPGPU skills:
- Emit `SYSTEM_COMPOSITION_IR` after `RESOLVED_CONFIG_IR` and before `ARCH_IR`.
- Represent compute, memory/data, control/MMIO, debug/trace, host-frontdoor, and
  interrupt/event planes as separate composition objects.
- Generate SM or cluster instances from attach records with stable IDs,
  crossing policy, trace policy, and harness effects.
- Keep clock/reset/interrupt crossings outside the execution pipeline and owned
  by wrapper or composition nodes.
- External DRAM, host, MMIO, and debug ports are config-owned attachments with
  protocol family, width, address range, ID policy, and harness closure.
- Emit memory map, resource map, graph, trace, and harness collateral from the
  same composition graph.

Anti-patterns:
- Building the NoC or control plane inside SM-local modules.
- Mixing launch MMIO, debug access, and throughput data traffic on one untyped
  crossbar.
- Maintaining firmware, debug, harness, or address-map metadata separately from
  the generated system.
