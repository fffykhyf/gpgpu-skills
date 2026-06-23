# Rocket Diplomacy Lessons for GPGPU Interface Contract

## Metadata

- Mode: `repository`
- Depth: `deep`
- Output profile: `model-evidence`
- Repo / subsystem: `ref_submodule/rocket-chip` at commit `55bcad0`
- Scope: Diplomacy / TileLink / AMBA negotiation only
- Files read: `adder_tutorial.md`, `select_tutorial.md`, `diplomacy/Parameters.scala`, `diplomacy/package.scala`, `tilelink/{Nodes,Parameters,Bundles,Edges,Monitor,Fragmenter,WidthWidget,Buffer,SourceShrinker,AtomicAutomata,ToAXI4}.scala`, `amba/axi4/{ToTL,Nodes}.scala`, `subsystem/Ports.scala`
- Files skipped by design: CPU pipeline internals, caches as microarchitecture, non-scope Rocket core files
- Contradictions found: none in scoped corpus
- Non-goals: no CPU pipeline summary

## Rocket Mechanism Summary

- `CONFIRMED` Node construction time declares protocol intent, not wires. `SourceNode` emits downward parameters, `SinkNode` emits upward parameters, `NexusNode`/`AdapterNode` transform them, and `LazyModuleImp` is deferred until the graph is negotiated. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/docs/src/diplomacy/adder_tutorial.md:48-55`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/docs/src/diplomacy/adder_tutorial.md:117-187`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Nodes.scala:16-47`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/diplomacy/package.scala:174-190`.
- `CONFIRMED` A TL client node declares `TLMasterPortParameters`/`TLMasterParameters`: `name`, `sourceId`, `visibility`, `requestFifo`, `supports*` for slave-to-master traffic, `emits*` for master-to-slave traffic, sideband field sets, and latency metadata. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:813-1015`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:1063-1291`.
- `CONFIRMED` A TL manager node declares `TLSlavePortParameters`/`TLSlaveParameters`: `address`, `regionType`, `executable`, `fifoId`, `supports*` for A-channel requests, `emits*` for B-channel requests, `mayDeny*`, `alwaysGrantsT`, `beatBytes`, `endSinkId`, `minLatency`, and sideband acceptance keys. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:172-458`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:523-811`.
- `CONFIRMED` The edge, not the raw bundle, computes interface facts: bundle widths, `hasBCE`, valid sideband intersections, alignment, masks, beat counts, address decoding, source visibility, request/response classification, legality builders, and inflight accounting. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:1293-1379`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Bundles.scala:173-260`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Edges.scala:18-333`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Edges.scala:342-840`.
- `CONFIRMED` Rocket solves common mismatches with explicit adapters: width (`TLWidthWidget`), transfer-size / burst shape (`TLFragmenter`), timing / buffering (`TLBuffer`), source-id capacity (`TLSourceShrinker`), missing atomics (`TLAtomicAutomata`), and protocol conversion / id remap (`TLToAXI4`, `AXI4ToTL`). Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/WidthWidget.scala:14-224`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Fragmenter.scala:26-113`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Buffer.scala:13-61`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/SourceShrinker.scala:16-88`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/AtomicAutomata.scala:16-60`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/ToAXI4.scala:31-75`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/amba/axi4/ToTL.scala:29-62`.
- `CONFIRMED` Rocket intentionally fails early on illegal combinations instead of guessing: overlapping addresses or source IDs, inconsistent transfer-size lattices, beat-size violations, non-FIFO fragmentation, cacheable traffic through source shrinking/fragmentation, unsupported AMO synthesis, missing AXI `maxFlight`, missing `TLError`, non-homogeneous AXI interleave ids, and impossible monitor invariants. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/diplomacy/Parameters.scala:28-125`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:220-250`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:605-607`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:844-855`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:1089-1092`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:1372-1373`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Fragmenter.scala:98-112`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/SourceShrinker.scala:53-56`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/AtomicAutomata.scala:26-29`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/AtomicAutomata.scala:51-60`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/ToAXI4.scala:107-109`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/amba/axi4/ToTL.scala:31-32`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/amba/axi4/ToTL.scala:90-100`.
- `CONFIRMED` Monitors consume the negotiated `TLEdge`, then assert runtime traffic matches those negotiated capabilities: opcode legality, `supports*`/`emits*`, address visibility, alignment, masks, source/sink ranges, multibeat field stability, A->D / C->D response matching, `minLatency`, and watchdog timeout. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Nodes.scala:24-29`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:15-25`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:69-381`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:384-418`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:535-715`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:807-882`.
- `MISSING` The scoped files do not provide a universal ordering/fence adapter. Ordering is expressed piecemeal through `requestFifo`, `fifoId`, `minLatency`, bridge-local stalls, and optional downstream fixers used in port chains. GPGPU should therefore model fence/order as a first-class contract, not as an implicit side effect of width/id adapters. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:179-187`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:820-824`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Buffer.scala:18-24`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/ToAXI4.scala:258-287`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:171-180`.

## Required Answers

### 1. What is declared at node construction time?

| Direction | Declared object | Declared fields before RTL binding | Evidence |
|---|---|---|---|
| Client to manager | `TLClientNode(Seq[TLMasterPortParameters])` | `TLMasterParameters.{name, sourceId, visibility, requestFifo, supports*, emits*, neverReleasesData}` plus port-level `{minLatency, echoFields, requestFields, responseKeys}` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Nodes.scala:40-47`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:813-1015`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:1063-1291` |
| Manager to client | `TLManagerNode(Seq[TLSlavePortParameters])` | `TLSlaveParameters.{address, regionType, executable, fifoId, supports*, emits*, alwaysGrantsT, mayDenyGet, mayDenyPut}` plus port-level `{channelBytes/beatBytes, endSinkId, minLatency, responseFields, requestKeys}` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Nodes.scala:40-47`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:172-458`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:523-811` |
| Graph transform | `TLAdapterNode`, `TLNexusNode`, `MixedAdapterNode` | Pure parameter rewrite / aggregation functions; no local wire invention is allowed outside the negotiation result | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/docs/src/diplomacy/adder_tutorial.md:99-170`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Nodes.scala:43-47`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Nodes.scala:69-73`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/diplomacy/package.scala:174-190` |

### 2. Which capability fields flow client-to-manager and manager-to-client?

| Flow | Capability fields | Why it matters |
|---|---|---|
| Client to manager (`TLMasterPortParameters`) | `sourceId`, `visibility`, `requestFifo`, `supportsProbe/Arithmetic/Logical/Get/PutFull/PutPartial/Hint`, `emitsAcquireT/AcquireB/Arithmetic/Logical/Get/PutFull/PutPartial/Hint`, `minLatency`, sideband request/echo/response key sets | Manager-side decode, monitor checks, bridge ID mapping, and bundle shaping depend on what each client can emit or accept. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:813-1015`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:1063-1188`. |
| Manager to client (`TLSlavePortParameters`) | `address`, `regionType`, `executable`, `fifoId`, `supportsAcquireT/AcquireB/Arithmetic/Logical/Get/PutFull/PutPartial/Hint`, `emitsProbe/Arithmetic/Logical/Get/PutFull/PutPartial/Hint`, `mayDenyGet`, `mayDenyPut`, `alwaysGrantsT`, `beatBytes`, `endSinkId`, `minLatency`, sideband response/request key sets | Client-side legality builders, bundle widths, response tracking, and adapter preconditions depend on these manager guarantees. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:172-458`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:523-718`. |

### 3. What does an edge know that raw wires do not?

| Edge knowledge | Raw wire lacks this | Evidence |
|---|---|---|
| Negotiated bundle widths: `addressBits`, `dataBits`, `sourceBits`, `sinkBits`, `sizeBits`, `hasBCE` | `TLBundle{A,B,C,D,E}` only carries bitfields after parameters are chosen | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:1293-1379`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Bundles.scala:173-260` |
| Alignment, masks, beat counts, first/last, request/response classification, `needT`, inflight estimates | A plain `Decoupled` channel cannot infer legality or multibeat structure | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Edges.scala:18-333` |
| Address- and size-dependent legality: `supports*Safe/Fast`, `emits*Safe/Fast`, source visibility, FIFO domain, source/sink bounds | Wires cannot prove protocol compatibility against the negotiated contract | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:611-705`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:1134-1188` |
| Builder helpers return both payload and legality bit | Bit constructors alone cannot say whether a request is valid for this path | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Edges.scala:342-563`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Edges.scala:627-786` |

