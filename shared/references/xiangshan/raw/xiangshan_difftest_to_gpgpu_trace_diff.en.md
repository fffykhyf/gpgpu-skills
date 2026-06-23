# Repository Architecture Report

## Part A. Human Handoff

### 0. Metadata

- Mode: repository
- Depth: deep
- Output profile: model-evidence
- Repo / subsystem: XiangShan DiffTest -> GPGPU trace diff
- Branch / commit if available: `ref_submodule/xiangshan` `5ff19c2`; `ref_submodule/xiangshan-nemu` `75d0019`
- Files read: `ref/skillref/xiangshan.md` sections 0-3, 5, 12; `ref_submodule/xiangshan/Makefile`; `ref_submodule/xiangshan/build.mill`; `ref_submodule/xiangshan/src/main/scala/top/{Top.scala,ArgParser.scala,XSNoCTop.scala}`; `ref_submodule/xiangshan/src/main/scala/xiangshan/{Parameters.scala,Bundle.scala}`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/{BackendParams.scala,rob/Rob.scala,datapath/DataPath.scala,fu/CSR.scala,fu/NewCSR/NewCSR.scala,rename/RenameTable.scala}`; `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/{Bundles.scala,MemBlock.scala,sbuffer/Sbuffer.scala,pipeline/AtomicsUnit.scala,lsqueue/NewStoreQueue.scala}`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/{mmu/TLB.scala,mmu/L2TLB.scala,dcache/mainpipe/MissQueue.scala,dcache/Uncache.scala}`; `ref_submodule/xiangshan/src/main/scala/xiangshan/frontend/icache/ICacheMissUnit.scala`; `ref_submodule/xiangshan-nemu/src/cpu/difftest/{dut.c,ref.c}`; `ref_submodule/xiangshan-nemu/src/isa/riscv64/difftest/{dut.c,ref.c}`; official DiffTest docs at `https://docs.xiangshan.cc/zh-cn/latest/tools/difftest/`
- Files skipped: deep PDF reading of `ref/xiangshan.pdf`; local `ref_submodule/xiangshan/difftest/**` is empty and could not be read
- Entry points inspected: `TopMain`, `DifftestModule.parseArgs`, `DiffInstrCommit`/`Diff*Event` probe sites, NEMU `init_difftest`, `difftest_step`, exported ref-side API
- Focus: development-loop infrastructure only; probe types, checked states, compression/replay, DUT/reference synchronization, mismatch packaging
- Questions answered: all 9 extraction questions, with `MISSING` called out where the empty local `difftest` submodule blocks exact confirmation
- Appendix: inline in this artifact
- Confidence: Medium

### 1. One-Paragraph Answer

XiangShan exposes a two-tier trace-diff contract that transfers cleanly to a GPGPU skill: a default `AlwaysBasicDiff` layer exports architectural commit, control state, rename maps, physical register state, and a few synchronization events, while `EnableDifftest` adds transaction-heavy probes for loads, stores, atomics, refills, TLBs, MMIO, and richer commit metadata such as `pc`, `instr`, and queue indices (`ref_submodule/xiangshan/src/main/scala/xiangshan/Parameters.scala:524-542`, `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1575-1655`). Standard non-FPGA debug builds enable full DiffTest by default (`ref_submodule/xiangshan/Makefile:205-216`), and the reference side is a DLL-style NEMU API exporting `memcpy`, `regcpy`, `exec`, interrupt injection, skip/catch-up, query/status, and sync helpers (`ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c:25-131`, `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:87-367`). The main evidence gap is structural, not interpretive: the local `ref_submodule/xiangshan/difftest` submodule is empty, so exact bundle type definitions, `--difftest-config` parser logic, `supportsDelta` / `updateDependency`, replay token format, and software checker internals remain `MISSING`.

### 2. Top Architecture Findings

1. `CONFIRMED`: XiangShan splits probe generation into `AlwaysBasicDiff` and `EnableDifftest`, with defaults `true` and `false` respectively, but the repo `Makefile` adds `--enable-difftest` for normal debug builds. Evidence: `ref_submodule/xiangshan/src/main/scala/xiangshan/Parameters.scala:524-542`, `ref_submodule/xiangshan/src/main/scala/top/ArgParser.scala:122-129`, `ref_submodule/xiangshan/Makefile:205-216`.
2. `CONFIRMED`: `DiffInstrCommit` is instantiated in both modes, but only its basic commit/writeback fields are driven unconditionally; `pc`, `instr`, `robIdx`, `lqIdx`, `sqIdx`, `isLoad`, and `isStore` are assigned only when `EnableDifftest` is set. Evidence: `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1594-1655`.
3. `CONFIRMED`: XiangShan exports not just commit state but also load/store/atomic/MMIO/refill/TLB/store-buffer/control-side synchronization events, plus rename-table and physical-register snapshots. Evidence: `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/sbuffer/Sbuffer.scala:765-776`, `:892-1010`; `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/pipeline/AtomicsUnit.scala:588-606`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/mmu/TLB.scala:761-787`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/mmu/L2TLB.scala:663-704`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/datapath/DataPath.scala:337-370`, `:470-474`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rename/RenameTable.scala:185-348`.
4. `CONFIRMED`: Control-state sync is broader than classic CSR diff: NewCSR also emits trigger CSR state, FP CSR state, non-register interrupt pending, HPM overflow, AIA sync, and custom L2 flush sync. Evidence: `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1653-1809`.
5. `CONFIRMED`: REF stepping is instruction-synchronous by default (`exec(1)` then `regcpy`+`checkregs`), but XiangShan/NEMU also support skip-ref, skip-dut catch-up, interrupt injection, guided execution, query/status, and memory / non-register side-channel sync. Evidence: `ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c:38-178`, `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:166-367`, `ref_submodule/xiangshan-nemu/src/isa/riscv64/difftest/ref.c:27-127`, `:196-208`, `:249-263`, `:291-300`.
6. `CONFIRMED` plus `MISSING`: Batch, Squash, Delta, NonBlock, and Replay are well documented, but the exact local implementation and whitelist logic are absent because `ref_submodule/xiangshan/difftest` is uninitialized. Evidence: official docs sections `Batch`, `Squash/Delta`, `NonBlock`, `Replay` at `https://docs.xiangshan.cc/zh-cn/latest/tools/difftest/`; missing local directory at `ref_submodule/xiangshan/difftest`.

