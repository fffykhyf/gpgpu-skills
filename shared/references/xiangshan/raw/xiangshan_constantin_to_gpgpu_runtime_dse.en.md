# Repository Architecture Report

## Part A. Human Handoff

### 0. Metadata

- Mode: repository
- Depth: deep
- Output profile: model-evidence
- Repo / subsystem: `ref_submodule/xiangshan` Constantin runtime DSE surface
- Branch / commit if available: `5ff19c2`
- Files read:
  - `ref/skillref/xiangshan.md` sections `0-3`, `9`, `12`
  - `ref_submodule/xiangshan/Makefile`
  - `ref_submodule/xiangshan/src/main/scala/top/{Top.scala,ArgParser.scala,Configs.scala}`
  - `ref_submodule/xiangshan/src/test/scala/top/SimTop.scala`
  - `ref_submodule/xiangshan/src/main/scala/xiangshan/{Parameters.scala,backend/Backend.scala}`
  - `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/{sbuffer/Sbuffer.scala,lsqueue/NewStoreQueue.scala,lsqueue/LoadQueueReplay.scala}`
  - `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/prefetch/{PrefetcherWrapper.scala,PrefetcherMonitor.scala,L1StridePrefetcher.scala,L1StreamPrefetcher.scala,Berti.scala}`
  - `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/{dcache/DCacheWrapper.scala,dcache/data/BankedDataArray.scala,dcache/mainpipe/{MissQueue.scala,MainPipe.scala},mmu/L2TLB.scala}`
  - `ref_submodule/xiangshan/scripts/{xiangshan.py,constantHelper.py}`
  - Official docs: `https://docs.xiangshan.cc/zh-cn/latest/tools/constantin/`
- Files skipped:
  - `xiangshan-nemu` and `ref/xiangshan.pdf` for this shard
  - CPU frontend / branch predictor / ROB / ISA details except where they expose a Constantin-controlled knob
  - local `utility.Constantin` / `MuxModule` implementation source: not present in this snapshot
- Entry points inspected:
  - build flag `WITH_CONSTANTIN`
  - CLI `--with-constantin`
  - `DebugOptions.EnableConstantin`
  - `Constantin.init(...)`
  - `createRecord(...)` sites in backend / mem / cache
  - `constantHelper.py` runtime search loop
- Focus:
  - XiangShan runtime-tunable constants
  - module version switching / feature flags
  - transferable GPGPU runtime DSE rules
- Questions answered:
  - which knobs are runtime-tunable vs structural
  - how build / CLI enable Constantin
  - how `createRecord` and `MuxModule` are intended to work
  - what a safe GPGPU runtime knob schema should allow
- Non-goals:
  - CPU microarchitecture summary
  - XiangShan-wide architecture review
  - implementation of Constantin itself
- Appendix: generated at `ref/skillref/xiangshan-reader-reports/xiangshan_constantin_to_gpgpu_runtime_dse.en.md`
- Confidence: Medium

### 1. One-Paragraph Answer

`Constantin` in XiangShan is a build-enabled but run-driven constant injection layer: once the simulator is built with `WITH_CONSTANTIN=1` / `--with-constantin`, named `createRecord(...)` call sites can change thresholds, feature enables, policy selects, and debug-table write gates at runtime without regenerating RTL (`Makefile:191-194`, `xiangshan.py:76,135-144,780`, `ArgParser.scala:110-113`, `Top.scala:413-418`, Constantin docs `简介` and `运行时可变常量值`). The safe transfer rule for a GPGPU skill is strict: only knobs that act on already-elaborated hardware behavior are runtime DSE knobs; widths, queue depths, bank counts, module presence, and ISA/ABI-visible parameters remain elaboration-time fixed (`Parameters.scala:157,169-170,524-538,584-585`, `DCacheWrapper.scala:44-55,150`, `PrefetcherWrapper.scala:154-159,166-168,216-218,257-259`). Local call sites confirm three useful families: behavioral thresholds/budgets, feature/policy switches, and debug-only trace gates; module-version switching via `MuxModule` is confirmed by official docs but its implementation and local use sites are missing from this snapshot.

### 2. Top Architecture Findings

1. `CONFIRMED` Constantin itself is enabled at build / elaboration time, not per-run only. `WITH_CONSTANTIN=1` adds `--with-constantin`; the parser sets `DebugOptions.EnableConstantin`; top-level elaboration calls `Constantin.init(enableConstantin && !envInFPGA)`. Evidence: `Makefile:191-194`, `xiangshan.py:76,135-144,780`, `ArgParser.scala:110-113`, `Top.scala:413-418`, `SimTop.scala:186-199`.
2. `CONFIRMED` Runtime values are name-bound via `createRecord("name")`; docs state repeated creation of the same name returns the same constant, allowing one knob to fan out across many RTL sites. Evidence: Constantin docs `运行时可变常量值`; local reuse patterns at `Backend.scala:486-492` and `BankedDataArray.scala:639-642,976-979`.
3. `CONFIRMED` Safe local runtime knobs are behavior-only controls on fixed structures: thresholds (`StoreBufferThreshold`, `StoreWaitThreshold`, `ColdDownThreshold`), budgets (`nMaxPrefetchEntry`), feature enables (`pf_enableSMS`, `enableL3StreamPrefetch`), and policy switches (`EnableMdp`, `LFSTEnable`, `pf_modeStrideBerti`). Evidence: `Sbuffer.scala:539-547`, `MainPipe.scala:258-264`, `LoadQueueReplay.scala:526-533`, `MissQueue.scala:1260-1268,1409-1411`, `Backend.scala:486-492`, `NewStoreQueue.scala:366-372`, `PrefetcherWrapper.scala:161-170,218-225,259-263`.
4. `CONFIRMED` Structural parameters stay compile-time fixed even when nearby behavior knobs are runtime-tunable. Examples: `prefetcherSeq`, `StoreBufferSize`, `StoreQueueSize`, `LoadPipelineWidth`, DCache `nMissEntries`, and `EnableConstantin` itself. Evidence: `Parameters.scala:157,159-170,524-538,584-585,711-738,764-766`, `DCacheWrapper.scala:44-55,150`, `Configs.scala:156-189,280-292`.
5. `CONFIRMED` XiangShan already couples runtime knobs to observability: the same subsystems expose `XSPerfAccumulate` / `XSPerfHistogram` counters and `ChiselDB.createTable(...).log(...)` hooks, so a DSE loop can score a configuration and selectively emit traces. Evidence: `PrefetcherMonitor.scala:212-266,284-312`, `PrefetcherWrapper.scala:323-338`, `MissQueue.scala:1409-1411,1440-1471`, `DCacheWrapper.scala:1393-1440,1523-1528,1771`, `L2TLB.scala:287-291,1021-1089`, `BankedDataArray.scala:617-645,954-982`.
6. `CONFIRMED` `constantHelper.py` implements a runtime search loop over Constantin knobs. It reads a JSON knob schema, runs `emu ... --cst-file stdin`, parses named performance outputs, and computes fitness with max/min policies. Evidence: `constantHelper.py:13-58,88-121,152-165,196-211,322-352`.
7. `MISSING` The local snapshot does not contain the `utility.Constantin` / `MuxModule` implementation or emulator-side `--cst-file` parser, so low-level DPI-C wiring and exact stdin grammar are not locally auditable here. Evidence: requested source set plus repo-wide search of this snapshot yielded only call sites and docs, not definitions.

