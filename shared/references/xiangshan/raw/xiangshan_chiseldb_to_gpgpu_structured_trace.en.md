# Repository Architecture Report

## Part A. Human Handoff

### 0. Metadata

- Mode: repository
- Depth: deep
- Output profile: model-evidence
- Repo / subsystem: XiangShan ChiselDB, TileLink memory trace, SQLite analysis scripts
- Branch / commit if available: `ref_submodule/xiangshan` @ `5ff19c2b59979fc3b2db2e44a823a22e4ba13642`
- Files read:
  - Planner / policy: `ref/skillref/xiangshan.md` sections `0-3`, `8`, `12`; `skill/reader/SKILL.md`; `skill/reader/references/output-policy.md`; `skill/reader/references/repository-mode-template.md`; `skill/reader/references/quality-gate.md`
  - Official docs: <https://docs.xiangshan.cc/zh-cn/latest/tools/chiseldb/>
  - Top / config / build: `ref_submodule/xiangshan/src/main/scala/top/Top.scala:409-435`, `src/test/scala/top/SimTop.scala:180-199`, `src/main/scala/top/ArgParser.scala:102-145`, `src/main/scala/top/ArgParser.scala:241-255`, `src/main/scala/top/Configs.scala:342-344`, `src/main/scala/top/Configs.scala:434-442`, `src/main/scala/top/Configs.scala:579-606`, `src/main/scala/xiangshan/Parameters.scala:524-542`, `Makefile:166-193`, `scripts/xiangshan.py:80-99`, `scripts/xiangshan.py:136-149`, `scripts/xiangshan.py:233-257`, `scripts/xiangshan.py:286-296`, `scripts/xiangshan.py:798-810`
  - Producers: `src/main/scala/system/SoC.scala:454-475`, `src/main/scala/xiangshan/L2Top.scala:92-99`, `src/main/scala/xiangshan/DbEntry.scala:13-81`, `src/main/scala/xiangshan/backend/rob/Rob.scala:348-363`, `src/main/scala/xiangshan/backend/rob/Rob.scala:1453-1512`, `src/main/scala/xiangshan/mem/MemTrace.scala:23-27`, `src/main/scala/xiangshan/cache/dcache/DCacheWrapper.scala:111-127`, `src/main/scala/xiangshan/cache/dcache/DCacheWrapper.scala:1391-1442`, `src/main/scala/xiangshan/cache/dcache/loadpipe/LoadPipe.scala:29-31`, `src/main/scala/xiangshan/cache/dcache/loadpipe/LoadPipe.scala:612-634`, `src/main/scala/xiangshan/cache/dcache/mainpipe/MissQueue.scala:1404-1411`, `src/main/scala/xiangshan/cache/dcache/data/BankedDataArray.scala:40-46`, `src/main/scala/xiangshan/cache/dcache/data/BankedDataArray.scala:615-642`, `src/main/scala/xiangshan/cache/dcache/data/BankedDataArray.scala:952-980`, `src/main/scala/xiangshan/cache/mmu/MMUBundle.scala:1548-1575`, `src/main/scala/xiangshan/cache/mmu/L2TLB.scala:287-291`, `src/main/scala/xiangshan/cache/mmu/L2TLB.scala:1041-1089`
  - Prefetch / frontend traces: `src/main/scala/xiangshan/mem/prefetch/BasePrefecher.scala:89-94`, `src/main/scala/xiangshan/mem/prefetch/PrefetcherWrapper.scala:162-170`, `src/main/scala/xiangshan/mem/prefetch/PrefetcherWrapper.scala:218-220`, `src/main/scala/xiangshan/mem/prefetch/PrefetcherWrapper.scala:259-260`, `src/main/scala/xiangshan/mem/prefetch/PrefetcherWrapper.scala:323-331`, `src/main/scala/xiangshan/mem/prefetch/L1PrefetchComponent.scala:489-532`, `src/main/scala/xiangshan/mem/prefetch/L1PrefetchComponent.scala:732-749`, `src/main/scala/xiangshan/mem/prefetch/L1StreamPrefetcher.scala:224-245`, `src/main/scala/xiangshan/mem/prefetch/L1StreamPrefetcher.scala:350-356`, `src/main/scala/xiangshan/mem/prefetch/SMSPrefetcher.scala:1252-1257`, `src/main/scala/xiangshan/mem/prefetch/Berti.scala:363-373`, `src/main/scala/xiangshan/mem/prefetch/Berti.scala:642-652`, `src/main/scala/xiangshan/mem/prefetch/Berti.scala:914-930`
  - BPU / ICache / IFU traces: `src/main/scala/xiangshan/frontend/bpu/Parameters.scala:34-56`, `src/main/scala/xiangshan/frontend/bpu/Bpu.scala:630-657`, `src/main/scala/xiangshan/frontend/bpu/mbtb/Parameters.scala:35-65`, `src/main/scala/xiangshan/frontend/bpu/mbtb/MainBtb.scala:182-186`, `src/main/scala/xiangshan/frontend/bpu/mbtb/Bundles.scala:90-100`, `src/main/scala/xiangshan/frontend/bpu/tage/Parameters.scala:46-83`, `src/main/scala/xiangshan/frontend/bpu/tage/Tage.scala:663-670`, `src/main/scala/xiangshan/frontend/bpu/tage/Bundles.scala:184-218`, `src/main/scala/xiangshan/frontend/bpu/sc/Parameters.scala:49-100`, `src/main/scala/xiangshan/frontend/bpu/sc/Sc.scala:892-898`, `src/main/scala/xiangshan/frontend/bpu/sc/Bundles.scala:97-124`, `src/main/scala/xiangshan/frontend/bpu/utage/Parameters.scala:37-61`, `src/main/scala/xiangshan/frontend/bpu/utage/MicroTage.scala:436-440`, `src/main/scala/xiangshan/frontend/bpu/utage/Bundles.scala:104-112`, `src/main/scala/xiangshan/frontend/icache/Parameters.scala:65-66`, `src/main/scala/xiangshan/frontend/icache/ICacheMainPipe.scala:448-482`, `src/main/scala/xiangshan/frontend/icache/ICacheMissUnit.scala:293-358`, `src/main/scala/xiangshan/frontend/ifu/Bundles.scala:148-163`, `src/main/scala/xiangshan/frontend/ifu/IfuPerfAnalysis.scala:193-228`
  - Offline analysis: `scripts/cache/l2DB_helper.py:17-46`, `scripts/cache/convert_tllog.sh:1-119`, `scripts/cache/convert_mp.sh:1-160`, `scripts/rolling.py:18-28`, `scripts/rolling.py:150-253`, `scripts/rolling.py:574-686`, `scripts/perfcct.py:60-79`, `scripts/perfcct.py:81-99`, `scripts/perfcct.py:164-185`
- Files skipped:
  - `ref_submodule/xiangshan/utility/` and `ref_submodule/xiangshan/XSCache/` exist but are empty in this snapshot; `utility.ChiselDB`, `utility.TLLogger`, and any related DPI-C backend source are `MISSING`
  - No local producer was found for `LifeTimeCommitTrace` or for rolling-counter table creation; only consumers were read