### 3. Minimal Architecture Map

| Module / layer | Role in XiangShan DiffTest | Why it transfers to GPGPU |
|---|---|---|
| `Makefile`, `ArgParser.scala`, `Top.scala`, `XSNoCTop.scala`, `build.mill` | Enable flags, top wrapping, resource packaging, checker wiring | Defines how a design turns probes on, bundles them, and ships the reference `.so` and trace infrastructure |
| `backend/rob/Rob.scala` | Commit, load, trap probes; commit-side debug buses | Natural template for `WarpInstrCommit` and mismatch localization around commit order |
| `backend/datapath/DataPath.scala`, `backend/rename/RenameTable.scala` | Full physical-register and logical-to-physical shadow state | Shows when to diff whole machine snapshots versus per-event writebacks |
| `backend/fu/{CSR.scala,NewCSR/NewCSR.scala}` | Control-state, interrupt, overflow, and side-channel sync | Template for GPGPU control-state and counter-overflow synchronization |
| `mem/*`, `cache/*` | Store/load/atomic/MMIO/refill/TLB probes and store-buffer shadowing | Template for `MemoryTransaction`, cache refill, TLB, and ordering-sensitive trace events |
| `xiangshan-nemu/src/cpu/difftest`, `src/isa/riscv64/difftest` | REF DLL exports, step loop, skip/catch-up, register compare | Template for the GPGPU golden-model API and compare-loop discipline |
| Official DiffTest docs | Compression, replay, perf/query, trace-only iteration | Template for speed vs. debug tradeoffs and replay safety rules |

### 4. Top State / Interface Contracts

| Contract | Status | Summary | Evidence |
|---|---|---|---|
| Basic architectural sync contract | CONFIRMED | Basic mode exports commit/writeback, trap summary, CSR/debug state, rename maps, physical reg state, and LR/SC success. | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1575-1683`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/datapath/DataPath.scala:337-370`, `:470-474`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rename/RenameTable.scala:185-348`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1653-1809`; `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/pipeline/AtomicsUnit.scala:601-606` |
| Full transaction sync contract | CONFIRMED | Full mode adds commit `pc`/`instr`/queue indices, load/store/atomic/MMIO/refill/TLB probes, and store-buffer visibility. | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1635-1655`; `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/sbuffer/Sbuffer.scala:765-776`, `:892-1010`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/dcache/mainpipe/MissQueue.scala:1414-1437`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/mmu/TLB.scala:761-787`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/mmu/L2TLB.scala:663-704`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/dcache/Uncache.scala:439-447` |
| REF DLL contract | CONFIRMED | REF side must support memory copy, register copy, one-step exec, interrupt injection, optional query/status, store-commit, and side-channel sync. | `ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c:25-131`; `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:87-367` |
| Compression / replay contract | UNCERTAIN | Docs confirm Batch, Squash, Delta, NonBlock, Replay semantics; exact local whitelist and token logic are missing. | `https://docs.xiangshan.cc/zh-cn/latest/tools/difftest/` sections `Batch`, `Squash/Delta`, `NonBlock`, `Replay`; missing `ref_submodule/xiangshan/difftest` |
| Mismatch attribution contract | INFERRED | A useful mismatch package must carry event type, state field, instruction or token range, cycle, and suspected module window. | Docs `Replay` and `Trace 调试支持` at `https://docs.xiangshan.cc/zh-cn/latest/tools/difftest/`; compare loop at `ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c:143-178`; register diff walker at `ref_submodule/xiangshan-nemu/src/isa/riscv64/difftest/ref.c:27-117` |

### 5. Top Risks / Missing Contracts

1. `MISSING`: `ref_submodule/xiangshan/difftest` is empty, so exact bundle class definitions, C++ DPI glue, replay/token code, and parser logic are absent locally.
2. `MISSING`: The exact local mapping from `--difftest-config` letters to generated hardware behavior is not source-visible here; only `Makefile` use and official docs are available.
3. `MISSING`: Official docs describe `supportsDelta` and `updateDependency`, but the actual bundle whitelist and dependency table are not locally inspectable.
4. `UNCERTAIN`: Exact software-side mismatch print format beyond register-by-register diffs is not locally anchored because the XiangShan-side checker lives in the missing submodule.
5. `UNCERTAIN`: Exact TLB / refill / store event bundle widths and any additional fields beyond the locally assigned subset remain unknown without the missing bundle definitions.

### 6. Evidence Snapshot

| Claim ID | Status | Short claim | Evidence |
|---|---|---|---|
| `XS-DIFF-001` | CONFIRMED | `AlwaysBasicDiff` defaults to `true`; `EnableDifftest` defaults to `false`. | `ref_submodule/xiangshan/src/main/scala/xiangshan/Parameters.scala:524-542` |
| `XS-DIFF-002` | CONFIRMED | Standard non-FPGA debug builds add `--enable-difftest`. | `ref_submodule/xiangshan/Makefile:205-216` |
| `XS-DIFF-003` | CONFIRMED | `DiffInstrCommit` basic fields are always emitted when basic diff is on. | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1594-1634` |
| `XS-DIFF-004` | CONFIRMED | `pc`, `instr`, queue indices, and load/store flags for commit are full-mode-only assignments. | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1635-1655` |
| `XS-DIFF-005` | CONFIRMED | Memory-side probes include store, store-buffer, atomic, refill, TLB, and uncache/MMIO events. | `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/sbuffer/Sbuffer.scala:765-776`, `:892-1010`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/mmu/TLB.scala:761-787`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/dcache/Uncache.scala:439-447` |
| `XS-DIFF-006` | CONFIRMED | NewCSR emits non-register interrupt pending and HPM overflow sync events. | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1767-1792` |
| `XS-DIFF-007` | CONFIRMED | REF stepping is `exec(1)` followed by `regcpy` and register comparison unless skip logic is active. | `ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c:143-178` |
| `XS-DIFF-008` | CONFIRMED | REF side exports `difftest_memcpy`, `difftest_regcpy`, `difftest_exec`, `difftest_status`, query and sync helpers. | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:87-367` |
| `XS-DIFF-009` | CONFIRMED | Docs define Batch, Squash, Delta, NonBlock, Replay as the main performance optimizations. | `https://docs.xiangshan.cc/zh-cn/latest/tools/difftest/` sections `Batch`, `Squash/Delta`, `NonBlock`, `Replay` |
| `XS-DIFF-010` | MISSING | Local `supportsDelta` / `updateDependency` implementation is unavailable. | empty `ref_submodule/xiangshan/difftest`; docs mention `Preprocess.scala` / `Difftest.scala` only |