### 4. Which mismatches are solved by adapters?

| Adapter | Solves | Key parameter rewrite | Evidence |
|---|---|---|---|
| `TLWidthWidget` | beat-byte / data-width mismatch | rewrites manager-facing `beatBytes`; splices/splits/merges beats and records address bits for D-channel narrowing | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/WidthWidget.scala:14-24`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/WidthWidget.scala:28-223` |
| `TLFragmenter` | transfer-size / burst-shape mismatch | expands manager `supports*` up to `maxSize`, compacts clients into a FIFO source space, reassembles D responses | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Fragmenter.scala:26-89`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Fragmenter.scala:98-255` |
| `TLBuffer` | latency / backpressure mismatch | adds queue stages and increments `minLatency` on affected directions | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Buffer.scala:13-24`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Buffer.scala:43-59` |
| `TLSourceShrinker` | source-id space mismatch | crushes client `sourceId` into `[0,maxInFlight)`, optionally forces manager `fifoId=0` for single-flight | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/SourceShrinker.scala:16-37`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/SourceShrinker.scala:57-86` |
| `TLAtomicAutomata` | missing AMO support downstream | widens manager atomic support when Get+PutFull at beat granularity and FIFO/tree constraints hold | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/AtomicAutomata.scala:16-33`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/AtomicAutomata.scala:41-60`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/AtomicAutomata.scala:92-177` |
| `TLToAXI4` | TL to AXI protocol / ID / response-shape mismatch | maps TL `sourceId` to AXI IDs, packs TL response state in AXI echo bits, stalls mixed read/write ordering when FIFO requested | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/ToAXI4.scala:31-75`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/ToAXI4.scala:107-189`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/ToAXI4.scala:258-287` |
| `AXI4ToTL` | AXI to TL protocol / burst / error-device mismatch | expands AXI IDs into TL source ranges, intersects manager `supports*` with AXI burst bounds, redirects illegal accesses to `TLError` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/amba/axi4/ToTL.scala:29-62`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/amba/axi4/ToTL.scala:89-118`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/amba/axi4/ToTL.scala:138-178` |

### 5. Which mismatches are illegal and should fail before RTL binding?

| Illegal mismatch | Rocket failure point | Evidence |
|---|---|---|
| Overlapping `sourceId` ownership across clients | `TLMasterPortParameters` `require` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:1089-1092` |
| Overlapping manager address ranges or transfer-size lattice violations | `TLSlaveParameters` `require`s | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:220-250` |
| Link `maxTransfer < beatBytes` | `TLEdgeParameters` `require` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:1369-1377` |
| Invalid `TransferSizes` or `IdRange` primitives | diplomacy primitive `require`s | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/diplomacy/Parameters.scala:28-125` |
| Fragmenting cacheable/probe traffic, fragmenting below beat, non-FIFO response domains, denial modes unsupported by settings | `TLFragmenter` `require`s | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Fragmenter.scala:98-112` |
| Shrinking sources across Acquire/Probe-capable traffic | `TLSourceShrinker` `require` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/SourceShrinker.scala:53-56` |
| Synthesizing atomics without beat-sized Get+PutFull, root-tree placement, or FIFO domains | `TLAtomicAutomata` `require`s | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/AtomicAutomata.scala:26-29`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/AtomicAutomata.scala:51-60` |
| Bridging AXI without `maxFlight`, without a reachable `TLError`, or with heterogeneous AXI interleave IDs | `AXI4ToTL` / `TLToAXI4` `require`s | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/amba/axi4/ToTL.scala:31-32`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/amba/axi4/ToTL.scala:93-100`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/ToAXI4.scala:107-109` |
| External slave TL port issuing Acquires | explicit subsystem rule | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:221-240` |

### 6. How do monitors turn negotiated parameters into checks?

- `CONFIRMED` `TLImp.monitor` instantiates the monitor from the final `TLEdgeIn`; the monitor never checks against ad-hoc constants. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Nodes.scala:24-29`.
- `CONFIRMED` Format checks use negotiated capabilities: `emits*`, `supports*Safe`, visibility, `beatBytes`, source/sink bounds, masks, and permission enums. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:63-381`.
- `CONFIRMED` Multibeat checks pin opcode/param/size/source/address/sink/denied stability across beats using `edge.first`. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:384-418`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:512-558`.
- `CONFIRMED` Source/sink uniqueness and response matching are derived from negotiated `endSourceId`, `endSinkId`, response opcode maps, and `minLatency`; the monitor tracks inflight state and timeouts. Evidence: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:606-715`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:717-847`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:849-882`.

