# XiangShan Repository Map for GPGPU Skill

## 0. Metadata

- Mode: `repository`
- Depth: `deep`
- Output profile: `model-evidence`
- Focus: development-loop infrastructure only; build, simulation, difftest, debug, trace, checkpoint, and performance entry points
- Non-goals: CPU frontend, branch predictor, rename, ROB, issue queues, CSR semantics, RVV semantics, detailed RISC-V pipeline behavior unless needed for tooling context
- Corpus:
  - `ref_submodule/xiangshan` at `5ff19c2`
  - `ref_submodule/xiangshan-nemu` at `75d0019`
  - `ref/xiangshan.pdf` inventoried only in this pass (`pdfinfo`: 561 pages, created 2025-03-18)
- Files read:
  - `ref/skillref/xiangshan.md:1-1046`
  - `ref_submodule/xiangshan/{README.md,readme.zh-cn.md,Makefile,build.mill}`
  - `ref_submodule/xiangshan/src/main/scala/top/{Top.scala,ArgParser.scala,Configs.scala}`
  - `ref_submodule/xiangshan/src/test/scala/top/SimTop.scala`
  - `ref_submodule/xiangshan/scripts/{xiangshan.py,Makefile.pdb}`
  - `ref_submodule/xiangshan/scripts/top-down/README.md`
  - `ref_submodule/xiangshan/docs/XSPdb/README.md`
  - `ref_submodule/xiangshan-nemu/{README.md,docs/perf_profile.md,docs/ref_so_runner.md}`
  - `ref_submodule/xiangshan-nemu/scripts/checkpoint_example/{checkpoint_env.sh,profiling.sh,cluster.sh,checkpoint.sh}`
  - `ref_submodule/xiangshan-nemu/tools/perf_profile.py`
- Files skipped:
  - deep microarchitecture code under `src/main/scala/xiangshan/frontend`, most of `backend`, most of `mem`, most of `cache`
  - `ref/xiangshan.pdf` content beyond repository inventory
  - uninitialized submodules `ref_submodule/xiangshan/{difftest,XSCache,ready-to-run}`
- Confidence: `High` for repository map and tool entry points; `Medium` for difftest/build internals gated by missing local submodules

## 1. XiangShan Role

XiangShan is useful for a GPGPU skill as a reference for agile hardware-development closure, not as a CPU template. The local README frames the project and its MICRO 2022 paper around agile development, functional verification, debugging, and performance validation rather than only around CPU structure (`ref_submodule/xiangshan/README.md:21-31`). The local tree reinforces that split: top generation and tool toggles live in `src/main/scala/top`, simulator closure in `src/test/scala/top/SimTop.scala`, repeatable flows in `scripts/`, interactive debug in `docs/XSPdb/` and `scripts/xspdb/`, and golden-model / checkpoint / profiling flows in `xiangshan-nemu` (`ref_submodule/xiangshan/README.md:59-78`, `ref_submodule/xiangshan-nemu/README.md:59-67`).

## 2. Local Evidence Boundary

| Item | Status | Evidence | Impact on Pass 0 |
|---|---|---|---|
| `ref_submodule/xiangshan/difftest` | `MISSING` | `git -C ref_submodule/xiangshan submodule status` shows leading `-` for `difftest`; local directory exists but is uninitialized (`ls -ld ref_submodule/xiangshan/difftest`) | Build and runtime calls into `./difftest` can be mapped only at the call boundary, not inside the framework |
| `ref_submodule/xiangshan/XSCache` | `MISSING` | same submodule-status evidence; local directory is uninitialized | Cache-related build/module dependencies can be named, but local cache implementation should not be inferred |
| `ref_submodule/xiangshan/ready-to-run` | `MISSING` | same submodule-status evidence; local directory is uninitialized | Example binaries and ref `.so` paths in README cannot be replayed from this checkout |
| `ref_submodule/xiangshan/verilator.mk` | `MISSING` | README points users to `Makefile` and `verilator.mk` for simulator details, but no local `verilator.mk` exists (`ref_submodule/xiangshan/README.md:112-116`; `find ref_submodule/xiangshan -maxdepth 1 -name 'verilator.mk'` returns empty) | Use `Makefile`, `ArgParser.scala`, `Top.scala`, and `SimTop.scala` as the local source of truth for Pass 0 |
| `build.mill` resource packaging depends on missing submodules | `CONFIRMED` | `build.mill` packages difftest sources and ready-to-run binaries from local submodule paths (`ref_submodule/xiangshan/build.mill:197-214`) | Pass 0 must keep a hard evidence boundary around packaged difftest / ready-to-run assets |

