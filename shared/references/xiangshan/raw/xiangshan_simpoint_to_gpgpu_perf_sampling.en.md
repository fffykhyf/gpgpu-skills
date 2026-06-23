# Repository Architecture Report

## Part A. Human Handoff

### 0. Metadata

- Mode: repository
- Depth: deep
- Output profile: model-evidence
- Repo / subsystem: XiangShan/NEMU SimPoint, checkpoint, host perf profiling, and XiangShan HPM/TopDown attribution; `ref_submodule/xiangshan-nemu` @ `75d0019`, `ref_submodule/xiangshan` @ `5ff19c2`, `ref/xiangshan.pdf` chapter 14 HPM
- Files read: `ref/skillref/xiangshan.md` sections 0-3/10/12; `skill/reader/{SKILL.md,references/output-policy.md,references/repository-mode-template.md,references/quality-gate.md}`; `ref_submodule/xiangshan-nemu/{README.md,Kconfig,docs/perf_profile.md,include/checkpoint/{cpt_env.h,serializer.h,simpoint.h},include/profiling/profiling_control.h,src/checkpoint/{path_manager.cpp,semantic_point.cpp,serializer.cpp,simpoint.cpp},src/profiling/profiling_control.c,src/monitor/monitor.c,src/isa/riscv64/{instr/special.h,reg.c},src/cpu/cpu-exec.c,scripts/checkpoint_example/{profiling.sh,cluster.sh,checkpoint.sh,uniform_cpt.sh,manual_uniform_cpt.sh,manual_oneshot_cpt.sh,semantic_checkpoint.sh},resource/simpoint/do_simpoint_clustering.py,onesimpoint.py,tools/perf_profile.py,tools/perf_profile/{catalog.py,cli.py,parse.py,report.py,util.py,collect/{stat.py,record.py},preflight.py}}`; `ref_submodule/xiangshan/scripts/top-down/{README.md,top_down.py,configs.py,resources/spec06_rv64gcb_o2_20m.json}`; `ref_submodule/xiangshan/src/main/scala/xiangshan/{PMParameters.scala,package.scala,Bundle.scala,XSCore.scala}`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/{TopDownGen.scala,rob/Rob.scala}`; `ref_submodule/xiangshan/src/main/scala/xiangshan/frontend/ibuffer/IBuffer.scala`; official SimPoint doc `https://docs.xiangshan.cc/zh-cn/latest/tools/simpoint/`
- Files skipped: broad CPU frontend/backend microarchitecture, most ISA semantics, most unrelated RTL; `PMParameters.scala` was read and found to be PMP/PMA configuration, not HPM/TopDown configuration
- Entry points inspected: `nemu_trap` start signal, per-basic-block profiler, cluster scripts, checkpoint serializer/path manager, monitor CLI, host `perf_profile` pipeline, TopDown counter sites, HPM PDF chapter
- Focus: only performance sampling, checkpoint, counter, and performance-attribution mechanisms reusable for a GPGPU skill
- Questions answered: all nine extraction questions for this shard
- Non-goals: CPU microarchitecture summary except where required to explain HPM/TopDown or checkpoint/perf infrastructure
- Appendix: inline
- Confidence: Medium-High

### 1. One-Paragraph Answer

XiangShan/NEMU implements a usable performance-sampling loop, not just a checkpoint utility. NEMU starts profiling only after a workload-side `nemu_trap` or `--dont-skip-boot`, emits interval BBVs, clusters them into weighted representative phases, re-runs the workload to generate warmup-aware checkpoints, and then hands those checkpoints to replay tools. XiangShan HPM/TopDown turns replay output into attributed bottleneck buckets through module-defined `generatePerfEvent` signals, `mhpmevent` selectors, HPM counters, and weighted post-processing across checkpoints. For a GPGPU skill, the transferable rule is: use realistic kernel phases, not toy tests; bind each checkpoint to phase metadata plus restore state; replay on RTL and golden; then accept or reject performance changes only after weighted counter and trace attribution.

### 2. Top Architecture Findings