### 7. Main Architect Next Actions

1. Define the GPGPU split between `basic trace diff` and `full transaction diff` explicitly, matching XiangShan's field-level gating, not just per-probe gating.
2. Use `WarpInstrCommit`, `LaneRegWriteback`, and `MemoryTransaction` as first-class schemas, then add separate side-channel sync events for trap, interrupt, counter overflow, and flush completion.
3. Treat compression conservatively until a GPGPU-side whitelist exists: only delta whole-state snapshots; never silently compress side-effecting transactions or asynchronous sync events.
4. Add a required mismatch package schema before implementing replay, so every future feature already knows its failure payload and trace dependencies.
5. If exact compression rules are needed later, initialize the matching XiangShan `difftest` submodule or inspect the matching remote commit for `Difftest.scala`, `Preprocess.scala`, and the checker path.

### 8. Compact Quality Gate

- Evidence status: PARTIAL
- Readability status: PASS
- Safe for GPT-5.5 planning: yes, with caveats
- Full appendix generated: inline
- Biggest evidence gap: local `ref_submodule/xiangshan/difftest` is empty
- Required next read: matching XiangShan `difftest` source (`Difftest.scala`, `Preprocess.scala`, replay/checker code)

## Part B. Evidence Appendix

### A1. Source-of-Truth Hierarchy

| Layer | Files | Role | Reliability | Notes |
|---|---|---|---|---|
| Planner / task rules | `ref/skillref/xiangshan.md` sections 0-3, 5, 12 | Defines pass scope, boundaries, output requirements | High | Governs this shard directly |
| Project rules | `AGENTS.md` plus repo instructions | Requires Superpowers and development-loop focus | High | Already followed |
| Local RTL integration | `Makefile`, `build.mill`, `Top.scala`, `ArgParser.scala`, `XSNoCTop.scala` | Shows how DiffTest is enabled and integrated into XiangShan | High | Local, commit-pinned |
| Local probe insertion | `Rob.scala`, `DataPath.scala`, `RenameTable.scala`, `CSR.scala`, `NewCSR.scala`, `mem/*`, `cache/*` | Shows where probes are inserted and which fields are driven | High | Local, commit-pinned |
| Local REF API | `xiangshan-nemu/src/cpu/difftest/*`, `src/isa/riscv64/difftest/*` | Shows reference DLL API and comparison loop | High | Local, commit-pinned |
| Official docs | `https://docs.xiangshan.cc/zh-cn/latest/tools/difftest/` | Only trustworthy source for Batch/Squash/Delta/Replay overview in this shard | Medium-High | High-level only; not commit-pinned |
| Missing local implementation | `ref_submodule/xiangshan/difftest` | Expected local source for bundle defs, parser, replay/checker | MISSING | Empty directory |

### A2. Corpus Inventory and Missing Boundary

- `ref_submodule/xiangshan` commit is `5ff19c2`.
- `ref_submodule/xiangshan-nemu` commit is `75d0019`.
- `ref/xiangshan.pdf` exists and has 561 pages, but was not deep-read because this shard is fully constrained to DiffTest and NEMU.
- `ref_submodule/xiangshan/difftest` is present as a directory but empty locally.
- `build.mill` expects the `difftest` submodule to exist as a Mill module and packages its tracked files into resources (`ref_submodule/xiangshan/build.mill:102-108`, `:124-214`).
- `Top.scala` relies on `DifftestModule` and `DifftestModule.collect`, and `ArgParser.scala` delegates argument parsing to `DifftestModule.parseArgs` (`ref_submodule/xiangshan/src/main/scala/top/Top.scala:409-444`, `ref_submodule/xiangshan/src/main/scala/top/ArgParser.scala:241-252`).

### A3. XiangShan Probe Catalog

#### A3.1 Basic or always-on architectural sync