## 3. Useful Directories

| XiangShan Path | XiangShan Role | GPGPU Skill Lesson | Source Anchors |
|---|---|---|---|
| `ref_submodule/xiangshan/src/main/scala/top` | top generation, debug/perf/difftest tool enablement, build-time flag parsing | keep one top-level switchboard for debug, diff, DB, and feature gates | `ref_submodule/xiangshan/README.md:63-78`; `ref_submodule/xiangshan/src/main/scala/top/ArgParser.scala:34-54,64-257`; `ref_submodule/xiangshan/src/main/scala/top/Top.scala:409-447` |
| `ref_submodule/xiangshan/src/test/scala/top` | simulation-only harness closure with memory, MMIO, JTAG, UART, log/perf wiring | keep a separate sim harness module that owns test-only plumbing | `ref_submodule/xiangshan/src/test/scala/top/SimTop.scala:90-177,179-199` |
| `ref_submodule/xiangshan/src/main/scala/system` | SoC wrapper layer used by top-level generation | isolate SoC integration from tool-control surfaces | `ref_submodule/xiangshan/README.md:66-71`; directory inventory from `find ref_submodule/xiangshan/src/main/scala -maxdepth 2 -type d` |
| `ref_submodule/xiangshan/src/main/scala/device` | simulation devices and adapters | put simulator-only devices behind explicit device/module boundaries | `ref_submodule/xiangshan/README.md:66-69`; directory inventory from `find ref_submodule/xiangshan/src/main/scala -maxdepth 2 -type d` |
| `ref_submodule/xiangshan/src/main/scala/xiangshan` | main design code, including backend/mem/cache/frontend subtrees | treat this tree as the producer of probe points and counters, not as a GPGPU microarchitecture template | `ref_submodule/xiangshan/README.md:69-72`; directory inventory from `find ref_submodule/xiangshan/src/main/scala -maxdepth 2 -type d` |
| `ref_submodule/xiangshan/scripts` | repo-local orchestration for build, run, coverage, perf, rolling DB, and top-down analysis | encode repeatable development loops as versioned scripts, not wiki-only commands | `ref_submodule/xiangshan/README.md:73-78`; `ref_submodule/xiangshan/scripts/xiangshan.py:756-816`; `find ref_submodule/xiangshan/scripts -maxdepth 3 -type f` |
| `ref_submodule/xiangshan/scripts/xspdb` | interactive CLI, batch scripts, wave control, trigger handling | debugger command surface should be scriptable and batchable | `ref_submodule/xiangshan/docs/XSPdb/README.md:3-11,44-66`; directory inventory from `find ref_submodule/xiangshan/scripts/xspdb -maxdepth 2 -type d` |
| `ref_submodule/xiangshan/scripts/top-down` | post-checkpoint Top-down counter analysis and weighted comparison plots | separate raw counter collection from attribution/visualization tooling | `ref_submodule/xiangshan/scripts/top-down/README.md:3-5,23-79,119-194` |
| `ref_submodule/xiangshan/docs/XSPdb` | debugger design notes and usage examples | pair debug tools with design docs and sample scripts in-repo | `ref_submodule/xiangshan/docs/XSPdb/README.md:13-40` |
| `ref_submodule/xiangshan-nemu/configs` | reference-mode and standalone-mode configuration entry points | keep multiple golden-model personas under named, checked-in configs | `ref_submodule/xiangshan-nemu/README.md:152-163`; `find ref_submodule/xiangshan-nemu/configs -maxdepth 2 -type f` |
| `ref_submodule/xiangshan-nemu/src/cpu/difftest` and `src/isa/riscv64/difftest` | NEMU-side dut/ref adaptation hooks for difftest | keep DUT/reference glue in a narrow adapter layer | directory inventory from `find ref_submodule/xiangshan-nemu/src/cpu/difftest ref_submodule/xiangshan-nemu/src/isa/riscv64/difftest -maxdepth 2 -type f`; `ref_submodule/xiangshan-nemu/README.md:61-65,150-175` |
| `ref_submodule/xiangshan-nemu/src/checkpoint` | checkpoint / SimPoint implementation support | make long-workload reduction first-class, not an afterthought | directory inventory from `find ref_submodule/xiangshan-nemu/src/checkpoint -maxdepth 2 -type f`; `ref_submodule/xiangshan-nemu/README.md:109-138,191-203` |
| `ref_submodule/xiangshan-nemu/src/profiling` | workload profiling support | isolate profiling-control code from core emulation | directory inventory from `find ref_submodule/xiangshan-nemu/src/profiling -maxdepth 2 -type f`; `ref_submodule/xiangshan-nemu/README.md:65-67` |
| `ref_submodule/xiangshan-nemu/scripts/checkpoint_example` | runnable scripts for profile -> cluster -> checkpoint flow | ship end-to-end scripts, not just abstract docs | `find ref_submodule/xiangshan-nemu/scripts/checkpoint_example -maxdepth 2 -type f`; `checkpoint_env.sh:3-13`; `profiling.sh:5-14`; `cluster.sh:5-22`; `checkpoint.sh:5-15` |
| `ref_submodule/xiangshan-nemu/tools/ref-so-runner` | standalone launcher for ref shared object benchmarking | benchmark the golden-model library outside the DUT harness too | `ref_submodule/xiangshan-nemu/docs/ref_so_runner.md:3-31` |
| `ref_submodule/xiangshan-nemu/tools/perf_profile` | host-side `perf` pipeline with raw/parsed/report outputs | keep host-profiler output structured and reproducible | `ref_submodule/xiangshan-nemu/docs/perf_profile.md:3-5,177-219`; `ref_submodule/xiangshan-nemu/tools/perf_profile.py:1-21` |

