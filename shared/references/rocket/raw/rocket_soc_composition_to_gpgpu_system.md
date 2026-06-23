# Rocket SoC Composition Lessons for GPGPU System Generator

## Metadata
- Mode: `repository`
- Depth: `deep`
- Output profile: `model-evidence`
- Corpus: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip` at commit `55bcad0`
- Planner file: `/home/cisl/Desktop/simple-gpgpu/ref/skillref/rocket.md`
- Write target: `/home/cisl/Desktop/simple-gpgpu/ref/skillref/rocket-reader-reports/rocket_soc_composition_to_gpgpu_system.md`
- Files read:
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/RocketSubsystem.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HasHierarchicalElements.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/SystemBus.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/MemoryBus.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/PeripheryBus.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/FrontBus.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/InterruptBus.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/BankedCoherenceParams.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/BusTopology.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Attachable.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HierarchicalElement.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HierarchicalElementPRCIDomain.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/system/ExampleRocketSystem.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/system/SimAXIMem.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/system/Configs.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tile/TilePRCIDomain.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/devices/tilelink/BootROM.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/devices/tilelink/CLINT.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/devices/tilelink/Plic.scala`
- Files skipped:
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/rocket/Rocket.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala`,
  `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tile/Core.scala`,
  detailed CPU pipeline and CSR semantics outside this shard
- Non-goals:
  CPU pipeline internals, cache microarchitecture internals, full debug register map, full MMIO ABI, verification coverage

## Rocket Pattern Summary
- `CONFIRMED`: `BaseSubsystem` is the SoC composition boundary. It owns PRCI attachment points, clock-group IO export, TileLink topology instantiation, the viewpoint bus used for unified manager/resource discovery, and elaboration collateral (`graphml`, `plusArgs`, `dts`, `json`, `memmap.json`). `RocketSubsystem` only layers tile/root-context plus CLINT/PLIC/debug mixins on top; `ExampleRocketSystem` adds external interrupts, off-chip ports, and ROMs. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala:31-45`, `:62-94`, `:97-171`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/RocketSubsystem.scala:36-48`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/system/ExampleRocketSystem.scala:11-22`.
- `CONFIRMED`: the tile boundary is `BaseTile` plus `TilePRCIDomain`, not the CPU core. `BaseTile` owns master/slave TL nodes, interrupt ingress/egress, hartid/reset-vector/NMI/trace sideband, and visible-manager-derived address sizing; `RocketTile` fills that shell with the core, icache frontend, dcache, optional DTIM, BEU, trace controller, vector, and RoCC plumbing. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala:219-378`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:58-164`, `:166-286`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tile/TilePRCIDomain.scala:15-29`.
- `CONFIRMED`: buses are role-specialized. `SBUS` is the default tile/master and DTS viewpoint bus; `CBUS` is the control/MMIO bus; `PBUS` is a downstream periphery bus with atomic/width/buffer adaptation; `MBUS` is the DRAM-side bus behind the coherence manager; `FBUS` is the inbound slave/front bus; `IBUS` is a separate interrupt fabric. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/BusTopology.scala:15-37`, `:71-113`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/SystemBus.scala:18-52`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/PeripheryBus.scala:23-77`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/MemoryBus.scala:17-55`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/FrontBus.scala:12-35`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/InterruptBus.scala:16-27`.
- `CONFIRMED`: tile instantiation is data-driven. Config fragments populate `TilesLocated(location)` with `RocketTileAttachParams`; `InstantiatesHierarchicalElements` sorts by stable `tileId`, wraps each tile in `TilePRCIDomain`, and `CanAttachTile.connect` wires master ports, slave ports, interrupts, PRC, constants, and trace in one narrow-waist path. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:62-97`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HasHierarchicalElements.scala:77-128`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:154-178`, `:181-303`.
- `CONFIRMED`: clock/reset/interrupt crossings are represented as first-class graph nodes, not leaf ad hoc logic. `HierarchicalElementPRCIDomain` encapsulates TL/int reset and clock crossings; `connectPRC` selects synchronous/rational/asynchronous clock sourcing; root context allocates per-tile `msip`, `meip`, `seip`, `debug`, `nmi`, `trace`, and hartid/reset-vector nodes. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HierarchicalElementPRCIDomain.scala:45-99`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:57-127`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:200-299`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HasHierarchicalElements.scala:181-248`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/InterruptBus.scala:17-27`, `:51-63`.
- `CONFIRMED`: external memory/MMIO/slave ports are optional config-owned attachments. `BaseConfig` enables default `ExtMem`, `ExtBus`, and `ExtIn`; the `Ports.scala` traits materialize AXI4/TL protocol adapters; `TestHarness` then connects memory and MMIO to `SimAXIMem`, ties off inbound slave traffic, and hooks debug. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/system/Configs.scala:14-24`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:268-320`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:53-245`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala:18-41`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/system/SimAXIMem.scala:33-54`.
- `CONFIRMED`: reset-vector collateral is integrated into composition. `BaseSubsystemConfig` disables external reset-vector IOs by default; `BootROM.attach` both attaches ROM to `CBUS` and drives the shared tile reset-vector nexus to `hang`, optionally appending the generated DTB into ROM contents. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:57-58`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:113-126`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/devices/tilelink/BootROM.scala:22-30`, `:73-117`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/system/ExampleRocketSystem.scala:17-20`.
- `INFERRED`: the transferable pattern is a strict three-plane generator: compute tiles/clusters attach through one API, memory traffic exits through coherence plus `MBUS`, and runtime/debug/periphery stay on `CBUS`/`PBUS`/`IBUS` with shared collateral. This is the right abstraction level to reuse for a GPGPU generator; copying Rocket core internals is not. Evidence basis: the aggregate composition above, especially `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/BusTopology.scala:79-113`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:170-303`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:53-245`.

