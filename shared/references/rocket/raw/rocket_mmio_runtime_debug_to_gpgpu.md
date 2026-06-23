# Rocket MMIO / Runtime / Debug Lessons for GPGPU Skill

## Metadata

- Mode: repository
- Depth: deep
- Output profile: model-evidence
- Corpus: `ref_submodule/rocket-chip` at commit `55bcad0`
- Planner file: `ref/skillref/rocket.md`
- Scope: MMIO / runtime / devices / debug / trace only
- Non-goals: CPU pipeline internals, frontend/FPU/cache microarchitecture, ISA execution walkthroughs
- Corpus inventory read: `regmapper/*`, `tilelink/RegisterRouter.scala`, `examples/ExampleDevice.scala`, `devices/tilelink/{BootROM,MaskROM,CLINT,Plic,BusBlocker,ClockBlocker,CanHaveBuiltInDevices}.scala`, `devices/debug/{Periphery,Debug,SBA}.scala`, `interrupts/{RegisterRouter,Parameters}.scala`, `resources/Resources.scala`, `subsystem/{BaseSubsystem,HasTiles,HasHierarchicalElements}.scala`, `tile/{BaseTile,Interrupts,RocketTile,BusErrorUnit}.scala`, `system/{ExampleRocketSystem,TestHarness}.scala`, `trace/*`, `bootrom/bootrom.S`
- Files skipped by scope: `src/main/scala/rocket/*` core pipeline internals, full memory hierarchy internals, non-debug ISA behavior

## Rocket Pattern Summary