## 4. What Not To Transfer

- Do not transfer XiangShan CPU frontend, branch predictor, rename, ROB, issue queues, or execution-pipeline structures into a GPGPU skill. These are non-goals for this shard (`ref/skillref/xiangshan.md:918-929`).
- Do not transfer RISC-V CSR semantics, RVV semantics, or XiangShan-specific trap/debug meanings except where they define a generic debug or diff interface boundary (`ref/skillref/xiangshan.md:916-923`).
- Do not copy XiangShan workload assumptions such as `ready-to-run` binaries, AM/Linux image layout, or NEMU-specific restore binaries as a GPGPU ABI.
- Do not transfer raw directory names as architecture rules. Transfer only the reusable mechanisms: top-level switchboards, harness closure, golden-model adapters, failure-capture scripts, structured trace flows, checkpoint flows, and performance attribution flows.
- Do not infer behavior from missing local submodules. For `difftest`, `XSCache`, and `ready-to-run`, use `MISSING` and switch to official docs in later passes.

## 5. Build / Sim / Difftest / XSPdb / NEMU / Checkpoint / Perf Entry Points

| Surface | Entry Point | Confirmed Command or Switch | Why It Matters for GPGPU Skill | Source Anchors |
|---|---|---|---|---|
| Verilog generation | `make verilog` -> `top.TopMain` | `make verilog`; `mill -i ... xiangshan.runMain top.TopMain --target-dir ... --config ...` | one canonical hardware-generation entry point | `ref_submodule/xiangshan/README.md:93-96`; `ref_submodule/xiangshan/Makefile:270-277` |
| Sim harness generation | `make sim-verilog` -> `top.XiangShanSim` | `make sim-verilog`; `mill -i ... xiangshan.test.runMain top.XiangShanSim ... $(SIM_ARGS)` | sim-only harness is generated from a separate entry point | `ref_submodule/xiangshan/Makefile:279-302`; `ref_submodule/xiangshan/src/test/scala/top/SimTop.scala:179-199` |
| Verilator/GSIM build | `make emu` / `make gsim` | `make emu`; `make gsim GSIM=1`; both delegate into `./difftest` | DUT build is explicitly coupled to difftest build infrastructure | `ref_submodule/xiangshan/README.md:112-122`; `ref_submodule/xiangshan/Makefile:341-348` |
| Difftest enablement in top | `ArgParser` + `TopMain` | `--enable-difftest`; `DifftestModule.parseArgs(args)`; `DifftestModule.top(...)`; `DifftestModule.collect("XiangShan")` | build/run flags and top wrapping stay synchronized | `ref_submodule/xiangshan/src/main/scala/top/ArgParser.scala:45-54,122-125,241-257`; `ref_submodule/xiangshan/src/main/scala/top/Top.scala:414-447` |
| ChiselDB / Constantin toggles | `Makefile`, `ArgParser`, `TopMain`, `SimTop` | `WITH_CHISELDB=1`, `WITH_CONSTANTIN=1`, `--with-chiseldb`, `--with-constantin` | debug/perf databases and runtime-tunable constants are optional, explicit tool surfaces | `ref_submodule/xiangshan/Makefile:166-194`; `ref_submodule/xiangshan/src/main/scala/top/ArgParser.scala:102-113`; `ref_submodule/xiangshan/src/main/scala/top/Top.scala:413-418`; `ref_submodule/xiangshan/src/test/scala/top/SimTop.scala:183-199` |
| XSPdb build/run | `make pdb`, `make pdb-run`, `python3 scripts/pdb-run.py` | `make pdb`; `make pdb-run`; batch mode `python3 scripts/pdb-run.py --script ...` | interactive and batch debug paths are both first-class | `ref_submodule/xiangshan/README.md:123-163`; `ref_submodule/xiangshan/scripts/Makefile.pdb:36-64`; `ref_submodule/xiangshan/docs/XSPdb/README.md:44-60` |
| Wrapper CLI | `python3 scripts/xiangshan.py` | `--generate`, `--build`, `--diff`, `--disable-fork`, `--dump-db`, `--with-constantin`, `--simfrontend`, `workload` | a single wrapper CLI normalizes env, build args, run args, and CI-oriented options | `ref_submodule/xiangshan/scripts/xiangshan.py:47-170,233-259,276-297,756-816` |
| NEMU reference mode | NEMU README + configs | `make xxx-ref_defconfig && make -j`; generated `./build/riscv64-nemu-interpreter-so`; DUT runs with `--diff ...so` | golden model is a build artifact, not a sidecar assumption | `ref_submodule/xiangshan-nemu/README.md:71-85,150-175`; `find ref_submodule/xiangshan-nemu/configs -maxdepth 2 -type f` |
| NEMU standalone + checkpoint flow | checkpoint example scripts | profile with `--simpoint-profile --cpt-interval`; cluster via SimPoint; checkpoint via `-S ... --cpt-interval ... --checkpoint-format zstd` | long workloads are reduced through a reproducible script chain | `ref_submodule/xiangshan-nemu/README.md:109-138,191-203`; `checkpoint_env.sh:3-13`; `profiling.sh:5-14`; `cluster.sh:5-22`; `checkpoint.sh:5-15` |
| NEMU ref shared-object runner | `tools/ref-so-runner/runner` | `tools/ref-so-runner/gen-xs-ref-perf-defconfig.sh ...`; `make ...`; `runner -b <image>` | golden-model performance can be measured outside difftest-in-DUT runs | `ref_submodule/xiangshan-nemu/docs/ref_so_runner.md:3-31` |
| Host-side NEMU perf | `python3 tools/perf_profile.py run` | `doctor`, `stat`, `record`, `report`, `run` subcommands; run directory with `raw/ parsed/ reports/` | host-side profiling artifacts are versioned and structured | `ref_submodule/xiangshan-nemu/docs/perf_profile.md:3-5,22-46,138-219`; `ref_submodule/xiangshan-nemu/tools/perf_profile.py:17-21` |
| Top-down checkpoint attribution | `scripts/top-down/top_down.py` and `draw.py` | `python top_down.py -b ... -r ... -j ...`; outputs weighted CSV and stacked-bar plots | performance attribution is separated from raw run generation | `ref_submodule/xiangshan/scripts/top-down/README.md:23-79,139-229` |