- `CONFIRMED` Tiny smoke tests are insufficient for performance decisions. `perf_profile.md` labels `-I 10000000` as smoke-only, warns that the real test is sample stability, and `report.py` emits low-sample warnings for both quick and precise modes. `README.md` also says small applications may have too few intervals to justify checkpointing. Evidence: `ref_submodule/xiangshan-nemu/docs/perf_profile.md:106-128,223-229`; `ref_submodule/xiangshan-nemu/tools/perf_profile/report.py:948-1008,1057-1064`; `ref_submodule/xiangshan-nemu/README.md:229-239`.
- `CONFIRMED` NEMU SimPoint BBV generation is runtime-gated, interval-based, and basic-block oriented. `nemu_trap` with `a0==0x101` calls `start_profiling()`, `cpu-exec.c` feeds each control-terminated basic block to `simpoint_profiling`, and `simpoint.cpp` emits `T:id:count` or `T:first_pc:second_pc:id:count` records every `--cpt-interval`. Evidence: `ref_submodule/xiangshan-nemu/src/isa/riscv64/instr/special.h:36-48`; `ref_submodule/xiangshan-nemu/src/profiling/profiling_control.c:18-23`; `ref_submodule/xiangshan-nemu/src/cpu/cpu-exec.c:317-381`; `ref_submodule/xiangshan-nemu/src/checkpoint/simpoint.cpp:78-176`; `ref_submodule/xiangshan-nemu/Kconfig:55-68`.
- `CONFIRMED` Clustering is the step that makes performance sampling representative rather than anecdotal. The cluster scripts convert `simpoint_bbv.gz` into `simpoints0` and `weights0`; the optional helper reruns clustering ten times and chooses the seed set with the strongest top-weight coverage; the checkpoint serializer then reads those weights and schedules checkpoints at weighted phase locations minus warmup. Evidence: `ref_submodule/xiangshan-nemu/scripts/checkpoint_example/cluster.sh:5-27`; `ref_submodule/xiangshan-nemu/resource/simpoint/do_simpoint_clustering.py:29-70,74-100`; `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:549-669`.
- `CONFIRMED` Checkpoint generation/restoration is not just memory dumping. NEMU stores integer, floating-point, vector, CSR, PC, privilege mode, `mtime`, `mtimecmp`, and memory/flash images; naming includes interval identity and weight; restoration requires a restorer binary unless the workload already embeds it or the checkpoint is stored in flash. Evidence: `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:198-366,376-476,482-515`; `ref_submodule/xiangshan-nemu/src/checkpoint/path_manager.cpp:38-109`; `ref_submodule/xiangshan-nemu/README.md:207-239`; official SimPoint doc sections `生成SimPoint checkpoint`, `Checkpoint 的恢复`.
- `CONFIRMED` XiangShan performance attribution is a two-layer system: hardware counters/selectors plus offline weighted analysis. The PDF says submodules define events, `generatePerfEvent` feeds Frontend/Backend/MemBlock/CoupledL2, `PFEvent` mirrors `mhpmevent`, and `HPerfMonitor` accumulates selected events into `mhpmcounter3-31`; `top_down.py` then weights per-checkpoint results using checkpoint weights and can normalize A/B runs by issue width. Evidence: `ref/xiangshan.pdf` chapter 14, printed pages 274-289; `ref_submodule/xiangshan/src/main/scala/xiangshan/XSCore.scala:102-117,176-180,195,232-240`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/TopDownGen.scala:69-120`; `ref_submodule/xiangshan/scripts/top-down/top_down.py:62-95,120-158,170-237`.
- `CONFIRMED` Host-side `tools/perf_profile.py` is a complementary attribution path for NEMU itself, not a replacement for checkpoint replay. It generates `manifest.json`, `raw/`, `parsed/`, `reports/`, and `logs/`, runs `doctor -> stat -> record -> report`, and clearly distinguishes quick grouped sampling from precise event-triggered attribution. Evidence: `ref_submodule/xiangshan-nemu/docs/perf_profile.md:1-5,138-229`; `ref_submodule/xiangshan-nemu/tools/perf_profile/cli.py:143-166,204-340,344-424`; `ref_submodule/xiangshan-nemu/tools/perf_profile/collect/{stat.py,record.py}:25-40,75-180`; `ref_submodule/xiangshan-nemu/tools/perf_profile/report.py:840-1109`.
- `CONFIRMED` `PMParameters.scala` is a naming trap for this pass. In this commit it defines PMP/PMA parameters, not HPM or TopDown controls, so it should not be used as a source for performance-sampling rules. Evidence: `ref_submodule/xiangshan/src/main/scala/xiangshan/PMParameters.scala:25-60`.

### 3. Minimal Architecture Map

- Profiling start and interval base: workload issues `nemu_trap`; NEMU records `checkpoint_icount_base`; profiler/checkpointer stay inactive until `workload_loaded` or `--dont-skip-boot`. Evidence: `src/isa/riscv64/instr/special.h:36-48`; `src/profiling/profiling_control.c:18-23`; `src/cpu/cpu-exec.c:317-342`.
- BBV generation: `simpoint.cpp` identifies control-terminated basic blocks, accumulates interval counts, and writes `simpoint_bbv.gz`. Evidence: `src/checkpoint/simpoint.cpp:95-176`.
- Representative phase selection: external SimPoint clustering produces `simpoints0` and `weights0`; NEMU reuses them to schedule checkpoints. Evidence: `scripts/checkpoint_example/cluster.sh:18-22`; `src/checkpoint/serializer.cpp:555-568,580-615`.
- Checkpoint package: `path_manager.cpp` defines the directory tree; `serializer.cpp` names files and serializes registers/control/memory. Evidence: `src/checkpoint/path_manager.cpp:57-109`; `src/checkpoint/serializer.cpp:215-220,222-366,376-476`.
- Replay attribution: XiangShan HPM/TopDown counters are emitted by modules, selected by `mhpmevent`, accumulated by HPM, and weighted offline by checkpoint metadata. Evidence: `ref/xiangshan.pdf` printed pages 274-289; `src/main/scala/xiangshan/backend/TopDownGen.scala:99-112`; `scripts/top-down/top_down.py:62-95,120-158`.

### 4. Top State / Interface Contracts

| Contract | Status | Why it matters | Evidence |
|---|---|---|---|
| Profiling starts only after explicit workload-phase handoff | `CONFIRMED` | Prevents boot noise from contaminating phase features | `ref_submodule/xiangshan-nemu/src/isa/riscv64/instr/special.h:36-48`; `ref_submodule/xiangshan-nemu/src/cpu/cpu-exec.c:317-342` |
| `--cpt-interval` defines both profiling interval and checkpoint interval | `CONFIRMED` | Cluster points and checkpoint replay must refer to the same window size | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:297-299`; official SimPoint doc section `命令` |
| Warmup defaults to interval size when unspecified | `CONFIRMED` | Replay windows must include pre-phase warmup, not just measured body | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:340-341`; official SimPoint doc section `性能分析 / Warm-Up` |
| `simpoints0` and `weights0` are workload-scoped inputs to checkpoint scheduling | `CONFIRMED` | Weighted representative phases are an external contract, not an internal heuristic | `ref_submodule/xiangshan-nemu/src/checkpoint/path_manager.cpp:59-61`; `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:555-568` |
| Checkpoint package includes arch state plus timing/control state | `CONFIRMED` | GPGPU restore must include PC/mode/timer-equivalent state, not just memory | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:376-476` |
| Weighted replay summary consumes `checkpoint.json` with `insts` and `points` | `CONFIRMED` | Performance attribution must preserve phase weight and whole-workload instruction mass | `ref_submodule/xiangshan/scripts/top-down/top_down.py:71-95,98-118`; `ref_submodule/xiangshan/scripts/top-down/resources/spec06_rv64gcb_o2_20m.json:1-30` |
| Quick-mode host perf is grouped sampling, not standalone event attribution | `CONFIRMED` | Avoid misusing grouped counters as proof of a root cause | `ref_submodule/xiangshan-nemu/docs/perf_profile.md:147-155`; `ref_submodule/xiangshan-nemu/tools/perf_profile/report.py:721-754,948-955` |

### 5. Top Risks / Missing Contracts