- `A1 [CONFIRMED]` Software-visible register maps are authored as `RegField.Map` tuples (`byteOffset -> Seq[RegField]`) inside `RegisterRouter` subclasses, then bound to a bus-specific register node; the TileLink path also emits `*.regmap.json` during elaboration. Evidence: `ref_submodule/rocket-chip/src/main/scala/regmapper/RegisterRouter.scala:17-48`; `ref_submodule/rocket-chip/src/main/scala/tilelink/RegisterRouter.scala:31-126`; `ref_submodule/rocket-chip/src/main/scala/examples/ExampleDevice.scala:25-70`.
- `A2 [CONFIRMED]` Special access policy is field-granular, not implied by comments: `RegFieldDesc` carries `access`, `wrType`, `rdAction`, `volatile`, `reset`, `enumerations`, and helper constructors encode common policies such as `r`, `w`, `w1ToClear`, `RWNotify`, `WNotifyVal`. Evidence: `ref_submodule/rocket-chip/src/main/scala/regmapper/RegFieldDesc.scala:31-151`; `ref_submodule/rocket-chip/src/main/scala/regmapper/RegField.scala:81-184`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Debug.scala:278-315`.
- `A3 [CONFIRMED]` Devices attach to buses as `LazyModule`s with `SimpleDevice`/`Device` metadata, `TLRegisterNode` or `TLManagerNode` address resources, and attach helpers using `coupleTo/coupleFrom`, `TLFragmenter`, `TLWidthWidget`, and `ResourceBinding`; `BaseSubsystem` emits DTS/DTB/JSON/memmap from the same resource graph. Evidence: `ref_submodule/rocket-chip/src/main/scala/resources/Resources.scala:72-269`; `ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala:31-45`; `ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala:115-139`; `ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala:143-156`; `ref_submodule/rocket-chip/src/main/scala/devices/tilelink/BootROM.scala:73-117`; `ref_submodule/rocket-chip/src/main/scala/devices/tilelink/MaskROM.scala:70-80`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:77-103`.
- `A4 [CONFIRMED]` BootROM, hart ID, reset vector, MMIO prefix, CLINT, PLIC, and debug interrupts are generator-wired at subsystem elaboration time, then fan out into per-tile bundle/int nodes; tiles consume these as externally supplied constants rather than inventing them locally. Evidence: `ref_submodule/rocket-chip/src/main/scala/system/ExampleRocketSystem.scala:17-20`; `ref_submodule/rocket-chip/src/main/scala/devices/tilelink/BootROM.scala:74-117`; `ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:57-127`; `ref_submodule/rocket-chip/src/main/scala/subsystem/HasHierarchicalElements.scala:187-249`; `ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:200-268`; `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala:240-320`; `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:229-231`.
- `A5 [CONFIRMED]` Trace is optional per tile via `RocketTileParams.traceParams`; when enabled Rocket generates an MMIO trace controller, a trace encoder, sink instances, a sink arbiter, optional file monitor, and raw/TraceCore bundle bridges. Evidence: `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:36-48`; `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:90-109`; `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:179-200`; `ref_submodule/rocket-chip/src/main/scala/trace/TraceEncoderController.scala:24-84`; `ref_submodule/rocket-chip/src/main/scala/trace/TraceEncoder.scala:13-32`; `ref_submodule/rocket-chip/src/main/scala/trace/TraceSinkArbiter.scala:15-34`; `ref_submodule/rocket-chip/src/main/scala/trace/TraceSinkMonitor.scala:7-19`; `ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:294-303`.
- `A6 [CONFIRMED]` The biggest runtime/debug pieces are generated with the system, not bolted on later: BootROM/MaskROM are parameterized attachments, debug transport protocol is selected by `ExportDebug`, debug module outer/inner split is built into the system graph, optional system-bus debug master is generated from `DebugModuleKey`, and test harness reset/debug wiring depends on those generated ports. Evidence: `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:22-42`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:77-185`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Debug.scala:671-752`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Debug.scala:1932-2025`; `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala:18-41`.
- `A7 [CONFIRMED]` Rocket repeatedly separates control from status/fault completion: `allow` vs `pending`, launch-like request vs `busy`, interrupt enable vs pending/accrued, DM control vs DM status, claim/complete side effects vs pure status. This is the right abstraction boundary for GPGPU runtime MMIO. Evidence: `ref_submodule/rocket-chip/src/main/scala/devices/tilelink/BusBlocker.scala:31-64`; `ref_submodule/rocket-chip/src/main/scala/devices/tilelink/ClockBlocker.scala:31-54`; `ref_submodule/rocket-chip/src/main/scala/tile/BusErrorUnit.scala:55-137`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/SBA.scala:46-260`; `ref_submodule/rocket-chip/src/main/scala/devices/tilelink/Plic.scala:236-313`.
- `A8 [INFERRED]` The GPGPU skill should require generator-owned MMIO schemas with explicit field semantics, exported metadata artifacts, subsystem-owned constant injection, and optional debug/trace blocks expressed as config-dependent address blocks rather than ad hoc RTL add-ons. Evidence basis: `A1-A7`.

## Required GPGPU MMIO Map YAML