## 6. Official Docs Required Because Local Evidence Is Missing

| Missing Local Area | Why Local Evidence Is Insufficient | Required Official Doc Anchor | Current Pass Status |
|---|---|---|---|
| DiffTest framework internals | local `ref_submodule/xiangshan/difftest` is uninitialized, but `make emu`, `make gsim`, `make pdb`, and top-level difftest wrapping all depend on it | `https://docs.xiangshan.cc/zh-cn/latest/tools/difftest/` listed in the primary plan (`ref/skillref/xiangshan.md:955-968`) | `MISSING` locally; doc read deferred to Pass 1 |
| LightSSS fork-based failure capture policy | local wrapper CLI exposes `--enable-fork` / `--disable-fork`, but the dedicated tool contract is not in the local code read set for this pass | `https://docs.xiangshan.cc/zh-cn/latest/tools/lightsss/` listed in the primary plan (`ref/skillref/xiangshan.md:985-993`) | `UNCERTAIN` until Pass 4 |
| ChiselDB structured-trace contract | local toggles and file-register hooks are present, but schema/query semantics are not established in this pass | `https://docs.xiangshan.cc/zh-cn/latest/tools/chiseldb/` listed in the primary plan (`ref/skillref/xiangshan.md:996-1004`) | `UNCERTAIN` until Pass 5 |
| Constantin runtime-DSE contract | local toggles are present, but record schema and runtime override semantics are not established in this pass | `https://docs.xiangshan.cc/zh-cn/latest/tools/constantin/` listed in the primary plan (`ref/skillref/xiangshan.md:1006-1013`) | `UNCERTAIN` until Pass 6 |
| SimPoint / checkpoint doc-level flow | local NEMU scripts exist, but the full doc contract for checkpoint generation and restoration is defined outside this pass | `https://docs.xiangshan.cc/zh-cn/latest/tools/simpoint/` listed in the primary plan (`ref/skillref/xiangshan.md:1015-1026`) | `CONFIRMED` as required next read for Pass 7 |