- `MISSING` The local corpus does not include the `env-scripts` producer that turns checkpoint runs into the stat-directory layout consumed by `scripts/top-down/top_down.py`. The consumer is clear; the producer path is external. Evidence: `ref_submodule/xiangshan/scripts/top-down/README.md:3-4,119-120`.
- `PARTIAL` The HPM/`HPerfMonitor` implementation logic is documented in the PDF, but the exact CSR/HPerfMonitor RTL was not in the scoped file list for this shard. Counter semantics are strong; selector datapath implementation is PDF-backed rather than line-by-line RTL-backed here. Evidence: `ref/xiangshan.pdf` printed pages 274-289.
- `CONFIRMED` Manual, semantic, and uniform checkpoints exist, but they are poor default inputs for performance acceptance because they are operator-driven or non-weighted. Evidence: `ref_submodule/xiangshan-nemu/src/profiling/profiling_control.h:11-19`; `ref_submodule/xiangshan-nemu/scripts/checkpoint_example/{uniform_cpt.sh,manual_uniform_cpt.sh,manual_oneshot_cpt.sh,semantic_checkpoint.sh}:1-21`; `ref_submodule/xiangshan-nemu/src/checkpoint/semantic_point.cpp:46-167`.
- `CONFIRMED` M-mode checkpointing is unsafe by default and only bypassable with an explicit force flag. Evidence: `ref_submodule/xiangshan-nemu/README.md:48,207-214`; `ref_submodule/xiangshan-nemu/src/isa/riscv64/reg.c:366-368`; `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:233-236`.
- `CONFIRMED` Passing the wrong `-S` path shape is an easy operational error: NEMU appends `/<workload>/` itself, so `-S` should point to the cluster root, not the workload leaf. Evidence: `ref_submodule/xiangshan-nemu/scripts/checkpoint_example/checkpoint.sh:9-15`; `ref_submodule/xiangshan-nemu/src/checkpoint/path_manager.cpp:59-61`.

### 6. Evidence Snapshot

| Claim ID | Status | Short claim | Evidence |
|---|---|---|---|
| `XS-SIM-001` | CONFIRMED | Smoke windows are for tool sanity, not performance decisions. | `ref_submodule/xiangshan-nemu/docs/perf_profile.md:106-128`; `ref_submodule/xiangshan-nemu/tools/perf_profile/report.py:1003-1009,1057-1063` |
| `XS-SIM-002` | CONFIRMED | SimPoint profiling starts from `nemu_trap` or `--dont-skip-boot`. | `ref_submodule/xiangshan-nemu/src/isa/riscv64/instr/special.h:36-48`; `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:227-231` |
| `XS-SIM-003` | CONFIRMED | BBV output is interval-based basic-block counting, emitted as `T:...` lines. | `ref_submodule/xiangshan-nemu/src/checkpoint/simpoint.cpp:105-176`; `ref_submodule/xiangshan-nemu/Kconfig:55-68` |
| `XS-SIM-004` | CONFIRMED | Weighted representative intervals are loaded from `simpoints0` and `weights0`. | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:555-568` |
| `XS-SIM-005` | CONFIRMED | SimPoint checkpoints are scheduled at `simpoint*interval - warmup`. | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:580-589` |
| `XS-SIM-006` | CONFIRMED | Checkpoints serialize registers, CSR array, PC, mode, timers, and compressed memory/flash. | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:222-366,376-476` |
| `XS-SIM-007` | CONFIRMED | `-D/-C/-w` define the directory contract and are effectively mandatory. | `ref_submodule/xiangshan-nemu/src/checkpoint/path_manager.cpp:38-61`; official SimPoint doc section `命令` |
| `XS-SIM-008` | CONFIRMED | `perf_profile.py` writes `manifest.json`, raw logs/data, parsed JSON, and Markdown reports. | `ref_submodule/xiangshan-nemu/docs/perf_profile.md:185-219`; `ref_submodule/xiangshan-nemu/tools/perf_profile/cli.py:143-166,301-340` |
| `XS-SIM-009` | CONFIRMED | XiangShan HPM aggregates submodule events through `generatePerfEvent`, `PFEvent`, and `HPerfMonitor`. | `ref/xiangshan.pdf` printed page 274; `ref_submodule/xiangshan/src/main/scala/xiangshan/XSCore.scala:176-180,232-240` |
| `XS-SIM-010` | CONFIRMED | TopDown post-processing is weighted by checkpoint points and can normalize A/B issue width. | `ref_submodule/xiangshan/scripts/top-down/top_down.py:71-95,120-158,202-219`; `ref_submodule/xiangshan/scripts/top-down/resources/spec06_rv64gcb_o2_20m.json:1-30` |
| `XS-SIM-011` | CONFIRMED | `PMParameters.scala` is PMP/PMA, not performance-monitor configuration. | `ref_submodule/xiangshan/src/main/scala/xiangshan/PMParameters.scala:25-60` |

### 7. Main Architect Next Actions

- Decision needed: define a GPGPU phase-feature schema before designing checkpoint producers.
  Files to inspect: this report, current GPGPU trace/counter schemas.
  Risk: collecting checkpoints before feature design will lock in the wrong phase abstraction.
  Acceptance test: one kernel run can emit phase features, weights, and a reproducible checkpoint manifest.
- Decision needed: separate three gates in the GPGPU workflow.
  Gates: correctness diff, representative checkpoint replay, attribution.
  Risk: a faster toy test may hide regressions in realistic phases.
  Acceptance test: every accepted perf change cites all three gates.
- Decision needed: define a checkpoint package schema that binds workload phase, golden restore state, RTL restore state, counter snapshot schema, and trace schema version.
  Files to inspect: current GPGPU checkpoint and replay tooling.
  Risk: replay results become non-comparable across RTL revisions.
  Acceptance test: two RTL versions can replay the same checkpoint package and produce versioned comparable outputs.
- Decision needed: decide whether host-side profiler support is needed for the GPGPU golden model itself.
  Files to inspect: current simulator/profiler stack.
  Risk: simulator hotspots get conflated with hardware bottlenecks.
  Acceptance test: host-hotspot reports and hardware-counter reports are emitted as separate artifacts.

### 8. Compact Quality Gate

- Evidence status: PASS
- Readability status: PASS
- Safe for GPT-5.5 planning: yes, with one caveat about missing local `env-scripts` producer code
- Full appendix generated: inline
- Biggest evidence gap: `checkpoint.json` production path and top-down stat-directory producer are external to the local corpus
- Required next read: external `env-scripts` checkpoint runner and XiangShan CSR/HPerfMonitor RTL if the planner needs implementation-level HPM wiring

## Part B. Evidence Appendix

### A1. Source-of-Truth Hierarchy

| Layer | Files / Docs | Role | Reliability | Notes |
|---|---|---|---|---|
| Project rules | `ref/skillref/xiangshan.md:17-94,770-874,914-1040`; `skill/reader/SKILL.md` | shard scope, evidence rules, required output | High | local planner contract |
| Official docs | `https://docs.xiangshan.cc/zh-cn/latest/tools/simpoint/` | user-facing SimPoint/checkpoint workflow, warm-up guidance, CLI semantics | High | current official corroboration |
| Local NEMU docs | `ref_submodule/xiangshan-nemu/README.md`; `docs/perf_profile.md` | checkpoint role, FAQ, host-side perf workflow | High | primary local narrative |
| NEMU source | `src/monitor/*`, `src/cpu/*`, `src/checkpoint/*`, `src/profiling/*`, `src/isa/riscv64/*` | actual profiler/checkpoint behavior | High | authoritative for runtime behavior |
| Example scripts | `scripts/checkpoint_example/*`, `resource/simpoint/do_simpoint_clustering.py`, `onesimpoint.py` | operational shell contract | Medium-High | examples can lag source |
| XiangShan docs | `ref/xiangshan.pdf` chapter 14 | HPM/TopDown architecture and formulas | High | primary source for attribution model |
| XiangShan source | `XSCore.scala`, `TopDownGen.scala`, `package.scala`, `IBuffer.scala`, `Rob.scala`, top-down scripts | event names, wiring, and weighted offline analysis | High | authoritative for implementation-facing names |
| Misleading non-source | `PMParameters.scala` | confirms what is not HPM | High | useful negative evidence |