| Probe / state | Gate | Locally confirmed fields | Source anchors | GPGPU transfer |
|---|---|---|---|---|
| `DiffInstrCommit` basic subset | `EnableDifftest || AlwaysBasicDiff` | `coreid`, `index`, `valid`, `skip`, `isRVC`, `rfwen`, `fpwen`, `vecwen`, `v0wen`, `wpdest`, `wdest`, `otherwpdest`, `nFused` | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1594-1634` | Base `WarpInstrCommit` plus architectural writeback summary |
| `DiffTrapEvent` basic subset | `EnableDifftest || AlwaysBasicDiff` | `coreid`, `hasTrap`, `cycleCnt`, `instrCnt`, `hasWFI`; `code` and `pc` are full-mode-only | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1659-1683` | Trap summary / timeout / WFI state event |
| `DiffArchEvent` | `EnableDifftest || AlwaysBasicDiff` | Exception or interrupt valid, cause, exception PC; `exceptionInst` only when full mode is enabled | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:1558-1569`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1620-1665` | Trap / interrupt sync contract |
| `DiffCSRState` | `EnableDifftest || AlwaysBasicDiff` | Privilege mode plus `mstatus/sstatus/mepc/sepc/mtval/stval/mtvec/stvec/mcause/scause/satp/mip/mie/mscratch/sscratch/mideleg/medeleg` | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:1571-1593`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1672-1692` | Control-state sync event |
| `DiffHCSRState` | `EnableDifftest || AlwaysBasicDiff` | Virtualization / hypervisor control state | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:1595-1615`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1721-1739` | Optional advanced control-state sync |
| `DiffDebugMode` | `EnableDifftest || AlwaysBasicDiff` | `debugMode`, `dcsr`, `dpc`, `dscratch0`, `dscratch1` | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:1617-1625`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1693-1699` | Debug-mode side channel |
| `DiffVecCSRState` | `EnableDifftest || AlwaysBasicDiff` | `vstart`, `vxsat`, `vxrm`, `vcsr`, `vl`, `vtype`, `vlenb` (NewCSR only) | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:1627-1635`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1707-1716` | Example of accelerator/vector control sync |
| `DiffFpCSRState` | `EnableDifftest || AlwaysBasicDiff` | `fcsr` | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1717-1720` | FP / special-unit control sync |
| `DiffTriggerCSRState` | `EnableDifftest || AlwaysBasicDiff` | `tselect`, `tdata1`, `tinfo` | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1701-1706` | Optional debug-trigger state |
| `DiffNonRegInterruptPendingEvent` | `EnableDifftest || AlwaysBasicDiff` | Pending external/timer/software/AIA interrupt lines plus local-counter-overflow request | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1767-1784` | GPGPU non-register side-channel sync event |
| `DiffMhpmeventOverflowEvent` | `EnableDifftest || AlwaysBasicDiff` | Overflow-valid pulse plus overflow vector | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1785-1792` | Counter-overflow sync event |
| `DiffSyncAIAEvent` | `EnableDifftest || AlwaysBasicDiff` | `mtopei`, `stopei`, `vstopei`, `hgeip` | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1793-1804` | Asynchronous external fabric sync |
| `DiffSyncCustomMflushpwrEvent` | `EnableDifftest || AlwaysBasicDiff` | `l2FlushDone` edge | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1806-1809` | Flush / barrier completion sync |
| `DiffArchIntRenameTable` | `EnableDifftest || AlwaysBasicDiff` | Current logical-int to physical-int mapping | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rename/RenameTable.scala:261-266` | Whole-map architectural rename snapshot |
| `DiffArchFpRenameTable` | `EnableDifftest || AlwaysBasicDiff` | Current logical-fp to physical-fp mapping | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rename/RenameTable.scala:300-306` | Same pattern for FP / predicate / special files |
| `DiffArchVecRenameTable` | `EnableDifftest || AlwaysBasicDiff` | Split vector/v0 physical mapping sequence | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rename/RenameTable.scala:337-348` | Whole-map vector register alias state |
| `DiffPhyIntRegState` | `EnableDifftest || AlwaysBasicDiff` | Full integer physical register file contents | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/datapath/DataPath.scala:337-346` | Whole-state snapshot; strong delta candidate |
| `DiffPhyFpRegState` | `EnableDifftest || AlwaysBasicDiff` | Full FP physical register file contents | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/datapath/DataPath.scala:366-370` | Same |
| `DiffPhyVecRegState` | `EnableDifftest || AlwaysBasicDiff` | Split vector physical register contents | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/datapath/DataPath.scala:470-474` | Same |
| `DiffLrScEvent` | `EnableDifftest || AlwaysBasicDiff` | `coreid`, `valid`, `success` | `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/pipeline/AtomicsUnit.scala:601-606` | Small ordering / atomic side channel |

#### A3.2 `EnableDifftest`-only or full-mode-only transaction sync