```yaml
mmio_contract:
  device:
    name: gpgpu-runtime
    compatible: ["vendor,gpgpu-runtime0"]
    base: required
    size: power_of_two_required
    beat_bytes: required
    undef_zero: true
    executable: false
    generated_outputs:
      - regmap.json
      - memmap.json
      - dts_or_json_resource_map
  top_level_constants:
    sm_visible_id: generated_from_system
    reset_vector_or_boot_entry: generated_from_system
    mmio_address_prefix: generated_from_system
    runtime_abi_major: generated_from_config
    runtime_abi_minor: generated_from_config
  blocks:
    discovery:
      required: true
      fields:
        abi_major: {access: R, reset: required_constant}
        abi_minor: {access: R, reset: required_constant}
        sm_count: {access: R, reset: generated_from_config}
        trace_present: {access: R, reset: generated_from_config}
        debug_present: {access: R, reset: generated_from_config}
        counter_banks: {access: R, reset: generated_from_config}
    launch:
      required: true
      fields:
        start: {access: W, pulse: true}
        abort: {access: W, pulse: true}
        queue_select: {access: RW}
        descriptor_addr_lo: {access: RW}
        descriptor_addr_hi: {access: RW}
        grid_dim: {access: RW}
        block_dim: {access: RW}
    status:
      required: true
      volatile: true
      fields:
        busy: {access: R, volatile: true}
        done: {access: R, volatile: true}
        faulted: {access: R, volatile: true}
        pending_transactions: {access: R, volatile: true}
        active_sm_mask: {access: R, volatile: true}
        completion_seq: {access: R, volatile: true}
    interrupt:
      required: true
      fields:
        enable: {access: RW}
        pending: {access: R, volatile: true}
        ack: {access: RW, wrType: ONE_TO_CLEAR}
    fault:
      required: true
      fields:
        cause: {access: R, volatile: true, enum_required: true}
        value: {access: R, volatile: true}
        accrued: {access: R, volatile: true}
        clear: {access: RW, wrType: ONE_TO_CLEAR}
    trace:
      present_if: has_trace
      fields:
        enable: {access: RW}
        target: {access: RW, enum_required: true}
        bp_mode: {access: RW}
    debug:
      present_if: has_debug
      fields:
        halt_req: {access: RW_or_W_pulse}
        resume_req: {access: W, pulse: true}
        reset_req: {access: RW_or_W_pulse}
        any_halted: {access: R, volatile: true}
        any_running: {access: R, volatile: true}
    counters:
      present_if: has_counters
      byte_addressable: true
      fields:
        freeze: {access: RW}
        snapshot: {access: W, pulse: true}
        clear_mask: {access: RW, wrType: ONE_TO_CLEAR}
        bank_select: {access: RW}
        data: {access: R, volatile: true}
  generator_rules:
    - all fields must carry explicit access metadata
    - all volatile status bits must be marked volatile in generated docs
    - register groups must be stable and named for downstream tooling
    - runtime-visible addresses must be generator-owned, never leaf-local constants
```

## Required Debug / Counter Register YAML

```yaml
debug_counter_contract:
  debug_block:
    present_if: has_debug
    split:
      transport_control: outer_domain
      debug_ram_and_state: inner_domain
    registers:
      dbg_control:
        fields:
          dmactive: {access: RW, reset: 0}
          ndreset: {access: RW, reset: 0}
          halt_req: {access: RW_or_W_pulse}
          resume_req: {access: W, pulse: true}
          ack_have_reset: {access: W, pulse: true}
          target_select: {access: RW}
          target_mask_window: {access: RW, volatile: true, present_if: supports_target_array}
      dbg_status:
        fields:
          any_halted: {access: R, volatile: true}
          all_halted: {access: R, volatile: true}
          any_running: {access: R, volatile: true}
          all_running: {access: R, volatile: true}
          any_have_reset: {access: R, volatile: true}
          authenticated: {access: R, volatile: true}
          authbusy: {access: R, volatile: true}
      dbg_fault:
        fields:
          cmderr: {access: RW, wrType: ONE_TO_CLEAR}
          busy: {access: R, volatile: true}
      dbg_trace:
        present_if: has_trace
        fields:
          trace_enable: {access: RW}
          trace_target: {access: RW, enum_required: true}
          trace_bp_mode: {access: RW}
      dbg_memory_window:
        present_if: has_debug_ram
        fields:
          data_bytes: {access: RW, volatile: true}
          program_buffer: {access: RW}
          generated_instructions: {access: R, volatile: true}
          flags: {access: R, volatile: true}
  counter_block:
    present_if: has_counters
    registers:
      counter_ctl:
        fields:
          freeze: {access: RW}
          snapshot: {access: W, pulse: true}
          clear_mask: {access: RW, wrType: ONE_TO_CLEAR}
          bank_select: {access: RW}
      counter_status:
        fields:
          busy: {access: R, volatile: true}
          overflow_pending: {access: R, volatile: true}
      counter_data:
        layout: repeated
        byte_split_allowed: true
        fields:
          value: {access: R, volatile: true}
  documentation_rules:
    - enumerated fault causes required
    - per-field reset values required when constant
    - volatile data windows required for debug RAM, flags, counters, and live status
    - optional registers must be conditioned on config and presence bits in discovery block
```