### 3. Minimal Architecture Map

- Build / enable path:
  - `scripts/xiangshan.py` maps `--with-constantin` to `WITH_CONSTANTIN=1`
  - `Makefile` appends `--with-constantin`
  - `ArgParser.scala` flips `DebugOptions.EnableConstantin`
  - `Top.scala` / `SimTop.scala` call `Constantin.init(...)`
- Runtime knob injection path:
  - named RTL sites call `Constantin.createRecord(...)`
  - docs bind names to `build/constantin.txt`
  - `constantHelper.py` also streams name/value tuples through `emu --cst-file stdin`
- Evaluation / attribution path:
  - perf signals via `XSPerfAccumulate` / `XSPerfHistogram`
  - debug traces via `ChiselDB.createTable(...).log(...)`
  - `constantHelper.py` parses perf text into a fitness score
- Most important modules:
  - `Backend.scala`: MDP master switch
  - `PrefetcherWrapper.scala` / `PrefetcherMonitor.scala`: prefetch mode / enable / adaptive-depth controls
  - `MissQueue.scala` / `MainPipe.scala`: prefetch admission and store-wait thresholds
  - `NewStoreQueue.scala` / `Sbuffer.scala` / `LoadQueueReplay.scala`: LSU thresholds and policy toggles
  - `DCacheWrapper.scala` / `L2TLB.scala` / `BankedDataArray.scala`: runtime debug-table write gates
- Missing boundary:
  - `utility.Constantin` and `MuxModule` source code

### 4. Top State / Interface Contracts

- `CONFIRMED` Build-time Constantin enable contract:
  - input: `WITH_CONSTANTIN=1` or `--with-constantin`
  - state owner: `DebugOptions.EnableConstantin`
  - effect: elaborated simulator includes Constantin runtime plumbing
  - evidence: `Makefile:191-194`, `xiangshan.py:76,135-144,780`, `ArgParser.scala:110-113`, `Top.scala:413-418`
- `CONFIRMED` Named runtime constant contract:
  - API: `Constantin.createRecord(name, initValue?)`
  - mapping: named constant -> RTL signal
  - repeated names: same runtime control
  - evidence: Constantin docs `运行时可变常量值`
- `CONFIRMED` Runtime module-select contract:
  - API: `MuxModule(ioType, versionCount)` with `sel` driven by a `createRecord` constant
  - constraint: all alternatives must already exist and share one IO type
  - evidence: Constantin docs `运行时切换模块版本`
- `INFERRED` Stdin Constantin contract:
  - helper writes count + `name value` lines, then runs `emu ... --cst-file stdin`
  - exact parser grammar is not locally confirmed because parser source is missing
  - evidence: `constantHelper.py:152-165`
- `CONFIRMED` DSE observability contract:
  - perf targets are named text metrics in `opt_target`
  - debug traces are emitted only when runtime trace gates are asserted
  - evidence: `constantHelper.py:39-46,196-211`, `DCacheWrapper.scala:1393-1440`, `L2TLB.scala:1041-1089`, `BankedDataArray.scala:639-642,976-979`

### 5. Top Risks / Missing Contracts

1. `MISSING` Local `Constantin` / `MuxModule` implementation is absent. This blocks source-level verification of width inference, duplicate-name resolution internals, and actual DPI-C registration.
2. `MISSING` Emulator-side `--cst-file` parser is absent. `constantHelper.py` implies a stdin protocol, but the precise accepted grammar is not confirmed locally.
3. `UNCERTAIN` Some numeric knobs appear only width-bounded, not semantics-bounded. A GPGPU rewrite loop should add explicit min/max constraints tied to elaborated capacity, not trust natural truncation.
4. `MISSING` No dedicated Constantin regression tests were found in the requested corpus. Runtime DSE safety is evidenced by use sites and docs, not by targeted tests.
5. `INFERRED` Module-version switching is transferable to GPGPU only when all alternatives share stable IO and internal structure differences do not leak into trace schema or ABI.

### 6. Evidence Snapshot

