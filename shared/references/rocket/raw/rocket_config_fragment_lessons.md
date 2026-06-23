# Rocket Config Fragment Lessons for GPGPU Skill

## Metadata
- Mode: `repository`
- Depth: `deep`
- Output profile: `model-evidence`
- Corpus: `ref_submodule/rocket-chip` at commit `55bcad0`
- Planner: `ref/skillref/rocket.md`
- Write target: `ref/skillref/rocket-reader-reports/rocket_config_fragment_lessons.md`
- Focus: Config / Parameters / Mixins only
- Questions answered: parameter keys, `WithXXX` overrides, `++` composition, ownership split, derived params and `require`, collateral fanout
- Non-goals: Rocket CPU pipeline detail except where it proves parameter ownership or generator structure
- Files read:
  `ref_submodule/rocket-chip/README.md`
  `ref_submodule/rocket-chip/src/main/scala/diplomacy/Main.scala`
  `ref_submodule/rocket-chip/src/main/scala/system/Configs.scala`
  `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala`
  `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala`
  `ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala`
  `ref_submodule/rocket-chip/src/main/scala/subsystem/RocketSubsystem.scala`
  `ref_submodule/rocket-chip/src/main/scala/subsystem/SystemBus.scala`
  `ref_submodule/rocket-chip/src/main/scala/subsystem/MemoryBus.scala`
  `ref_submodule/rocket-chip/src/main/scala/subsystem/PeripheryBus.scala`
  `ref_submodule/rocket-chip/src/main/scala/subsystem/BusTopology.scala`
  `ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala`
  `ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala`
  `ref_submodule/rocket-chip/src/main/scala/subsystem/BankedCoherenceParams.scala`
  `ref_submodule/rocket-chip/src/main/scala/subsystem/InterruptBus.scala`
  `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala`
  `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala`
  `ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala`
  `ref_submodule/rocket-chip/src/main/scala/tile/Core.scala`
  `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala`
  `ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala`
  `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala`
  `ref_submodule/rocket-chip/src/main/scala/unittest/Configs.scala`
  `ref_submodule/rocket-chip/src/main/scala/groundtest/Configs.scala`
  `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala`
- Files skipped: full Rocket microarchitecture beyond parameter definitions, parameter consumers, and `require(...)` sites; unrelated AMBA/TileLink implementation details not needed for this shard

## Corpus Inventory
- Rocket is a generator repo, not a CPU-only repo: the README describes `make verilog CONFIG=...` flow and states the repository is a Scala program that emits a complete SoC (`ref_submodule/rocket-chip/README.md`).
- This shard's source-of-truth chain is:
  `system/Configs.scala` for named end-user config classes;
  `subsystem/*.scala` for global keys, topology keys, port keys, and subsystem consumers;
  `rocket/Configs.scala` for tile/core/cache mixins;
  `tile/*.scala` and `rocket/*.scala` for local parameter owners and `require(...)` guards;
  `unittest/Configs.scala` and `groundtest/Configs.scala` for test collateral;
  `devices/debug/Periphery.scala` and `system/TestHarness.scala` for debug collateral.