## GPGPU Interface Contract Schema in YAML

```yaml
sm_memory_client:
  role: client
  declare_before_rtl:
    node_type: TLClientNode
    source_id_range: {start: 0, end: 64}
    visibility:
      - global_mem
      - constant_mem
      - runtime_mmio
    request_fifo: true
    min_latency: 0
    supports_from_manager:
      probe: [0, 0]
      arithmetic: [0, 0]
      logical: [0, 0]
      get: [0, 0]
      put_full: [0, 0]
      put_partial: [0, 0]
      hint: [0, 0]
    emits_to_manager:
      acquire_t: [0, 0]
      acquire_b: [0, 0]
      arithmetic: [4, 32]
      logical: [4, 32]
      get: [4, 256]
      put_full: [4, 256]
      put_partial: [4, 256]
      hint: [0, 0]
    request_fields:
      - cache_policy
      - fence_scope
    echo_fields:
      - txn_class
    response_keys:
      - error_code
      - poison

l2_noc_manager:
  role: manager
  declare_before_rtl:
    node_type: TLManagerNode
    address_sets:
      - {name: global_mem, base: 0x00000000, mask: 0x3fffffff}
      - {name: runtime_mmio, base: 0x40000000, mask: 0x0000ffff}
    region_type: UNCACHED
    executable: false
    fifo_id: 0
    beat_bytes: 32
    end_sink_id: 4
    min_latency: 1
    supports_from_client:
      acquire_t: [0, 0]
      acquire_b: [0, 0]
      arithmetic: [4, 16]
      logical: [4, 16]
      get: [4, 256]
      put_full: [4, 256]
      put_partial: [4, 256]
      hint: [0, 0]
    emits_to_client:
      probe: [0, 0]
      arithmetic: [0, 0]
      logical: [0, 0]
      get: [0, 0]
      put_full: [0, 0]
      put_partial: [0, 0]
      hint: [0, 0]
    may_deny_get: false
    may_deny_put: false
    response_fields:
      - error_code
      - poison
    request_keys:
      - cache_policy
      - fence_scope

negotiated_edge_rules:
  derive_bundle_from_edge: true
  forbid_raw_wire_binding_without_edge: true
  derived_fields:
    - address_bits
    - data_bits
    - source_bits
    - sink_bits
    - size_bits
    - has_bce
    - full_mask
    - num_beats
    - first_last
    - supports_safe_fast
  allowed_adapters:
    - width_widget
    - fragmenter
    - buffer
    - source_shrinker
    - atomic_automata
    - tl_to_axi4
    - axi4_to_tl
  hard_fail_if:
    - source_id_ranges_overlap
    - address_sets_overlap
    - max_transfer_lt_beat_bytes
    - atomic_exposed_without_get_putfull_fifo_support
    - acquire_path_crosses_source_shrinker
    - fragmenter_used_on_cacheable_probe_path
    - bridge_missing_error_device_or_max_flight
```