| Claim ID | Status | Short claim | Evidence |
|---|---|---|---|
| `XSCON-001` | CONFIRMED | Constantin enable path is `WITH_CONSTANTIN` -> `--with-constantin` -> `EnableConstantin` -> `Constantin.init(...)` | `Makefile:191-194`; `xiangshan.py:76,135-144,780`; `ArgParser.scala:110-113`; `Top.scala:413-418`; `SimTop.scala:186-199` |
| `XSCON-002` | CONFIRMED | XiangShan also enables Constantin via config presets | `Configs.scala:415-442` |
| `XSCON-003` | CONFIRMED | `createRecord` binds a name to a runtime constant; repeated names share one control | Constantin docs `运行时可变常量值` |
| `XSCON-004` | CONFIRMED | `MuxModule` is the intended runtime module-version switch mechanism | Constantin docs `运行时切换模块版本` |
| `XSCON-005` | CONFIRMED | Local safe runtime knobs are thresholds / feature enables / policy switches on fixed hardware | `Backend.scala:486-492`; `Sbuffer.scala:539-547`; `PrefetcherWrapper.scala:161-170,218-225,259-263`; `MissQueue.scala:1260-1268`; `MainPipe.scala:258-264`; `NewStoreQueue.scala:366-372,841-848`; `LoadQueueReplay.scala:526-533` |
| `XSCON-006` | CONFIRMED | Structural parameters remain elaboration-time fixed | `Parameters.scala:157,159-170,524-538,584-585,711-738,764-766`; `DCacheWrapper.scala:44-55,150`; `Configs.scala:156-189,280-292` |
| `XSCON-007` | CONFIRMED | Runtime DSE loop is already scripted with knob schema + fitness parsing | `constantHelper.py:13-58,88-121,152-165,196-211,322-352` |
| `XSCON-008` | CONFIRMED | Runtime knobs are already linked to perf counters and trace tables | `PrefetcherMonitor.scala:212-266,284-312`; `PrefetcherWrapper.scala:323-338`; `DCacheWrapper.scala:1393-1440`; `MissQueue.scala:1409-1411,1440-1471`; `L2TLB.scala:1041-1089`; `BankedDataArray.scala:639-642,976-979` |
| `XSCON-009` | MISSING | Local `Constantin` / `MuxModule` source is not in this snapshot | snapshot search result; no definition under requested local source set |

### 7. Main Architect Next Actions

1. Encode a GPGPU knob classifier with a hard reject on structural and ISA/ABI-visible parameters. Acceptance test: a config that changes `num_sm`, `warp_size`, or memory-bank counts is rejected before simulation.
2. Require every runtime knob to declare bounds, default, metrics, and optional trace tables. Acceptance test: `runtime_switch` schema can express XiangShan-like knobs such as `pf_modeStrideBerti`, `nMaxPrefetchEntry`, and `isWriteLoadMissTable`.
3. Allow module-policy comparison only through pre-elaborated alternatives with one stable IO shape. Acceptance test: a scheduler or coalescer switch can flip variants without changing generated RTL or trace schema.
4. Separate performance knobs from debug-only knobs. Acceptance test: debug-table gates are off in throughput ranking runs and on only in attribution runs.
5. If implementation work follows, next read should be the actual Constantin library or emulator-side `--cst-file` parser. Acceptance test: source-level confirmation of width rules and stdin/file grammar.

## Quality Gate

- Overall status: PARTIAL
- Evidence status: PARTIAL
- Readability status: PASS
- Safe for GPT-5.5 planning: with caveats
- Full appendix generated: yes
- Biggest evidence gap: local `utility.Constantin` / `MuxModule` source and emulator-side `--cst-file` parser are absent from this snapshot
- Biggest readability issue: wide evidence density; readers should use the appendix tables rather than Part A for exact knob classification
- Required next read: Constantin library / emulator parser source that implements `createRecord`, `MuxModule`, and `--cst-file`

## Part B. Evidence Appendix

### A1. Source-of-Truth Hierarchy

| Layer | Files | Role | Reliability | Notes |
|---|---|---|---|---|
| Planner / project rules | `AGENTS.md`; `ref/skillref/xiangshan.md` sections `0-3`, `9`, `12` | task scope and non-goals | High | Shard explicitly limits scope to Constantin -> GPGPU runtime DSE |
| Official docs | Constantin docs at `https://docs.xiangshan.cc/zh-cn/latest/tools/constantin/` | normative description of `createRecord`, `MuxModule`, runtime file flow | High | Only direct source for `MuxModule` in this pass |
| Top-level enable path | `Makefile`; `scripts/xiangshan.py`; `top/{ArgParser.scala,Top.scala,Configs.scala}`; `src/test/scala/top/SimTop.scala` | build / CLI / elaboration enablement | High | Confirms Constantin is compile-enabled |
| Runtime search harness | `scripts/constantHelper.py` | runtime experiment loop, knob schema, fitness parsing | High | Confirms DSE control surface and perf binding |
| RTL call sites | backend / mem / cache files listed in task | actual knob consumers | High | Confirms safe behavioral runtime knobs |
| Missing local implementation | no local `utility.Constantin` / `MuxModule` definition in requested source set | implementation boundary | Medium | Must be treated as `MISSING`, not inferred away |

### A2. Full Architecture Map

| Module | Responsibility | Inputs | Outputs | State Owned | Owner Files | Tests |
|---|---|---|---|---|---|---|
| build / CLI enable path | turn Constantin on during sim build | `WITH_CONSTANTIN`, `--with-constantin` | `DebugOptions.EnableConstantin` | build config | `Makefile`; `scripts/xiangshan.py`; `ArgParser.scala` | none found |
| top-level init | initialize Constantin runtime plumbing | `EnableConstantin`, `FPGAPlatform` | `Constantin.init(...)` side effect | runtime tool enable state | `Top.scala`; `SimTop.scala` | none found |
| runtime constant injection | expose named runtime knobs into RTL | `createRecord(name, init?)` | `UInt` / `Bool`-usable RTL signal | logical runtime knob registry | docs + use sites | none found |
| runtime module select | switch among pre-elaborated module versions | `MuxModule.in(*)`, `sel` from `createRecord` | selected module IO | selection signal only | docs only | no local use found |
| perf / trace attribution | tie knob changes to metrics / traces | perf events and ChiselDB enables | counters, histograms, DB logs | counters and trace tables | `PrefetcherMonitor.scala`; `PrefetcherWrapper.scala`; `MissQueue.scala`; `DCacheWrapper.scala`; `L2TLB.scala`; `BankedDataArray.scala` | none found |
| runtime DSE harness | generate candidates and score them | JSON constants, `opt_target`, workload | `emu --cst-file stdin`; fitness ranking | GA population / fitness map | `constantHelper.py` | none found |