## Rocket-to-GPGPU Mapping Table
| Rocket pattern | GPGPU analogue | Keep | Do not copy |
|---|---|---|---|
| `BaseSubsystem` + `RocketSubsystem` | `BaseGPGPUSubsystem` + `GPGPUSubsystem` | one SoC composition owner for buses, PRCI, collateral, and optional planes | putting composition logic inside SM or cache modules |
| `TilesLocated` + `RocketTileAttachParams` | `SMsLocated` or `ClustersLocated` + `SMAttachParams` | config-generated attach list with stable IDs and crossing params | instantiating SMs ad hoc in top-level code |
| `TilePRCIDomain` | `SMPRCIDomain` / `ClusterPRCIDomain` | isolate clock/reset/int crossing, boundary buffers, and trace crossing outside compute logic | burying CDC/reset logic inside schedulers/LSUs |
| `SBUS` + `COH` + `MBUS` | compute/data fabric ingress + L2/directory/NoC + DRAM egress fabric | one memory-plane handoff between tile-local caches and global memory system | letting each SM invent its own DRAM adapter or coherence rule |
| `CBUS` + `PBUS` + `IBUS` | runtime/MMIO/debug bus + slow periphery bus + event/interrupt fabric | separate runtime/control/debug plane from throughput data plane | sharing launch MMIO, debug SBA, and DRAM traffic on one untyped crossbar |
| `BootROM` + DTS/JSON/memmap + `TestHarness` | launch ROM / firmware blob + generated address map + simulation harness | generate software-visible collateral from the same elaboration graph | maintaining a second hand-written address map or reset-entry source |