## Required Compatibility Checks

| Check | Rocket enforcement | GPGPU rule | Failure example |
|---|---|---|---|
| Source ID capacity and disjointness | `IdRange.overlaps`, `endSourceId`, `TLSourceShrinker` remap state | Every SM/coalescer outstanding slot must live in a declared non-overlapping source-id range or pass through an explicit remapper | `8` SMs x `16` outstanding requests but NoC source range only covers `64`; scoreboard reuses an inflight ID |
| Address-space ownership | manager address overlap forbidden; visibility checked in monitor | Every address space must have a unique manager route and each client must declare visibility explicitly | MMIO launch write is routed into cacheable global-memory path |
| Data width / beat bytes | `TLBundleParameters.dataBits = slave.beatBytes*8`; `TLWidthWidget` required for mismatch | Never infer flit width locally; insert width adapter or fail | Coalescer emits `256b`, L2 beat is `128b`, D-channel truncates silently |
| Transfer size / burst shape | `TransferSizes`, `TLFragmenter`, `maxTransfer >= beatBytes` | Request size lattice must be explicit; burst expansion/fragmentation must be owned by an adapter | DRAM expects bursts up to `256B`, client only emits single-beat `32B` and no fragmenter is present |
| Atomic support | `TLAtomicAutomata` requires beat-sized Get+PutFull plus FIFO/tree constraints | ISA/runtime may only expose AMOs that a negotiated path supports or that an atomic adapter can synthesize | Runtime exposes `atomicCAS`, L2 path only supports plain loads/stores |
| FIFO / ordering contract | `requestFifo`, `fifoId`, bridge stalls, optional FIFO fixers in port chains | Fence/order expectations must be encoded as a first-class capability, not assumed from transport reuse | Scoreboard assumes in-order write-after-read completion across a bridge that permits AXI reordering |
| Denial / error semantics | manager `mayDeny*`, bridge error-device requirements, monitor denied/corrupt checks | Client retry/error model must match manager deny policy; denial is part of contract | Runtime assumes every access completes successfully, but bridge redirects bad address to error device |
| Cacheability / coherence coupling | AcquireB/Probe implications, fragmenter/source-shrinker prohibitions | If probes/acquires exist, adapters that break coherence semantics are forbidden on that path | L2 coherence path is routed through source shrinker or fragmenter |
| Bridge prerequisites | `AXI4ToTL` requires `maxFlight` and `TLError`; `TLToAXI4` requires homogeneous interleave ids | Bridge ownership includes ID, error, and response-shape translation; do not direct-wire TL <-> AXI | External AXI master lacks max inflight metadata, TL fabric cannot allocate source IDs safely |