### A3. Full Execution Flow

1. Build with Constantin support:
   - `xiangshan.py --with-constantin` sets `WITH_CONSTANTIN=1` (`xiangshan.py:76,135-144,780`)
   - `Makefile` appends `--with-constantin` (`Makefile:191-194`)
2. Elaborate sim with Constantin enabled:
   - `ArgParser.scala` sets `DebugOptions.EnableConstantin = true` (`ArgParser.scala:110-113`)
   - `Top.scala` / `SimTop.scala` call `Constantin.init(enableConstantin && !envInFPGA)` (`Top.scala:413-418`, `SimTop.scala:186-188`)
3. RTL sites declare runtime knobs:
   - behavioral thresholds / selectors / trace gates via `createRecord(...)`
4. Supply a runtime config:
   - docs: `${NOOP_HOME}/build/constantin.txt` contains `name value`
   - helper: feed named values to `emu --cst-file stdin` (`constantHelper.py:152-165`)
5. Run a workload:
   - knobs alter behavior on fixed hardware structures only
6. Collect observability:
   - perf via `XSPerfAccumulate` / `XSPerfHistogram`
   - debug trace via `ChiselDB.createTable(...).log(...)`
7. Score and iterate:
   - `constantHelper.py` parses named metric strings and computes fitness (`constantHelper.py:196-211,322-352`)

### A4. Full State Contracts

| State | Owner | Updated by | Read by | Reset behavior | Architectural or internal? | Evidence |
|---|---|---|---|---|---|---|
| `DebugOptions.EnableConstantin` | top-level config | CLI / config preset | `TopMain`, `SimTop` | default `false`; set by parser/config | internal tooling state | `Parameters.scala:524-538`; `ArgParser.scala:110-113`; `Configs.scala:439-442`; `Top.scala:413-418` |
| named runtime constant | Constantin runtime registry | config file / stdin at sim run | any `createRecord` consumer | init value from call site when unspecified externally | internal runtime-control state | Constantin docs `运行时可变常量值`; many use sites |
| prefetch adaptive depth / enable | `PrefetcherMonitor` | runtime constant + online counters | prefetchers | counters reset, runtime constants override depth behavior | internal performance-control state | `PrefetcherMonitor.scala:194-195,207-266` |
| debug-table write enables | per-table `createRecord` booleans | runtime constant | ChiselDB `log(...)` enables | off unless runtime value set | debug-only internal state | `DCacheWrapper.scala:1393-1440`; `L2TLB.scala:1041-1089`; `BankedDataArray.scala:639-642,976-979` |

### A5. Full Interface Contracts

| Interface | Producer | Consumer | Fields / Signals | Valid-ready / protocol | Backpressure | Evidence |
|---|---|---|---|---|---|---|
| build flag | `xiangshan.py` / make env | `Makefile` / generator | `WITH_CONSTANTIN=1` | make variable | n/a | `xiangshan.py:76,135-144`; `Makefile:191-194` |
| elaboration CLI | `Makefile` / user | `ArgParser.scala` | `--with-constantin` | argv option | n/a | `Makefile:191-194`; `ArgParser.scala:110-113` |
| runtime file contract | user / docs | Constantin runtime | `name value` per line in `build/constantin.txt` | file-based | n/a | Constantin docs `运行时可变常量值` |
| runtime stdin contract | `constantHelper.py` | emulator `--cst-file stdin` parser | count + `name value` lines | stdin stream | parser unknown locally | `constantHelper.py:152-165` |
| runtime module select | `createRecord("sel")` | `MuxModule.sel` | selector value | combinational mux select | n/a | Constantin docs `运行时切换模块版本` |
| DSE fitness contract | perf print path | `constantHelper.py` | `opt_target` metric name, policy, baseline | string match over run output | n/a | `constantHelper.py:39-46,196-211` |

### A6. Parameter Classification Table