## GPGPU System Skeleton
```scala
case class GPGPUCrossingParams(
  crossingType: ClockCrossingType,
  master: HierarchicalElementPortParamsLike,
  slave: HierarchicalElementSlavePortParams,
  mmioBaseAddressPrefixWhere: TLBusWrapperLocation,
  resetCrossingType: ResetCrossingType,
  forceSeparateClockReset: Boolean = false)

case class SMAttachParams(
  smParams: SMTileParams,
  crossingParams: GPGPUCrossingParams) extends CanAttachTileLike

class GPGPUSubsystem(implicit p: Parameters) extends BaseSubsystem
    with InstantiatesHierarchicalElements
    with HasComputeInputConstants
    with CanHavePeripheryRuntime
    with CanHavePeripheryInterruptFabric
    with CanHavePeripheryDebugLike
    with HasHierarchicalElementsRootContext
    with HasHierarchicalElements {
  val launchROM = p(BootROMLocated(location)).map { LaunchROM.attach(_, this, CBUS) }
  override lazy val module = new GPGPUSubsystemModuleImp(this)
}

// Config stack shape:
// WithNSMClusters ++ WithRuntimeBusTopology ++ WithCoherentMemoryTopology ++
// WithExternalDRAMPorts ++ WithLaunchMMIO ++ WithTraceDebug ++ BaseGPGPUConfig
```

## Rule Candidates
- Compute plane:
  `CONFIRMED rule`: generate compute tiles/clusters only from resolved attach params with stable IDs; feed them through one `instantiate/connect` path like `RocketTileAttachParams` -> `TilePRCIDomain` -> `CanAttachTile.connect`.
  `CONFIRMED rule`: keep SM-local state and L1/shared-memory-like structures inside the tile wrapper; expose only master/slave/int/trace/hartid-reset-style boundary nodes.
  `CONFIRMED rule`: make external launch IDs, trap vectors, and trace sideband explicit graph inputs, not hard-coded constants in the compute block.
- Memory/data plane:
  `CONFIRMED rule`: split compute ingress (`SBUS`-like) from DRAM egress (`MBUS`-like), with one subsystem-owned coherence/directory/banking wrapper in between.
  `CONFIRMED rule`: own width adaptation, fragmentation, source/id shrinking, and protocol conversion in shared adapters (`TLWidthWidget`, `TLFragmenter`, `TLToAXI4`, `AXI4ToTL` analogues), never in SM-local memory clients.
  `CONFIRMED rule`: if you need host-initiated access into the accelerator, give it a dedicated `FBUS`-like front/slave bus instead of mixing it into the DRAM port path.
- Runtime/control/debug plane:
  `CONFIRMED rule`: keep launch MMIO, boot/firmware ROM, timer/event sources, interrupt controllers, and debug slave on a `CBUS`/`PBUS`-like plane distinct from the throughput fabric.
  `CONFIRMED rule`: if debug/runtime can master the memory system, model that as an explicit debug/management bus master (`masterWhere = FBUS` by default for Rocket SBA), not as hidden backdoors.
  `CONFIRMED rule`: emit `dts`/`dtb`/`json`/`memmap`-like collateral directly from the elaborated graph so runtime software, simulators, and generators share one address truth.

