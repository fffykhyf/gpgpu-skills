# Rocket Chip Local Reference For GPGPU Config

This note expands the Rocket Chip references that matter for the `gpgpu-config` skill. It focuses on named config fragments, typed parameter bundles, derived values, Diplomacy-negotiated protocol parameters, legality checks, and generated resource/capability consistency.

Terminology note: Rocket config names describe a RISC-V SoC. Use Rocket names only when discussing the source. In local GPGPU config, translate them to compute core/CU, SIMT group, active lane mask, CTA/workgroup, memory partition, command queue, runtime ABI, and capability fields.

## What Rocket Chip Teaches For This Skill

Rocket Chip's strongest lesson is that configuration is part of the design:

- configs are named and composable;
- related knobs live in typed params;
- derived values are calculated near owners;
- illegal combinations fail early with `require`;
- bus/address/source capability is negotiated or checked;
- resource output and test harness assumptions track config choices.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/rocket.md` | Config lessons and seven-skill mapping. |
| `ref_submodule/rocket-chip/src/main/scala/system/Configs.scala` | `BaseConfig`, `DefaultConfig`, `DualCoreConfig`, memory-channel and benchmark configs. |
| `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala` | `WithRoccExample`, `WithNMemoryChannels`, bus/topology fragments. |
| `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala` | `WithNBigCores`, medium/small/tiny cores, `RocketTileConfig`, `RocketCoreConfig`, `RocketDCacheConfig`. |
| `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala` | `RocketTileParams`: core, ICache, DCache, BTB, boundary buffers, clock crossing. |
| `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala` | `DCacheParams`: sets, ways, rowBits, nMSHRs, nSDQ, nRPQ, nMMIOs, ECC, scratchpad. |
| `ref_submodule/rocket-chip/src/main/scala/diplomacy/Parameters.scala` | Dynamic parameter system and parameter lookup discipline. |
| `ref_submodule/rocket-chip/src/main/scala/resources/` | Device-tree/resource output for runtime-visible capabilities. |

## Config Fragments

Rocket uses small composable fragments such as `WithNBigCores`, `WithNMemoryChannels`, `WithRoccExample`, `WithRV32`, `WithFP16`, `WithHypervisor`, and benchmark/no-memory variants. Local GPGPU config should use the same style:

- avoid copying a full config to change one knob;
- name smoke, target, and experiment configs;
- record config names in tests and PPA reports;
- separate hardware-private, simulator-private, HW/SW ABI, test-only, and debug-only values.

## Typed Params And Derived Fields

`RocketTileParams`, `RocketCoreParams`, and `DCacheParams` group related values. `DCacheParams` includes cache shape, MSHRs, store-data queue, replay queue, MMIO slots, scratchpad, ECC, and replacement policy. `HellaCache.scala` derives source ID ranges for cached and MMIO requests from `nMSHRs` and `nMMIOs`.

For local GPGPU config:

- derive active mask width from SIMT group width;
- derive source/tag width from outstanding memory capacity;
- derive register-bank and writeback-port counts from issue/FU config;
- derive cache/coalescer masks from line/beat/lane widths;
- fail early on unsupported bank, queue, source ID, or ABI combinations.

## Diplomacy Lesson

Diplomacy nodes negotiate or check widths, transfer sizes, address sets, source ID ranges, and manager/client capabilities. A local project does not need to implement Diplomacy, but it must not hide those values as scattered constants.

If a config affects address ranges, transfer sizes, queue depth, source IDs, MMIO maps, or optional ports, update:

- RTL params;
- simulator params;
- runtime ABI or capability query;
- tests and monitor assumptions;
- PPA config IDs.

## Caveats

- Rocket's core-size configs are CPU pipeline configs, not SIMT occupancy configs.
- Rocket's hart IDs and CSR settings are not GPU public ABI.
- TileLink capability negotiation is a design pattern; local protocols still need GPU-specific fields such as SIMT group, lane mask, CTA/workgroup, scope, and memory space.