| Parameter / knob | Category | Runtime tunable? | Why | Evidence |
|---|---|---|---|---|
| `EnableConstantin` | structural | no | enables tooling path during elaboration; not a per-run experiment knob | `Parameters.scala:537`; `ArgParser.scala:110-113`; `Top.scala:416-417` |
| `prefetcherSeq` | structural | no | determines which prefetcher modules exist at all | `Parameters.scala:157,584-585`; `PrefetcherWrapper.scala:154-159,166-168,216-218,257-259` |
| `StoreBufferSize` | structural | no | changes queue depth / vector widths / storage arrays | `Parameters.scala:169,737`; `Sbuffer.scala:546-547` |
| `StoreQueueSize` | structural | no | changes queue size and signal widths | `Parameters.scala:111,711-714`; `NewStoreQueue.scala:368-371,841-844` |
| `LoadPipelineWidth` | structural | no | changes port counts and equality constraints to backend exu counts | `Parameters.scala:159,727,764-766` |
| `DCacheParameters.nMissEntries` | structural | no | changes number of MSHR entries | `DCacheWrapper.scala:49,55,150`; `Parameters.scala:270-280`; `Configs.scala:184-188,285-289` |
| `warp_size` (GPGPU transfer example) | ISA/ABI-visible | no | changes lane semantics, masks, memory behavior, and SW-visible assumptions | GPGPU transfer rule, inferred from XiangShan classification |
| `num_sm` (GPGPU transfer example) | structural | no | changes replicated hardware count and topology | GPGPU transfer rule, inferred from XiangShan classification |
| `StoreBufferThreshold_<hart>` | runtime-tunable | yes | only adjusts eviction threshold on fixed `StoreBufferSize` | `Sbuffer.scala:539-547` |
| `StoreBufferBase_<hart>` | runtime-tunable | yes | only offsets force-write threshold on fixed buffer | `Sbuffer.scala:541-546` |
| `StoreWaitThreshold_<hart>` | runtime-tunable | yes | only changes store admission timing policy | `MainPipe.scala:258-264` |
| `ColdDownThreshold_<hart>` | runtime-tunable | yes | only changes replay cooldown threshold on fixed counter width | `LoadQueueReplay.scala:526-533` |
| `nMaxPrefetchEntry<hart>` | runtime-tunable | yes, bounded | caps which fixed MSHR IDs may accept prefetches; structure unchanged | `MissQueue.scala:468,808-824,1260,1303` |
| `EnableMdp` | runtime-tunable | yes | gates MDP metadata use; hardware fields already exist | `Backend.scala:486-492` |
| `LFSTEnable` | runtime-tunable | yes | selects between two already-elaborated dependency policies | `Parameters.scala:813`; `NewStoreQueue.scala:366-372` |
| `pf_modeStrideBerti<hart>` | runtime-tunable | yes, with guard | valid only if both candidate prefetchers were elaborated from `prefetcherSeq` | `PrefetcherWrapper.scala:154-164` |
| `pf_enableSMS<hart>` / `pf_enableL1StreamPrefetcher<hart>` / `pf_enableBerti<hart>` | runtime-tunable | yes | feature enables for instantiated prefetchers | `PrefetcherWrapper.scala:168-171,218-221,259-263` |
| `${prefetcher}_depth<hart>` / `enableDynamicPrefetcher<hart>` | runtime-tunable | yes | switch between fixed runtime depth and online adaptive controller | `PrefetcherMonitor.scala:194-195,233-266` |
| `l1_stride_ratio<hart>` / `l2_stride_ratio<hart>` | runtime-tunable | yes | changes prefetch stride distance, not structure | `L1StridePrefetcher.scala:197-206` |
| `l2DepthRatio<hart>` / `l3DepthRatio<hart>` / `streamL{1,2,3}Depth<hart>` | runtime-tunable | yes | changes stream prefetch reach on fixed implementation | `L1StreamPrefetcher.scala:266-286` |
| `thresholdOf{Reset,Update,L1PF,L2PF,L2PFR}` | runtime-tunable | yes | changes Berti prefetch heuristics only | `Berti.scala:392-396` |
| `isWrite*Table<hart>` / `isFirstHitWrite<hart>` | debug-only | yes, but not a perf knob | gates ChiselDB logging only | `DCacheWrapper.scala:1393-1440`; `L2TLB.scala:287-291,1041-1089`; `BankedDataArray.scala:639-642,976-979`; `MissQueue.scala:1409-1411` |
| `seed`, `max_instr`, `concurrent_emu` in `constantHelper.py` | test-only / harness-only | yes | affect experiment harness, not RTL behavior | `constantHelper.py:48-57,99-110` |

### A7. GPGPU Runtime-Switch YAML Schema

```yaml
runtime_switches:
  - name: warp_scheduler_policy
    category: runtime-tunable
    knob_type: enum
    selected_by: runtime_config_file
    allowed_values: [gto, round_robin, two_level, age_aware]
    requires_preelaborated_modules: true
    stable_io_contract: scheduler_io_v1
    metrics: [ipc, active_warps, issue_slot_util, scoreboard_stall_cycles]
    trace_tables: [WARP_SCHEDULE_LOG]
    default: gto

  - name: coalescer_policy
    category: runtime-tunable
    knob_type: enum
    selected_by: runtime_config_file
    allowed_values: [simple_contiguous, segment_aware, cacheline_aware]
    requires_preelaborated_modules: true
    stable_io_contract: coalescer_io_v1
    metrics: [merge_rate, memory_transactions_per_inst, global_mem_stall_cycles]
    trace_tables: [COALESCER_LOG, MEMORY_TRANSACTION_LOG]
    default: cacheline_aware

  - name: l1_prefetch_mode
    category: runtime-tunable
    knob_type: enum
    selected_by: runtime_config_file
    allowed_values: [off, stride, stream, berti, stride_plus_berti]
    requires_preelaborated_modules: true
    stable_io_contract: prefetch_io_v1
    metrics: [prefetch_hit_rate, prefetch_late_rate, cache_pollution, dram_bw]
    trace_tables: [PREFETCH_REQ_LOG]
    default: off

  - name: l1_prefetch_depth
    category: runtime-tunable
    knob_type: uint
    width: 8
    min: 0
    max: 255
    must_be_within_elaborated_capacity: true
    metrics: [prefetch_hit_rate, prefetch_drop_rate, l2_queue_pressure]
    trace_tables: [PREFETCH_REQ_LOG]
    default: 32

  - name: trace_load_miss_enable
    category: debug-only
    knob_type: bool
    selected_by: runtime_config_file
    metrics: []
    trace_tables: [LOAD_MISS_LOG]
    default: false

  - name: trace_bank_conflict_enable
    category: debug-only
    knob_type: bool
    selected_by: runtime_config_file
    metrics: []
    trace_tables: [BANK_CONFLICT_LOG]
    default: false

  - name: perf_counter_group
    category: counter-only
    knob_type: enum
    selected_by: runtime_config_file
    allowed_values: [base, scheduler, memory, prefetch, debug]
    metrics: [counter_dump]
    trace_tables: []
    default: memory
```

### A8. Rewrite-Loop Rules

- Tune only `runtime-tunable`, `debug-only`, or `counter-only` knobs without regenerating RTL.
- Reject any knob that changes module count, vector width, memory depth, bank count, queue size, routing topology, or address mapping.
- Reject any knob that is ISA/ABI-visible to software, kernels, binaries, or traces used for cross-run comparison.
- Allow enum switches only when all candidate implementations are already elaborated and share one stable IO contract. This is XiangShan `MuxModule` semantics transferred to GPGPU.
- Bind every numeric runtime knob to an explicit width and semantic bounds derived from elaborated capacity. Do not rely on silent truncation.
- Keep trace schema stable across a comparison batch. A perf run may turn trace emission on or off, but not change field definitions.
- Separate ranking runs from attribution runs:
  - ranking runs: debug-only trace gates off unless overhead is characterized
  - attribution runs: selected trace gates on for the chosen candidate only