### A2. Why Tiny Smoke Tests Are Insufficient

| Signal | What XiangShan/NEMU says | GPGPU transfer |
|---|---|---|
| Smoke windows | `perf_profile.md` says `-I 10000000` is only a smoke check to verify toolchain and command line. Evidence: `ref_submodule/xiangshan-nemu/docs/perf_profile.md:106-115` | Do not accept a memory/scheduler/coalescer optimization from a 10M-instruction or toy-kernel sanity window. |
| Stability criterion | `perf_profile.md` says the real test is stable sample counts and stable hotspot ordering; increase `-I` if results move around. Evidence: `ref_submodule/xiangshan-nemu/docs/perf_profile.md:122-128` | Use fixed representative windows for A/B comparisons; do not compare runs with drifting phase coverage. |
| Low-sample warnings | `report.py` emits warnings when grouped or precise sample counts are under 20. Evidence: `ref_submodule/xiangshan-nemu/tools/perf_profile/report.py:1003-1009,1057-1063` | Require minimum sample/support thresholds before trusting attribution. |
| Small-app warning | `README.md` says small applications with few intervals do not need checkpoints and may yield empty BBVs. Evidence: `ref_submodule/xiangshan-nemu/README.md:229-239` | Toy kernels can be useful for mechanism debugging, but not for weighted performance decisions. |
| Weighted whole-workload summary | `top_down.py` multiplies checkpoint metrics by checkpoint weights and whole-workload instruction mass. Evidence: `ref_submodule/xiangshan/scripts/top-down/top_down.py:71-118`; `ref_submodule/xiangshan/scripts/top-down/resources/spec06_rv64gcb_o2_20m.json:1-30` | Realistic performance decisions must preserve phase weighting, not just pick one hand-chosen replay point. |

### A3. GPGPU Performance Sampling Flow

```text
golden/profiler run
-> collect kernel phase features
-> cluster representative phases
-> generate checkpoint package
-> replay checkpoint on RTL and golden model
-> collect counters and structured traces
-> compare against previous design
-> decide keep / tune / rewrite / revert
```

Evidence anchors:

- profiler start and interval basis: `ref_submodule/xiangshan-nemu/src/isa/riscv64/instr/special.h:36-48`, `ref_submodule/xiangshan-nemu/src/profiling/profiling_control.c:18-23`
- phase features via BBV intervals: `ref_submodule/xiangshan-nemu/src/checkpoint/simpoint.cpp:105-176`
- clustering to representative points: `ref_submodule/xiangshan-nemu/scripts/checkpoint_example/cluster.sh:18-22`, `ref_submodule/xiangshan-nemu/resource/simpoint/do_simpoint_clustering.py:29-70`
- checkpoint package creation: `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:198-366,376-476,549-669`
- weighted replay attribution: `ref_submodule/xiangshan/scripts/top-down/top_down.py:71-118,120-158`
- counter fabric: `ref/xiangshan.pdf` printed pages 274-289; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/TopDownGen.scala:99-112`

### A4. GPGPU `phase_features` YAML

```yaml
phase_features:
  interval_insts: 20000000
  warmup_insts: 20000000
  feature_set:
    - instruction_mix
    - memory_access_density
    - shared_memory_access_density
    - branch_divergence_rate
    - global_load_store_ratio
    - atomic_frequency
    - barrier_frequency
    - coalescing_efficiency
    - l1_hit_rate
    - l2_hit_rate
    - noc_backpressure_rate
    - dram_queue_occupancy
  per_phase_metadata:
    phase_id: uint64
    interval_index: uint64
    feature_vector_hash: string
    sample_weight: float
    kernel_name: string
    launch_signature: string
