# Rocket Chip Local Reference For GPGPU Golden Simulation

This note expands the Rocket Chip references that matter for the `gpgpu-golden-sim` skill. It focuses on protocol monitors, constrained fuzzing, unit-test harnesses, trace sinks, and validation collateral that complements a functional or timing golden simulator.

Terminology note: Rocket Chip does not provide a GPGPU ISA oracle. Preserve Rocket terms such as TileLink, Monitor, Fuzzer, UnitTest, and TestHarness when discussing the source. For local GPGPU work, translate the pattern to memory/control protocol monitors, legal random traffic, launch harnesses, trace schemas, and first-divergence debugging.

## What Rocket Chip Teaches For This Skill

Rocket's useful golden-sim lesson is that not every oracle is an ISA simulator. Protocol legality, source-ID lifetime, address/mask stability, start/finish/timeout, and trace integrity can be checked with smaller executable contracts.

Borrow these habits:

- write monitors for memory/control protocols;
- generate constrained legal random traffic instead of arbitrary bitstreams;
- give hardware tests explicit start, finish, timeout, and success semantics;
- keep trace sinks stable enough for first-divergence analysis.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/rocket.md` | Golden-sim lessons and seven-skill mapping. |
| `ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala` | TileLink legality assertions, multibeat field stability, source/sink in-flight checks. |
| `ref_submodule/rocket-chip/src/main/scala/tilelink/Fuzzer.scala` | Legal randomized TileLink traffic, source allocation/free, in-flight operations. |
| `ref_submodule/rocket-chip/src/main/scala/tilelink/Edges.scala` | Helper functions for mask, hasData, first/last/done, source/address. |
| `ref_submodule/rocket-chip/src/main/scala/unittest/UnitTest.scala` | Hardware unit-test start/finished conventions. |
| `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala` | SoC-level memory/debug/success harness wiring. |
| `ref_submodule/rocket-chip/src/main/scala/trace/` | Trace encoder/controller/sink/arbiter/monitor structure. |
| `ref_submodule/rocket-chip/regression/` | Scripted regression organization. |

## Monitor Pattern

`Monitor.scala` checks that multibeat TileLink operations do not change opcode, param, size, source, address, sink, denied, or mask across beats. It also tracks in-flight source IDs and rejects source ID reuse or responses for nothing in flight.

For local GPGPU golden work, create comparable local monitors for:

- memory request/response source tags;
- SIMT group and lane-mask stability;
- coalescer mapping from lanes to transactions;
- command queue entry ownership;
- barrier/fence/atomic ordering;
- fault/replay/completion responses.

## Fuzzer Pattern

`Fuzzer.scala` uses legal address/mask generation, source ID allocation, in-flight tracking, and response free logic. The local rule is that random tests must preserve legal protocol constraints. Illegal random bitstreams are less useful than constrained traffic that stresses the real contract.

## Harness And Trace Pattern

Rocket's unit tests and system harness make pass/fail visible. Trace infrastructure provides a structured event path. For GPGPU:

- every smoke test should have start, timeout, completion, and failure status;
- traces should include launch ID, compute core/CU, simt_group_id, PC, active lane mask, memory tag, and completion/fault;
- first divergence should identify protocol legality bugs separately from ISA/SIMT semantic bugs.

## Caveats

- Rocket monitors do not replace a GPGPU functional oracle.
- TileLink fields are not enough for GPU memory without lane masks, scope, address space, coalescer metadata, and SIMT identity.
- Use Rocket verification structure, not Rocket CPU instruction semantics.