| Probe / state | Gate | Locally confirmed fields | Source anchors | GPGPU transfer |
|---|---|---|---|---|
| `DiffInstrCommit` full subset | `EnableDifftest` | `pc`, `instr`, `robIdx`, `lqIdx`, `sqIdx`, `isLoad`, `isStore` | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1635-1655` | Full `WarpInstrCommit` context |
| `DiffLoadEvent` | `EnableDifftest` | `coreid`, `index`, `valid`, `paddr`, `opType`, `isAtomic`, `isLoad`, `isVLoad` | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1644-1655` | Load-side `MemoryTransaction` or `MemoryResponse` event |
| `DiffStoreEvent` | `EnableDifftest` | `coreid`, `index`, `valid`, `wLine`, `vecNeedSplit`, `eew`, `offset`, `pc`, `robidx`, `addr`, `data`, `highData`, `mask` | `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/sbuffer/Sbuffer.scala:947-1010` | Store-side `MemoryTransaction` with replay metadata |
| `DiffSbufferEvent` | `EnableDifftest` | `coreid`, `index`, `valid`, `addr`, `data`, `mask` | `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/sbuffer/Sbuffer.scala:765-776`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/dcache/mainpipe/MissQueue.scala:1424-1437` | Store-buffer visibility / refill-to-store merge trace |
| `DiffAtomicEvent` | `EnableDifftest` | `coreid`, `valid`, `addr`, `data`, `mask`, `cmp`, `fuop`, `out` | `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/pipeline/AtomicsUnit.scala:588-599` | Atomic transaction schema |
| `DiffCMOInvalEvent` | `EnableDifftest` | `coreid`, `valid`, `addr` | `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/lsqueue/NewStoreQueue.scala:1288-1297` | Cache-management / invalidate event |
| `DiffUncacheMMStoreEvent` | `EnableDifftest` | `coreid`, `index`, `valid`, `addr`, `data`, `mask` | `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/dcache/Uncache.scala:439-447` | MMIO / side-effecting store event |
| `DiffRefillEvent` | `EnableDifftest` | `coreid`, `index`, `valid`, `addr`, `data`, `mask`; observed indices: `0` icache, `1` dcache miss queue, `2` L2TLB/PTW refill | `ref_submodule/xiangshan/src/main/scala/xiangshan/frontend/icache/ICacheMissUnit.scala:369-377`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/dcache/mainpipe/MissQueue.scala:1414-1422`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/mmu/L2TLB.scala:663-676` | Cache / translation refill event |
| `DiffL1TLBEvent` | `EnableDifftest` | `coreid`, `valid`, `index`, `vpn`, `ppn`, `satp`, `vsatp`, `hgatp`, `s2xlate` | `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/mmu/TLB.scala:761-787` | Translation-compare event |
| `DiffL2TLBEvent` | `EnableDifftest` | `coreid`, `valid`, `index`, `vpn`, `pbmt`, `g_pbmt`, `ppn[]`, `valididx[]`, `pteidx[]`, `perm`, `level`, `pf`, `satp`, `vsatp`, `hgatp`, `gvpn`, `g_perm`, `g_level`, `s2ppn`, `gpf`, `s2xlate` | `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/mmu/L2TLB.scala:678-704` | Rich translation-event schema |

### A4. Internal Shadow Buses that Feed Diff Logic

These are local XiangShan helper bundles, not external DiffTest bundles. They matter because a GPGPU skill often needs the same split between internal shadow buses and exported compare events.

| Helper bundle | Locally confirmed fields | Source anchors | Transfer lesson |
|---|---|---|---|
| `DiffCommitIO` | `isCommit`, `commitValid[]`, `info[]` | `ref_submodule/xiangshan/src/main/scala/xiangshan/Bundle.scala:342-347` | Keep a local architectural-commit shadow bus separate from the external compare event |
| `DiffVlCommitBundle` | `commitValid[]`, `pdestVl[]` | `ref_submodule/xiangshan/src/main/scala/xiangshan/Bundle.scala:349-352` | Specialized helper buses are acceptable if they simplify event reconstruction |
| `DiffStoreIO` | `diffInfo[]`, `cacheableStore[]`, `ncStore` | `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/Bundles.scala:425-438` | Transaction export often needs a local aggregation bus first |
| `ToSbufferDifftestInfoBundle` | `uop`, `start`, `offset` | `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/Bundles.scala:412-417` | Export enough local context to reconstruct split or replayable vector / coalesced stores |
| `MemBlock` difftest mux | Selects vector-store or LSQ-originated diff info into `sbuffer.io.diffStore` | `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/MemBlock.scala:1131-1148` | Centralize event muxing near the last point before side effects |

### A5. NEMU Reference API and Step-Sync Contract

| API / behavior | Local anchor | Purpose in XiangShan | Transferable GPGPU contract | Status |
|---|---|---|---|---|
| `difftest_memcpy` / `difftest_memcpy_init` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:87-105` | Copy DUT memory into REF or back | Bulk initialize or restore golden memory | CONFIRMED |
| `difftest_regcpy` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:127-139`; `ref_submodule/xiangshan-nemu/src/isa/riscv64/difftest/ref.c:196-208` | Copy register state DUT<->REF | Snapshot architectural state at boundaries or on skip | CONFIRMED |
| `difftest_exec` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:180-182` | Advance REF by `n` instructions | Default golden stepping primitive | CONFIRMED |
| `difftest_step` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c:143-178` | `exec(1)` then `regcpy` and compare, unless skip logic is active | Base compare loop | CONFIRMED |
| `difftest_skip_ref` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c:44-57` | Copy DUT reg state directly into REF for uncomparable instructions | Allow explicit `skip_diff` holes | CONFIRMED |
| `difftest_skip_dut` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c:59-71` | Let REF run ahead, wait for DUT `npc` to catch up | Needed for packed / replay-group execution | CONFIRMED |
| `difftest_raise_intr` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:230-240`; `ref_submodule/xiangshan-nemu/src/isa/riscv64/difftest/ref.c:279-300` | Inject interrupt into REF | Golden control-side sync | CONFIRMED |
| `difftest_raise_nmi_intr` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:243-247` | Sync NMI pending state | Side-channel sync event | CONFIRMED |
| `difftest_raise_mhpmevent_overflow` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:255-259` | Sync counter-overflow side effects | Counter-overflow sync | CONFIRMED |
| `difftest_non_reg_interrupt_pending` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:261-273` | Sync interrupt-pending lines not represented only by regular CSRs | Non-register async sync | CONFIRMED |
| `difftest_sync_aia` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:311-318` | Sync AIA state | External fabric / interrupt fabric sync | CONFIRMED |
| `difftest_sync_custom_mflushpwr` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:321-323` | Sync custom flush completion | Flush / barrier-like side channel | CONFIRMED |
| `difftest_store_commit` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:166-172` | Export store-commit checking hook | Golden memory-ordering hook | CONFIRMED |
| `difftest_guided_exec` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:197-216` | Optional guided execution for replay/lightqs | Replay assist path | CONFIRMED |
| `difftest_query_ref` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:224-227` | Export typed query hook | Offline or replay query API | CONFIRMED |
| `difftest_status` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:184-195` | Return REF status code | Golden-model health / halt API | CONFIRMED |
| `init_difftest` + `dlsym` binding | `ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c:78-131` | Binds the `.so`, copies memory, copies registers, starts compare mode | Final golden-model ABI boundary | CONFIRMED |

### A6. Batch / Squash / Delta / NonBlock / Replay

Local source for the implementation is missing; this section is doc-backed and should be treated as architectural guidance, not a commit-pinned code reading.

| Mechanism | Official doc anchor | What it accelerates | Debug cost | Safe GPGPU transfer rule |
|---|---|---|---|---|
| Batch | DiffTest docs section `Batch` | Reduces communication call count by packing many bundles into fixed-size packets | Minimal if metadata is correct; parser complexity rises | Safe for any event class if per-packet metadata can recover type, width, and ordering |
| Squash | DiffTest docs section `Squash/Delta` | Fuses multiple same-type updates, e.g. multiple commits into one fused submission | Loses per-instruction granularity unless replay exists | Only squash events whose combined final state is sufficient for comparison; carry `n_fused` plus token / stamp range |
| Delta | DiffTest docs section `Squash/Delta` | Drops unchanged elements for high-repeat bundles such as whole-state register arrays | Software must reconstruct cached full state; whitelist is critical | Restrict to cached snapshot-style bundles such as regfiles, rename maps, or counters; never use blindly on side effects |
| NonBlock | DiffTest docs section `NonBlock` | Hides lockstep blocking latency | Mismatch appears later; requires buffering and backpressure | Safe only if hardware and software each keep lossless queues and mismatches can still be attributed by token/range |
| Replay | DiffTest docs section `Replay` | Restores instruction-level debug precision after Squash / NonBlock | Requires token tracking and reference-state restore | Mandatory whenever Squash can enlarge the failing window beyond one architecturally meaningful event |

#### A6.1 Compression / replay safety rules

| Event class | Batch | Squash | Delta | Must remain immediate / fully ordered | Basis |
|---|---|---|---|---|---|
| `WarpInstrCommit` | yes | yes, if `n_fused_or_replay_group` and token/stamp range are preserved | no, not as a per-event record | yes for ordering | Docs explicitly cite commit fusion with `nfused`; local `DiffInstrCommit` carries fused count and commit ordering context |
| `LaneRegWriteback` stream | yes | usually no; keep as event stream or derive from commit | yes for snapshot form | no | Docs cite regfile-like state as high-repeat delta candidates; local XiangShan exports full physical reg arrays |
| Rename / regfile snapshots | yes | optional, but usually unnecessary | yes | no | Docs cite delta on repeated bundle elements; local XiangShan exports whole-state arrays/maps |
| Cacheable memory transactions | yes | `UNCERTAIN` in XiangShan local code; use conservative mode in GPGPU | no | yes | Docs warn that memory values needed for REF alignment must be fully synchronized, especially in multi-agent cases |
| MMIO / uncache MM stores | yes | no | no | yes | Docs explicitly list MMIO / external-device accesses as non-fusible sync points; local `DiffUncacheMMStoreEvent` exists |
| Trap / exception / interrupt side channels | yes | no | no | yes | Docs explicitly list exception and interrupt classes as non-fusible sync points; local side-channel events exist |
| Atomics / fence-like ordering events | yes | no unless replay + strict token semantics exist | no | yes | GPGPU transfer is conservative because these events change global visible ordering |
| Refill / TLB translation events | yes | usually no | `UNCERTAIN` | keep per-event order | XiangShan exports them as event streams, not snapshots |

#### A6.2 Conservative GPGPU rule

Use compression only after the event owner writes down:

1. The exact compare state that software reconstructs.
2. The token / stamp ordering used across compressed and uncompressed events.
3. The rollback or checkpoint method needed for replay.
4. The event classes that may never be delta-dropped.

If any of the four are missing, do not compress that event class.

### A7. GPGPU Transfer Contract

#### A7.1 Required rule

Every RTL feature must define:

1. golden-model behavior
2. RTL event probe
3. trace schema
4. comparison rule
5. compression / replay safety rule
6. mismatch report
7. replay/debug strategy

#### A7.2 Canonical event schemas

```yaml
event: WarpInstrCommit
fields:
  cycle: uint64
  sm_id: uint16
  warp_id: uint16
  commit_index: uint16
  pc: uint64
  instr: uint32
  active_mask: uint64
  predicate_mask: uint64
  n_fused_or_replay_group: uint16
  skip_diff: bool
  is_rvc_or_compact: bool
  is_load: bool
  is_store: bool
  is_atomic: bool
  is_barrier: bool
  reg_write_count: uint8
  load_queue_id: optional<uint16>
  store_queue_id: optional<uint16>
  replay_token_begin: optional<uint64>
  replay_token_end: optional<uint64>
  trap_or_fault: optional<string>