```

Status:

- `CONFIRMED` XiangShan uses interval BBVs and weighted checkpoint points.
- `INFERRED` The feature names above are the GPGPU transfer of XiangShan’s BBV-plus-counter phase abstraction.

### A5. SimPoint / Checkpoint CLI Contract

| Argument | Meaning in XiangShan/NEMU | Required contract for GPGPU | Evidence |
|---|---|---|---|
| `--simpoint-profile` | Enables SimPoint profiling mode. | Distinguish profiling pass from checkpointing pass. | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:222-226,309-311` |
| `--cpt-interval` | Profiling interval for SimPoint; checkpoint interval for replay generation. | Use one canonical interval per experiment family. | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:297-299`; official SimPoint doc section `命令` |
| `-D` | Output base dir. | Artifact root for all phase-profile and checkpoint outputs. | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:102-105,158-160,288-290`; `ref_submodule/xiangshan-nemu/src/checkpoint/path_manager.cpp:38-61` |
| `-C` | Config / run-name component. | Encodes experiment family or design revision. | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:105,160,290`; `ref_submodule/xiangshan-nemu/src/checkpoint/path_manager.cpp:42-43,57` |
| `-w` | Workload-name component. | Must identify kernel / input / launch case. | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:104,159,289`; `ref_submodule/xiangshan-nemu/src/checkpoint/path_manager.cpp:45-46,57` |
| `-S` / `--simpoint-dir` | Cluster directory root used during checkpoint generation. | Pass cluster root, not the workload leaf. | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:114,195-200,295`; `ref_submodule/xiangshan-nemu/src/checkpoint/path_manager.cpp:59-61` |
| `--checkpoint-format` | Select `gz` or `zstd`; default is `gz`. | Persist format in checkpoint manifest; do not guess on restore. | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:50,262-269,302`; `ref_submodule/xiangshan-nemu/include/checkpoint/cpt_env.h:19-28` |
| `-r` / `--cpt-restorer` | Path to `gcpt.bin` restorer. | Require explicit restorer unless the image already embeds one or flash mode is used. | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:109-110,186-188,292`; official SimPoint doc section `命令` |
| `--warmup-interval` | Explicit warmup length; defaults to checkpoint interval when omitted. | Warmup is first-class experiment metadata. | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:119,277,340-341,298` |
| `--dont-skip-boot` | Start profiling/checkpointing immediately after boot. | Keep boot-inclusive runs explicit and opt-in. | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:128-130,227-231,311` |

### A6. Clustering and Weighted Representative Intervals

| Mechanism | Confirmed behavior | Evidence |
|---|---|---|
| Standard cluster flow | `cluster.sh` runs SimPoint on `simpoint_bbv.gz` and saves `simpoints0` + `weights0` with random seeds. | `ref_submodule/xiangshan-nemu/scripts/checkpoint_example/cluster.sh:5-27` |
| Multi-seed stability helper | `do_simpoint_clustering.py` runs clustering 10 times, sorts cluster candidates by summed top weights, and writes `simpoints-final` / `weights-final`. | `ref_submodule/xiangshan-nemu/resource/simpoint/do_simpoint_clustering.py:29-70,86-100` |
| One-shot automation | `onesimpoint.py` prints or runs the full BBV -> cluster -> checkpoint shell sequence. | `ref_submodule/xiangshan-nemu/onesimpoint.py:23-50` |
| Serializer consumption | NEMU reads `simpoints0` and `weights0`, maps `simpoint_location -> weight`, and schedules checkpoint taking accordingly. | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:555-568,580-589` |
| Weighted post-processing | XiangShan TopDown later normalizes checkpoint weights and multiplies them into metrics. | `ref_submodule/xiangshan/scripts/top-down/top_down.py:71-95,120-158` |

Representative-interval rule:

```text
Use smoke or microbenchmarks to isolate a mechanism,
but use weighted representative checkpoints to decide whether the design should stay.
```

### A7. Checkpoint Generation, Naming, and Restore

#### A7.1 Output tree

```text
<output_base_dir>/<config_name>/<workload_name>/simpoint_bbv.gz
<output_base_dir>/<config_name>/<workload_name>/<cptID>/_<simpoint_or_icount>_<weight_if_simpoint>_memory_.{gz,zstd}
<output_base_dir>/<config_name>/<workload_name>/<cptID>/_<simpoint_or_icount>_<weight_if_simpoint>_flash_.{gz,zstd}
```

Evidence:

- profiling dir creation: `ref_submodule/xiangshan-nemu/src/checkpoint/path_manager.cpp:65-77`
- checkpoint dir creation: `ref_submodule/xiangshan-nemu/src/checkpoint/path_manager.cpp:79-103`
- file naming: `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:215-220,222-366`

#### A7.2 Saved state

| Saved state | Evidence |
|---|---|
| integer registers | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:377-383` |
| floating-point registers | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:385-391` |
| vector registers | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:394-404` |
| PC | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:408-410` |
| CSR array + prepared `mstatus`/`mepc` | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:413-457` |
| checkpoint magic, privilege mode, `mtime`, `mtimecmp` | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:460-474` |
| memory image | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:198-366,507-509` |
| optional flash image | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:205-210,238-260,303-353,506-507` |

#### A7.3 Restore modes

| Restore target | Command contract | Evidence |
|---|---|---|
| NEMU restore | `--cpt-restorer gcpt.bin <checkpoint>` | official SimPoint doc section `Checkpoint 的恢复` |
| NEMU restore with flash | `--flash-image <flash_cpt> --cpt-restorer gcpt.bin <mem_cpt>` | official SimPoint doc section `Checkpoint 的恢复` |
| XiangShan replay | `./build/emu -i <checkpoint.gz>` | `ref_submodule/xiangshan-nemu/README.md:195-203` |

### A8. Constraints Checklist

| Constraint | Status | Evidence | GPGPU rule |
|---|---|---|---|
| Do not run `bbv.gz` as a checkpoint/workload | `CONFIRMED` | `ref_submodule/xiangshan-nemu/README.md:50-53,224-227` | Never hand a phase-feature file to RTL/golden replay. |
| Do not produce checkpoints in M-mode | `CONFIRMED` | `ref_submodule/xiangshan-nemu/README.md:48,207-214`; `ref_submodule/xiangshan-nemu/src/isa/riscv64/reg.c:366-368` | Avoid snapshots while privileged control state is being repurposed for restore. |
| `--cpt-mmode` exists only as an escape hatch | `CONFIRMED` | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:233-236,299` | If a bypass exists, it must be explicitly marked unsupported in the GPGPU skill. |
| Interval must be smaller than total instruction count | `CONFIRMED` | `ref_submodule/xiangshan-nemu/README.md:229-232` | Empty feature files are an experiment-definition error. |
| Typical interval sizing is 10M-200M, warmup 20M-100M | `CONFIRMED` | `ref_submodule/xiangshan-nemu/README.md:234-239` | Pick windows based on memory hierarchy reach, not convenience. |
| Default warmup is interval size | `CONFIRMED` | `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:340-341`; official SimPoint doc section `性能分析 / Warm-Up` | Store warmup length beside every checkpoint. |
| Manual checkpoints cannot be automated cleanly in shell scripts | `CONFIRMED` | `ref_submodule/xiangshan-nemu/scripts/checkpoint_example/{manual_uniform_cpt.sh,manual_oneshot_cpt.sh}:5-21`; official SimPoint doc section `Manual Uniform / Manual Oneshot` | Do not base CI or acceptance gates on operator-timed snapshots. |

### A9. Host-Side `perf_profile.py` Artifact Contract

#### A9.1 Flow

```text
doctor
-> perf stat
-> perf record
-> parse samples
-> aggregate functions and basic blocks
-> summary/report generation
```

Evidence:

- `run` command executes `doctor -> stat -> record -> report`: `ref_submodule/xiangshan-nemu/tools/perf_profile/cli.py:301-340`
- quick mode uses grouped `{instructions,cycles,branches,branch-misses,cache-references,cache-misses}:S`: `ref_submodule/xiangshan-nemu/docs/perf_profile.md:142-155`; `ref_submodule/xiangshan-nemu/tools/perf_profile/catalog.py:22-39`
- precise mode records each sampled event in a separate NEMU run: `ref_submodule/xiangshan-nemu/docs/perf_profile.md:161-175`; `ref_submodule/xiangshan-nemu/tools/perf_profile/collect/record.py:147-180`

#### A9.2 Run directory

```text
<run_dir>/
  manifest.json
  logs/
  raw/
    stat/
      perf.stat.stdout.log
      perf.stat.stderr.log
    record/
      quick.data
      quick.script.txt
      <event_slug>/<event_slug>.data
      <event_slug>/<event_slug>.script.txt
  parsed/
    doctor.json
    stat.json
    quick_samples.json
    quick_functions.json
    basic_blocks_quick.json
    samples_<event>.json
    functions_<event>.json
    basic_blocks_<event>.json
  reports/
    doctor.md
    summary.md
    functions_quick.md
    basic_blocks_quick.md
    functions_<event>.md
    basic_blocks_<event>.md