## 7. Evidence Table

| XiangShan Mechanism | Source Files / Docs | Problem Solved | Transferable GPGPU Abstraction | Skill Rule | Required Schema | Anti-Pattern to Avoid |
|---|---|---|---|---|---|---|
| `CONFIRMED: Unified top-level tool switchboard` | `ref_submodule/xiangshan/Makefile:166-194,270-348`; `ref_submodule/xiangshan/src/main/scala/top/ArgParser.scala:34-54,98-149,241-257`; `ref_submodule/xiangshan/src/main/scala/top/Top.scala:409-447` | build/run/debug/perf knobs stay synchronized instead of drifting across scripts | one GPGPU `tool_control` surface spanning generation, sim harness, diff, DB, and perf toggles | every reusable GPGPU tool feature must have exactly one build-time owner, one CLI flag, and one top/harness integration point | `tool_control.schema = {name, stage:[gen|sim|run], cli_flag, make_var, owner_file, default, artifact_outputs[]}` | ad hoc `ifdef` islands with no repo-wide manifest |
| `CONFIRMED: Separate sim harness closure` | `ref_submodule/xiangshan/src/test/scala/top/SimTop.scala:90-177,179-199` | simulation-only memory, MMIO, JTAG, UART, and perf/log wiring stay out of the hardware top | a dedicated `sim_harness` module for GPGPU DUT closure | keep simulation plumbing in a test-only top that can be regenerated and versioned independently of the DUT top | `sim_harness.schema = {dut_top, memory_model, mmio_model, debug_io, uart_io, log_ctrl, perf_ctrl, optional_diff_memio}` | stuffing test-only devices directly into production RTL top |
| `CONFIRMED: Repo-local orchestration CLI` | `ref_submodule/xiangshan/scripts/xiangshan.py:47-170,233-259,276-297,756-816` | developers need one stable command surface for generate/build/run/CI across environments | a GPGPU `run_recipe` wrapper CLI with env normalization and reproducible arguments | ship one repo-local orchestration entry point for build and run modes; document raw commands second | `run_recipe.schema = {action, env_vars, chisel_args[], make_args[], emu_args[], workload, wave_dir, outputs[]}` | tribal-knowledge shell snippets scattered across wiki pages |
| `CONFIRMED: Interactive + batch debugger surface` | `ref_submodule/xiangshan/docs/XSPdb/README.md:3-11,13-40,44-66`; `ref_submodule/xiangshan/scripts/Makefile.pdb:38-64` | failure localization needs breakpoints, wave control, scripted replay, and command discovery | a GPGPU `debug_cli` contract that supports both TUI/interactive and batch scripts | every debug action must be invocable both interactively and from a checked-in script | `debug_cli.schema = {command, args, category:[break|watch|wave|state|batch], batchable, output_artifacts[]}` | waveform-only debugging with no reproducible command script |
| `CONFIRMED: Golden model in shared-object and standalone forms` | `ref_submodule/xiangshan-nemu/README.md:61-67,150-175`; `ref_submodule/xiangshan-nemu/docs/ref_so_runner.md:3-31`; `find ref_submodule/xiangshan-nemu/configs -maxdepth 2 -type f` | the same reference engine serves diff, checkpoint production, standalone run, and host-side benchmarking | a GPGPU `golden_model` with library mode and standalone mode | golden models should expose both co-sim and standalone entry points, not only an ISS binary or only an in-sim DPI library | `golden_model.schema = {mode:[shared_so|standalone], config, load_image, init, step, trap_status, max_instr, stats}` | a golden model that can only run inside one simulator integration |
| `CONFIRMED: Scripted profile -> cluster -> checkpoint flow` | `ref_submodule/xiangshan-nemu/README.md:109-138,191-203`; `checkpoint_env.sh:3-13`; `profiling.sh:5-14`; `cluster.sh:5-22`; `checkpoint.sh:5-15` | detailed simulation of long workloads must be reduced to representative windows and restartable states | a GPGPU `phase_sampling` flow with explicit profile, cluster, and checkpoint stages | make sampling and checkpoint generation first-class repo scripts with stable environment variables and output directories | `phase_sampling.schema = {workload, interval, bbv_path, simpoints_path, weights_path, checkpoint_dir, restore_bin, format}` | benchmarking only from full workloads with no restartable representative states |
| `CONFIRMED: Structured perf artifact layout` | `ref_submodule/xiangshan-nemu/docs/perf_profile.md:3-5,22-46,177-219`; `ref_submodule/xiangshan-nemu/tools/perf_profile.py:17-21` | host-side performance work needs raw data, parsed artifacts, manifests, and reports kept together | a GPGPU `perf_run` bundle for host-side profiling | profiling flows must emit raw, parsed, and rendered outputs under one run directory with a manifest | `perf_run.schema = {mode, workload, guest_instr_budget, manifest, raw_dir, parsed_dir, reports_dir, summary}` | one-off `perf record` files with no manifest or regenerated report path |
| `CONFIRMED: Weighted Top-down post-processing` | `ref_submodule/xiangshan/scripts/top-down/README.md:23-79,139-229` | raw checkpoint stats need aggregation, weighting, and base/ref comparison before rewrite decisions | a GPGPU `counter_attribution` stage separated from raw simulation | separate counter extraction from attribution and plotting; preserve per-point raw stats and weighted summaries | `counter_attribution.schema = {base_stat_dir, ref_stat_dir?, checkpoint_json, base_issue, ref_issue, weighted_csvs[], plots[]}` | rewriting based on a single aggregate number with no per-phase attribution |
| `MISSING: Honest evidence boundary around submodules` | `git -C ref_submodule/xiangshan submodule status`; `ref_submodule/xiangshan/build.mill:197-214`; `ref/skillref/xiangshan.md:31-37` | large hardware repos often ship critical tooling as submodules; local checkouts may be incomplete | a GPGPU `evidence_boundary` rule that blocks unsupported inference | if a local submodule is uninitialized, mark it `MISSING`, cite the gap, and fall back to official docs before transferring its mechanism | `evidence_boundary.schema = {component, local_status, blocking_surfaces[], fallback_docs[], allowed_inference_scope}` | inferring missing tool behavior from directory names or README examples alone |