## Explicit Adapter List

| Adapter | Interface family | Problem solved | Non-negotiable preconditions | Evidence |
|---|---|---|---|---|
| `TLWidthWidget` | TL | beat-width conversion | negotiated `beatBytes`; D-channel narrowing records address bits per source | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/WidthWidget.scala:14-24`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/WidthWidget.scala:173-223` |
| `TLFragmenter` | TL | request/response fragmentation and reassembly | FIFO response domain, no cacheable probe path, no sub-beat fragmentation, deny-mode compatibility | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Fragmenter.scala:66-89`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Fragmenter.scala:98-112` |
| `TLBuffer` | TL | buffering and latency shaping | only changes timing, not semantics; updates `minLatency` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Buffer.scala:13-24`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Buffer.scala:43-59` |
| `TLSourceShrinker` | TL | reduce required source-id width | no Acquire/Probe-capable path through shrinker | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/SourceShrinker.scala:21-37`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/SourceShrinker.scala:53-86` |
| `TLAtomicAutomata` | TL | synthesize unsupported atomics | beat-sized Get+PutFull, FIFO manager, tree-root placement | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/AtomicAutomata.scala:22-33`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/AtomicAutomata.scala:51-60` |
| `TLToAXI4` | TL -> AXI4 | protocol conversion, source-id to AXI-id mapping, TL state preservation | homogeneous `interleavedId`, limited size encoding, no LR/SC forward-progress promise | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/ToAXI4.scala:36-75`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/ToAXI4.scala:107-189`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/ToAXI4.scala:258-287` |
| `AXI4ToTL` | AXI4 -> TL | protocol conversion, AXI-id expansion into TL source ids, illegal-access redirection | per-ID `maxFlight`, reachable `TLError`, FIFO manager view | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/amba/axi4/ToTL.scala:29-62`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/amba/axi4/ToTL.scala:89-118`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/amba/axi4/ToTL.scala:138-224` |
| Port-chain examples | subsystem composition | shows adapters are first-class topology elements, not hidden synthesis passes | adapters are inserted explicitly in port attachment chains | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:107-117`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:141-149`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:171-180`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:205-212`, `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:235-240` |