## Required Evidence Table
| Rocket Mechanism | Source Files | Problem Solved in Rocket | Transferable Abstraction | GPGPU Skill Rule | Anti-Pattern to Avoid |
|---|---|---|---|---|---|
| `BaseSubsystem` + `TLNetworkTopologyLocated` + `Attachable` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala:62-171`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Attachable.scala:25-56` | gives one composition root for PRCI, topology instantiation, manager discovery, and collateral generation | subsystem owns attachment surfaces and metadata | all fabric/bus/metadata generators must hang off one `BaseGPGPUSubsystem` root | composing buses/peripherals from multiple unrelated tops with duplicated address metadata |
| `TilesLocated` + `RocketTileAttachParams` + `WithNBigCores` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/rocket/Configs.scala:62-97`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/RocketSubsystem.scala:13-25` | turns config fragments into a stable list of tile attach descriptors with crossing metadata | attach-param list is the source of truth for compute instances | generate SM/cluster instances from resolved attach records, not direct constructor calls | top-level code manually `new`-ing compute blocks and discovering IDs later |
| `InstantiatesHierarchicalElements` + `CanAttachTile.connect` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HasHierarchicalElements.scala:77-128`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:170-303` | guarantees each tile gets the full set of standard connections: master, slave, interrupts, PRC, constants, trace | narrow-waist attachment API for compute blocks | require one standard attach method per compute tile/cluster | per-module bespoke wiring that omits trace, reset vector, or interrupt plumbing |
| `TilePRCIDomain` + `HierarchicalElementPRCIDomain` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tile/TilePRCIDomain.scala:15-29`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/HierarchicalElementPRCIDomain.scala:45-99` | localizes CDC/reset-domain logic and boundary buffers outside the tile logic | explicit PRCI wrapper per compute cluster | wrap every SM cluster in a domain object that owns CDC/reset/trace boundary logic | scattering CDC FIFOs and reset gating inside execution pipelines |
| `BusTopology` + `SystemBus` + `PeripheryBus` + `MemoryBus` + `FrontBus` + `InterruptBus` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/BusTopology.scala:71-113`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/SystemBus.scala:18-52`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/PeripheryBus.scala:23-77`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/MemoryBus.scala:17-55`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/FrontBus.scala:12-35`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/InterruptBus.scala:16-27` | separates high-bandwidth coherent traffic, low-speed MMIO, inbound host traffic, and interrupts | explicit traffic-role buses | define compute/data, control/periphery, host-frontdoor, and interrupt planes separately in the generator schema | a single monolithic interconnect with implicit traffic classes |
| `BankedCoherenceParams` + `CoherenceManagerWrapper` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/BankedCoherenceParams.scala:22-43`; `:45-109`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:88-105` | centralizes global coherence, bank count, optional no-coherence mode, and control-port exposure | subsystem-owned memory-system wrapper between tiles and DRAM | place L2/directory/bank binding outside compute tiles and drive it from config | giving each SM cluster private inconsistent coherence policy or bank mapping |
| `Ports.scala` + top-level configs | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:53-245`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala:268-320`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/system/Configs.scala:14-24` | makes off-chip DRAM, off-chip MMIO, and inbound slave ports configurable and protocol-adapted | external interface traits plus config keys | external HBM/PCIe/host ports must be config-owned attachment traits with width/id/base encoded in one schema | leaf modules inventing off-chip base addresses, bus widths, or ID spaces locally |
| `BootROM` + `HasPeripheryDebug` + `TestHarness` + `HasDTSImp` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/devices/tilelink/BootROM.scala:73-117`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:30-39`, `:77-125`, `:245-275`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala:18-41`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala:37-45`, `:143-171` | keeps boot entry, debug transport, harness connectivity, and software-visible collateral synchronized with the generated SoC | integrated runtime/debug/collateral plane | generate launch ROM, reset entry, debug transport, harness hookups, and address artifacts from the same elaboration pass | separate hand-maintained firmware/debug/harness metadata that drifts from RTL |

## Open Gaps
- `MISSING`: this shard does not inspect register-level runtime ABI construction (`regmapper`, per-device register blocks, debug internal registers). That belongs to the MMIO/runtime/debug shard.
- `MISSING`: there is no Rocket analogue for GPU kernel launch ABI, warp scheduling ABI, or SIMT state in this scope; those must be defined as new GPGPU contracts, not inferred from CPU internals.
- `CONFLICTED`: none found in the inspected SoC-composition scope.

## Quality Gate
- Overall status: `PASS`
- Evidence status: `PASS`
- Readability status: `PASS`
- Safe for GPT-5.5 planning: `yes, with caveats`
- Full appendix generated: `yes`
- Biggest evidence gap: `register-level runtime/debug/MMIO schema is outside this shard`
- Biggest readability issue: `none`
- Required next read: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/regmapper/RegisterRouter.scala` and `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/devices/debug/Debug.scala`