```

Evidence:

- documented layout: `ref_submodule/xiangshan-nemu/docs/perf_profile.md:185-219`
- manifest base schema: `ref_submodule/xiangshan-nemu/tools/perf_profile/cli.py:143-166`
- stat raw artifacts: `ref_submodule/xiangshan-nemu/tools/perf_profile/collect/stat.py:25-40`
- record raw artifacts: `ref_submodule/xiangshan-nemu/tools/perf_profile/collect/record.py:89-115`
- report outputs: `ref_submodule/xiangshan-nemu/tools/perf_profile/report.py:840-1109`

#### A9.3 Semantics to transfer

| XiangShan/NEMU behavior | GPGPU transfer rule |
|---|---|
| quick mode grouped counters are auxiliary, not independent trigger rankings | Keep “fast hotspot scan” separate from “root-cause attribution” |
| precise mode runs one event per NEMU execution | Keep expensive root-cause runs explicit and event-specific |
| summary report stores throughput, counters, samples, warnings, report links | Emit one manifest-backed summary per profiling run |
| doctor validates tool availability and symbolization | CI should fail early on a broken profiling environment |

### A10. XiangShan HPM / TopDown Attribution Mechanisms

#### A10.1 HPM selector/counter fabric

| Mechanism | Confirmed behavior | Evidence |
|---|---|---|
| Event definition in submodules | Submodules define performance events and export them with `generatePerfEvent`. | `ref/xiangshan.pdf` printed page 274; `ref_submodule/xiangshan/src/main/scala/xiangshan/frontend/ibuffer/IBuffer.scala:483-497`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1708-1724`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/TopDownGen.scala:105-112` |
| Major aggregation domains | Events flow into Frontend, Backend, MemBlock, and CoupledL2. | `ref/xiangshan.pdf` printed page 274; `ref_submodule/xiangshan/src/main/scala/xiangshan/XSCore.scala:176-180,195` |
| Selector copy and accumulation | `PFEvent` mirrors `mhpmevent`; `HPerfMonitor` maps selected events into `mhpmcounter3-31`. | `ref/xiangshan.pdf` printed pages 274-275 |
| Control and access | `mcountinhibit` gates counting; `mcounteren`/`scounteren`/`hcounteren` gate privilege access. | `ref/xiangshan.pdf` printed pages 275-277 |
| Event composition | One selector can combine up to four events. | `ref/xiangshan.pdf` printed page 274 |

#### A10.2 TopDown event sites and formulas

| Source | Counter / signal | Role |
|---|---|---|
| `ref_submodule/xiangshan/src/main/scala/xiangshan/frontend/ibuffer/IBuffer.scala:483-497` | `if_fetch_bubble`, `if_fetch_bubble_eq_max`, `Front_Bubble`, `Fetch_Latency_Bound` | frontend latency/bubble attribution |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1325-1330,1709-1724` | `clock_cycle`, `rob_commitInstr`, `BR_MIS_PRED`, `TOTAL_FLUSH`, rolling `ipc/cpi` | retire and bad-spec base signals |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/TopDownGen.scala:91-112` | `EXEC_STALL_CYCLE`, `MEMSTALL_STORE`, `MEMSTALL_L1MISS`, `MEMSTALL_L2MISS`, `MEMSTALL_L3MISS` | backend and memory stall breakdown |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/package.scala:1159-1250` | `TopDownCounters` stall taxonomy | stable bucket names for offline analysis |
| `ref/xiangshan.pdf` printed pages 288-289 | TopDown formulas for Retiring / FrontEnd Bound / Bad Speculation / BackEnd Bound / Memory sub-buckets | analytical interpretation layer |

#### A10.3 Offline weighted comparison

| Mechanism | Confirmed behavior | Evidence |
|---|---|---|
| Completion filter | `top_down.py` only processes finished jobs marked by `EXCEEDING CYCLE/INSTR LIMIT` or `HIT GOOD TRAP`. | `ref_submodule/xiangshan/scripts/top-down/top_down.py:25-37` |
| Weighted per-input aggregation | Metrics are sorted by point and multiplied by point weights from `checkpoint.json`. | `ref_submodule/xiangshan/scripts/top-down/top_down.py:62-95` |
| Weighted whole-benchmark aggregation | Multiple inputs are weighted again by total instruction counts. | `ref_submodule/xiangshan/scripts/top-down/top_down.py:98-118` |
| Issue-width normalization | A/B comparisons can scale weighted metrics by issue-width ratio. | `ref_submodule/xiangshan/scripts/top-down/top_down.py:202-219` |
| Output artifacts | `results_base.csv`, `results_ref.csv`, `results-weighted_base.csv`, `results-weighted_ref.csv`, plus plots. | `ref_submodule/xiangshan/scripts/top-down/README.md:55-78,171-194`; `ref_submodule/xiangshan/scripts/top-down/configs.py:3-7` |

### A11. GPGPU Checkpoint Package Schema

