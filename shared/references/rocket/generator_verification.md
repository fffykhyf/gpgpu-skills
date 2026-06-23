# Rocket Generator Verification Summary

Raw report: `raw/rocket_generator_verification_to_gpgpu.md`

Rocket verification shows that generator outputs include tests, harnesses,
monitors, fuzzers, trace sinks, and compile-only coverage. These are reusable
patterns for GPGPU verification closure.

Rules for GPGPU skills:
- Each unit-testable RTL block exposes `start`, `finished`, and a local timeout.
- A harness closure artifact lists every external DRAM, MMIO, debug, host,
  trace, interrupt, and clock/reset port as connected to a model or tied off.
- Protocol monitors are generated per negotiated edge and include timeout,
  multibeat stability, source/sink uniqueness, and response matching when
  applicable.
- Memory and atomic features require a shadow memory or semantic checker in
  addition to protocol monitors.
- Adapters require legal-traffic fuzzers with a deterministic finish condition.
- Runtime-visible behavior requires a trace schema and a trace sink or checker
  path.
- Named configs are classified as executed or compile-only so unsupported-to-run
  configurations still elaborate and cannot rot.

Anti-patterns:
- Floating harness ports.
- Tests that only print logs without a completion bit.
- Random generators that mostly produce illegal transactions.
- Compile-only configs that are undocumented or omitted from CI evidence.