## Rule Candidates

1. `launch/status`: `START` must be a write-only pulse or explicit control bit; `BUSY`, `DONE`, `FAULTED`, and `PENDING` must live in separate read-side status fields. Rocket precedent: `BusBlocker.allow/pending`, `SBA.sbbusy`, `DMCONTROL` vs `DMSTATUS`.
2. `fault`: Every asynchronous or accrued fault path must expose `cause`, `value`, `accrued`, and `clear(W1C)` separately. Rocket precedent: `BusErrorUnit` latches cause/value and keeps local/global interrupt masks distinct.
3. `special semantics`: GPGPU register schemas must encode `wrType`, `rdAction`, `volatile`, and enumerations explicitly; documentation-only metadata is still mandatory because Rocket exports it into generated artifacts. Rocket precedent: `RegFieldDesc`, `w1ToClear`, PLIC claim/complete, SBA `sberror/sbbusyerror`.
4. `clock-domain runtime control`: Any MMIO-visible register crossing clock or reset domains must use an explicit crossing primitive with one-in-flight control and bypass semantics. Rocket precedent: `RegisterReadCrossing`, `RegisterWriteCrossing`, `AsyncRWSlaveRegField`, Debug outer/inner split.
5. `runtime ABI`: Top-level constants such as `sm_id`, reset entry, MMIO prefix, and ABI version must be injected from the subsystem/config level. Leaf compute RTL may consume them but may not invent them. Rocket precedent: `tileId may not be hartid`, `tileHartIdNexusNode`, `tileResetVectorNexusNode`, `mmioAddressPrefixNode`, `BootROM.attach`.
6. `debug generation`: Debug transport, debug RAM, system-bus debug master, and attach protocol must be generator options, with presence reflected in runtime metadata. Rocket precedent: `ExportDebug`, `DebugModuleKey`, `debug-attach` property, optional `SBToTL`.
7. `trace routing`: Trace must be modeled as a configurable producer -> encoder -> sink graph with a runtime-selectable target register and optional monitor path. Rocket precedent: `TraceEncoderParams`, `TraceEncoderController.target`, `TraceSinkArbiter`, `TraceSinkMonitor`.
8. `counter layout`: Counter values must be byte-addressable read-only volatile fields; counter control (`freeze`, `snapshot`, `clear_mask`) must be separate from counter data. Rocket precedent: `RegField.bytes`, CLINT `mtime/mtimecmp`, Debug data/progbuf byte fields.
9. `START/DONE smoke`: minimum regression should be: write descriptor, write `START`, observe `BUSY=1`, eventually observe exactly one of `{DONE, FAULTED}`, require `DONE/FAULTED` to persist until software ACK, and require a second `START` while `BUSY=1` to set an error/pending condition rather than silently enqueueing a second launch. Rocket precedent: `pending`/`busy` separation and explicit clear/complete paths.
10. `anti-aliasing`: keep control, status, debug memory window, trace control, and fault space as distinct blocks with named groups; do not collapse them into one undocumented CSR blob. Rocket precedent: `RegFieldGroup`, separate DMI outer map, DMI inner map, TL debug memory window, trace controller block.

## Evidence Table