- Persist the full runtime knob vector with every metric sample and trace artifact.

### A9. Explicit XiangShan `createRecord` Examples

| Knob | Role in XiangShan | Category | Why it is safe / unsafe for runtime DSE | Evidence |
|---|---|---|---|---|
| `EnableMdp` | master switch for mem dependence predictor metadata use | runtime-tunable | safe: existing fields are muxed to zero or passthrough; no structure changes | `Backend.scala:486-492` |
| `LFSTEnable` | choose LFST vs StoreSet-based dependency policy | runtime-tunable | safe: both policy paths are already elaborated | `NewStoreQueue.scala:366-372`; `Parameters.scala:813` |
| `pf_modeStrideBerti<hart>` | choose stride vs Berti prefetch mode | runtime-tunable | safe only if both modules were compiled in via `prefetcherSeq` | `PrefetcherWrapper.scala:154-164`; `Parameters.scala:157,584-585` |
| `${prefetcher}_enableDynamicPrefetcher<hart>` | disable online controller and use fixed depth | runtime-tunable | safe: swaps control policy over same prefetcher | `PrefetcherMonitor.scala:194-195,259-266` |
| `StoreBufferThreshold_<hart>` / `StoreBufferBase_<hart>` | control sbuffer eviction pressure | runtime-tunable | safe with explicit bounds; hardware capacity is fixed by `StoreBufferSize` | `Sbuffer.scala:539-547`; `Parameters.scala:169-170,737-738` |
| `nMaxPrefetchEntry<hart>` | reserve part of MSHR space against prefetches | runtime-tunable | safe with bounds `<= nMissEntries`; only admission policy changes | `MissQueue.scala:468,808-824,1260,1303`; `DCacheWrapper.scala:49,55,150` |
| `isWriteLoadMissTable<hart>` / `isFirstHitWrite<hart>` | gate miss/access DB emission | debug-only | safe for attribution runs; should not be ranked as a perf policy | `DCacheWrapper.scala:1393-1440` |
| `isWriteBankConflictTable<hart>` | gate bank-conflict DB emission | debug-only | safe; repeated name across duplicated logic matches docs' same-name reuse rule | `BankedDataArray.scala:639-642,976-979`; Constantin docs `运行时可变常量值` |
| `thresholdOfL1PF` etc. | Berti prefetch heuristics | runtime-tunable | safe: changes heuristic thresholds only | `Berti.scala:392-396` |

### A10. Runtime Constants Inventory for This Shard

#### A10.1 Thresholds / budgets

- `StoreBufferThreshold_<hart>`; `StoreBufferBase_<hart>`: `Sbuffer.scala:539-547`
- `ColdDownThreshold_<hart>`: `LoadQueueReplay.scala:526-533`
- `StoreWaitThreshold_<hart>`: `MainPipe.scala:258-264`
- `ForceWriteUpper_<hart>`; `ForceWriteLower_<hart>`: `NewStoreQueue.scala:841-848`
- `nMaxPrefetchEntry<hart>`: `MissQueue.scala:1260,1303`
- `${param.name}_depth<hart>`: `PrefetcherMonitor.scala:194-195`
- `l1_stride_ratio<hart>`; `l2_stride_ratio<hart>`: `L1StridePrefetcher.scala:197-200`
- `l2DepthRatio<hart>`; `l3DepthRatio<hart>`; `streamL1Depth<hart>`; `streamL2Depth<hart>`; `streamL3Depth<hart>`: `L1StreamPrefetcher.scala:266-286`
- `*_thresholdOfReset`, `*_thresholdOfUpdate`, `*_thresholdOfL1PF`, `*_thresholdOfL2PF`, `*_thresholdOfL2PFR`: `Berti.scala:392-396`

#### A10.2 Feature enables / policy switches

- `EnableMdp`: `Backend.scala:486-492`
- `LFSTEnable`: `NewStoreQueue.scala:366-372`
- `pf_modeStrideBerti<hart>`: `PrefetcherWrapper.scala:161-164`
- `pf_enableSMS<hart>`: `PrefetcherWrapper.scala:168-171`
- `pf_enableL1StreamPrefetcher<hart>`: `PrefetcherWrapper.scala:218-221`
- `pf_enableBerti<hart>`: `PrefetcherWrapper.scala:259-263`
- `${param.name}_enableDynamicPrefetcher<hart>`: `PrefetcherMonitor.scala:259-266`
- `always_update<hart>`: `L1StridePrefetcher.scala:181-190`
- `enableL3StreamPrefetch<hart>`: `L1StreamPrefetcher.scala:433-435`

#### A10.3 Debug-only write gates

- `isWriteLoadMissTable<hart>`; `isFirstHitWrite<hart>`; `isWriteLoadAccessTable<hart>`: `DCacheWrapper.scala:1393-1440`
- `isWriteL1MissQMissTable<hart>`: `MissQueue.scala:1409-1411`
- `isWriteL2TlbPrefetchTable<hart>`; `isWriteL1TlbTable<hart>`; `isWritePageCacheTable<hart>`; `isWritePTWTable<hart>`; `isWriteL2TlbMissQueueTable<hart>`: `L2TLB.scala:287-291,1041-1089`
- `isWriteBankConflictTable<hart>`: `BankedDataArray.scala:639-642,976-979`

#### A10.4 Out-of-scope but found by repo-wide search

- frontend / predictor debug controls in `frontend/bpu/Bpu.scala` and `frontend/ifu/IfuPerfAnalysis.scala`
- `slvpredctl` in `backend/fu/CSR.scala`

These were not deep-read because the task forbids CPU microarchitecture summary except for runtime-control mechanisms.

### A11. Evidence Table

