# rocket Source Summary

Distilled active summary from archived reference notes.

## README

# Rocket Generator Reference

This directory records Rocket Chip lessons that are safe to reuse in the GPGPU
skill system. Rocket is used here as a generator, configuration, interface,
MMIO, debug, and verification reference.

Use these lessons for:
- ordered config fragments and resolved config ownership
- system composition roots and generated collateral
- negotiated interface edges, adapters, and protocol monitors
- declarative MMIO register maps and debug/counter blocks
- harness closure, unit-test contracts, fuzzers, trace sinks, and compile-only drift gates

Do not use Rocket as a GPU pipeline reference. Do not copy Rocket scalar
pipeline stages, CLINT or PLIC register layout, TileLink as a mandatory protocol,
or CPU privilege semantics.

Raw reader reports are copied under `raw/`. Curated summaries in this directory
are the preferred AI-facing references for skill rules.

## config_fragment_lessons

# Rocket Config Fragment Lessons Summary

Raw report: `raw/rocket_config_fragment_lessons.md`

Rocket config fragments show how a generator can compose product, debug, test,
and harness variants without forking RTL. The reusable abstraction is the
ordered config stack, not the Rocket core.

Rules for GPGPU skills:
- Emit `CONFIG_STACK_IR` before resolving architecture candidates.
- Emit `RESOLVED_CONFIG_IR` with every raw key, final value, owner skill, source
  fragment, consumers, derived fields, invariants, and collateral.
- Highest-priority overrides appear first; base defaults appear last.
- A fragment that changes one field of a structured record must transform the
  prior value instead of replacing unrelated fields.
- Global geometry such as cache-line bytes, beat bytes, source-id bits, bank
  counts, queue depths, and address ranges has one owner and explicit consumers.
- Builder-like options must declare extra ports, decode space, MMIO blocks,
  harness effects, trace effects, and tests.
- Validation invariants live beside the owning field and are generator-time
  checks, not late simulation surprises.

Anti-patterns:
- Anonymous nested maps with no owner.
- Multiple fragments silently owning the same leaf field.
- Runtime/debug/test side files that shadow generator truth.
- Local modules inventing widths, addresses, IDs, or queue depths.

## diplomacy_interface_contract

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

## generator_verification

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

## mmio_runtime_debug

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

## repo_map

# Rocket Repository Map Summary

Raw report: `raw/rocket_repo_map_for_gpgpu.md`

Rocket Chip is useful because it is a parameterized SoC generator, not because it
contains a scalar CPU implementation. The transferable packages are `subsystem`,
`system`, `diplomacy`, `tilelink`, `amba`, `devices`, `regmapper`, `trace`,
`unittest`, and `groundtest`.

Transferable rules:
- Put topology, MMIO address ownership, debug/control planes, and generated
  collateral under one subsystem composition root.
- Declare protocol capabilities before RTL binding and derive concrete widths,
  IDs, masks, and monitors from negotiated edges.
- Generate memory maps, resolved config, interface maps, launch ABI collateral,
  test harnesses, and trace schemas beside RTL.
- Keep SM/cluster wrappers as system integration surfaces, not raw execution
  pipelines.

Do not transfer:
- Rocket scalar pipeline staging, frontend speculation, or CPU decode/control.
- CLINT/PLIC/debug register layouts as fixed GPGPU ABI.
- TileLink as mandatory transport.
- CPU privilege semantics or Rocket coherence assumptions as GPU truth.

## soc_composition

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