## Rocket Mechanism Summary
- `CONFIRMED`: Rocket parameter keys are typed Scala keys, mostly `case object ... extends Field[T]`, sometimes `case class` when location-scoped, and sometimes function-valued when the config selects a builder. Examples: `SystemBusKey`, `MemoryBusKey`, `CacheBlockBytes`, `ExtMem`, `TilesLocated(loc)`, `ExportDebug`, `TileKey`, `BuildRoCC`, `BuildHellaCache` (`ref_submodule/rocket-chip/src/main/scala/subsystem/BusTopology.scala:15-19`, `ref_submodule/rocket-chip/src/main/scala/subsystem/BankedCoherenceParams.scala:23-36`, `ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:47-49`, `ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:23-29`, `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:30-42`, `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala:29-31`, `ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala:22`, `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala:261`).
- `CONFIRMED`: `WithXXX` fragments use four recurring update patterns. Pattern 1: set a leaf directly, e.g. `case CacheBlockBytes => linesize`. Pattern 2: transform an existing record with `up(Key).copy(...)`, e.g. `WithNBanks`, `WithDebugSBA`, `WithNMemoryChannels`, bus-frequency mixins. Pattern 3: append to a sequence with `up(Key) :+ ...` or `List.tabulate(...) ++ prev`, e.g. cluster and tile attach fragments. Pattern 4: bulk-rewrite nested tile/core/cache params through helper fragments such as `RocketTileConfig`, `RocketCoreConfig`, `RocketICacheConfig`, and `RocketDCacheConfig` (`ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:107-160`, `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:126-143`, `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:217-257`, `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:349-367`, `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:19-50`, `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:203-245`, `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:264-301`).
- `CONFIRMED`: `site(Key)` is used when a fragment needs the resolved value of another key, including values defined to its right in the config stack; `up(Key)` is used when a fragment wants the lower-priority value and only tweaks part of it. Examples: tile fragments read `site(SystemBusKey).beatBits` and `site(CacheBlockBytes)` while subsystem fragments tweak existing case-class records through `up(...)`. `here` is present in signatures but not materially used in this shard (`ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:30-64`, `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:126-143`, `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:66-87`, `ref_submodule/rocket-chip/src/main/scala/groundtest/Configs.scala:43-72`).
- `INFERRED from local call sites`: `A ++ B` layers `A` over `B`. Evidence: named configs place targeted overrides on the left of `BaseConfig`; `TinyConfig` only removes memory if `WithNoMemPort` overrides `BaseConfig`; `GroundTestBaseConfig` overlays `BaseConfig().alter(...)`; CLI composition in `diplomacy/Main.scala` folds config names right-to-left and applies `currentConfig ++ config`. Exact `Config` internals are outside this repo snapshot, so composition order is not locally proven from the library implementation (`ref_submodule/rocket-chip/src/main/scala/system/Configs.scala:14-107`, `ref_submodule/rocket-chip/src/main/scala/groundtest/Configs.scala:28-35`, `ref_submodule/rocket-chip/src/main/scala/diplomacy/Main.scala:23-27`).
- `CONFIRMED`: ownership splits into system-connection keys and module-local params. System keys instantiate buses, coherence managers, port IO, debug transport attachment, tile reset-vector IO, and DTS/memmap artifacts. Tile-local params live inside `RocketTileParams`, `RocketCoreParams`, `ICacheParams`, `DCacheParams`, and builder keys, but some local fields still fan out into system structure such as DCache port counts, TL clients, decode table contents, trace blocks, and tile properties (`ref_submodule/rocket-chip/src/main/scala/subsystem/BusTopology.scala:70-133`, `ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:53-245`, `ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:57-127`, `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:58-164`, `ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala:84-115`, `ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala:16-84`, `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala:23-62`, `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala:199-286`).
- `CONFIRMED`: derived params are first-class. `BaseSubsystemConfig` computes `MaxXLen` and `MaxHartIdBits` from the final tile population. Tile/core traits derive fetch width, decode width, address widths, hart-id width, scratchpad size, and cache geometry from resolved config plus negotiated bus visibility (`ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:30-35`, `ref_submodule/rocket-chip/src/main/scala/tile/Core.scala:62-146`, `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala:66-104`, `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala:196-217`, `ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala:63-83`, `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala:64-100`).
- `CONFIRMED`: invalid combinations are rejected close to the owner with `require(...)`: bank count legality, VM/page geometry, XLEN, RoCC CSR uniqueness, cache scratchpad legality, `CFLUSH_D_L1` versus scratchpad, hartid truncation, and DCache port accounting (`ref_submodule/rocket-chip/src/main/scala/subsystem/BankedCoherenceParams.scala:38-43`, `ref_submodule/rocket-chip/src/main/scala/tile/Core.scala:124-145`, `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala:79-87`, `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala:198-206`, `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:49-50`, `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:230-232`, `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:278-282`, `ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala:71`, `ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala:87-88`, `ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala:94-95`, `ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala:324-326`, `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala:56-61`, `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala:95-99`, `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala:229`, `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala:249-255`).
- `CONFIRMED`: config affects collateral beyond RTL. Base subsystem emits `graphml`, `plusArgs`, `dts`, `json`, and `memmap.json`; debug config changes exported DMI/JTAG/APB IO and optional SBA master path; mem/MMIO/slave keys generate or remove external AXI4/TL ports; unit tests and ground tests are normal config fragments in the same parameter graph (`ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala:31-45`, `ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala:115-139`, `ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala:151-155`, `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:50-61`, `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:77-103`, `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:123-184`, `ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:53-245`, `ref_submodule/rocket-chip/src/main/scala/unittest/Configs.scala:15-179`, `ref_submodule/rocket-chip/src/main/scala/groundtest/Configs.scala:16-72`, `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala:18-41`).