| XiangShan Mechanism | Source Files / Docs | Problem Solved | Transferable GPGPU Abstraction | Skill Rule | Required Schema | Anti-Pattern to Avoid |
|---|---|---|---|---|---|---|
| Named runtime constants via `createRecord` | Constantin docs `运行时可变常量值`; `Backend.scala:486-492`; `Sbuffer.scala:539-547`; `BankedDataArray.scala:639-642,976-979` | avoid full RTL rebuild for behavior-only experiments | `runtime_switch` with stable name -> RTL signal binding | A GPGPU runtime knob must map to a fixed pre-elaborated signal and keep one stable semantic meaning | `name`, `category`, `width`, `default`, `bounds`, `metrics`, `trace_tables` | treating structural parameters as runtime knobs |
| Runtime module version switching with `MuxModule` | Constantin docs `运行时切换模块版本` | compare algorithm variants without regenerating RTL | pre-elaborated scheduler / coalescer / prefetch variant mux | Only variants with identical IO and trace schema may be runtime-selected | `allowed_values`, `requires_preelaborated_modules`, `stable_io_contract` | swapping modules whose interface or counters differ |
| Build-time Constantin enable path | `Makefile:191-194`; `xiangshan.py:76,135-144,780`; `ArgParser.scala:110-113`; `Top.scala:413-418`; `SimTop.scala:186-199` | ensure one compiled sim supports runtime knob injection | compile once with runtime-switch plumbing, then reuse | Distinguish `compile_enable` from `run_value` in the skill | `compile_guard`, `run_config_source` | claiming a runtime knob exists when the design was built without support |
| Threshold knobs on fixed queues | `Sbuffer.scala:539-547`; `MainPipe.scala:258-264`; `LoadQueueReplay.scala:526-533`; `MissQueue.scala:808-824,1260,1303` | tune pressure, wait, and replay policy on fixed storage | bounded scheduler / coalescer / MSHR / replay thresholds | Numeric runtime knobs must be explicitly bounded by elaborated capacity | `min`, `max`, `must_be_within_elaborated_capacity` | relying on overflow / truncation as tuning behavior |
| Policy / feature switches on existing logic | `Backend.scala:486-492`; `NewStoreQueue.scala:366-372`; `PrefetcherWrapper.scala:161-170,218-225,259-263`; `PrefetcherMonitor.scala:259-266` | compare policies without changing structure | bool / enum switches for scheduler, MDP, coalescer, prefetch | Policy switches are runtime-safe only if every branch already exists in hardware | `allowed_values`, `requires_preelaborated_modules`, `default` | trying to toggle in a module that was not elaborated |
| Runtime debug-table write gates | `DCacheWrapper.scala:1393-1440`; `MissQueue.scala:1409-1411`; `L2TLB.scala:1041-1089`; `BankedDataArray.scala:639-642,976-979` | targeted attribution without always-on trace cost | debug-only switch for DB / trace logging | Keep debug-only knobs out of headline performance ranking unless overhead is characterized | `category: debug-only`, `trace_tables`, `rank_in_perf_runs: false` | mixing trace-on and trace-off runs in one performance leaderboard |
| Perf-driven search harness | `constantHelper.py:13-58,88-121,152-165,196-211,322-352` | automate exploration over runtime knob vectors | DSE driver that pairs knob vectors with metric names | Every tuning run must persist knob vector, workload, seed, metric policy, and artifact paths | `search.constants[]`, `opt_target[]`, `workload`, `seed`, `artifact_dir` | collecting metrics without recording the exact knob vector |

### A12. Full Test and Evidence Map

| Behavior | Test / Log / Trace | What it proves | What it does not prove | Evidence |
|---|---|---|---|---|
| build enable path | top-level build and arg flow | Constantin is opt-in at build / elaboration time | does not prove runtime parser implementation | `Makefile:191-194`; `xiangshan.py:76,135-144,780`; `ArgParser.scala:110-113`; `Top.scala:413-418` |
| runtime knob declaration | `createRecord` call sites | local subsystems are built to accept runtime control | does not prove parser or type-width internals | many call sites listed above |
| runtime DSE loop | `constantHelper.py` | XiangShan already searches over named knobs and perf metrics | does not prove every target metric exists in every run | `constantHelper.py:13-58,152-165,196-211,322-352` |
| trace gating | ChiselDB `log(...)` enable signals | debug traces can be turned on selectively at runtime | does not quantify logging overhead here | `DCacheWrapper.scala:1393-1440`; `L2TLB.scala:1041-1089`; `BankedDataArray.scala:639-642,976-979` |
| module-version switching | docs example | intended usage model exists | no local XiangShan use site in this snapshot | Constantin docs `运行时切换模块版本` |

### A13. Full Design Invariants

- Invariant: runtime tuning may not change generated structure.
  - Owner: GPGPU skill classifier
  - Enforced by: reject structural and ISA/ABI-visible knobs
  - Tested by: schema validation before launch
  - Violated if: queue depth, bank count, module count, width, or topology changes
  - Evidence: `Parameters.scala:157,159-170,524-538,584-585`; `DCacheWrapper.scala:44-55`
  - Confidence: High

- Invariant: runtime module switching requires all variants to be pre-elaborated and IO-compatible.
  - Owner: runtime-switch generator
  - Enforced by: `MuxModule`-style abstraction
  - Tested by: compile-time interface check
  - Violated if: selected variants expose different IO or trace schema
  - Evidence: Constantin docs `运行时切换模块版本`; `PrefetcherWrapper.scala:154-159,166-168,216-218,257-259`
  - Confidence: High

- Invariant: every runtime knob used for DSE must have observable metrics and reproducibility metadata.
  - Owner: experiment harness
  - Enforced by: required schema fields and run manifest
  - Tested by: run manifest validation
  - Violated if: a run changes knobs without recording metrics / seed / workload / trace path
  - Evidence: `constantHelper.py:39-46,99-121,196-211`
  - Confidence: High