## Required Evidence Table

| Rocket Mechanism | Source Files | Problem Solved in Rocket | Transferable Abstraction | GPGPU Skill Rule | Anti-Pattern to Avoid |
|---|---|---|---|---|---|
| Lazy diplomatic node graph | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/docs/src/diplomacy/adder_tutorial.md:48-187`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Nodes.scala:40-47` | Separate capability declaration from final wires | Declare interface contracts before elaborating RTL | Require every SM/L2/NoC boundary to instantiate a contract node before bundle creation | Let RTL modules invent widths, IDs, or legal opcodes locally |
| `TLMasterParameters` / `TLSlaveParameters` ownership split | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:172-458`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:813-1015` | Makes producer and consumer obligations explicit and directional | Separate client-emits/client-accepts from manager-supports/manager-emits | Model SM request capabilities and L2 acceptance capabilities as different schemas | Collapse both sides into one vague "bus config" blob |
| `TLEdge` + `TLBundleParameters` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Parameters.scala:1293-1379`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Edges.scala:18-333` | Derives concrete wires and legality from both sides together | Use an edge object as the single source of truth for derived interface facts | Generate `source_bits`, `sink_bits`, `data_bits`, masks, beat counts, and legality from negotiation output | Bind raw ready/valid channels first and retrofit metadata later |
| `TLWidthWidget` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/WidthWidget.scala:14-24`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/WidthWidget.scala:151-223` | Safe width conversion including D-channel response narrowing | Width mismatch requires explicit stateful adapter | If SM/L1/L2 widths differ, insert a width adapter with source-indexed D bookkeeping | Silent truncation, duplicated lanes, or ad-hoc repacking logic |
| `TLFragmenter` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Fragmenter.scala:26-112` | Expands/splits legal transfer sizes while preserving protocol semantics | Fragmentation is a negotiated semantic transform, not a free rewrite | Burst/fragment mismatch must be owned by a fragmenter contract with FIFO/coherence prechecks | Fragment cacheable or probed traffic blindly, or accept denials without policy |
| `TLSourceShrinker` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/SourceShrinker.scala:16-88` | Reduce source-id width under bounded inflight state | Source-space compression needs explicit remap memory and legal-traffic limits | If source IDs are squeezed, track remap state and forbid coherence traffic on that path | Reuse source IDs early without a remapper or inflight guard |
| `TLAtomicAutomata` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/AtomicAutomata.scala:16-60`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/AtomicAutomata.scala:92-177` | Synthesizes AMOs only when underlying read/write semantics are strong enough | Optional features may be synthesized, but only under explicit structural preconditions | Expose atomics in GPGPU only if the path natively supports them or an atomic adapter passes its checks | Advertise CAS/AMO support because "L2 can do loads and stores" |
| TL <-> AXI bridges | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/ToAXI4.scala:36-75`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/amba/axi4/ToTL.scala:29-62`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:107-117`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:171-180` | Own protocol, ID, error, and ordering translation at fabric boundaries | Protocol conversion is an adapter contract with explicit id/error/order metadata | Make NoC/DRAM/host bridges declare ID mapping, error routing, burst limits, and ordering stalls | Direct-wire different bus families and hope field names line up |
| `TLMonitor` | `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Nodes.scala:24-29`; `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:69-882` | Converts negotiated parameters into executable assertions | Contract negotiation should generate monitors automatically | Emit monitor/checker logic from the final negotiated contract for every external interface | Treat interface negotiation as documentation-only and skip runtime assertions |

## Quality Gate

- Overall status: `PASS`
- Evidence status: `PASS`
- Readability status: `PASS`
- Safe for GPT-5.5 planning: `yes`
- Full appendix generated: `yes`
- Biggest evidence gap: No scoped file provides a universal ordering/fence adapter; ordering must be modeled explicitly in the GPGPU contract.
- Biggest readability issue: Absolute local paths make the evidence tables wide but preserve the requested source exactness.
- Required next read: `/home/cisl/Desktop/simple-gpgpu/ref_submodule/rocket-chip/src/main/scala/tilelink/FIFOFixer.scala` if the planner wants Rocket's strongest cross-manager FIFO ordering story.