## Module-Local vs System-Connection-Affecting

| Class | Rocket examples | Owner files | Generated effects |
|---|---|---|---|
| System-connection-affecting | `SystemBusKey`, `MemoryBusKey`, `PeripheryBusKey`, `TLNetworkTopologyLocated`, `SubsystemBankedCoherenceKey`, `ExtMem`, `ExtBus`, `ExtIn`, `ExportDebug`, `DebugModuleKey`, `HasTilesExternalResetVectorKey`, crossing keys | `ref_submodule/rocket-chip/src/main/scala/subsystem/BusTopology.scala`, `ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala`, `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala`, `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala`, `ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala` | bus wrappers, coherence manager, external AXI4/TL IOs, debug IOs, tile reset-vector IOs, clock/reset topology, DTS/memmap artifacts |
| Module-local | `RocketCoreParams`, `RocketTileParams`, `ICacheParams`, `DCacheParams`, `BTBParams`, `TileKey`, `BuildHellaCache`, `TestDurationMultiplier` | `ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala`, `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala`, `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala`, `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala`, `ref_submodule/rocket-chip/src/main/scala/unittest/Configs.scala` | core/cache shape, fetch/decode widths, cache organization, test duration scaling |
| Hybrid local-with-system-fanout | `CacheBlockBytes`, `BuildRoCC`, vector params, `traceParams`, `blockerCtrlAddr`, `beuAddr` | `ref_submodule/rocket-chip/src/main/scala/subsystem/BankedCoherenceParams.scala`, `ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala`, `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala`, `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala` | extra TL masters/slaves, extra DCache/PTW ports, trace controller slaves, tile properties, coherence line size, debug-visible error units |

## GPGPU Equivalent Config Skeleton
```scala
case object NumSMs extends Field[Int](0)
case object WarpSize extends Field[Int](32)
case object WarpsPerSM extends Field[Int](4)
case object SharedMemBytes extends Field[Int](32 * 1024)
case object CacheLineBytes extends Field[Int](64)
case object NoCKey extends Field[NoCParams]
case object L2Key extends Field[L2Params]
case object ExtHBM extends Field[Option[MemPortParams]](None)
case object RuntimeMMIOKey extends Field[RuntimeMMIOParams]
case object TraceKey extends Field[TraceParams](TraceParams())
case object SMsLocated extends Field[Seq[SMAttachParams]](Nil)
case object BuildAccel extends Field[Seq[Parameters => LazyAccel]](Nil)

class BaseGPGPUConfig extends Config((site, here, up) => {
  case NoCKey => NoCParams(beatBytes = 32, blockBytes = site(CacheLineBytes))
  case L2Key => L2Params(nBanks = 4, lineBytes = site(CacheLineBytes))
  case ExtHBM => Some(MemPortParams(beatBytes = site(NoCKey).beatBytes, channels = 4))
  case RuntimeMMIOKey => RuntimeMMIOParams(base = 0x40000000L, beatBytes = site(NoCKey).beatBytes)
  case SMsLocated => Nil
})

class WithNumSMs(n: Int) extends Config((site, here, up) => {
  case SMsLocated =>
    val prev = up(SMsLocated)
    val idOffset = up(NumSMs)
    List.tabulate(n) { i =>
      SMAttachParams(
        SMParams(
          smId = idOffset + i,
          warpSize = site(WarpSize),
          warpsPerSM = site(WarpsPerSM),
          sharedMemBytes = site(SharedMemBytes),
          l1 = L1Params(rowBits = site(NoCKey).beatBits, blockBytes = site(CacheLineBytes))
        )
      )
    } ++ prev
  case NumSMs => up(NumSMs) + n
})

class SMConfig(f: SMParams => SMParams) extends Config((site, here, up) => {
  case SMsLocated => up(SMsLocated).map(a => a.copy(smParams = f(a.smParams)))
})

class WithWarpSize(n: Int) extends Config((site, here, up) => { case WarpSize => n })
class WithWarpsPerSM(n: Int) extends Config((site, here, up) => { case WarpsPerSM => n })
class WithSharedMemory(bytes: Int) extends SMConfig(_.copy(sharedMemBytes = bytes))
class WithL2Banks(n: Int) extends Config((site, here, up) => { case L2Key => up(L2Key).copy(nBanks = n) })
class WithGlobalMemoryAXI(widthBits: Int) extends Config((site, here, up) => {
  case ExtHBM => up(ExtHBM).map(_.copy(beatBytes = widthBits / 8))
})
class WithRuntimeMMIO extends Config((site, here, up) => {
  case RuntimeMMIOKey => up(RuntimeMMIOKey).copy(enableLaunchRegs = true, enableCounters = true)
})

class DefaultGPGPUConfig extends Config(
  new WithNumSMs(4) ++
  new WithWarpSize(32) ++
  new WithWarpsPerSM(8) ++
  new WithSharedMemory(64 * 1024) ++
  new WithL2Banks(8) ++
  new WithGlobalMemoryAXI(256) ++
  new WithRuntimeMMIO ++
  new BaseGPGPUConfig
)
```