- Entry points inspected: `scripts/xiangshan.py`, `Makefile`, `top/ArgParser.scala`, `top/Top.scala`, `top/SimTop.scala`, `system/SoC.scala`, `xiangshan/L2Top.scala`, `scripts/rolling.py`, `scripts/perfcct.py`, `scripts/cache/l2DB_helper.py`
- Focus: extract structured trace / SQL analysis mechanisms reusable in a GPGPU skill
- Questions answered: `1-7`; question `6` is partial because some producer-side details are `MISSING`
- Appendix: generated inline in this file
- Confidence: Medium

### 1. One-Paragraph Answer

`CONFIRMED`: XiangShan uses ChiselDB for structured, high-cardinality debug/performance data that is inefficient to keep in waveforms, with a documented DPI-C -> `sqlite3` path and a codebase-wide pattern of schema-first tables, explicit write triggers, and SQL/helper-script post-processing (<https://docs.xiangshan.cc/zh-cn/latest/tools/chiseldb/>; `Top.scala:415-418`; `SimTop.scala:185-199`). The transferable GPGPU lesson is not XiangShan CPU microarchitecture; it is the development loop: every memory/scheduling/sync/atomics/perf feature should emit timestamped, queryable rows with producer tags, selective gates, and offline attribution queries rather than relying on ad hoc waveform spelunking.

### 2. Top Architecture Findings

- `CONFIRMED`: XiangShan explicitly positions ChiselDB as the place for structured data that is too inefficient or inconvenient to analyze in waveforms, with memory trace as the canonical example. Evidence: official ChiselDB doc, retrieved `2026-06-23`, lines `117-119`.
- `CONFIRMED`: ChiselDB enablement is two-layered: build/configuration enables database instrumentation, then emulator runtime `--dump-db` requests an output DB file. Evidence: `scripts/xiangshan.py:88-99`, `scripts/xiangshan.py:136-149`, `scripts/xiangshan.py:286-296`, `scripts/xiangshan.py:805`; `Makefile:166-173`; `ArgParser.scala:102-109`; `Top.scala:415-418`; `SimTop.scala:185-199`.
- `CONFIRMED`: TileLink memory trace has a fixed schema centered on `NAME`, `CHANNEL`, `OPCODE`, `PARAM`, `SOURCE`, `SINK`, `ADDRESS`, `DATA_0..3`, `USER`, `ECHO`, and `STAMP`, and XiangShan attaches TL loggers at L2 and L3 interconnect edges. Evidence: official doc lines `121-142`; `SoC.scala:456-475`; `L2Top.scala:95-98`.
- `CONFIRMED`: XiangShan records multiple table families beyond memory trace: commit/writeback/load debug (`Tip_`, `InstTable`, `LoadDebugTable`), DCache miss/access/bank conflict, TLB/PTW/page cache, prefetch activity, BPU training/prediction, ICache access/miss, and IFU traces. Evidence: `Rob.scala:355-363`, `Rob.scala:1456-1512`, `DCacheWrapper.scala:1393-1442`, `LoadPipe.scala:620-634`, `MissQueue.scala:1409-1411`, `BankedDataArray.scala:617-642`, `L2TLB.scala:287-291`, `L2TLB.scala:1041-1089`, `PrefetcherWrapper.scala:325-331`, `Bpu.scala:639-657`, `ICacheMainPipe.scala:479-482`, `ICacheMissUnit.scala:313-358`, `IfuPerfAnalysis.scala:193-228`.
- `CONFIRMED`: Debug-only row emission is usually gated either by per-feature config flags such as `EnableBpTrace` / `EnableTrace` / `EnableMainbtbTrace` or by Constantin runtime records such as `isWriteLoadMissTable`, `isWriteL1TlbTable`, and `isWriteFetchToIBufferTable`. Evidence: `BpuParameters.scala:38-56`, `ICache/Parameters.scala:65-66`, `MainBtb/Parameters.scala:35-65`, `Tage/Parameters.scala:46-83`, `Sc/Parameters.scala:49-100`, `MicroTage/Parameters.scala:37-61`, `DCacheWrapper.scala:1393-1422`, `L2TLB.scala:287-291`, `L2TLB.scala:1041-1084`, `IfuPerfAnalysis.scala:193-228`.
- `CONFIRMED`: XiangShan’s offline tooling assumes database-first debug, not raw dumps only: `l2DB_helper.py` runs filtered SQL and pipes to AWK protocol decoders, `rolling.py` plots/diffs/correlates rolling counters from SQLite tables, and `perfcct.py` reconstructs per-instruction lifetimes from a commit-trace table. Evidence: `l2DB_helper.py:17-46`; `convert_tllog.sh:1-119`; `convert_mp.sh:1-160`; `rolling.py:18-28`, `rolling.py:150-253`, `rolling.py:574-686`; `perfcct.py:81-99`, `perfcct.py:164-185`.
- `INFERRED`: For a GPGPU skill, the XiangShan pattern should become a hard rule: any feature affecting memory, scheduling, synchronization, atomics, or performance must ship one trace table, one dump trigger, one offline debug query, and one performance-attribution query.

### 3. Minimal Architecture Map

`scripts/xiangshan.py --dump-db`
-> sets `WITH_CHISELDB=1` for build and passes emulator `--dump-db` at run time (`scripts/xiangshan.py:88-99`, `scripts/xiangshan.py:136-149`, `scripts/xiangshan.py:286-296`)
-> `Makefile` maps `WITH_CHISELDB=1` to Scala arg `--with-chiseldb`; `WITH_ROLLINGDB=1` maps to `--with-rollingdb` (`Makefile:166-173`)
-> `ArgParser` converts CLI flags into `DebugOptions.EnableChiselDB`, `EnableRollingDB`, `AlwaysBasicDB`, `EnableConstantin` (`ArgParser.scala:102-145`, `Parameters.scala:524-542`)
-> `TopMain` / `SimTop` call `Constantin.init(...)` and `ChiselDB.init(...)`; `SimTop` also emits generated file registrations (`Top.scala:415-418`; `SimTop.scala:185-199`)
-> producers log rows into typed tables or TL loggers:
  - TL interconnect: `SoC.scala`, `L2Top.scala`
  - commit / load debug: `Rob.scala`
  - DCache / miss / bank conflict: `DCacheWrapper.scala`, `LoadPipe.scala`, `MissQueue.scala`, `BankedDataArray.scala`
  - TLB / PTW: `L2TLB.scala`, `MMUBundle.scala`
  - prefetchers: `PrefetcherWrapper.scala`, `L1PrefetchComponent.scala`, `L1StreamPrefetcher.scala`, `SMSPrefetcher.scala`, `Berti.scala`
  - predictor / ICache / IFU: `Bpu.scala`, `MainBtb.scala`, `Tage.scala`, `Sc.scala`, `MicroTage.scala`, `ICacheMainPipe.scala`, `ICacheMissUnit.scala`, `IfuPerfAnalysis.scala`
-> offline consumers query raw SQLite tables or decode them into human-readable forms (`rolling.py`, `perfcct.py`, `l2DB_helper.py`, `convert_tllog.sh`, `convert_mp.sh`)

### 4. Top State / Interface Contracts

- `CONFIRMED`: `ChiselDB.createTable(tableName, hw, basicDB = false)` uses a `Record`/`Bundle` as schema and auto-adds `ID`, `STAMP`, `SITE`. Evidence: official doc lines `195-206`.
- `CONFIRMED`: `table.log(data, en, site, clock, reset)` binds each row to an explicit write condition and an optional producer tag. Evidence: official doc lines `228-243`; `L2TLB.scala:1048-1089`; `LoadPipe.scala:622-634`.
- `CONFIRMED`: shared tables often multiplex multiple producers via `SITE` instead of defining a new schema per sub-source, e.g. `L1Tlb_hartX` uses `ITlbReq`, `DTlbReq`, `ITlbResp`, `DTlbResp`; `PTW_hartX` uses `PTWReq`, `PTWResp`, `LLPTWReq`, `LLPTWResp`. Evidence: `L2TLB.scala:1048-1089`.
- `CONFIRMED`: rolling-counter consumers require table names matching `<perf_name>_rolling_<hart>` and columns `XAXISPT`, `YAXISPT`, plus `STAMP` for stats. Evidence: `rolling.py:28`, `rolling.py:160-179`, `rolling.py:224-239`.
- `MISSING`: the local `utility.ChiselDB` implementation is unavailable, so the exact interaction between `basicDB = true` and `Top.scala` `ChiselDB.init(enableChiselDB && !envInFPGA)` is not proven from source in this shard.

### 5. Top Risks / Missing Contracts

- `MISSING`: `utility/` is empty in this checkout, so DPI-C backend details, actual SQLite DDL generation, and `TLLogger` implementation are unavailable (`ls -la ref_submodule/xiangshan/utility` shows no files).
- `MISSING`: `LifeTimeCommitTrace` producer was not found locally; `perfcct.py` proves the consumer-side contract only (`perfcct.py:164-185`).
- `MISSING`: rolling-counter producer code was not found locally; `rolling.py` proves the consumer-side naming and column contract only (`rolling.py:160-239`).
- `CONFLICTED`: official docs say the TileLink table name is `TL_LOG`, while `l2DB_helper.py` queries `TLLOG` (`docs` lines `126-142`; `l2DB_helper.py:42-43`). Treat the exact raw table name as unstable until the backend implementation is read.
- `UNCERTAIN`: complex nested BPU tables (`BpuMeta`, `BpuTrain`, `MicroTageTrace`) are confirmed to exist, but their flattened column names were not enumerated in this shard.

### 6. Evidence Snapshot

| Claim ID | Status | Short claim | Evidence |
|---|---|---|---|
| `XS-CHDB-C001` | CONFIRMED | ChiselDB exists for structured data that is inefficient in waveforms. | Official doc, retrieved `2026-06-23`, lines `117-119` |
| `XS-CHDB-C002` | CONFIRMED | `--dump-db` in `xiangshan.py` drives both build-time `WITH_CHISELDB` and runtime emulator dumping. | `scripts/xiangshan.py:88-99`, `scripts/xiangshan.py:136-149`, `scripts/xiangshan.py:286-296`, `scripts/xiangshan.py:805`; `Makefile:166-169` |
| `XS-CHDB-C003` | CONFIRMED | Top-level Scala initialization uses `ChiselDB.init(enableChiselDB && !envInFPGA)`. | `Top.scala:415-418`; `SimTop.scala:185-188` |
| `XS-CHDB-C004` | CONFIRMED | TL memory trace schema includes node name, TL channel/opcode/param/source/sink/address/data/user/echo/stamp. | Official doc lines `126-142` |
| `XS-CHDB-C005` | CONFIRMED | TL loggers are attached at L2/L3 boundaries with `AlwaysBasicDB` gating. | `SoC.scala:456-475`; `L2Top.scala:95-98` |
| `XS-CHDB-C006` | CONFIRMED | XiangShan logs commit/writeback/load/miss/bank-conflict/TLB/PTW/prefetch/frontend tables via typed `createTable(...).log(...)` calls. | `Rob.scala:355-363`, `Rob.scala:1456-1512`, `DCacheWrapper.scala:1393-1442`, `L2TLB.scala:287-291`, `L2TLB.scala:1041-1089`, `PrefetcherWrapper.scala:325-331`, `ICacheMissUnit.scala:313-358` |
| `XS-CHDB-C007` | CONFIRMED | Selective row emission is controlled by config booleans or Constantin records. | `Bpu.scala:639-657`; `ICacheMainPipe.scala:479-482`; `DCacheWrapper.scala:1393-1422`; `L2TLB.scala:1041-1084`; `IfuPerfAnalysis.scala:193-228` |
| `XS-CHDB-C008` | CONFIRMED | `rolling.py` expects `<perf>_rolling_<hart>` tables with `XAXISPT`, `YAXISPT`, and `STAMP`. | `rolling.py:28`, `rolling.py:160-179`, `rolling.py:224-239` |
| `XS-CHDB-C009` | CONFIRMED | `perfcct.py` reconstructs instruction-stage timelines from `LifeTimeCommitTrace` `At*` columns. | `perfcct.py:81-99`, `perfcct.py:164-185` |
| `XS-CHDB-C010` | CONFLICTED | TileLink raw table name is either `TL_LOG` or `TLLOG`. | Official doc lines `126-142`; `l2DB_helper.py:42-43` |

### 7. Main Architect Next Actions

- Define the mandatory GPGPU trace families as first-class schemas: `WARP_COMMIT_LOG`, `WARP_ISSUE_LOG`, `SCOREBOARD_LOG`, `MEMORY_TRANSACTION_LOG`, `COALESCER_LOG`, `CACHE_BANK_CONFLICT_LOG`, `TLB_EVENT_LOG`, `SYNC_EVENT_LOG`, `ATOMIC_EVENT_LOG`.
- Require every table to include at least `stamp`, `site`, `sm_id`, and the narrowest useful producer context (`warp_id`, `cta_id`, `mem_txn_id`, `barrier_id`, or `atomic_id`).
- If a future checkout includes `utility/`, read `ChiselDB` / `TLLogger` to resolve `basicDB` semantics and raw table naming.
- If stage-lifetime debugging is needed for a GPGPU scoreboard skill, locate the producer of `LifeTimeCommitTrace` before drafting timeline schema rules.
- Add one SQL debug query and one SQL performance-attribution query to every new GPGPU feature review.

## Quality Gate

- Overall status: PARTIAL
- Evidence status: PARTIAL
- Readability status: PASS
- Safe for GPT-5.5 planning: yes, with caveats
- Full appendix generated: yes
- Biggest evidence gap: `utility.ChiselDB` / `utility.TLLogger` backend source and producer-side definitions for `LifeTimeCommitTrace` and rolling tables are missing
- Biggest readability issue: the exact flattened column names for complex nested BPU bundles were intentionally not expanded because they are not planning-critical for this GPGPU shard
- Required next read: initialize or provide `ref_submodule/xiangshan/utility` and the producer for `LifeTimeCommitTrace`

## Part B. Evidence Appendix

### A1. Source-of-Truth Hierarchy

| Layer | Files | Role | Reliability | Notes |
|---|---|---|---|---|
| Project rules | `ref/skillref/xiangshan.md` sections `0-3`, `8`, `12` | Planner constraints, non-goals, required output | High | Governs this shard directly |
| Official tool doc | <https://docs.xiangshan.cc/zh-cn/latest/tools/chiseldb/> | ChiselDB purpose, TL schema, API, dump method | High | Needed because `utility/` implementation is unavailable |
| Top / build glue | `Top.scala`, `SimTop.scala`, `ArgParser.scala`, `Parameters.scala`, `Makefile`, `scripts/xiangshan.py` | Enablement path and generator/runtime integration | High | Source of truth for flag plumbing |
| RTL producers | `DbEntry.scala`, `Rob.scala`, `DCacheWrapper.scala`, `LoadPipe.scala`, `MissQueue.scala`, `BankedDataArray.scala`, `L2TLB.scala`, prefetch / frontend trace files | Row schemas and dump triggers | High | Primary local evidence for transferable table design |
| Analysis scripts | `rolling.py`, `perfcct.py`, `l2DB_helper.py`, `convert_tllog.sh`, `convert_mp.sh` | Consumer-side query, decode, plot, diff, correlation behavior | High | Shows how DB output is meant to be used |
| Backend implementation | `ref_submodule/xiangshan/utility/`, `ref_submodule/xiangshan/XSCache/` | ChiselDB/TLLogger implementation details | Missing | Directories are empty in this snapshot |

### A2. Extraction Answers

1. Which data is too structured for waveform and belongs in a DB?

`CONFIRMED`: XiangShan explicitly names memory trace as too structured for efficient waveform storage and analysis (official doc lines `117-119`). The code extends the same pattern to commit/writeback timing, load debug, TLB/PTW activity, prefetch events, bank conflicts, predictor traces, and ICache miss/response state (`Rob.scala:1456-1512`; `DCacheWrapper.scala:1393-1442`; `L2TLB.scala:1041-1089`; `ICacheMissUnit.scala:313-358`). Transfer rule: if an event stream is row-shaped, repeated, and queried by predicate or aggregation, it belongs in a DB, not a waveform.

2. How does ChiselDB initialize at top-level and how is it enabled by CLI/config?

`CONFIRMED`:

- Build/config layer:
  - `scripts/xiangshan.py --dump-db` sets `self.with_chiseldb = 1` and includes `WITH_CHISELDB` in Makefile arguments (`scripts/xiangshan.py:88`, `scripts/xiangshan.py:136-149`)
  - `Makefile` maps `WITH_CHISELDB=1` to Scala generator arg `--with-chiseldb` and `WITH_ROLLINGDB=1` to `--with-rollingdb` (`Makefile:166-173`)
  - `ArgParser` maps `--with-chiseldb` to `EnableChiselDB = true`, `--with-rollingdb` to `EnableRollingDB = true`, and `--disable-alwaysdb` to `AlwaysBasicDB = false` (`ArgParser.scala:102-145`)
- Top-level init layer:
  - `TopMain` and `SimTop` call `Constantin.init(enableConstantin && !envInFPGA)` and `ChiselDB.init(enableChiselDB && !envInFPGA)` (`Top.scala:415-418`; `SimTop.scala:185-188`)
  - `SimTop` registers generated C++ support files through `ChiselDB.addToFileRegisters`, `Constantin.addToFileRegisters`, and `FileRegisters.write("./build")` (`SimTop.scala:196-199`)
- Runtime dump layer:
  - `scripts/xiangshan.py` passes emulator `--dump-db` when requested (`scripts/xiangshan.py:292`, `scripts/xiangshan.py:805`)
  - official docs say `--dump-db` causes `emu` to emit a timestamped `.db` file under `build/` (doc lines `145-151`)
- `UNCERTAIN`: exact interaction between `basicDB = true` and `ChiselDB.init(false)` is not locally provable because `utility.ChiselDB` source is missing.

3. What are the TileLink memory trace fields?

`CONFIRMED`: official doc defines the raw table as:

| Field | Meaning |
|---|---|
| `NAME` | node name such as `L2_L1D_0`, `L3_L2_0`, `MEM_L3` |
| `CHANNEL` | TileLink channel number |
| `OPCODE` | TileLink opcode |
| `PARAM` | TileLink param |
| `SOURCE` | TileLink source id |
| `SINK` | TileLink sink id |
| `ADDRESS` | address |
| `DATA_0..DATA_3` | data lanes / beat payload words |
| `USER` | user field |
| `ECHO` | echo field |
| `STAMP` | timestamp |

Evidence: official doc lines `126-142`. Readability scripts decode channel/opcode/param integers into human-readable strings (`convert_tllog.sh:3-116`).

4. Which tables exist for commit, load debug, TLB, PTW, prefetch, DCache miss/access, bank conflict, BPU/ICache traces?

`CONFIRMED`: see the inventory in section `A3`. The short answer is yes for all requested families, with exact producer sites in `Rob.scala`, `DCacheWrapper.scala`, `LoadPipe.scala`, `MissQueue.scala`, `BankedDataArray.scala`, `L2TLB.scala`, prefetcher files, `Bpu.scala`, `MainBtb.scala`, `Tage.scala`, `Sc.scala`, `MicroTage.scala`, `ICacheMainPipe.scala`, `ICacheMissUnit.scala`, and `IfuPerfAnalysis.scala`.

5. How are debug-only traces gated by Constantin records or config flags?

`CONFIRMED`:

- Config flags as trace gates:
  - `EnableBpTrace`, `EnableMainbtbTrace`, `EnableTageTrace`, `EnableScTrace`, `EnableTraceAndDebug`, `EnableTrace` are default `false` and passed directly to `createTable(..., basicDB = flag)` or equivalent (`Bpu.scala:639-640`; `MainBtb.scala:182`; `Tage.scala:663-665`; `Sc.scala:892-894`; `MicroTage.scala:436`; `ICacheMainPipe.scala:479`; `ICacheMissUnit.scala:313-315`)
- Constantin row-enable bits:
  - `isWriteLoadMissTable`, `isWriteLoadAccessTable`, `isWriteL1TlbTable`, `isWritePTWTable`, `isWriteBankConflictTable`, `isWriteFetchToIBufferTable`, `isWriteIfuWbToFtqTable`, and similar records gate `.log(...)` enables without changing schema (`DCacheWrapper.scala:1393-1442`; `L2TLB.scala:287-291`; `L2TLB.scala:1041-1089`; `BankedDataArray.scala:639-642`; `IfuPerfAnalysis.scala:193-228`)
- Build-level / always-on knobs:
  - `AlwaysBasicDB` gates TL loggers and monitor DB usage in the SoC/L2 configs (`SoC.scala:456-475`; `L2Top.scala:95-98`; `Configs.scala:342-344`)

6. How do scripts query/convert/analyze DB outputs?

`CONFIRMED`:

- Raw SQL / predicate filtering:
  - `l2DB_helper.py` builds `sqlite3` queries with optional predicates such as `STAMP > 10000` or `ADDRESS=0x80000000`, optionally selecting the last `N` rows, then pipes output into shell decoders (`l2DB_helper.py:17-30`)
- Protocol decode:
  - `convert_tllog.sh` decodes raw TL fields into readable channel/opcode/param/address/data/user/echo text (`convert_tllog.sh:3-116`)
  - `convert_mp.sh` decodes `L2MP` rows into channel/opcode/tag/set/address/MSHR metadata (`convert_mp.sh:14-157`)
- Rolling performance analysis:
  - `rolling.py` finds tables matching `<perf_name>_rolling_<hart>`, reads `XAXISPT`, `YAXISPT`, uses `STAMP` for table stats, and supports `plot`, `diff`, `list`, and `corr` subcommands (`rolling.py:28`, `rolling.py:160-239`, `rolling.py:574-686`)
- Commit timeline reconstruction:
  - `perfcct.py` reads `LifeTimeCommitTrace`, converts `At*` positions into cycles, and can render textual or visual instruction lifetimes (`perfcct.py:81-99`, `perfcct.py:164-185`)

7. How should structured trace support failure attribution and performance attribution?

`INFERRED` from XiangShan:

- failure attribution requires per-event rows with `stamp`, `site`, and narrow context ids so a failing interval can be sliced across commit, issue, memory, bank, TLB, barrier, and atomic tables
- performance attribution requires event tables plus rolling counters so row-level causes can be correlated with higher-level throughput counters
- every feature must define:
  - one table schema
  - one dump trigger
  - one row enable gate
  - one debug query
  - one attribution query
  - one stable join key or time-window strategy

### A3. XiangShan Table and Gate Inventory

| Family | XiangShan tables | Key fields confirmed in this shard | Dump trigger | Gate | Evidence |
|---|---|---|---|---|---|
| TL memory trace | `TL_LOG` or `TLLOG` | `NAME`, `CHANNEL`, `OPCODE`, `PARAM`, `SOURCE`, `SINK`, `ADDRESS`, `DATA_0..3`, `USER`, `ECHO`, `STAMP` | TL edge activity | `AlwaysBasicDB` at logger attachment | official doc lines `126-142`; `SoC.scala:456-475`; `L2Top.scala:95-98` |
| Commit summary | `Tip_<hart>` | `state`, `commits`, `redirect`, `redirect_pc`, `debugLsInfo` | every cycle | non-basic DB, no explicit extra gate in call site | `Rob.scala:348-363` |
| Writeback timing | `InstTable<hart>` | `robIdx`, `dvaddr`, `dpaddr`, `issueTime`, `writebackTime`, latency fields, `tlbLatency`, `lsInfo`, `exceptType` | `wb.valid` | `basicDB = true`, not FPGA | `DbEntry.scala:28-52`; `Rob.scala:1453-1486` |
| Load commit debug | `LoadDebugTable<hart>` | `pc`, `vaddr`, `paddr`, `cacheMiss`, `tlbQueryLatency`, `exeLatency` | load commit | `basicDB = true` | `DbEntry.scala:54-61`; `Rob.scala:1491-1512` |
| DCache miss/access | `LoadMissDB<hart>`, `LoadAccessDB<hart>` | `timeCnt`, `robIdx`, `paddr`, `vaddr`, `missState`, `pred_way_num`, `dm_way_num`, `real_way_num` | miss request / first hit / response | Constantin `isWriteLoadMissTable`, `isWriteLoadAccessTable` | `DbEntry.scala:13-26`; `DCacheWrapper.scala:1391-1442` |
| DCache pipe traces | `LoadTrace*`, `LoadPfTrace*`, `LoadTraceMiss*`, `LoadPfMshr*` | `paddr` | demand load, pf, real miss, pf miss_req fire | non-basic DB | `LoadPipe.scala:29-31`; `LoadPipe.scala:620-634` |
| DCache miss queue | `L1MissQMissTrace_hart*` | `vaddr`, `paddr`, `source`, `pc` | miss queue alloc | Constantin `isWriteL1MissQMissTable` | `MemTrace.scala:23-27`; `MissQueue.scala:1404-1411` |
| Bank conflict | `BankConflict<hart>` | per-pipe `addr`, `set_index`, per-bank `bank_index`, `way_index`, `fake_rr_bank_conflict` | read/read bank conflict | Constantin `isWriteBankConflictTable` | `BankedDataArray.scala:40-46`; `BankedDataArray.scala:615-642`; `BankedDataArray.scala:952-980` |
| TLB/PTW | `L2TlbPrefetch_hart*`, `L1Tlb_hart*`, `PageCache_hart*`, `PTW_hart*`, `L2TlbMissQueue_hart*` | `vpn`; plus `source`, `bypassed`, `is_first`, `prefetched`, `prefetch`, `l2Hit`, `l1Hit`, `hit` for page cache | req/resp/fire events | Constantin `isWrite*Table` records | `MMUBundle.scala:1548-1575`; `L2TLB.scala:287-291`; `L2TLB.scala:1041-1089` |
| Prefetch | `L2PrefetchTrace*`, `StreamPFTrace*`, `StreamPFTraceOut*`, `StreamTrainTraceTable*`, `StreamArrayTable*`, `L1SMSMissTrace*`, `berti_*` | trigger PC/VA, prefetch VA, sink, source prefetch request, delta/coverage, line VAs | prefetch enqueue/fire/train/response | non-basic DB; some path selection via Constantin | `DbEntry.scala:63-81`; `PrefetcherWrapper.scala:323-331`; `L1PrefetchComponent.scala:489-532`; `L1PrefetchComponent.scala:732-749`; `L1StreamPrefetcher.scala:224-245`; `L1StreamPrefetcher.scala:350-356`; `SMSPrefetcher.scala:1252-1257`; `Berti.scala:363-373`; `Berti.scala:642-652`; `Berti.scala:914-930` |
| BPU | `BpuPredictionTrace`, `BpuTrainTrace`, `MBTBTrace`, `CondTrace_i`, `scCondTrace_i`, `microTageTrace` | predictor meta/perfMeta, train bundle, branch trace bundles, MBTB write trace, SC trace, MicroTage trace | predictor output / train / write / resolve | `EnableBpTrace`, `EnableMainbtbTrace`, `EnableTageTrace`, `EnableScTrace`, `EnableTraceAndDebug` | `Bpu.scala:630-657`; `MainBtb.scala:182-186`; `Tage.scala:663-670`; `Sc.scala:892-898`; `MicroTage.scala:436-440`; bundle defs cited in metadata |
| ICache / IFU | `ICacheAccessTable`, `ICacheFetchMissTrace`, `ICachePrefetchMissTrace`, `ICacheMissRespTrace`, `FetchToIBuffer<hart>`, `IfuWbToFtq<hart>` | access address/way/raw hit/refill wait/exception; miss request/resp; fetch-block start addresses, mispredict/fault flags | `s1_fire`, request fire, response event, IFU fire/check | `EnableTrace` or Constantin `isWrite*Table` | `ICacheMainPipe.scala:448-482`; `ICacheMissUnit.scala:293-358`; `IfuPerfAnalysis.scala:193-228` |
| Rolling / lifetime consumers | `<perf>_rolling_<hart>`, `LifeTimeCommitTrace` | `XAXISPT`, `YAXISPT`, `STAMP`; `At*` stage columns | consumer-side only in this shard | unknown producer | `rolling.py:160-239`; `perfcct.py:164-185` |

### A4. Skill Rule for GPGPU Structured Trace

`INFERRED` skill rule:

1. Any feature affecting memory, scheduling, synchronization, atomics, or performance must define:
   - a trace table name
   - row schema and units
   - dump trigger
   - enable gate
   - one offline debug query
   - one performance-attribution query
2. Every row must include:
   - `stamp`
   - `site`
   - `sm_id`
   - the narrowest useful context id such as `warp_id`, `cta_id`, `barrier_id`, `txn_id`, or `atomic_id`
3. Heavy tables must be selectively gated.
4. Low-volume, always-useful tables may be always-on.
5. Avoid one monolithic mega-table; group by event family.
6. Provide at least one decoder or helper script for any protocol-shaped raw row format.
7. Treat missing `site` or missing `stamp` as a schema bug.

### A5. Proposed GPGPU SQL Schemas

`INFERRED` from XiangShan table patterns, especially `STAMP`, `SITE`, commit/debug tables, TL memory trace, bank conflicts, TLB/PTW tables, and offline scripts.

```sql
CREATE TABLE WARP_COMMIT_LOG (
  id INTEGER PRIMARY KEY,
  stamp INTEGER NOT NULL,
  site TEXT NOT NULL,
  sm_id INTEGER NOT NULL,
  cta_id INTEGER,
  warp_id INTEGER NOT NULL,
  pc INTEGER NOT NULL,
  instr INTEGER NOT NULL,
  opcode TEXT,
  active_mask TEXT NOT NULL,
  commit_state TEXT NOT NULL,
  redirect_pc INTEGER,
  exception_code INTEGER,
  mem_txn_id INTEGER,
  diff_valid INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE WARP_ISSUE_LOG (
  id INTEGER PRIMARY KEY,
  stamp INTEGER NOT NULL,
  site TEXT NOT NULL,
  sm_id INTEGER NOT NULL,
  warp_id INTEGER NOT NULL,
  scheduler_id INTEGER,
  pc INTEGER,
  issued INTEGER NOT NULL,
  stall_reason TEXT,
  scoreboard_blocked_mask TEXT,
  pending_barrier_id INTEGER,
  pending_mem_txns INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE SCOREBOARD_LOG (
  id INTEGER PRIMARY KEY,
  stamp INTEGER NOT NULL,
  site TEXT NOT NULL,
  sm_id INTEGER NOT NULL,
  warp_id INTEGER NOT NULL,
  event TEXT NOT NULL,
  blocked_reg INTEGER,
  producer_warp_id INTEGER,
  producer_stage TEXT,
  stall_reason TEXT,
  unblock_stamp INTEGER,
  pending_mask TEXT
);

CREATE TABLE MEMORY_TRANSACTION_LOG (
  id INTEGER PRIMARY KEY,
  stamp INTEGER NOT NULL,
  site TEXT NOT NULL,
  sm_id INTEGER NOT NULL,
  warp_id INTEGER,
  mem_txn_id INTEGER NOT NULL,
  level TEXT NOT NULL,
  channel TEXT,
  opcode TEXT NOT NULL,
  param TEXT,
  source_id INTEGER,
  sink_id INTEGER,
  address INTEGER NOT NULL,
  byte_mask TEXT,
  coalesced_lane_mask TEXT,
  data_0 INTEGER,
  data_1 INTEGER,
  data_2 INTEGER,
  data_3 INTEGER,
  user_bits INTEGER,
  echo_bits INTEGER,
  addr_space TEXT,
  is_prefetch INTEGER NOT NULL DEFAULT 0,
  is_atomic INTEGER NOT NULL DEFAULT 0,
  l1_hit INTEGER,
  l2_hit INTEGER,
  total_latency INTEGER
);

CREATE TABLE COALESCER_LOG (
  id INTEGER PRIMARY KEY,
  stamp INTEGER NOT NULL,
  site TEXT NOT NULL,
  sm_id INTEGER NOT NULL,
  warp_id INTEGER NOT NULL,
  pc INTEGER,
  request_id INTEGER,
  requested_lanes INTEGER NOT NULL,
  unique_cachelines INTEGER NOT NULL,
  emitted_transactions INTEGER NOT NULL,
  replay_count INTEGER NOT NULL DEFAULT 0,
  merged INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE CACHE_BANK_CONFLICT_LOG (
  id INTEGER PRIMARY KEY,
  stamp INTEGER NOT NULL,
  site TEXT NOT NULL,
  sm_id INTEGER NOT NULL,
  bank_id INTEGER NOT NULL,
  set_index INTEGER,
  way_index INTEGER,
  requester_count INTEGER NOT NULL,
  requester_warps TEXT,
  is_real_conflict INTEGER NOT NULL
);

CREATE TABLE PREFETCH_EVENT_LOG (
  id INTEGER PRIMARY KEY,
  stamp INTEGER NOT NULL,
  site TEXT NOT NULL,
  sm_id INTEGER NOT NULL,
  warp_id INTEGER,
  prefetcher TEXT NOT NULL,
  trigger_pc INTEGER,
  trigger_addr INTEGER,
  prefetch_addr INTEGER NOT NULL,
  target_level TEXT,
  source_type TEXT,
  hit INTEGER,
  miss INTEGER,
  accepted INTEGER
);

CREATE TABLE TLB_EVENT_LOG (
  id INTEGER PRIMARY KEY,
  stamp INTEGER NOT NULL,
  site TEXT NOT NULL,
  sm_id INTEGER NOT NULL,
  warp_id INTEGER,
  event TEXT NOT NULL,
  vpn INTEGER NOT NULL,
  source_id INTEGER,
  l1_hit INTEGER,
  l2_hit INTEGER,
  bypassed INTEGER,
  prefetched INTEGER
);

CREATE TABLE SYNC_EVENT_LOG (
  id INTEGER PRIMARY KEY,
  stamp INTEGER NOT NULL,
  site TEXT NOT NULL,
  sm_id INTEGER NOT NULL,
  cta_id INTEGER,
  warp_id INTEGER,
  barrier_id INTEGER,
  event TEXT NOT NULL,
  active_mask TEXT,
  waiters INTEGER
);

CREATE TABLE ATOMIC_EVENT_LOG (
  id INTEGER PRIMARY KEY,
  stamp INTEGER NOT NULL,
  site TEXT NOT NULL,
  sm_id INTEGER NOT NULL,
  warp_id INTEGER NOT NULL,
  mem_txn_id INTEGER,
  address INTEGER NOT NULL,
  op TEXT NOT NULL,
  scope TEXT,
  lane_mask TEXT,
  serialized INTEGER NOT NULL,
  total_latency INTEGER
);

CREATE TABLE FAILURE_CONTEXT_LOG (
  id INTEGER PRIMARY KEY,
  stamp INTEGER NOT NULL,
  site TEXT NOT NULL,
  failure_id TEXT NOT NULL,
  category TEXT NOT NULL,
  sm_id INTEGER,
  warp_id INTEGER,
  pc INTEGER,
  mem_txn_id INTEGER,
  notes TEXT
);
```

### A6. Example SQL Queries

`INFERRED` from XiangShan’s SQL + decoder + rolling + lifetime tooling.

Stall attribution:

```sql
SELECT stall_reason, COUNT(*) AS stalls
FROM WARP_ISSUE_LOG
WHERE issued = 0
GROUP BY stall_reason
ORDER BY stalls DESC;
```

Memory latency by SM:

```sql
SELECT sm_id,
       AVG(total_latency) AS avg_total_latency,
       AVG(COALESCE(l2_hit, 0)) AS l2_hit_rate
FROM MEMORY_TRANSACTION_LOG
WHERE addr_space = 'global' AND is_prefetch = 0
GROUP BY sm_id
ORDER BY sm_id;
```

Coalescer effectiveness:

```sql
SELECT sm_id,
       SUM(requested_lanes) AS requested_lanes,
       SUM(emitted_transactions) AS emitted_transactions,
       ROUND(1.0 * SUM(requested_lanes) / NULLIF(SUM(emitted_transactions), 0), 3) AS lanes_per_transaction,
       SUM(replay_count) AS total_replays
FROM COALESCER_LOG
GROUP BY sm_id
ORDER BY lanes_per_transaction DESC;
```

Bank conflicts:

```sql
SELECT sm_id, bank_id, COUNT(*) AS conflicts, AVG(requester_count) AS avg_requesters
FROM CACHE_BANK_CONFLICT_LOG
WHERE is_real_conflict = 1
GROUP BY sm_id, bank_id
ORDER BY conflicts DESC, sm_id, bank_id;
```

Failure trace slice:

```sql
WITH fail AS (
  SELECT stamp, sm_id, warp_id, mem_txn_id
  FROM FAILURE_CONTEXT_LOG
  WHERE failure_id = :failure_id
),
win AS (
  SELECT stamp - 5000 AS begin_stamp, stamp + 200 AS end_stamp
  FROM fail
)
SELECT 'commit' AS src, stamp, sm_id, warp_id, pc, opcode, mem_txn_id
FROM WARP_COMMIT_LOG
WHERE stamp BETWEEN (SELECT begin_stamp FROM win) AND (SELECT end_stamp FROM win)
UNION ALL
SELECT 'issue' AS src, stamp, sm_id, warp_id, pc, stall_reason, NULL
FROM WARP_ISSUE_LOG
WHERE stamp BETWEEN (SELECT begin_stamp FROM win) AND (SELECT end_stamp FROM win)
UNION ALL
SELECT 'mem' AS src, stamp, sm_id, warp_id, address, opcode, mem_txn_id
FROM MEMORY_TRANSACTION_LOG
WHERE stamp BETWEEN (SELECT begin_stamp FROM win) AND (SELECT end_stamp FROM win)
ORDER BY stamp, src;
```

Atomic serialization hot spots:

```sql
SELECT sm_id, address, op, COUNT(*) AS ops, AVG(total_latency) AS avg_latency
FROM ATOMIC_EVENT_LOG
WHERE serialized = 1
GROUP BY sm_id, address, op
ORDER BY avg_latency DESC, ops DESC;
```

### A7. Evidence Transfer Table

| XiangShan Mechanism | Source Files / Docs | Problem Solved | Transferable GPGPU Abstraction | Skill Rule | Required Schema | Anti-Pattern to Avoid |
|---|---|---|---|---|---|---|
| `[CONFIRMED]` ChiselDB stores structured debug data in SQLite instead of waveforms | Official doc lines `117-119`, `195-243` | Waveforms are inefficient for row-shaped, repetitive events; SQL is easier to filter/aggregate | Per-event DB tables for warp/memory/scoreboard/sync state | Put query-driven event streams in DBs, not only in waves | Every table needs `stamp`, `site`, and family-specific columns | Dumping everything to a waveform and hoping GTKWave replaces structured queries |
| `[CONFIRMED]` `createTable` + auto `ID/STAMP/SITE` + `table.log(..., site, ...)` | Official doc lines `198-206`, `228-243`; `L2TLB.scala:1048-1089` | Makes row origin and timing explicit | Shared GPGPU tables with producer tagging | Require `site` on all shared tables | `*_LOG` tables with `stamp` and `site` columns | Tables without timestamps or without producer/source tags |
| `[CONFIRMED]` TL memory trace at L2/L3 edges | Official doc lines `126-142`; `SoC.scala:456-475`; `L2Top.scala:95-98`; `convert_tllog.sh:3-116` | Reconstructs memory traffic offline without full NoC/L2 waveforms | `MEMORY_TRANSACTION_LOG` with channel/opcode/param/source/sink/address/data fields | Memory-path features must emit protocol-visible rows | `MEMORY_TRANSACTION_LOG` | Free-form text logs for protocol traffic |
| `[CONFIRMED]` ROB writeback / load debug tables | `DbEntry.scala:28-61`; `Rob.scala:1456-1512` | Explains latency and memory behavior per instruction | `WARP_COMMIT_LOG` plus optional lane/memory timing slices | Commit-visible operations need a low-volume, analyzable log | `WARP_COMMIT_LOG` | Only aggregate IPC counters, no per-warp/per-op provenance |
| `[CONFIRMED]` DCache miss/access/bank-conflict tables | `DbEntry.scala:13-26`; `DCacheWrapper.scala:1393-1442`; `BankedDataArray.scala:40-46`, `615-642`; `MissQueue.scala:1404-1411` | Distinguishes miss type, access quality, and bank conflict sources | `MEMORY_TRANSACTION_LOG`, `COALESCER_LOG`, `CACHE_BANK_CONFLICT_LOG` | Memory/coalescer changes must ship miss/conflict attribution rows | `MEMORY_TRANSACTION_LOG`, `CACHE_BANK_CONFLICT_LOG`, `COALESCER_LOG` | Benchmark regressions without miss/conflict decomposition |
| `[CONFIRMED]` TLB / PTW / page-cache tables share schema and differentiate source with `SITE` | `MMUBundle.scala:1548-1575`; `L2TLB.scala:1041-1089` | Captures translation-path misses/hits with one table family | `TLB_EVENT_LOG` keyed by `event` and `site` | Translation or address-space features need their own trace rows | `TLB_EVENT_LOG` | Folding TLB effects into generic memory stalls with no source separation |
| `[CONFIRMED]` Prefetch tables cover trigger, target, sink, source type, and delta evolution | `DbEntry.scala:63-81`; `BasePrefecher.scala:89-94`; `PrefetcherWrapper.scala:323-331`; `L1PrefetchComponent.scala:489-532`, `732-749`; `Berti.scala:363-373`, `642-652`, `914-930` | Separates training, request generation, and dispatch behavior | `PREFETCH_EVENT_LOG` plus optional `COALESCER_LOG` joins | Prefetch features need both debug rows and acceptance/perf attribution queries | `PREFETCH_EVENT_LOG` | A prefetch enable bit without traceable prefetch outcomes |
| `[CONFIRMED]` Predictor / ICache / IFU traces are feature-gated and row-shaped | `Bpu.scala:639-657`; `MainBtb.scala:182-186`; `Tage.scala:663-670`; `Sc.scala:892-898`; `MicroTage.scala:436-440`; `ICacheMainPipe.scala:448-482`; `ICacheMissUnit.scala:293-358`; `IfuPerfAnalysis.scala:193-228` | Keeps frontend/pathology debug out of default fast path but available when needed | Optional GPGPU fetch / scheduler / reconvergence trace families | Heavy debug tables must be selectively gateable | `WARP_ISSUE_LOG`, optional fetch/scheduler tables | Always-on verbose tracing that destroys simulation throughput |
| `[CONFIRMED]` Constantin records gate row emission at runtime | `DCacheWrapper.scala:1393-1422`; `L2TLB.scala:287-291`, `1041-1089`; `IfuPerfAnalysis.scala:193-228` | Enables narrow debug capture without RTL rebuild | Runtime trace switches for failure windows or feature-specific probes | Each heavy table needs a runtime gate | `*_LOG` plus runtime knob metadata | Recompiling RTL just to turn one trace on |
| `[CONFIRMED]` `rolling.py` and `perfcct.py` prove DB outputs are expected to support plot/diff/correlation and lifetime reconstruction | `rolling.py:160-239`, `574-686`; `perfcct.py:81-99`, `164-185` | Connects event rows to performance attribution and failure localization | Ship SQL plus plot/diff/correlation tools with trace schemas | Every feature must define one debug query and one attribution query | `WARP_ISSUE_LOG`, `MEMORY_TRANSACTION_LOG`, rolling tables | Trace tables with no analysis path or only one-off manual queries |

### A8. Claim Index

| Claim ID | Claim | Status | Evidence | Confidence |
|---|---|---|---|---|
| `XS-CHDB-001` | XiangShan uses ChiselDB because structured data such as memory trace is awkward and inefficient in waveforms. | CONFIRMED | Official doc lines `117-119` | High |
| `XS-CHDB-002` | ChiselDB uses DPI-C and stores results in `sqlite3`. | CONFIRMED | Official doc lines `119-120` | High |
| `XS-CHDB-003` | `scripts/xiangshan.py --dump-db` affects both build-time `WITH_CHISELDB` and emulator runtime arguments. | CONFIRMED | `scripts/xiangshan.py:88-99`, `136-149`, `286-296`, `805`; `Makefile:166-169` | High |
| `XS-CHDB-004` | Top-level Scala initialization calls `ChiselDB.init(enableChiselDB && !envInFPGA)`. | CONFIRMED | `Top.scala:415-418`; `SimTop.scala:185-188` | High |
| `XS-CHDB-005` | TL memory trace schema includes protocol fields plus data lanes and timestamp. | CONFIRMED | Official doc lines `126-142` | High |
| `XS-CHDB-006` | TL loggers are attached at `MEM_L3`, `L3_L2_i`, `L2_L1D_i`, `L2_L1I_i`, and `L2_PTW_i`. | CONFIRMED | `SoC.scala:456-475`; `L2Top.scala:95-98` | High |
| `XS-CHDB-007` | XiangShan logs writeback timing and load debug rows in ROB-originated tables. | CONFIRMED | `DbEntry.scala:28-61`; `Rob.scala:1456-1512` | High |
| `XS-CHDB-008` | XiangShan logs DCache miss/access/bank-conflict rows with explicit debug gates. | CONFIRMED | `DCacheWrapper.scala:1393-1442`; `BankedDataArray.scala:615-642`, `952-980` | High |
| `XS-CHDB-009` | XiangShan logs TLB/PTW/page-cache activity with shared schemas and `SITE` tags. | CONFIRMED | `MMUBundle.scala:1548-1575`; `L2TLB.scala:1041-1089` | High |
| `XS-CHDB-010` | Prefetch tracing covers trigger, request, target, and delta evolution. | CONFIRMED | `PrefetcherWrapper.scala:323-331`; `L1PrefetchComponent.scala:489-532`, `732-749`; `Berti.scala:363-373`, `642-652`, `914-930` | High |
| `XS-CHDB-011` | `rolling.py` expects rolling tables named `<perf>_rolling_<hart>` with `XAXISPT`, `YAXISPT`, and `STAMP`. | CONFIRMED | `rolling.py:28`, `160-239` | High |
| `XS-CHDB-012` | The exact semantics of `basicDB` versus `ChiselDB.init(false)` cannot be proven from the local snapshot because backend implementation is missing. | MISSING | empty `utility/`; `Top.scala:415-418`; official doc lines `198-206` | Medium |
| `XS-CHDB-013` | The raw TL table name may be `TL_LOG` or `TLLOG`; the snapshot contains conflicting evidence. | CONFLICTED | official doc lines `126-142`; `l2DB_helper.py:42-43` | Medium |
| `XS-CHDB-014` | A GPGPU skill should require table + trigger + debug query + perf query for every memory/scheduler/sync/atomic feature. | INFERRED | Cross-cutting evidence from producers and scripts in this report | Medium |

### A9. Missing / Conflicted Evidence

- `MISSING`: `ref_submodule/xiangshan/utility/` is empty, so `ChiselDB` internals, generated DDL, and TL logger backend code are not inspectable.
- `MISSING`: no local producer for `LifeTimeCommitTrace` was found; only the consumer contract is visible in `perfcct.py`.
- `MISSING`: no local producer for rolling tables was found; only the consumer contract is visible in `rolling.py`.
- `CONFLICTED`: official docs use `TL_LOG`; helper script uses `TLLOG`.
- `UNCERTAIN`: exact flattened SQL column names for nested BPU bundles are not expanded here because the trace-family existence, gates, and role are the planning-relevant facts.

### A10. Full Quality Gate

Overall status: `PARTIAL`

Evidence gate:

| Check | Result | Notes |
|---|---|---|
| Scope declared | PASS | Files read, skipped, and focus/non-goals are stated |
| Planner focus answered | PASS | All seven extraction questions are answered |
| Evidence attached | PASS | Claims cite file paths or official docs |
| Claim status used | PASS | `CONFIRMED`, `INFERRED`, `UNCERTAIN`, `CONFLICTED`, `MISSING` used |
| Contradictions reported | PASS | `TL_LOG` vs `TLLOG` recorded |
| Missing contracts reported | PASS | Missing backend and producer-side gaps recorded |
| Handoff actionable | PASS | Next actions are concrete and skill-facing |

Readability gate:

| Check | Result | Notes |
|---|---|---|
| Handoff length | PASS | Part A is compact |
| Findings capped | PASS | Top findings kept short |
| Tables limited | PASS | Full tables are in appendix |
| Empty sections removed | PASS | No mechanical filler |
| Decision relevance | PASS | Report stays on structured trace / SQL analysis |
| Appendix separation | PASS | Part A is compact; details moved below |

Repository extra gate:

| Topic | Status | Notes |
|---|---|---|
| ISA semantics | not applicable | Non-goal for this shard |
| instruction encoding | not applicable | Non-goal for this shard |
| decode path | not applicable | Non-goal for this shard |
| PC / warp state | inferred | Needed only as future `WARP_COMMIT_LOG` schema field |
| active mask | inferred | Included in proposed commit schema |
| SIMT divergence | inferred | Relevant only to future scheduler/failure tables |
| register file | not applicable | Not studied here |
| scoreboard / hazards | inferred | Proposed `SCOREBOARD_LOG`; no XiangShan equivalent read here |
| issue / execute / writeback | confirmed | `InstTable`, `LoadDebugTable`, `perfcct.py` consumer contract |
| memory coalescing | inferred | XiangShan memory/bank/prefetch traces transfer to coalescer attribution |
| shared memory | not applicable | Not present in XiangShan CPU cache shard |
| barrier semantics | inferred | Proposed GPGPU rule only |
| CSR / DCR / config state | confirmed | Trace enablement/config path confirmed |
| launch protocol | not applicable | Out of scope |
| kernel arguments | not applicable | Out of scope |
| grid/block/warp mapping | inferred | Added only in proposed GPGPU schemas |
| CModel / golden model | not applicable | Not the focus of this shard |
| trace diff / compare path | inferred | `perfcct.py` and commit-style tables inform failure slicing, but DiffTest itself is another pass |
| tests and coverage | not applicable | No ChiselDB-specific tests inspected here |
| synthesis / FPGA / PPA evidence | not applicable | Out of scope |

## Quality Gate

- Overall status: PARTIAL
- Evidence status: PARTIAL
- Readability status: PASS
- Safe for GPT-5.5 planning: yes, with caveats
- Full appendix generated: yes
- Biggest evidence gap: `utility.ChiselDB` / `utility.TLLogger` backend source and producer-side definitions for `LifeTimeCommitTrace` and rolling tables are missing
- Biggest readability issue: the exact flattened column names for complex nested BPU bundles were intentionally not expanded because they are not planning-critical for this GPGPU shard
- Required next read: initialize or provide `ref_submodule/xiangshan/utility` and the producer for `LifeTimeCommitTrace`