| Rocket Mechanism | Source Files | Problem Solved in Rocket | Transferable Abstraction | GPGPU Skill Rule | Anti-Pattern to Avoid |
|---|---|---|---|---|---|
| Register router + TL register node + regmap JSON | `ref_submodule/rocket-chip/src/main/scala/regmapper/RegisterRouter.scala:17-48`; `ref_submodule/rocket-chip/src/main/scala/tilelink/RegisterRouter.scala:36-126` | Define MMIO fields once and bind them to a bus while emitting software collateral | Single source of truth for runtime-visible register schema | Require generator-owned register schema that emits docs/artifacts during elaboration | Hand-maintained register spreadsheets disconnected from RTL |
| Field-level semantics (`access`, `wrType`, `rdAction`, `volatile`, enums) | `ref_submodule/rocket-chip/src/main/scala/regmapper/RegFieldDesc.scala:31-151`; `ref_submodule/rocket-chip/src/main/scala/regmapper/RegField.scala:114-184` | Encode W1C, RO, side-effecting reads, volatile status, enumerated causes | Software contract is per field, not per whole register | Every GPGPU field must carry explicit semantics metadata | Implicit semantics hidden in driver code or comments only |
| Example W1C pending register | `ref_submodule/rocket-chip/src/main/scala/examples/ExampleDevice.scala:40-56` | Show a simple R/W state register plus volatile W1C pending register | Separate control value from latched pending/event state | Use W1C acks for pending/fault/event clear paths | Clearing faults/status by raw overwrites or implicit reads |
| Cross-domain register access helpers | `ref_submodule/rocket-chip/src/main/scala/regmapper/RegisterCrossing.scala:10-125`; `ref_submodule/rocket-chip/src/main/scala/regmapper/RegisterCrossing.scala:180-232`; `ref_submodule/rocket-chip/src/main/scala/regmapper/Test.scala:220-257` | Safely expose MMIO across clock/reset domains with bounded inflight control | Runtime/debug registers need explicit CDC design | Require crossing primitive when runtime block is not in host/control clock domain | Unacknowledged multi-clock MMIO or hidden CDC in leaf logic |
| Resource graph, DTS/JSON/memmap export | `ref_submodule/rocket-chip/src/main/scala/resources/Resources.scala:98-215`; `ref_submodule/rocket-chip/src/main/scala/subsystem/BaseSubsystem.scala:115-156` | Keep address map, compat strings, interrupts, and ranges consistent with generated hardware | Device metadata is part of elaboration graph | GPGPU generator must emit machine-readable memmap/resource metadata | Separate host runtime ABI repo with no direct elaboration linkage |
| BootROM attach drives reset ABI | `ref_submodule/rocket-chip/src/main/scala/devices/tilelink/BootROM.scala:21-30`; `ref_submodule/rocket-chip/src/main/scala/devices/tilelink/BootROM.scala:73-117`; `ref_submodule/rocket-chip/bootrom/bootrom.S:5-20` | Bind boot image, DTB append, and reset vector in one generator-owned attachment | Runtime entry contract is a generated subsystem property | Make launch/reset entry and ABI constants subsystem-owned outputs | Hardcoding launch/reset addresses inside compute cores |
| CLINT/PLIC register blocks and interrupt metadata | `ref_submodule/rocket-chip/src/main/scala/devices/tilelink/CLINT.scala:44-101`; `ref_submodule/rocket-chip/src/main/scala/devices/tilelink/Plic.scala:82-129`; `ref_submodule/rocket-chip/src/main/scala/devices/tilelink/Plic.scala:233-313` | Expose timer/interrupt controller state with precise pending/enable/claim semantics and resource bindings | Separate enable, pending, threshold, and complete actions | GPGPU runtime IRQ block must separate enable/pending/ack and use volatile RO status + side-effecting ack path | Single mixed RW status register where software can accidentally destroy state |
| Root-context and tile interrupt/reset fanout | `ref_submodule/rocket-chip/src/main/scala/subsystem/HasHierarchicalElements.scala:187-249`; `ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:57-127`; `ref_submodule/rocket-chip/src/main/scala/subsystem/HasTiles.scala:200-268` | Route debug/MSIP/MEIP/SEIP/NMI/reset/hartid into each tile with explicit nodes and crossings | Runtime/debug delivery is a first-class system graph, not ad hoc wires | GPGPU generator must own SM interrupt/debug/reset fanout at subsystem level | Letting each SM invent its own runtime/debug ingress |
| Debug generated as outer/inner modules with protocol selection | `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:22-42`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:77-185`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Debug.scala:317-337`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Debug.scala:671-752`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Debug.scala:1932-2025` | Allow debug to work across reset/clock domains and switch transport (`DMI`/`JTAG`/`APB`) by config | Debug is a generated subsystem with transport/control/data planes | Model GPGPU debug as generator-owned optional subsystem with discoverable capabilities | Attaching a debugger later via simulation-only wires with no runtime contract |
| Debug register maps and memory window | `ref_submodule/rocket-chip/src/main/scala/devices/debug/Debug.scala:533-593`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Debug.scala:1363-1458`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Debug.scala:1678-1708` | Split debug control, status, abstract command state, auth, SBA, and debug RAM/ROM window | Separate external control from execution-side data window | Use distinct debug blocks: control/status, scratch/data/progbuf, generated instructions, flags | One monolithic debug CSR file with no domain or function separation |
| SBA busy/error/autoincrement rules | `ref_submodule/rocket-chip/src/main/scala/devices/debug/SBA.scala:46-260` | Safely drive system-bus accesses from debug with busy/error gating and W1C clear | Long-latency runtime accesses need explicit busy/error protocol | Launch queue doorbells or memory peek/poke windows need `busy`, `error`, alignment/access legality | Fire-and-forget MMIO writes to long-latency engines with no busy/error visibility |
| Fault latch + interrupt masks | `ref_submodule/rocket-chip/src/main/scala/tile/BusErrorUnit.scala:39-137` | Capture first error cause/value, keep accrued mask, and expose local/global interrupt enables | Fault handling should be latched, inspectable, and software-clearable | Require `cause/value/accrued/local_irq/global_irq/enable` pattern for GPGPU fault block | Overwriting first-fault evidence before software can inspect it |
| Runtime `allow/pending` control blocks | `ref_submodule/rocket-chip/src/main/scala/devices/tilelink/BusBlocker.scala:31-64`; `ref_submodule/rocket-chip/src/main/scala/devices/tilelink/ClockBlocker.scala:16-54` | Separate software control from in-flight completion state | Control register + volatile pending register is a reusable runtime pattern | Launch/status blocks should expose both desired state and in-flight state | Interpreting a control bit alone as proof that work completed |
| Trace config, routing, sink selection, monitor | `ref_submodule/rocket-chip/src/main/scala/trace/TraceEncoderController.scala:24-84`; `ref_submodule/rocket-chip/src/main/scala/trace/TraceEncoder.scala:13-32`; `ref_submodule/rocket-chip/src/main/scala/trace/TraceSinkArbiter.scala:15-34`; `ref_submodule/rocket-chip/src/main/scala/trace/TraceSinkMonitor.scala:7-19`; `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:90-109`; `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala:179-200` | Make trace optional, runtime-configurable, and observable without changing the core datapath | Trace should be a pluggable graph with MMIO control and optional file sink | Require generated trace block with enable/target/bp_mode registers and sink IDs | Hardwired trace path or compile-time-only sink choice |

## Quality Gate

- Overall status: PASS
- Evidence status: PASS
- Readability status: PASS
- Safe for GPT-5.5 planning: yes
- Full appendix generated: yes
- Biggest evidence gap: no concrete software consumer for generated `regmap.json`/trace sink payload format was read in this shard
- Biggest readability issue: none material; table is wide because source anchoring was prioritized
- Required next read: `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala` and `ref_submodule/rocket-chip/src/main/scala/system/Configs.scala` to map these generated blocks back to config fragments and ownership rules