- Invariant: debug-only knobs are attribution aids, not ranking knobs.
  - Owner: report / skill policy
  - Enforced by: separate ranking vs attribution runs
  - Tested by: report manifest
  - Violated if: trace-on overhead contaminates throughput comparison
  - Evidence: `DCacheWrapper.scala:1393-1440`; `L2TLB.scala:1041-1089`; `BankedDataArray.scala:639-642,976-979`
  - Confidence: Medium

### A14. Full Contradictions / Risks

| Issue | Files involved | Why it matters | Severity | Suggested owner |
|---|---|---|---|---|
| missing Constantin library source | requested local source set | blocks source-level audit of `createRecord` width and registration semantics | High | tooling / simulator owner |
| missing local `MuxModule` use site | docs only | module-switch transfer is docs-backed but not locally exemplified | Medium | tooling / microarch owner |
| missing emulator `--cst-file` parser source | `constantHelper.py` only | stdin protocol is only inferred from helper | High | simulator owner |
| weak semantic bounds on numeric runtime knobs | multiple RTL sites | out-of-range values may produce meaningless comparisons even if hardware does not structurally change | Medium | DSE skill author |

### A15. Full Missing Contracts

| Missing contract | Evidence gap | Why it matters | Suggested owner |
|---|---|---|---|
| `createRecord` implementation contract | no local `utility.Constantin` source | width inference, duplicate-name behavior, and DPI registration cannot be source-verified | XiangShan tooling owner |
| `MuxModule` implementation contract | no local `MuxModule` source | local transfer of runtime module switching has docs support only | XiangShan tooling owner |
| `--cst-file` parser contract | parser source absent locally | exact accepted stdin/file grammar is not locally confirmable | simulator owner |
| dedicated Constantin regression tests | none found in requested corpus | runtime DSE safety is not covered by a visible test suite in this shard | verification owner |

### A16. Full Main Architect Next Actions

- Decision needed: exact GPGPU runtime knob taxonomy.
  - Files to inspect: this report plus future GPGPU scheduler / coalescer / prefetch / trace modules
  - Proposed work order: add classifier -> add schema -> add validation -> add run manifest
  - Risk: structural knobs leak into runtime path
  - Acceptance test: runtime config rejects structural and ISA-visible knobs

- Decision needed: whether to support runtime module switching.
  - Files to inspect: Constantin docs; future GPGPU module factories
  - Proposed work order: add `MuxModule`-style abstraction only after IO contracts are frozen
  - Risk: comparing variants with incompatible observability
  - Acceptance test: all variants compile behind one shared IO type and one trace schema

- Decision needed: which debug tables are worth runtime gating.
  - Files to inspect: GPGPU memory / coalescer / scheduler trace sites
  - Proposed work order: define `debug-only` knob set separately from perf knob set
  - Risk: debug overhead pollutes perf results
  - Acceptance test: ranking runs and attribution runs are clearly separated

- Decision needed: whether to adopt XiangShan-style search harness.
  - Files to inspect: `constantHelper.py`
  - Proposed work order: port schema and run-manifest ideas, not the exact GA implementation unless needed
  - Risk: copying harness details without stable metric names
  - Acceptance test: harness can replay a knob vector deterministically and emit matching artifacts

### A17. Full Quality Gate

#### Evidence Gate

| Check | Result | Notes |
|---|---|---|
| Scope declared | PASS | files read, skipped, focus, questions, non-goals, and confidence are stated |
| Planner focus answered | PASS | report stays on Constantin -> GPGPU runtime DSE knobs |
| Evidence attached | PASS | every major claim cites local paths or official docs |
| Claim status used | PASS | `CONFIRMED`, `INFERRED`, `UNCERTAIN`, and `MISSING` are used |
| Contradictions reported | PASS | no direct contradictions found; missing implementation boundary is explicit |
| Missing contracts reported | PASS | local implementation and parser gaps are listed |
| Handoff actionable | PASS | next actions are concrete and testable |

#### Readability Gate

| Check | Result | Notes |
|---|---|---|
| Handoff length | PASS | Part A is compact; appendix holds the bulk |
| Findings capped | PASS | seven top findings |
| Tables limited | PASS | wide tables moved to appendix |
| Empty sections removed | PASS | only relevant sections kept |
| Decision relevance | PASS | every section ties back to runtime DSE transfer |
| Appendix separation | PASS | model-evidence content is written here, not duplicated in chat |

#### Repository Extra Gate

| Topic | Status | Notes |
|---|---|---|
| ISA semantics | not applicable | outside Constantin-only shard |
| instruction encoding | not applicable | outside Constantin-only shard |
| decode path | not applicable | outside Constantin-only shard |
| PC / warp state | not applicable | XiangShan CPU repo; this shard is runtime DSE only |
| active mask | not applicable | XiangShan CPU repo; this shard is runtime DSE only |
| SIMT divergence | not applicable | XiangShan CPU repo; this shard is runtime DSE only |
| register file | not applicable | outside Constantin-only shard |
| scoreboard / hazards | inferred | policy-switch transfer rule affects these in GPGPU mapping |
| issue / execute / writeback | not applicable | outside Constantin-only shard |
| memory coalescing | inferred | XiangShan threshold / policy pattern transfers directly |
| shared memory | not applicable | XiangShan CPU repo; use GPGPU transfer rules only |
| barrier semantics | not applicable | outside Constantin-only shard |
| CSR / DCR / config state | confirmed | `DebugOptions.EnableConstantin` and runtime knob plumbing are config-state evidence |
| launch protocol | not applicable | outside Constantin-only shard |
| kernel arguments | not applicable | outside Constantin-only shard |
| grid/block/warp mapping | not applicable | outside Constantin-only shard |
| CModel / golden model | missing | not read in this pass |
| trace diff / compare path | inferred | traces / perf logs are used for DSE attribution, but DiffTest is another shard |
| tests and coverage | missing | no Constantin tests found in requested corpus |
| synthesis / FPGA / PPA evidence | missing | not part of this shard |

Overall status: `PARTIAL`