```yaml
gpgpu_checkpoint_package:
  schema_version: 1
  workload:
    suite: string
    kernel_name: string
    input_name: string
    launch_signature: string
    total_kernel_insts: uint64
  phase:
    phase_id: uint64
    interval_insts: uint64
    warmup_insts: uint64
    start_inst: uint64
    measure_start_inst: uint64
    measure_end_inst: uint64
    sample_weight: float
    feature_vector_hash: string
    feature_vector_file: path
  restore:
    golden_state_file: path
    rtl_state_file: path
    memory_image_file: path
    shared_memory_seed_file: path
    restorer_binary: path
    privilege_or_mode_contract: string
  observability:
    counter_schema_version: string
    trace_schema_version: string
    counter_snapshot_before: path
    counter_snapshot_after: path
    required_trace_tables:
      - WARP_ISSUE_LOG
      - MEMORY_TRANSACTION_LOG
      - SCOREBOARD_LOG
  correctness:
    golden_commit_digest: string
    rtl_commit_digest: string
    diff_mode: trace_diff
    known_exclusions: []
  provenance:
    producer_commit:
      nemu_like: string
      rtl: string
      golden_model: string
    generation_command: string
    replay_command: string
```

Rule:

```text
Every representative checkpoint must bind phase metadata, restore state,
trace schema version, and counter schema version.
Otherwise counter deltas and trace deltas are not comparable across revisions.
```

Status:

- `CONFIRMED` XiangShan binds checkpoint to interval index, weight, restore state, and replay tooling.
- `INFERRED` The GPGPU schema above is the required transfer.

### A12. Performance Gate

| Gate | Purpose | Required evidence | Reject if |
|---|---|---|---|
| smoke test | fast correctness sanity | trap status, basic diff pass | used as the only perf evidence |
| microbenchmark | isolate one design mechanism | focused correctness diff, focused counter delta | benchmark phase is not representative of target kernel |
| representative checkpoint | evaluate realistic phase without full replay cost | weighted checkpoint package, warmup contract, replay command | phase weight or interval metadata missing |
| full kernel run | confirm end-to-end behavior when available | whole-kernel correctness and coarse perf | omitted for final sign-off when practical to run |
| counter attribution | prove why performance moved | counter snapshot schema, weighted counter deltas, TopDown bucket movement | only wall-clock/IPC moved without cause |
| trace attribution | connect counter movement to concrete events | structured trace slice, event-level explanation | counter change cannot be tied to events/modules |

Required rule:

```text
Performance optimization cannot be accepted using only toy tests.
It must include correctness diff, representative checkpoint replay, counter attribution,
and a rewrite decision tied to evidence.
```

### A13. Required Evidence Transfer Table

