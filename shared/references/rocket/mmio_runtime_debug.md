# Rocket MMIO Runtime Debug Summary

Raw report: `raw/rocket_mmio_runtime_debug_to_gpgpu.md`

Rocket regmapper and debug devices are references for generator-owned
software-visible state. Transfer the declarative register-map pattern, not
CLINT, PLIC, debug-module, or CPU privilege ABI layouts.

Rules for GPGPU skills:
- Emit `MMIO_REGISTER_MAP_IR` from the generator for runtime-visible registers.
- Required blocks are discovery, launch, status, interrupt, fault, trace, debug,
  and counters.
- Each field records access, reset, volatility, side effects, enumerations when
  needed, and generated documentation/resource-map output.
- `START` is separate from `BUSY`, `DONE`, `FAULTED`, and `ACK`.
- `START/BUSY/DONE/FAULTED/ACK` smoke gate writes a descriptor, pulses START,
  observes BUSY, reaches exactly one terminal state, holds that state until ACK,
  and rejects or records a second START while BUSY.
- Fault state records cause, value, accrued state, and W1C or explicit clear
  semantics.
- Counter control is separate from read-only volatile counter data.
- Debug and trace presence is discoverable and conditioned on resolved config.

Anti-patterns:
- A single undocumented CSR blob.
- Control bits used as completion proof.
- Field semantics hidden in drivers or comments.
- Runtime address maps maintained outside generator collateral.