## 8. Quality Gate Detail

### 8.1 Evidence Gate

| Check | Status | Notes |
|---|---|---|
| Scope declared | `PASS` | files read, skipped, corpus, non-goals, and pass boundaries are listed in metadata |
| Planner focus answered | `PASS` | report stays on development-loop infrastructure and repository/tool map only |
| Evidence attached | `PASS` | all planning-relevant rows have narrow file, line, script, or command anchors |
| Claim status used | `PASS` | `CONFIRMED`, `UNCERTAIN`, and `MISSING` are used explicitly |
| Contradictions reported | `PASS` | one local mismatch is recorded: README references `verilator.mk`, but the file is absent |
| Missing contracts reported | `PASS` | uninitialized submodules and later-pass doc dependencies are explicit |
| Handoff actionable | `PASS` | next read is concrete: DiffTest docs and local difftest-dependent top surfaces |

### 8.2 Readability Gate

| Check | Status | Notes |
|---|---|---|
| Handoff length | `PASS` | appendix artifact is dense but scoped to Pass 0 only |
| Findings capped | `PASS` | reusable mechanisms are summarized in one evidence table |
| Tables limited | `PASS` | tables are used for repository map content, not long prose |
| Empty sections removed | `PASS` | only requested sections are present |
| Decision relevance | `PASS` | each section maps XiangShan mechanisms to GPGPU skill rules |
| Appendix separation | `PASS` | this file is the model-evidence artifact; chat handoff remains concise |