```

```yaml
event: LaneRegWriteback
fields:
  cycle: uint64
  sm_id: uint16
  warp_id: uint16
  lane_id: uint16
  reg_file: scalar|vector|predicate|special
  reg_id: uint16
  value: bytes
  valid: bool
  commit_index: optional<uint16>
  replay_token: optional<uint64>
```

```yaml
event: MemoryTransaction
fields:
  cycle: uint64
  sm_id: uint16
  warp_id: uint16
  transaction_kind: load|store|atomic|refill|mmio|tlb
  addr_space: global|shared|local|constant|mmio|translation
  address: uint64
  byte_mask: bytes
  data: bytes
  transaction_id: uint32
  coalesced_lane_mask: uint64
  cache_or_noc_stage: optional<string>
  replay_token_begin: optional<uint64>
  replay_token_end: optional<uint64>
  source_probe: optional<string>
```

#### A7.3 Comparison rules

| Event | Comparison rule | Why |
|---|---|---|
| `WarpInstrCommit` | Compare architecturally visible control outcome, writeback intent, skip marker, and any load/store classification. If the event is squashed, compare the reconstructed per-instruction sequence during replay. | XiangShan uses fused commit plus replay to keep debug precision. |
| `LaneRegWriteback` | Compare value by lane and file type only after the matching commit or replay token is known. | XiangShan keeps writeback-related state aligned with commit dependencies. |
| `MemoryTransaction` | Compare address, mask, data, transaction kind, and ordering token. Any MMIO, atomic, barrier-visible, or inter-warp-visible transaction must compare in exact order. | XiangShan treats side-effecting sync points conservatively. |

#### A7.4 Mismatch report schema

```yaml
mismatch:
  test: string
  cycle: uint64
  event: WarpInstrCommit|LaneRegWriteback|MemoryTransaction|ControlSync
  event_index: uint16
  field: string
  rtl: bytes|hex|string
  golden: bytes|hex|string
  context:
    sm_id: uint16
    warp_id: uint16
    pc: uint64
    instr: optional<uint32>
    active_mask: optional<uint64>
    load_queue_id: optional<uint16>
    store_queue_id: optional<uint16>
    transaction_id: optional<uint32>
    replay_token_begin: optional<uint64>
    replay_token_end: optional<uint64>
  attribution:
    source_probe: string
    suspected_modules:
      - string
    required_debug_trace:
      - warp_commit_trace
      - lane_writeback_trace
      - scoreboard_trace
      - memory_transaction_trace
      - counter_snapshot
    local_cycle_window:
      pre_failure_cycles: 5000
      post_failure_cycles: 200
  replay:
    mode: token_range|checkpoint|fork_window
    command: string
    requires_ref_restore: true