## Required Config Categories

| Category | Rocket anchors | GPGPU fields | Owner skill |
|---|---|---|---|
| compute config | `TilesLocated`, `NumTiles`, `RocketTileParams`, `RocketCoreParams` (`ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala`, `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala`, `ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala`) | `num_sm`, `warp_size`, `lanes_per_warp`, `warps_per_sm` | `skill/gpgpu-arch` |
| local memory config | `DCacheParams`, `ICacheParams`, `CacheBlockBytes`, scratchpad config (`ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala`, `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala`) | `shared_mem_size`, `bank_count`, `bank_width` | `skill/gpgpu-memory` |
| global memory config | `SystemBusKey`, `MemoryBusKey`, `PeripheryBusKey`, `SubsystemBankedCoherenceKey`, `ExtMem` (`ref_submodule/rocket-chip/src/main/scala/subsystem/BusTopology.scala`, `ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala`, `ref_submodule/rocket-chip/src/main/scala/subsystem/BankedCoherenceParams.scala`) | `l1`, `l2`, `noc`, `dram`, `mshr`, `beat_bytes` | `skill/gpgpu-memory`, `skill/gpgpu-interconnect` |
| ISA/ABI config | `RocketCoreParams`, `BuildRoCC`, `MaxXLen` (`ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala`, `ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala`, `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala`) | instruction subset, launch ABI version, address spaces | `skill/gpgpu-runtime`, `skill/gpgpu-golden` |
| runtime config | `ExtBus`, `HasTilesExternalResetVectorKey`, `DTSTimebase`, `DTSModel`, `DTSCompat` (`ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala`, `ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala`, `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala`) | MMIO base, launch registers, queue depth | `skill/gpgpu-runtime` |
| debug config | `ExportDebug`, `DebugModuleKey`, `traceParams`, `beuAddr`, `blockerCtrlAddr` (`ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala`, `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala`) | trace enable, counter set, snapshot path | `skill/gpgpu-rtl`, `skill/gpgpu-simppa` |
| verification config | `UnitTests`, `TestDurationMultiplier`, `WithTraceGen`, `GroundTestBaseConfig` (`ref_submodule/rocket-chip/src/main/scala/unittest/Configs.scala`, `ref_submodule/rocket-chip/src/main/scala/groundtest/Configs.scala`) | smoke/regression/perf gates | `skill/gpgpu-golden`, `skill/gpgpu-loop` |

## Rule Candidates for `resolved_config.md` and Ownership Gates
- `resolved_config.md` must list every raw key, every derived field, the producing fragment, the owning skill/module, direct consumers, and affected collateral.
- Every leaf field gets exactly one declared owner. Multiple fragments may touch the field only if the final fragment is documented as the owner and transforms the prior value with `up(...).copy(...)`.
- Every use of `site(Key)` or `p(Key)` outside the owner becomes a declared dependency edge in `resolved_config.md`.
- Any field that changes external IO, address map, MMIO ABI, debug interface, trace schema, or test selection is `system-visible`; it cannot remain implicit inside a local module case class.
- Global geometry keys such as cache-line bytes, beat bytes, source-id bits, queue depths, and bank counts must have a single source of truth and zero local invention.
- Every Rocket-style `require(...)` must become both a generator validator and a documented invariant entry with owner, condition, and failure text.
- Any fragment that instantiates compute blocks must update attachment list, global count, and stable IDs together.
- Builder-valued keys like `BuildRoCC` or `BuildHellaCache` need explicit declarations of extra ports, clients, CSRs, decode space, and harness collateral.
- Test/debug/runtime variants must compose through the same fragment stack as product variants; no side-channel config files are allowed to shadow generator truth.
- Minimum `resolved_config.md` row shape:

| Field | Value | Owner | Source fragment | Consumers | Derived from | Invariants | Collateral |
|---|---|---|---|---|---|---|---|
| `cache_line_bytes` | `64` | interconnect owner | `WithCacheBlockBytes` or base config | L1/L2/NoC/MMIO/test generators | none | power-of-two, shared globally | RTL, MMIO, traces, tests |

## Anti-Patterns
- Replacing an entire structured record for a one-field tweak instead of using `up(...).copy(...)`.
- Letting multiple fragments silently own the same leaf field without a declared precedence rule.
- Duplicating shared geometry such as line size or beat width in cache, NoC, MMIO, and trace generators.
- Adding SM/tile/cluster instances without also updating global count and stable IDs.
- Hiding extra memory clients, CSRs, or decode space behind local optional params without surfacing them at top level.
- Generating runtime MMIO maps, debug endpoints, or test matrices from hand-maintained side files rather than the same config graph.
- Treating validation as a late simulation concern instead of emitting generator-time invariants beside the owning field.

## Required Evidence Table

| Rocket Mechanism | Source Files | Problem Solved in Rocket | Transferable Abstraction | GPGPU Skill Rule | Anti-Pattern to Avoid |
|---|---|---|---|---|---|
| `CONFIRMED`: typed parameter keys with defaults, location scope, and builder hooks | `ref_submodule/rocket-chip/src/main/scala/subsystem/BusTopology.scala:15-19`; `ref_submodule/rocket-chip/src/main/scala/subsystem/BankedCoherenceParams.scala:23-36`; `ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:47-49`; `ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:23-29`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:30-42`; `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala:29-31`; `ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala:22`; `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala:261` | Rocket can carry SoC keys, tile-placement keys, optional port keys, and factory-selection keys through one config namespace. | Typed schema keys should support scalar, optional, located, and builder-valued forms. | Define every GPGPU config field as a named typed key; reserve builder keys for pluggable accelerators, cache backends, or trace blocks. | Stringly typed maps or anonymous nested JSON blobs with no owner file. |
| `CONFIRMED`: base config computes derived globals from final tile population | `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:30-35`; `ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:23-29`; `ref_submodule/rocket-chip/src/main/scala/tile/Core.scala:140-145` | Rocket derives `MaxXLen`, `MaxHartIdBits`, and reset-vector width from actual instantiated tiles instead of duplicating them. | Central derived-config layer above module elaboration. | Derive `max_smid_bits`, address widths, launch ID widths, and reset-vector widths once, then treat them as read-only global outputs. | Each module recomputes global widths independently. |
| `CONFIRMED`: fragments transform prior structured values with `up(...).copy(...)` | `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:126-143`; `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:217-257`; `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:349-367`; `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:203-245`; `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:264-301` | Rocket can tweak only one field of a bus/debug/cache/core record without dropping unrelated defaults. | Config fragment helper layer for nested record rewrites. | Any GPGPU fragment touching an existing structured field must transform the previous value instead of rebuilding the whole record. | Whole-struct replacement for a single-field change. |
| `INFERRED`: `++` layers named presets and targeted overrides | `ref_submodule/rocket-chip/src/main/scala/system/Configs.scala:14-107`; `ref_submodule/rocket-chip/src/main/scala/groundtest/Configs.scala:28-35`; `ref_submodule/rocket-chip/src/main/scala/diplomacy/Main.scala:23-27` | Rocket assembles product, FPGA, tiny, cluster, and test variants from reusable fragment stacks. | Ordered config stack with documented precedence and reusable named top-level configs. | Keep base GPGPU defaults on the right, overlays on the left, and emit final fragment order in `resolved_config.md`. | Hidden override precedence or multiple unnamed ad hoc overlays. |
| `CONFIRMED`: tile/cluster fragments append attach params and update global counts | `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:19-50`; `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:62-97`; `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:99-163`; `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:107-124`; `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:146-160`; `ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:154-186` | Rocket supports heterogeneous tile placement while preserving stable IDs and attach metadata. | Compute-block attach fragments with stable IDs and location metadata. | A GPGPU fragment that instantiates SMs, clusters, or DMA engines must update attach list, count, placement, and naming together. | Adding instances without stable IDs or without attach metadata. |
| `CONFIRMED`: one geometry key fans out across buses, caches, and coherence | `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:37-55`; `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:138-140`; `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:75-81`; `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:109-123`; `ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:142-156`; `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala:97-99`; `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala:148-161`; `ref_submodule/rocket-chip/src/main/scala/subsystem/BankedCoherenceParams.scala:89-95` | Rocket keeps cache line size and beat geometry coherent across system bus, memory bus, L1 caches, tile properties, and broadcast coherence. | Single-source global geometry keys with explicit downstream consumers. | `cache_line_bytes`, `beat_bytes`, and related geometry must each have one owner and a consumer list spanning cache, interconnect, MMIO, runtime, and tests. | Divergent line-size or beat-size constants in separate generators. |
| `CONFIRMED`: port keys materialize external memory, MMIO, and slave IO plus harness hookups | `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:247-307`; `ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:33-245`; `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala:28-29` | Rocket uses the same config graph to decide port count, width, address range, and whether the harness creates connections. | Runtime-visible IO is config-owned, not manually patched into the harness. | Every GPGPU external port field must declare IO count, width, address range, protocol, and harness connection behavior in `resolved_config.md`. | Separate handwritten harness settings that drift from generator config. |
| `CONFIRMED`: debug config is ordinary generator config with transport and SBA attachment choices | `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:222-232`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:30-42`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:50-61`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:77-103`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:123-184`; `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala:23`; `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala:41` | Rocket switches between DMI, JTAG, and APB exports, and optionally gives debug a TL master path, without leaving the config system. | Debug/runtime plane is a first-class config category with port, reset, and bus-attachment ownership. | GPGPU debug fields must declare protocol, bus attachment points, reset semantics, optional master access, and harness connection. | Ad hoc debug toggles outside the main config graph. |
| `CONFIRMED`: validation lives near the owner through `require(...)` | `ref_submodule/rocket-chip/src/main/scala/subsystem/BankedCoherenceParams.scala:38-43`; `ref_submodule/rocket-chip/src/main/scala/tile/Core.scala:124-145`; `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala:79-87`; `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala:198-206`; `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:49-50`; `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:230-232`; `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:278-282`; `ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala:71`; `ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala:87-88`; `ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala:94-95`; `ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala:324-326`; `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala:56-61`; `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala:95-99`; `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala:229`; `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala:249-255` | Rocket rejects illegal feature combinations before or during elaboration instead of relying on downstream failures. | Generator-time invariant ledger tied to field ownership. | Every GPGPU invariant must name the owning field, owning module, exact condition, and expected failure text; validator output belongs in `resolved_config.md`. | Late discovery of bad combinations in simulation or synthesis only. |
| `CONFIRMED`: tests and elaboration artifacts are produced from the same config graph | `ref_submodule/rocket-chip/src/main/scala/unittest/Configs.scala:15-179`; `ref_submodule/rocket-chip/src/main/scala/groundtest/Configs.scala:16-72`; `ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala:40-45`; `ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala:151-155` | Rocket treats unit suites, ground-test tiles, plusargs, memmap, DTS, and JSON as config-driven collateral, not separate maintenance domains. | Verification profiles and emitted metadata should be generator config outputs. | GPGPU smoke, regression, perf, trace, MMIO-map, and runtime artifacts must all derive from the same resolved config stack. | Separate verification spreadsheets or metadata files disconnected from generator parameters. |

## Quality Gate

- Overall status: `PARTIAL`
- Evidence status: `PARTIAL`
- Readability status: `PASS`
- Safe for GPT-5.5 planning: `yes, with caveats`
- Full appendix generated: `yes`
- Biggest evidence gap: exact `org.chipsalliance.cde.config.Config` / `Field` implementation is not present in this repo snapshot, so `++` precedence is locally `INFERRED` from call sites rather than library source.
- Biggest readability issue: the evidence table is dense because this shard must preserve exact source anchors.
- Required next read: local source for `org.chipsalliance.cde.config.Config` and `Parameters` if available outside the snapshot; otherwise this report is already sufficient for GPGPU config-schema planning.
