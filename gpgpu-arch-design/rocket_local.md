# Rocket Chip Local Reference For GPGPU Architecture Design

This note expands the Rocket Chip references that matter for the `gpgpu-arch-design` skill. It focuses on SoC generator organization, named configurations, Diplomacy boundaries, tile/core/periphery layering, RoCC accelerator control, runtime-visible resources, protocol checks, and harness integration.

Terminology note: Rocket Chip is a scalar RISC-V SoC generator, not a GPGPU. Preserve Rocket names such as tile, hart, RoCC, TileLink, BootROM, and DTS when discussing the source. In local GPGPU contracts, translate the lesson to compute core/CU, SIMT group, active lane mask, CTA/workgroup, command queue, memory/control protocol, and runtime capability.

## What Rocket Chip Teaches For This Skill

Rocket Chip's architecture value is generator and integration discipline:

- architecture is a generated system, not just a datapath;
- configuration, protocol capability, tile boundary, resource exposure, debug, and harness wiring are architecture-level concerns;
- optional features have config, interface, resource, test, and perf/debug consequences;
- protocol contracts are executable through monitors/fuzzers.

Do not use Rocket Core as a SIMT core template. Use Rocket Chip to make GPGPU architecture proposals more explicit and reproducible.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/rocket.md` | Top-level summary and seven-skill mapping. |
| `ref_submodule/rocket-chip/README.md` | Repository purpose, generator structure, build commands, package map. |
| `ref_submodule/rocket-chip/src/main/scala/system/Configs.scala` | `BaseConfig`, `DefaultConfig`, named SoC configs. |
| `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala` | memory channels, RoCC example, bus/topology config fragments. |
| `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala` | tile params, hart ID, cache/MMU/PMP, tile master/slave boundaries. |
| `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala` | core, frontend, DCache, RoCC, trace, interrupt, bus error, scratchpad integration. |
| `ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala` | accelerator command/response/memory/busy/interrupt control plane. |
| `ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala` | executable protocol checks and in-flight source tracking. |
| `ref_submodule/rocket-chip/src/main/scala/system/ExampleRocketSystem.scala` | BootROM, external memory/MMIO/interrupt integration. |
| `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala` | simulator-facing memory/debug/success wiring. |

## Architecture Boundary Pattern

Rocket Chip separates:

- subsystem/periphery: buses, memory ports, MMIO, interrupts, BootROM, debug;
- tile: core, caches, optional accelerators, trace, interrupt, error handling;
- core: scalar pipeline, decode, CSR, event counters, optional FPU/RoCC/vector hooks;
- protocol layer: TileLink nodes, edges, adapters, monitors, and fuzzers.

For local GPGPU architecture, require proposals to name whether a new feature belongs to:

- SIMT core internals;
- compute core/CU boundary;
- memory client or cache hierarchy;
- runtime-visible command/status block;
- debug/trace/perf plane;
- test harness only.

## Generator And Diplomacy Lessons

Rocket's `Config` fragments and Diplomacy/LazyModule style show that address ranges, source IDs, transfer sizes, bus widths, and capabilities should be derived or checked before RTL generation. Local architecture docs should therefore state:

- which config fragment enables the feature;
- which protocol fields or ID ranges it consumes;
- how runtime/software discovers the capability;
- which monitor or harness observes it.

## RoCC As Control-Plane Analogy

`LazyRoCC.scala` defines command, response, memory, busy, interrupt, exception, CSR, PTW, TileLink client, command router, and response arbiter. A GPGPU launch/control plane can borrow this structure:

- command queue or doorbell;
- kernel descriptor fields;
- memory access path;
- busy/completion/fault/interrupt;
- optional debug/perf ports.

RoCC is not a GPU runtime. It is a clean accelerator boundary pattern.

## Caveats

- Do not infer warp/SIMT/CTA semantics from Rocket Core.
- Do not copy RISC-V CSR/exception/privileged behavior as GPU kernel ABI.
- Do not treat TileLink coherence policy as the local GPU memory model.
- Do not skip Vortex, MIAOW, or GPGPU-Sim when defining actual GPU execution semantics.