### 8.3 Repository Extra Gate

| Topic | Status | Notes |
|---|---|---|
| ISA semantics | `not applicable` | intentionally excluded in Pass 0 |
| instruction encoding | `not applicable` | intentionally excluded in Pass 0 |
| decode path | `not applicable` | intentionally excluded in Pass 0 |
| PC / warp state | `not applicable` | deferred; this pass maps tool surfaces only |
| active mask | `not applicable` | deferred; this pass maps tool surfaces only |
| SIMT divergence | `not applicable` | deferred; this pass maps tool surfaces only |
| register file | `not applicable` | deferred; this pass maps tool surfaces only |
| scoreboard / hazards | `not applicable` | deferred; this pass maps tool surfaces only |
| issue / execute / writeback | `not applicable` | deferred; this pass maps tool surfaces only |
| memory coalescing | `not applicable` | deferred; this pass maps tool surfaces only |
| shared memory | `not applicable` | deferred; this pass maps tool surfaces only |
| barrier semantics | `not applicable` | deferred; this pass maps tool surfaces only |
| CSR / DCR / config state | `inferred` | only generic config/debug flag management is relevant here (`ArgParser.scala`, `Configs.scala`) |
| launch protocol | `not applicable` | XiangShan is CPU-oriented; this shard is infrastructure-only |
| kernel arguments | `not applicable` | XiangShan is CPU-oriented; this shard is infrastructure-only |
| grid/block/warp mapping | `not applicable` | XiangShan is CPU-oriented; this shard is infrastructure-only |
| CModel / golden model | `confirmed` | `xiangshan-nemu` reference mode, standalone mode, and ref-so runner are explicit |
| trace diff / compare path | `confirmed` | local top/Makefile expose difftest entry points; internals remain blocked by missing submodule |
| tests and coverage | `inferred` | repo-local scripts include coverage helpers and CI wrapper surfaces, but this pass did not deep-read test suites |
| synthesis / FPGA / PPA evidence | `inferred` | top and parser expose FPGA-platform toggles, but PPA evidence is outside Pass 0 scope |

## Quality Gate

- Overall status: `PARTIAL`
- Evidence status: `PARTIAL` because Pass 0 repository and tool-map claims are source-backed, but difftest/XSCache/ready-to-run internals are blocked by uninitialized local submodules
- Readability status: `PASS`
- Safe for GPT-5.5 planning: `yes, with caveats`
- Full appendix generated: `yes`
- Biggest evidence gap: local `difftest` submodule is uninitialized, yet `make emu`, `make gsim`, and `make pdb` all depend on it
- Biggest readability issue: some source anchors rely on inventory-command output because the relevant local code is missing
- Required next read: official DiffTest docs plus `Top.scala` / backend probe sites for Pass 1 trace-diff extraction