| XiangShan Mechanism | Source Files / Docs | Problem Solved | Transferable GPGPU Abstraction | Skill Rule | Required Schema | Anti-Pattern to Avoid |
|---|---|---|---|---|---|---|
| `[CONFIRMED]` Smoke-vs-real profiling windows | `ref_submodule/xiangshan-nemu/docs/perf_profile.md:106-128,223-229`; `ref_submodule/xiangshan-nemu/tools/perf_profile/report.py:1003-1009,1057-1063` | Prevents trusting unstable or undersampled perf conclusions | phase-gated profiling windows with minimum support thresholds | `[INFERRED]` Reject performance conclusions from smoke-only or low-sample runs | `profiling_run_manifest: {window_insts, mode, sample_counts, warnings[]}` | accepting an optimization because one short run looked faster |
| `[CONFIRMED]` Runtime-triggered BBV interval profiler | `ref_submodule/xiangshan-nemu/src/isa/riscv64/instr/special.h:36-48`; `ref_submodule/xiangshan-nemu/src/cpu/cpu-exec.c:317-329`; `ref_submodule/xiangshan-nemu/src/checkpoint/simpoint.cpp:105-176`; `ref_submodule/xiangshan-nemu/Kconfig:55-68` | Starts profiling at the real workload phase and emits interval features | kernel-phase profiler that starts after launch/setup and emits per-interval phase vectors | `[INFERRED]` Phase features must begin after workload handoff, not during boot or loader noise | `phase_features.yaml` plus `phase_vector.bin` | clustering boot/setup instructions with the target kernel body |
| `[CONFIRMED]` SimPoint clustering into `simpoints0` / `weights0` | `ref_submodule/xiangshan-nemu/scripts/checkpoint_example/cluster.sh:18-22`; `ref_submodule/xiangshan-nemu/resource/simpoint/do_simpoint_clustering.py:29-70,86-100` | Converts many intervals into weighted representative intervals | representative-phase clustering with weight metadata | `[INFERRED]` Perf sampling must preserve representative weights from clustering | `cluster_manifest.json: {interval, points{phase_id: weight}, seeds, algorithm}` | choosing one favorite checkpoint by eye |
| `[CONFIRMED]` Warmup-aware checkpoint scheduler | `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:549-589`; `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:340-341`; official SimPoint doc section `性能分析 / Warm-Up` | Makes replay checkpoints realistic for cache/MMU/predictor state | warmup-before-measure replay contract | `[INFERRED]` Store `warmup_insts` beside every checkpoint and replay `warmup + measure`, not `measure` only | `checkpoint_package.phase.{interval_insts,warmup_insts,measure_start,measure_end}` | replaying only the measured body and calling it realistic |
| `[CONFIRMED]` Structured checkpoint package with naming and restore contract | `ref_submodule/xiangshan-nemu/src/checkpoint/path_manager.cpp:57-109`; `ref_submodule/xiangshan-nemu/src/checkpoint/serializer.cpp:215-366,376-476`; `ref_submodule/xiangshan-nemu/README.md:195-239` | Makes checkpoints restartable and attributable | versioned checkpoint bundle with restore binary and state payload | `[INFERRED]` Each replayable GPGPU checkpoint must include phase ID, restore state, and observability schema version | `gpgpu_checkpoint_package` | unlabeled memory dumps that cannot be compared across revisions |
| `[CONFIRMED]` Auxiliary checkpoint modes: uniform / manual / semantic | `ref_submodule/xiangshan-nemu/src/profiling/profiling_control.h:11-19`; `ref_submodule/xiangshan-nemu/scripts/checkpoint_example/{uniform_cpt.sh,manual_uniform_cpt.sh,manual_oneshot_cpt.sh,semantic_checkpoint.sh}:1-21`; `ref_submodule/xiangshan-nemu/src/checkpoint/semantic_point.cpp:46-167` | Supports debugging and ad hoc snapshot capture beyond SimPoint | secondary sampling/debug modes | `[INFERRED]` Allow debug-only snapshot modes, but do not let them bypass representative-phase gates | `snapshot_mode: simpoint | uniform | manual | semantic` | using manual Ctrl-C checkpoints as evidence for final performance claims |
| `[CONFIRMED]` Host-side `perf_profile.py` run bundle | `ref_submodule/xiangshan-nemu/docs/perf_profile.md:185-219`; `ref_submodule/xiangshan-nemu/tools/perf_profile/cli.py:143-166,301-340`; `ref_submodule/xiangshan-nemu/tools/perf_profile/collect/{stat.py,record.py}:25-40,75-180`; `ref_submodule/xiangshan-nemu/tools/perf_profile/report.py:840-1109` | Keeps raw perf data, parsed artifacts, warnings, and reports together | manifest-backed profiler output bundle | `[INFERRED]` Every GPGPU profiler run must emit raw, parsed, reports, and manifest artifacts together | `perf_bundle/{manifest.json,raw/,parsed/,reports/,logs/}` | pasting screenshots or ad hoc text instead of durable artifacts |
| `[CONFIRMED]` HPM selector/counter fabric | `ref/xiangshan.pdf` printed pages 274-277; `ref_submodule/xiangshan/src/main/scala/xiangshan/XSCore.scala:176-180,195`; `ref_submodule/xiangshan/src/main/scala/xiangshan/frontend/ibuffer/IBuffer.scala:483-497`; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala:1708-1724` | Separates event production from event selection and accumulation | module-emitted performance events routed into a central selector/counter fabric | `[INFERRED]` GPGPU counters must be selectable and composable, not hardwired one-off debug signals | `counter_catalog.yaml: {event_name, module, meaning, aggregation_domain}` | adding bespoke counters that cannot be routed, versioned, or compared |
| `[CONFIRMED]` TopDown formulas plus weighted post-processing | `ref/xiangshan.pdf` printed pages 288-289; `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/TopDownGen.scala:99-112`; `ref_submodule/xiangshan/src/main/scala/xiangshan/package.scala:1159-1250`; `ref_submodule/xiangshan/scripts/top-down/top_down.py:62-95,120-158,202-219`; `ref_submodule/xiangshan/scripts/top-down/resources/spec06_rv64gcb_o2_20m.json:1-30` | Turns counter movement into bottleneck attribution and whole-workload comparison | weighted counter attribution with stable bucket taxonomy | `[INFERRED]` A performance change is incomplete until it is mapped to a stable bucket and weighted across representative phases | `attribution_report.json: {bucket_deltas, weights, scaling, evidence_links}` | claiming “IPC improved” without explaining which bottleneck moved |
| `[CONFIRMED]` Negative evidence from `PMParameters.scala` | `ref_submodule/xiangshan/src/main/scala/xiangshan/PMParameters.scala:25-60` | Prevents reading the wrong file as the source of HPM semantics | name-vs-content validation | `[INFERRED]` Validate that a “performance” file actually defines performance contracts before reusing it | `source_audit: {file, reason_used, reason_rejected}` | cargo-culting similarly named files into the skill |

### A14. Full Quality Gate

#### Evidence Gate

| Check | Result | Notes |
|---|---|---|
| Scope declared | PASS | metadata lists files read, skipped, focus, non-goals |
| Planner focus answered | PASS | all nine extraction questions answered in Part A/A2-A13 |
| Evidence attached | PASS | every planning-relevant claim carries local file anchors or official doc anchors |
| Claim status used | PASS | `CONFIRMED`, `INFERRED`, `MISSING`, `PARTIAL` used explicitly |
| Contradictions reported | PASS | no internal source conflicts found for core flow; one naming trap and one external-gap caveat recorded |
| Missing contracts reported | PASS | external `env-scripts` producer and local HPerfMonitor RTL gap recorded |
| Handoff actionable | PASS | next actions, rules, schemas, and anti-patterns are concrete |

#### Readability Gate

| Check | Result | Notes |
|---|---|---|
| Handoff length | PASS | Part A is compact; detail moved to appendix |
| Findings capped | PASS | Part A findings capped |
| Tables limited | PASS | wide tables confined to appendix |
| Empty sections removed | PASS | only relevant sections kept |
| Decision relevance | PASS | every section supports GPGPU performance-sampling rule transfer |
| Appendix separation | PASS | detailed evidence is in Part B |

#### Repository Extra Gate

| Topic | Status | Notes |
|---|---|---|
| ISA semantics | not applicable | outside pass scope |
| instruction encoding | not applicable | outside pass scope |
| decode path | not applicable | outside pass scope |
| PC / warp state | inferred | appears only in proposed GPGPU checkpoint schema |
| active mask | inferred | appears only in proposed GPGPU phase/checkpoint schema |
| SIMT divergence | inferred | appears in proposed GPGPU phase features |
| register file | confirmed | checkpoint package must save architectural register state |
| scoreboard / hazards | inferred | required for GPGPU trace/counter schema, not local XiangShan checkpoint code |
| issue / execute / writeback | confirmed | XiangShan TopDown measures issue/retire stalls through event taxonomy |
| memory coalescing | inferred | target GPGPU phase feature/counter, not a XiangShan checkpoint feature |
| shared memory | inferred | target GPGPU checkpoint/trace concern |
| barrier semantics | inferred | target GPGPU phase feature/counter concern |
| CSR / DCR / config state | confirmed | XiangShan checkpoint serializer stores CSR and mode state |
| launch protocol | confirmed | profiling begins only after explicit workload handoff |
| kernel arguments | inferred | should be part of GPGPU launch signature in checkpoint package |
| grid/block/warp mapping | inferred | should be part of GPGPU checkpoint metadata |
| CModel / golden model | confirmed | NEMU is the golden-side producer of checkpoints and profiler outputs |
| trace diff / compare path | inferred | required by the acceptance rule, though not implemented in this pass |
| tests and coverage | partial | example scripts exist; no local regression corpus for this pass |
| synthesis / FPGA / PPA evidence | not applicable | outside pass scope |

## Quality Gate

- Overall status: PASS
- Evidence status: PASS
- Readability status: PASS
- Safe for GPT-5.5 planning: yes, with caveats
- Full appendix generated: yes
- Biggest evidence gap: the local corpus does not include the external `env-scripts` producer that turns checkpoint runs into the stat-directory and `checkpoint.json` artifacts consumed by XiangShan top-down analysis
- Biggest readability issue: none material; the evidence table is intentionally dense
- Required next read: external checkpoint runner / manifest producer and XiangShan CSR/HPerfMonitor RTL if implementation-level HPM selector details become necessary