```

#### A7.5 Replay / debug strategy

| Failure class | Required replay strategy |
|---|---|
| Wrong register value | Replay the token range containing the matching commit and lane writebacks; dump commit, writeback, regfile, and scoreboard traces |
| Wrong memory value | Replay the enclosing memory transaction range; dump coalescer, cache/NoC, and memory traces |
| Barrier / ordering hang | Replay around the barrier or fence token range; dump warp state, outstanding transactions, and scheduler traces |
| Atomic mismatch | Replay exact atomic transaction range; preserve address, compare value, mask, return value, and ordering token |
| Control-side mismatch | Replay the trap / interrupt sync edge; dump control-state and side-channel sync traces |

### A8. Evidence Table for Skill Transfer

| XiangShan Mechanism | Source Files / Docs | Problem Solved | Transferable GPGPU Abstraction | Skill Rule | Required Schema | Anti-Pattern to Avoid |
|---|---|---|---|---|---|---|
| `CONFIRMED: basic-vs-full probe split` | `ref_submodule/xiangshan/src/main/scala/xiangshan/Parameters.scala:524-542`; `ref_submodule/xiangshan/Makefile:205-216`; `ref_submodule/xiangshan/src/main/scala/top/ArgParser.scala:122-129` | Keeps debug always available while reserving heavier probes for full diff runs | `basic_trace_diff` vs `full_transaction_diff` modes | Every schema must declare whether it exists in basic mode, full mode, or both | Mode tag on every event family | A single monolithic trace mode that is too slow for routine iteration |
| `CONFIRMED: commit probe with field-level full-mode enrichment` | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1594-1655` | Separates always-needed commit outcome from heavier context fields | `WarpInstrCommit` with optional queue and replay metadata | Optional fields must be explicit and mode-gated | `WarpInstrCommit` | Assuming that a probe's existence implies all of its fields are valid in every mode |
| `CONFIRMED: store/load/atomic/refill/TLB/MMIO event probes` | `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/sbuffer/Sbuffer.scala:765-776`, `:892-1010`; `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/pipeline/AtomicsUnit.scala:588-606`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/mmu/TLB.scala:761-787`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/mmu/L2TLB.scala:663-704`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/dcache/Uncache.scala:439-447` | Makes side-effecting memory and translation behavior observable and replayable | `MemoryTransaction` plus specialized control-side sync events | Any externally visible side effect needs its own probe, not just a final state diff | `MemoryTransaction` | Hiding MMIO, atomic, or translation behavior behind only end-state register comparison |
| `CONFIRMED: rename-table and physical-reg shadow state` | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rename/RenameTable.scala:185-348`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/datapath/DataPath.scala:337-370`, `:470-474` | Supports strong debugging when per-event traces are insufficient | Whole-state snapshots for regfiles and mapping tables | Snapshot-style bundles may be delta-compressed only if software reconstructs full state | `LaneRegWriteback` plus optional full-state snapshot schema | Recording only writeback events and then being unable to reconstruct state at the failure point |
| `CONFIRMED: CSR / interrupt / HPM / flush sync events` | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1653-1809` | Synchronizes side effects not represented by ordinary instruction commits | `ControlSync` / `CounterOverflow` / `FlushSync` events | Any async side effect requires a dedicated sync event | Control-side sync schema | Pretending control-state sync can be inferred from normal instruction commit alone |
| `CONFIRMED: DLL-style NEMU reference API` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c:25-131`; `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:87-367` | Clean ABI between DUT harness and golden model | GPGPU golden `.so` or service interface | Golden API must minimally support memory copy, register copy, step, skip, interrupt/sync hooks, and status | Golden-model interface contract | Baking the golden model directly into the simulator with no reusable ABI |
| `CONFIRMED: skip-ref and skip-dut catch-up logic` | `ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c:44-71`, `:148-167` | Handles instructions or grouped execution that cannot be compared one-by-one in lockstep | `skip_diff` plus replay-group / catch-up contract | If skipping is allowed, the event must carry a reason and a recovery rule | `WarpInstrCommit.skip_diff`, replay token fields | Allowing skips with no accounting, causing silent loss of coverage |
| `CONFIRMED(doc) / MISSING(local): Batch/Squash/Delta/NonBlock/Replay optimization stack` | DiffTest docs sections `Batch`, `Squash/Delta`, `NonBlock`, `Replay` at `https://docs.xiangshan.cc/zh-cn/latest/tools/difftest/` | Balances throughput against debug precision | Compression / replay layer over GPGPU trace diff | No compression without explicit safety and replay rules | Compression-safety table, replay token schema | Turning on trace compression first and inventing replay semantics later |
| `MISSING: local bundle definitions, parser, whitelist, replay internals` | empty `ref_submodule/xiangshan/difftest`; `ref_submodule/xiangshan/build.mill:197-214`; `ref_submodule/xiangshan/src/main/scala/top/ArgParser.scala:241-252` | Blocks exact field-width and whitelist confirmation | Treat remote or future source as a separate validation step | Report `MISSING` explicitly and do not overclaim | Missing-contract ledger | Filling gaps by memory or by assuming docs describe the exact local commit |

### A9. Missing Local Contracts

| Missing contract | Evidence gap | Why it matters | Suggested owner |
|---|---|---|---|
| Bundle class definitions for `DiffInstrCommit`, `DiffLoadEvent`, `DiffStoreEvent`, `DiffRefillEvent`, `DiffL1TLBEvent`, `DiffL2TLBEvent`, etc. | Local `ref_submodule/xiangshan/difftest` is empty | Exact field widths, defaults, and any hidden fields are unknown | Reader follow-up after submodule init |
| `DifftestModule.parseArgs` and `--difftest-config` parser | `ArgParser.scala` delegates to missing module | Exact CLI behavior is not locally inspectable | Reader follow-up after submodule init |
| `supportsDelta` bundle whitelist | Docs mention `Difftest.scala` only | Exact delta-safe bundle list cannot be confirmed | Reader follow-up after submodule init |
| `updateDependency` state-dependency table | Docs mention `Difftest.scala` only | Needed to know what can squash without breaking compare semantics | Reader follow-up after submodule init |
| Replay token and rollback implementation | Docs mention token ranges and rollback, local code absent | Needed for faithful GPGPU replay contract | Reader follow-up after submodule init |
| Software checker mismatch output format | Local XiangShan-side checker not readable | Needed for a one-to-one mismatch-report transfer | Reader follow-up after submodule init |

### A10. Full Claim Index

| Claim ID | Claim | Status | Evidence | Confidence |
|---|---|---|---|---|
| `XS-DIFF-C001` | Basic diff is enabled by default through `AlwaysBasicDiff = true`. | CONFIRMED | `ref_submodule/xiangshan/src/main/scala/xiangshan/Parameters.scala:529-530` | High |
| `XS-DIFF-C002` | Full DiffTest is explicitly enabled by `--enable-difftest`. | CONFIRMED | `ref_submodule/xiangshan/src/main/scala/top/ArgParser.scala:122-125` | High |
| `XS-DIFF-C003` | The repo `Makefile` adds `--enable-difftest` for normal debug builds and disables it for FPGA builds. | CONFIRMED | `ref_submodule/xiangshan/Makefile:205-216` | High |
| `XS-DIFF-C004` | `TopMain` treats either `EnableDifftest` or `AlwaysBasicDiff` as enough to enable the DiffTest path. | CONFIRMED | `ref_submodule/xiangshan/src/main/scala/top/Top.scala:413-444` | High |
| `XS-DIFF-C005` | `DiffInstrCommit` is a basic probe, but some of its richer fields are driven only in full mode. | CONFIRMED | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1607-1655` | High |
| `XS-DIFF-C006` | XiangShan exports whole physical register files and rename maps as diff state. | CONFIRMED | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/datapath/DataPath.scala:337-370`, `:470-474`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rename/RenameTable.scala:261-348` | High |
| `XS-DIFF-C007` | Memory-side probes cover stores, sbuffer visibility, atomics, MMIO stores, refills, and TLB events. | CONFIRMED | `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/sbuffer/Sbuffer.scala:765-776`, `:892-1010`; `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/pipeline/AtomicsUnit.scala:588-606`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/dcache/Uncache.scala:439-447`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/mmu/TLB.scala:761-787`; `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/mmu/L2TLB.scala:663-704` | High |
| `XS-DIFF-C008` | NewCSR adds non-register interrupt pending, HPM overflow, AIA sync, and custom flush sync events. | CONFIRMED | `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:1767-1809` | High |
| `XS-DIFF-C009` | REF stepping is single-step lockstep by default, with explicit skip and catch-up modes. | CONFIRMED | `ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c:44-71`, `:143-178` | High |
| `XS-DIFF-C010` | REF side exports query/status and side-channel sync helpers in addition to the basic step API. | CONFIRMED | `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:184-323` | High |
| `XS-DIFF-C011` | Docs define Batch, Squash, Delta, NonBlock, and Replay and describe the main tradeoffs. | CONFIRMED | `https://docs.xiangshan.cc/zh-cn/latest/tools/difftest/` sections `Batch`, `Squash/Delta`, `NonBlock`, `Replay` | Medium-High |
| `XS-DIFF-C012` | Exact local delta whitelist, dependency table, and replay internals are not inspectable in this workspace. | MISSING | empty `ref_submodule/xiangshan/difftest` | High |

### A11. Full Quality Checklist

#### Evidence Gate

| Check | Result | Notes |
|---|---|---|
| Scope declared | PASS | Mode, depth, corpus slice, focus, and non-goals are explicit |
| Planner focus answered | PASS | All 9 extraction questions are addressed |
| Evidence attached | PASS | All major claims carry file or doc anchors |
| Claim status used | PASS | `CONFIRMED`, `INFERRED`, `UNCERTAIN`, `MISSING` are used for evidence claims; `PARTIAL` is reserved for the quality gate |
| Contradictions reported | PASS | No material contradictions found; only missing local implementation |
| Missing contracts reported | PASS | Empty local `difftest` submodule is called out repeatedly |
| Handoff actionable | PASS | Next actions map directly to GPGPU skill work |

#### Readability Gate

| Check | Result | Notes |
|---|---|---|
| Handoff length | PASS | Part A is compact for `model-evidence` |
| Findings capped | PASS | Six top findings |
| Tables limited | PASS | Full tables are kept in the appendix section |
| Empty sections removed | PASS | Only relevant sections included |
| Decision relevance | PASS | Every section supports the GPGPU transfer decision |
| Appendix separation | PASS | Part A is concise; detail is in Part B |

#### Repository Extra Gate

| Topic | Status | Notes |
|---|---|---|
| ISA semantics | not applicable | Explicit non-goal for this shard |
| instruction encoding | not applicable | Explicit non-goal for this shard |
| decode path | not applicable | Explicit non-goal for this shard |
| PC / warp state | inferred | Only as GPGPU transfer target in `WarpInstrCommit` |
| active mask | inferred | GPGPU transfer field, not XiangShan CPU-local evidence |
| SIMT divergence | not applicable | Not part of XiangShan CPU DiffTest pass |
| register file | confirmed | Only as shadow diff state, not as microarchitectural study |
| scoreboard / hazards | not applicable | Not part of this shard |
| issue / execute / writeback | not applicable | Only touched as probe sources |
| memory coalescing | not applicable | Not part of XiangShan CPU DiffTest pass |
| shared memory | not applicable | Not part of XiangShan CPU DiffTest pass |
| barrier semantics | inferred | Only in GPGPU replay/mismatch rules |
| CSR / DCR / config state | confirmed | CSR and side-channel sync probes are directly read |
| launch protocol | not applicable | Not part of this shard |
| kernel arguments | not applicable | Not part of this shard |
| grid/block/warp mapping | inferred | Only as transfer target |
| CModel / golden model | confirmed | NEMU DLL and step loop were read |
| trace diff / compare path | confirmed | Main topic of the shard |
| tests and coverage | missing | No local test harness or coverage pass was read in this shard |
| synthesis / FPGA / PPA evidence | not applicable | This shard is about trace diff and REF sync, not synthesis/PPA |

## Quality Gate

- Overall status: PARTIAL
- Evidence status: PARTIAL
- Readability status: PASS
- Safe for GPT-5.5 planning: yes, with caveats
- Full appendix generated: inline
- Biggest evidence gap: local `ref_submodule/xiangshan/difftest` is empty, so bundle definitions, `--difftest-config` parser logic, compression whitelist, replay token format, and checker internals are `MISSING`
- Biggest readability issue: a few compression rules are necessarily conservative because the local whitelist and dependency tables are missing
- Required next read: initialize or otherwise inspect the matching XiangShan `difftest` source, especially `Difftest.scala`, `Preprocess.scala`, the replay path, and the software checker
