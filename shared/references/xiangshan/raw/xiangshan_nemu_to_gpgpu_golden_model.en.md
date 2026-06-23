# Repository Architecture Report

## Part A. Human Handoff

### 0. Metadata

- Mode: repository
- Depth: deep
- Output profile: model-evidence
- Repo / subsystem: XiangShan NEMU golden-model interface, `ref_submodule/xiangshan-nemu` @ `75d0019`; XiangShan simulator command context only, `ref_submodule/xiangshan` @ `5ff19c2`
- Files read: `ref/skillref/xiangshan.md` sections 0-3/6/12; `skill/reader/SKILL.md`; `skill/reader/references/{output-policy,repository-mode-template,quality-gate}.md`; `ref_submodule/xiangshan-nemu/{README.md,Kconfig,Makefile,docs/ref_so_runner.md,docs/perf_profile.md,configs/riscv64-xs{-ref,_defconfig,-cpt_defconfig,-cpt-with-libcheckpoint_defconfig},src/cpu/difftest/{ref.c,dut.c},src/isa/riscv64/difftest/{ref.c,dut.c},src/isa/riscv64/include/isa-def.h,src/isa/riscv64/instr/special.h,src/cpu/cpu-exec.c,src/memory/{paddr.c,store_queue_wrapper.cpp},src/device/{device.c,flash.c,io/mmio.c},src/monitor/{monitor.c,image_loader.c},src/checkpoint/{serializer.cpp,simpoint.cpp},src/profiling/profiling_control.c,include/{cpu/difftest.h,memory/paddr.h,profiling/profiling_control.h},lib-include/difftest.h,tools/ref-so-runner/{runner.c,gen-xs-ref-perf-defconfig.sh}}`; `ref_submodule/xiangshan/README.md`; official docs URL `https://docs.xiangshan.cc/zh-cn/latest/tools/nemu/`
- Files skipped: broad ISA instruction semantics, unrelated device internals, most XiangShan RTL, and uninitialized `ref_submodule/xiangshan/difftest`
- Entry points inspected: build/config (`README.md`, official docs, `Kconfig`, `Makefile`, `scripts/build.mk`, `scripts/isa.mk`); reference export path (`src/cpu/difftest/ref.c`, `src/isa/riscv64/difftest/ref.c`); exemplar consumer path (`src/cpu/difftest/dut.c`, `src/isa/riscv64/difftest/dut.c`, `tools/ref-so-runner/runner.c`); standalone checkpoint/profiling path (`src/monitor/monitor.c`, `src/cpu/cpu-exec.c`, `src/checkpoint/*`, `src/profiling/*`); MMIO/device path (`src/memory/paddr.c`, `src/device/*`)
- Focus: reusable NEMU golden-model integration mechanisms for a GPGPU skill; not RISC-V ISA study except sync/control/MMIO/checkpoint behavior
- Questions answered: how the `.so` is built; ref vs standalone split; caller/consumer pattern; memory/register/control/interrupt/store sync; exported/consumed APIs; checkpoint/profiler relation; limits relevant to a GPGPU golden model
- Appendix: inline
- Confidence: Medium-High

### 1. One-Paragraph Answer

NEMU exposes one reusable live golden-model contract and three offline support modes. The live contract is `CONFIG_SHARE` reference mode: build a shared object, `dlopen` it, bulk-copy memory and architectural state into it, then step it one instruction/event at a time through `difftest_exec(1)` while using side channels for interrupts, store commits, and optional event queries. Standalone, profiling, and checkpoint modes are separate `!SHARE` executable flows for long-running full-system simulation, SimPoint BBV generation, host-side perf attribution, and checkpoint emission; they are not the same surface as the live diff API. For a GPGPU skill, the direct transfer is not RISC-V behavior but the contract shape: executable ref model, compact state blob, explicit memory copy, single-step/event stepping, separate non-architectural sync, standalone-only snapshot/profiling services, and a formal status API rather than leaked globals.

### 2. Top Architecture Findings

- `CONFIRMED` Reference mode is a shared-library build, not a standalone binary mode. `CONFIG_SHARE=y` in `riscv64-xs-ref_defconfig`, `Kconfig` describes SHARE as “Build shared library as processor difftest reference”, and `scripts/build.mk` emits `build/riscv64-nemu-interpreter-so`. Evidence: `ref_submodule/xiangshan-nemu/configs/riscv64-xs-ref_defconfig:210-219`, `ref_submodule/xiangshan-nemu/Kconfig:366-423`, `ref_submodule/xiangshan-nemu/scripts/build.mk:3-18`, `ref_submodule/xiangshan-nemu/scripts/isa.mk:16-21`, `ref_submodule/xiangshan-nemu/README.md:152-160`.
- `CONFIRMED` Standalone mode is a different product configuration optimized for long full-system runs, device modeling, checkpointing, and profiling. It disables SHARE, enables `PERF_OPT`, and uses richer device configs. Evidence: `ref_submodule/xiangshan-nemu/configs/riscv64-xs_defconfig:147-149,180-212,241-248`, `ref_submodule/xiangshan-nemu/README.md:87-115`, `https://docs.xiangshan.cc/zh-cn/latest/tools/nemu/`.
- `CONFIRMED` The canonical live synchronization path is `init -> memory copy -> optional flash copy -> reg/state copy -> exec(1) -> reg/state copy back/check`. Evidence: `ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c:78-130,143-179`, `ref_submodule/xiangshan-nemu/tools/ref-so-runner/runner.c:213-247,337-385`.
- `CONFIRMED` NEMU uses one compact architecture-visible state blob and a separate set of non-architectural side channels. `DIFFTEST_REG_SIZE` spans `gpr` through `difftest_state_end`; CSR shadow fields are materialized through `csr_prepare()`/`csr_writeback()`. LR/SC and other pending state are separate. Evidence: `ref_submodule/xiangshan-nemu/lib-include/difftest.h:22-44`, `ref_submodule/xiangshan-nemu/src/isa/riscv64/include/isa-def.h:93-180`, `ref_submodule/xiangshan-nemu/src/isa/riscv64/difftest/ref.c:47-172,196-277`.
- `CONFIRMED` Checkpoint and profiling are standalone-only auxiliary modes. `PERF_OPT` and `MEM_COMPRESS` both depend on `!SHARE`, and `monitor.c` initializes serializer/simpoint only when checkpoint or profiling output is enabled. Evidence: `ref_submodule/xiangshan-nemu/Kconfig:467-503`, `ref_submodule/xiangshan-nemu/src/memory/Kconfig:79-84`, `ref_submodule/xiangshan-nemu/src/monitor/monitor.c:349-369`.
- `MISSING` The corpus is strong on ref-side exports and exemplar consumer patterns, but weak on XiangShan’s actual external consumer binding. The local XiangShan read set only shows `--diff .../riscv64-nemu-interpreter-so`, and the local plan explicitly marks `ref_submodule/xiangshan/difftest` as uninitialized. Evidence: `ref_submodule/xiangshan/README.md:117-122`, `ref/skillref/xiangshan.md:37-45`.

### 3. Minimal Architecture Map

- Build and mode selection: `README.md`, official NEMU doc, `Kconfig`, defconfigs, `Makefile`, `scripts/build.mk`, `scripts/isa.mk`
- Reference `.so` export surface: `src/cpu/difftest/ref.c`, `src/isa/riscv64/difftest/ref.c`, `lib-include/difftest.h`
- Exemplar consumer surface: `src/cpu/difftest/dut.c`, `src/isa/riscv64/difftest/dut.c`, `tools/ref-so-runner/runner.c`
- Standalone output services: `src/monitor/monitor.c`, `src/cpu/cpu-exec.c`, `src/profiling/profiling_control.c`, `src/checkpoint/{serializer.cpp,simpoint.cpp}`
- Memory and MMIO boundary: `src/memory/paddr.c`, `src/device/io/mmio.c`, `src/device/flash.c`, `src/device/device.c`, `src/monitor/image_loader.c`

### 4. Top State / Interface Contracts

| Contract | Status | Why it matters | Evidence |
|---|---|---|---|
| Architecture-visible state blob | `CONFIRMED` | Golden model must copy one compact compare-visible block, not ad hoc fields. | `lib-include/difftest.h:22-44`; `src/isa/riscv64/difftest/ref.c:196-208` |
| Non-architectural sync sidecars | `CONFIRMED` | LR/SC validity, interrupt routing, query events, and guided faults should not be hidden inside the main state blob. | `src/isa/riscv64/difftest/ref.c:249-277,319-377`; `src/isa/riscv64/include/isa-def.h:28-87` |
| Bulk memory/bootstrap copy | `CONFIRMED` | Ref init needs explicit image copy, optional flash copy, optional RAM-size override, and defined reset surface. | `src/cpu/difftest/ref.c:87-126`; `src/cpu/difftest/dut.c:125-130`; `tools/ref-so-runner/runner.c:224-245,344-347` |
| Store-commit compare channel | `CONFIRMED` | Memory correctness cannot rely only on final-state compare; committed store tuples must be observable. | `src/memory/paddr.c:546-678`; `include/cpu/difftest.h:67-92` |
| Snapshot/restore package | `CONFIRMED` | Standalone checkpointing needs registers, CSRs, PC, mode, timer state, memory/flash image, and layout metadata. | `src/checkpoint/serializer.cpp:376-510,517-669` |
| Formal status reporting | `CONFIRMED` | A reusable GPGPU ref API should export `status()`, but default NEMU ref mode leaks status through `nemu_state` globals instead. | `src/cpu/difftest/ref.c:184-195`; `configs/riscv64-xs-ref_defconfig:219`; `tools/ref-so-runner/runner.c:221-245,358-377` |

### 5. Top Risks / Missing Contracts

- `MISSING` XiangShan’s actual simulator-side consumer code is not in the read corpus; only the CLI example is present locally. Evidence: `ref_submodule/xiangshan/README.md:117-122`, `ref/skillref/xiangshan.md:37-45`.
- `CONFLICTED` Flash-copy symbol naming is inconsistent inside this NEMU snapshot. Ref-side code exports `difftest_load_flash`, runner loads `difftest_load_flash`, but exemplar DUT code looks up `difftest_load_flash_v2`. Evidence: `src/cpu/difftest/ref.c:107-113`; `tools/ref-so-runner/runner.c:224-229,299-303`; `src/cpu/difftest/dut.c:110-113`.
- `MISSING` Mid-run attach-safe non-register state synchronization is not solved. `difftest_attach()` ends in `assert(0)` because non-register state synchronization is incomplete. Evidence: `src/cpu/difftest/dut.c:184-196`; `src/isa/riscv64/difftest/dut.c:120-126`.
- `UNCERTAIN` Standalone `PERF_OPT` changes counting and disables PMP/PMA checks, so it is useful for performance windows but should not be treated as the highest-fidelity correctness oracle. Evidence: `configs/riscv64-xs_defconfig:69-80,241-248`; `Kconfig:467-520`; `src/cpu/cpu-exec.c:107-133`.
- `CONFIRMED` Checkpoint generation in M-mode is unsafe by default because restore uses EPC and can break architectural state. Evidence: `README.md:48,207-214`.

### 6. Evidence Snapshot

| Claim ID | Status | Short claim | Evidence |
|---|---|---|---|
| `NEMU-GM-001` | CONFIRMED | Reference mode is a SHARE-built `.so` at `build/riscv64-nemu-interpreter-so`. | `configs/riscv64-xs-ref_defconfig:210-219`; `Kconfig:366-423`; `scripts/build.mk:3-18`; `README.md:152-160` |
| `NEMU-GM-002` | CONFIRMED | Standalone mode is full-system only and not direct ELF/user-emulation. | `README.md:42-48,87-94`; `https://docs.xiangshan.cc/zh-cn/latest/tools/nemu/` |
| `NEMU-GM-003` | CONFIRMED | Live diff caller pattern is `dlopen/dlsym`, then init/memcpy/regcpy/exec/regcpy. | `src/cpu/difftest/dut.c:78-130,143-179`; `tools/ref-so-runner/runner.c:213-247,337-385` |
| `NEMU-GM-004` | CONFIRMED | Architecture-visible state is one compact blob with CSR shadow prepare/writeback. | `lib-include/difftest.h:22-44`; `src/isa/riscv64/difftest/ref.c:47-172,196-208` |
| `NEMU-GM-005` | CONFIRMED | Store commits are queued as `{addr,data,mask,pc}` and compared separately. | `include/memory/paddr.h:101-125`; `src/memory/paddr.c:546-678`; `include/cpu/difftest.h:67-92` |
| `NEMU-GM-006` | CONFIRMED | QUERY_REF exposes memory-access event query as an optional side channel. | `Kconfig:404-407`; `src/engine/interpreter/rtl-basic.h:125-163`; `src/isa/riscv64/difftest/ref.c:360-377` |
| `NEMU-GM-007` | CONFIRMED | Checkpoint/profiling modes are initialized only in standalone flows and start counting after workload-loaded or explicit override. | `src/monitor/monitor.c:222-230,349-369`; `src/profiling/profiling_control.c:18-23`; `src/isa/riscv64/instr/special.h:36-48`; `src/cpu/cpu-exec.c:317-381` |
| `NEMU-GM-008` | CONFIRMED | Checkpoints serialize registers, vector state, CSR array, PC, privilege mode, timers, memory, and optional flash. | `src/checkpoint/serializer.cpp:198-240,376-510` |
| `NEMU-GM-009` | CONFLICTED | Flash-copy API name is inconsistent across ref-side and consumer-side code in this snapshot. | `src/cpu/difftest/ref.c:107-113`; `src/cpu/difftest/dut.c:110-113`; `tools/ref-so-runner/runner.c:224-229` |
| `NEMU-GM-010` | MISSING | Actual XiangShan consumer-side diff binding is not locally available. | `ref_submodule/xiangshan/README.md:117-122`; `ref/skillref/xiangshan.md:37-45` |

### 7. Main Architect Next Actions

- Decision needed: separate live golden-model API from offline checkpoint/profiling API in the GPGPU skill.
  Files to inspect: this report plus current GPGPU skill golden-model contract target.
  Risk: mixing live diff and snapshot services will make the API stateful and fragile.
  Acceptance test: live diff can run without checkpoint codepaths enabled.
- Decision needed: define one compact architecture-visible state blob and one non-architectural sidecar set.
  Files to inspect: `src/isa/riscv64/include/isa-def.h`, `src/isa/riscv64/difftest/ref.c`.
  Risk: mid-run resync becomes impossible if barrier/scoreboard/pending-interrupt state is hidden.
  Acceptance test: cold boot sync and one-instruction guided fault sync both work.
- Decision needed: add explicit store-commit and memory-event query channels to the GPGPU golden-model contract.
  Files to inspect: `src/memory/paddr.c`, `include/memory/paddr.h`, `src/engine/interpreter/rtl-basic.h`.
  Risk: final-state-only checking misses transient coalescer/shared-memory bugs.
  Acceptance test: one mismatching store tuple localizes a failing warp/store event without dumping full memory.
- Decision needed: verify XiangShan’s actual processor-side consumer contract before freezing symbol names.
  Files to inspect: `ref_submodule/xiangshan/difftest` if initialized, or official `OpenXiangShan/difftest`.
  Risk: copying `dut.c` literally would inherit the flash-symbol conflict and possibly the wrong consumer API.
  Acceptance test: every required symbol in the GPGPU `.so` has one confirmed consumer callsite.

## Part B. Evidence Appendix

### A1. Source-of-Truth Hierarchy

| Layer | Files | Role | Reliability | Notes |
|---|---|---|---|---|
| Project rules | `ref/skillref/xiangshan.md:17-45,385-470,914-1001`; `skill/reader/SKILL.md` | shard scope, evidence rules, output contract | High | local instruction source |
| Official docs | `https://docs.xiangshan.cc/zh-cn/latest/tools/nemu/` | mode split and user-facing build flow | High | current official corroboration |
| Repo docs | `ref_submodule/xiangshan-nemu/README.md`; `docs/ref_so_runner.md`; `docs/perf_profile.md` | role/mode descriptions and workflows | High | primary local narrative |
| Build/config | `Makefile`, `scripts/{build.mk,isa.mk}`, `Kconfig`, defconfigs | actual build products and feature gating | High | authoritative for mode boundaries |
| Golden model export | `src/cpu/difftest/ref.c`; `src/isa/riscv64/difftest/ref.c`; `lib-include/difftest.h` | exported reference-side API shape | High | core source of live contract |
| Consumer examples | `src/cpu/difftest/dut.c`; `src/isa/riscv64/difftest/dut.c`; `tools/ref-so-runner/runner.c`; `ref_submodule/xiangshan/README.md` | loader/caller patterns | Medium | NEMU DUT pattern is exemplar, not XiangShan proof |
| Standalone services | `src/monitor/monitor.c`; `src/cpu/cpu-exec.c`; `src/checkpoint/*`; `src/profiling/*` | profiling/checkpoint behavior | High | authoritative for offline modes |
| Memory/device | `src/memory/paddr.c`; `src/device/*`; `src/monitor/image_loader.c` | MMIO, flash, reset, checkpoint I/O boundaries | High | needed for memory-space rules |

### A2. GPGPU Golden Model Modes Table

| Mode | NEMU realization | Purpose | Output / interface | Transferable GPGPU abstraction | Evidence |
|---|---|---|---|---|---|
| `reference mode` | `riscv64-xs-ref_defconfig`; `CONFIG_SHARE=y`; output `build/riscv64-nemu-interpreter-so` | live RTL diff at instruction/event boundary | shared-object API: init, state/memory copy, exec, interrupt/query side channels | the golden model must be executable and API-addressable | `configs/riscv64-xs-ref_defconfig:210-219`; `Kconfig:366-423`; `README.md:152-174` |
| `standalone mode` | `riscv64-xs_defconfig`; `CONFIG_SHARE` off; `CONFIG_PERF_OPT=y`; executable `build/riscv64-nemu-interpreter` | long-running full-system reference execution | CLI run, final traps/output, optional final memory image | offline golden run and trace-generation mode distinct from live diff mode | `configs/riscv64-xs_defconfig:147-149,180-212,241-248`; `README.md:87-106` |
| `profiling mode` | standalone plus `--simpoint-profile` and/or `tools/perf_profile.py` | workload phase profiling and host-hotspot analysis | `simpoint_bbv.gz`; host perf reports and JSON/Markdown bundles | separate performance-attribution surface; do not overload correctness API | `src/monitor/monitor.c:222-230,359-369`; `src/checkpoint/simpoint.cpp:78-92,145-176`; `docs/perf_profile.md:1-229` |
| `checkpoint mode` | standalone `riscv64-xs-cpt*_defconfig`; `CONFIG_MEM_COMPRESS=y`; serializer enabled | restartable simulation points | compressed memory/flash dumps plus embedded register/control metadata | standalone-only snapshot/restore package with manifest/layout | `configs/riscv64-xs-cpt_defconfig:166-168,231-238`; `configs/riscv64-xs-cpt-with-libcheckpoint_defconfig:107-109,166-168,231-238`; `src/checkpoint/serializer.cpp:198-240,376-510,549-669` |

### A3. Exported Reference APIs vs Exemplar Consumers

| API / symbol | Ref-side export in this shard | Consumer in this shard | Status | Notes |
|---|---|---|---|---|
| `difftest_init` | yes | `src/cpu/difftest/dut.c`; `tools/ref-so-runner/runner.c` | `CONFIRMED` | mandatory init entry |
| `difftest_memcpy_init` | yes | runner only, optional | `CONFIRMED` | optimized first copy fallback to `difftest_memcpy` |
| `difftest_memcpy` | yes | `dut.c`; runner | `CONFIRMED` | bulk memory copy |
| `difftest_set_ramsize` | yes | runner only, optional | `CONFIRMED` | must be called before `difftest_init()` |
| `difftest_regcpy` | yes | `dut.c`; runner | `CONFIRMED` | architecture-visible state copy |
| `difftest_exec` | yes | `dut.c`; runner | `CONFIRMED` | single-step/event boundary |
| `difftest_raise_intr` | yes | `dut.c` | `CONFIRMED` | interrupt injection |
| `difftest_guided_exec` | yes when `CONFIG_GUIDED_EXEC` | no local caller in this shard | `CONFIRMED` | useful escape hatch for guided fault/jump sync |
| `difftest_query_ref` | yes when `CONFIG_QUERY_REF` | no local caller in this shard | `CONFIRMED` | current query type is memory event |
| `difftest_store_commit` | yes when store-commit queue enabled | not loaded in local `dut.c` unless Spike case | `UNCERTAIN` | consumer pattern outside this shard likely differs |
| `difftest_load_flash` | yes | runner optional | `CONFIRMED` | ref-side flash bootstrap entry in this commit |
| `difftest_load_flash_v2` | no local definition | `dut.c` expects it under `CONFIG_HAS_FLASH` | `CONFLICTED` | consumer/ref mismatch in this snapshot |
| `difftest_status` | optional, only if `CONFIG_REF_STATUS` | no local user | `MISSING` | default XiangShan ref defconfig disables it |
| `nemu_state` global | yes | runner reads it directly | `CONFIRMED` | works locally but is a bad reusable contract |
| `DIFFTEST_REG_SIZE` global | yes | runner uses it to size reg buffer | `CONFIRMED` | good pattern for opaque state buffer sizing |

### A4. C-Style GPGPU Golden API Schema

```c
typedef enum {
  GPGPU_REF_TO_DUT = 0,
  GPGPU_REF_TO_MODEL = 1,
} gpgpu_copy_dir_t;

typedef enum {
  GPGPU_REF_RUN,
  GPGPU_REF_GOOD_TRAP,
  GPGPU_REF_BAD_TRAP,
  GPGPU_REF_ABORT,
} gpgpu_ref_status_kind_t;

typedef struct {
  /* Architecture-visible only. Keep barrier/scoreboard/pending lines elsewhere. */
  uint64_t pc;
  uint32_t grid_dim[3];
  uint32_t block_dim[3];
  uint32_t block_idx[3];
  uint16_t sm_id;
  uint16_t warp_id;
  uint64_t active_mask;
  uint64_t scalar_regs[/* implementation-defined */];
  uint8_t  vector_regs[/* opaque packed bytes */];
  uint8_t  pred_regs[/* opaque packed bytes */];
  uint64_t csr_like_state[/* launch/config/exception visible state */];
} gpgpu_ref_arch_state_t;

typedef struct {
  bool force_raise_fault;
  uint32_t fault_kind;
  uint64_t fault_addr;
  bool force_set_next_pc;
  uint64_t next_pc;
} gpgpu_ref_exec_guide_t;  /* NEMU pattern: ExecutionGuide */

typedef struct {
  uint64_t addr;
  uint64_t data;
  uint16_t byte_mask;
  uint64_t event_pc;
} gpgpu_ref_store_commit_t;  /* NEMU pattern: store_commit_t */

typedef struct {
  gpgpu_ref_status_kind_t kind;
  uint64_t halt_pc;
  uint32_t halt_code;
} gpgpu_ref_status_t;

typedef struct {
  uint64_t global_mem_bytes;
  bool enable_mmio_spaces;
  bool enable_boot_rom_or_flash;
  bool enable_query_events;
} gpgpu_ref_config_t;

bool gpgpu_ref_set_mem_bytes(size_t bytes);  /* before init; NEMU: difftest_set_ramsize */
bool gpgpu_ref_init(const gpgpu_ref_config_t *cfg);
bool gpgpu_ref_memcpy_init(uint64_t addr, void *buf, size_t n, gpgpu_copy_dir_t dir);
bool gpgpu_ref_memcpy(uint64_t addr, void *buf, size_t n, gpgpu_copy_dir_t dir);
bool gpgpu_ref_statecpy(gpgpu_ref_arch_state_t *state, gpgpu_copy_dir_t dir);
bool gpgpu_ref_non_arch_statecpy(void *sidecar, uint32_t sidecar_kind, gpgpu_copy_dir_t dir);
bool gpgpu_ref_exec(uint64_t n_events);  /* usually exec(1) at commit/event boundary */
bool gpgpu_ref_guided_exec(const gpgpu_ref_exec_guide_t *guide);
bool gpgpu_ref_raise_interrupt_or_fault(uint32_t kind, const void *payload);
bool gpgpu_ref_query(uint32_t query_kind, void *out);  /* NEMU pattern: query mem event */
bool gpgpu_ref_store_commit(gpgpu_ref_store_commit_t *inout);

/* Standalone-only services; do not require them in live reference mode. */
bool gpgpu_ref_snapshot(const char *snapshot_id);
bool gpgpu_ref_restore(const char *snapshot_id);

/* Make this an API, not an exported mutable global. */
bool gpgpu_ref_status(gpgpu_ref_status_t *out);
```

Schema notes:

- `CONFIRMED`: separate `statecpy`, `memcpy`, `exec`, `guided_exec`, `query`, and `store_commit` surfaces map directly to NEMU patterns.
- `INFERRED`: warp/block/grid fields are the GPGPU transfer of NEMU’s compact architectural diff blob.
- `REQUIRED`: `gpgpu_ref_status()` is an intentional improvement; local NEMU ref mode defaults to `nemu_state` global inspection instead.

### A5. Rules for GPGPU State Copy, Memory Copy, Event Stepping, Interrupts/Faults, Store Commit, Snapshot/Restore, Status

#### State copy

- `Rule`: define one compact architecture-visible blob and version its size explicitly.
- `Rule`: materialize mirrored control/config state before copying out and write it back before copying in.
- `Rule`: keep non-architectural side state separate; do not pretend attach/resume is correct without it.
- `NEMU anchor`: `DIFFTEST_REG_SIZE` and `gpr ... difftest_state_end` in `lib-include/difftest.h:22-44` and `isa-def.h:93-152`; `csr_prepare()`/`csr_writeback()` in `src/isa/riscv64/difftest/ref.c:47-172`.
- `Anti-pattern`: stuffing scoreboard/barrier/pending-interrupt state into an undocumented reg blob.

#### Memory copy

- `Rule`: bulk-copy program image before first step; optionally provide a separate first-copy optimization path.
- `Rule`: if the ref owns memory, allow pre-init RAM sizing; if the DUT owns memory, make ownership explicit.
- `Rule`: model boot/reset ROM or flash separately from main memory.
- `NEMU anchor`: `difftest_memcpy_init()`, `difftest_memcpy()`, `difftest_set_ramsize()` in `src/cpu/difftest/ref.c:87-126`; runner pre-init RAM-size call in `tools/ref-so-runner/runner.c:237-245`.
- `Anti-pattern`: silently mixing global memory, boot ROM, and MMIO into one flat copy space.

#### Event stepping

- `Rule`: treat the live API step as one compare boundary, usually `exec(1)`.
- `Rule`: add explicit skip/catch-up/guided paths for instructions/events that cannot be matched naively.
- `Rule`: keep query surfaces explicit; do not depend on logs for core comparison.
- `NEMU anchor`: `difftest_step()` in `src/cpu/difftest/dut.c:143-179`; `difftest_skip_ref()`/`difftest_skip_dut()` in `src/cpu/difftest/dut.c:44-71`; `difftest_guided_exec()` in `src/cpu/difftest/ref.c:197-215`; memory-event query in `src/engine/interpreter/rtl-basic.h:125-163` and `src/isa/riscv64/difftest/ref.c:360-377`.
- `Anti-pattern`: allowing “uncomparable” events to pass without either state reseed or guided execution.

#### Interrupts and faults

- `Rule`: expose interrupt/fault injection as explicit APIs, not implicit state mutations.
- `Rule`: for hard-to-match faults, allow guided fault address / next-PC override as a distinct path.
- `Rule`: if pending interrupt routing matters, expose it as a sidecar contract.
- `NEMU anchor`: `difftest_raise_intr()` and AIA/NMI helpers in `src/cpu/difftest/ref.c:230-323`; `ExecutionGuide` in `src/isa/riscv64/include/isa-def.h:28-43`.
- `Anti-pattern`: encoding trap replay behavior only in prose or hidden device state.

#### Store commit

- `Rule`: expose committed store tuples `{addr,data,mask[,pc]}` as a pull/compare channel.
- `Rule`: record split/misaligned/coalesced stores in the same granularity the DUT commits them.
- `Rule`: keep AMO policy explicit; do not let it be an accidental queue side effect.
- `NEMU anchor`: `store_commit_t` and queue API in `include/memory/paddr.h:101-125`; queue population/check in `src/memory/paddr.c:503-682`; queue container in `src/memory/store_queue_wrapper.cpp:23-68`.
- `Anti-pattern`: comparing memory only at end-of-run or emitting opaque “store happened” booleans.

#### Snapshot / restore

- `Rule`: snapshot/restore belongs to standalone mode unless the live API explicitly guarantees full non-architectural sync.
- `Rule`: snapshot package must contain register state, control/config state, PC, timing state, and memory/flash image plus layout metadata.
- `Rule`: forbid or loudly gate contexts known to corrupt state on restore.
- `NEMU anchor`: standalone-only gating through `!SHARE` in `Kconfig:467-503` and `src/memory/Kconfig:79-84`; serializer contents in `src/checkpoint/serializer.cpp:376-510`; M-mode caveat in `README.md:48,207-214`.
- `Anti-pattern`: claiming a live diff `.so` can safely attach mid-run just because a checkpoint writer exists elsewhere.

#### Status

- `Rule`: export a formal `status()` API with `running/good-trap/bad-trap/abort` and halt metadata.
- `Rule`: never force external harnesses to read mutable globals for stop reason.
- `NEMU anchor`: optional `difftest_status()` in `src/cpu/difftest/ref.c:184-195`; default ref config disables it in `configs/riscv64-xs-ref_defconfig:219`; runner instead reads `nemu_state` directly in `tools/ref-so-runner/runner.c:234-245,358-377`.
- `Anti-pattern`: coupling the harness to internal globals because a real API was omitted “for now”.

### A6. Evidence Table

| XiangShan Mechanism | Source Files / Docs | Problem Solved | Transferable GPGPU Abstraction | Skill Rule | Required Schema | Anti-Pattern to Avoid |
|---|---|---|---|---|---|---|
| `CONFIRMED` SHARE-built reference `.so` | `configs/riscv64-xs-ref_defconfig:210-219`; `Kconfig:366-423`; `scripts/build.mk:3-18`; `README.md:152-160`; official NEMU doc | make the golden model callable by a simulator instead of only runnable as a CLI app | `reference mode` must be a loadable binary contract | the golden model must be executable and API-addressable | `gpgpu_ref_init`, exported symbol/version list | prose ISA or final-output checker only |
| `CONFIRMED` standalone executable mode split from ref mode | `configs/riscv64-xs_defconfig:147-149,180-212,241-248`; `README.md:87-115` | long-running full-system runs need different performance/device settings than live diff | distinct `standalone mode` for trace generation and expected-output runs | keep offline modes separate from live diff mode | `standalone_config`, final-output manifest | one binary mode trying to serve correctness diff and long-run profiling equally |
| `CONFIRMED` `dlopen`/`dlsym` consumer pattern | `src/cpu/difftest/dut.c:78-130`; `tools/ref-so-runner/runner.c:213-247` | simulator needs a stable dynamic binding surface | golden-model loader contract with required/optional symbols | define mandatory vs optional symbols explicitly | ABI manifest, symbol compatibility table | ad hoc symbol lookup without versioning or mandatory/optional separation |
| `CONFIRMED` compact architecture-state blob with CSR mirror | `lib-include/difftest.h:22-44`; `src/isa/riscv64/include/isa-def.h:93-152`; `src/isa/riscv64/difftest/ref.c:47-172,196-208` | avoid piecemeal register/control sync and inconsistent compare state | opaque architecture-visible state blob plus mirror/writeback hooks | keep compare-visible state compact and explicitly sized | `gpgpu_ref_arch_state_t`, state-size query | scattering compare-visible state across dozens of unversioned APIs |
| `CONFIRMED` explicit bulk memory copy and pre-init RAM sizing | `src/cpu/difftest/ref.c:87-126`; `tools/ref-so-runner/runner.c:237-245,344-347` | large initial state must be seeded quickly and repeatably | explicit `memcpy`/`memcpy_init`/`set_mem_bytes` API | separate first-load, normal copy, and memory-size control | memory region descriptor, direction enum | implicit host-side hacks to poke DUT-owned memory directly |
| `CONFIRMED` skip/catch-up/guided exec escape hatches | `src/cpu/difftest/dut.c:44-71,161-179`; `src/cpu/difftest/ref.c:197-215`; `src/isa/riscv64/include/isa-def.h:28-43` | some events cannot be matched by naive lockstep | guided single-event replay and controlled catch-up | mismatches need structured escape hatches, not silent ignores | `gpgpu_ref_exec_guide_t`, skip policy | “just skip this instruction/event” without state repair |
| `CONFIRMED` store-commit queue side channel | `src/memory/paddr.c:503-682`; `include/memory/paddr.h:101-125`; `include/cpu/difftest.h:67-92` | final-state compare misses transient memory-order/address-mask bugs | committed memory-event queue | compare committed memory effects as first-class events | `gpgpu_ref_store_commit_t` | final-memory checksum as the only memory oracle |
| `CONFIRMED` queryable memory-event channel | `Kconfig:404-407`; `src/engine/interpreter/rtl-basic.h:125-163`; `src/isa/riscv64/difftest/ref.c:360-377`; `src/isa/riscv64/include/isa-def.h:74-87` | consumer may need a precise event-side query beyond registers | optional query/event API | event queries should be machine-readable and resettable | `query_kind`, event structs | parsing textual logs to recover memory events |
| `CONFIRMED` standalone-only profiling and checkpoint services | `Kconfig:467-503`; `src/memory/Kconfig:79-84`; `src/monitor/monitor.c:222-230,359-369`; `src/cpu/cpu-exec.c:317-381` | performance windows and snapshots need different runtime and output management from live diff | `profiling mode` and `checkpoint mode` as offline services | do not force profiling/snapshot logic into the live ref ABI | profiling manifest, snapshot manifest | letting checkpoint code mutate live diff semantics |
| `CONFIRMED` checkpoint package includes memory plus control metadata | `src/checkpoint/serializer.cpp:198-240,376-510,517-669`; `README.md:207-214` | restart must restore more than raw memory | snapshot package with reg/control/timer/layout metadata | snapshots must include control/timer state and layout versioning | checkpoint header, memory/flash payload schema | memory-only dumps with implicit restore assumptions |
| `CONFIRMED` MMIO/device holes are distinct from real devices | `src/device/io/mmio.c:37-69`; `src/memory/paddr.c:295-317,423-445`; `src/device/flash.c:69-73`; `README.md:34-39` | full-system golden model must distinguish RAM, configured MMIO space, and actual devices | typed memory spaces with device-backed regions | treat MMIO as a separate contract, not RAM aliasing | address-space enum, device region table | letting unimplemented MMIO addresses behave like ordinary memory |
| `CONFLICTED` flash bootstrap symbol naming | `src/cpu/difftest/ref.c:107-113`; `src/cpu/difftest/dut.c:110-113`; `tools/ref-so-runner/runner.c:224-229,299-303` | caller and callee must agree on boot-surface symbols | symbol-versioned boot/flash API | every required symbol needs one confirmed provider and one confirmed consumer | ABI manifest with versions | copying an example consumer surface without checking local exports |
| `MISSING` actual XiangShan processor-side consumer binding | `ref_submodule/xiangshan/README.md:117-122`; `ref/skillref/xiangshan.md:37-45` | skill needs confirmed simulator-side callsites before freezing names | consumer-side binding audit as a separate shard | do not infer consumer behavior from README-only command lines | caller-side ABI map | assuming README `--diff` implies a proven symbol contract |

### A7. Explicit Limitations and Evidence Boundaries

- `CONFIRMED` NEMU is full-system only for this workflow. It does not directly run ELF, does not support GEM5 SE checkpoints, and is not user-space emulation. Evidence: `README.md:42-48,87-94`.
- `CONFIRMED` Checkpoint generation in M-mode is unsafe by default because restore uses EPC and can break architectural state. Evidence: `README.md:48,207-214`.
- `CONFIRMED` Standalone profiling/perf flows are host-performance attribution tools or SimPoint BBV generators, not proof of guest architectural correctness. Evidence: `docs/perf_profile.md:1-229`; `src/checkpoint/simpoint.cpp:78-176`.
- `UNCERTAIN` `PERF_OPT` standalone builds may sacrifice exception/permission fidelity for speed; defconfigs explicitly disable PMP/PMA checks when PERF_OPT is on, and default instruction counting becomes BB-level. Evidence: `configs/riscv64-xs_defconfig:69-80,241-248`; `Kconfig:467-520`; `src/cpu/cpu-exec.c:107-133`.
- `CONFIRMED` MMIO behavior is simplified and device-backed only where maps exist. Configured MMIO address space can be larger than the set of real devices, and holes raise access faults. Evidence: `src/memory/Kconfig:86-90`; `src/device/io/mmio.c:37-69`; `src/memory/paddr.c:295-317,423-445`.
- `MISSING` The shard confirms NEMU’s ref-side API shape and generic consumer patterns, but not XiangShan’s actual processor-side diff binding implementation because `ref_submodule/xiangshan/difftest` is uninitialized locally. Evidence: `ref/skillref/xiangshan.md:37-45`.
- `CONFLICTED` Flash bootstrap entry naming is inconsistent in this commit snapshot. A GPGPU skill should not import that inconsistency. Evidence: `src/cpu/difftest/ref.c:107-113`; `src/cpu/difftest/dut.c:110-113`; `tools/ref-so-runner/runner.c:224-229`.
- `CONFIRMED` Mid-run reattach is intentionally unsupported in this local code because non-register state cannot be fully reconstructed. Evidence: `src/cpu/difftest/dut.c:184-196`; `src/isa/riscv64/difftest/dut.c:120-126`.

### A8. Claim Index

| Claim ID | Claim | Status | Evidence | Confidence |
|---|---|---|---|---|
| `NEMU-GM-001` | Ref mode builds a shared object for live diff consumption. | CONFIRMED | `configs/riscv64-xs-ref_defconfig:210-219`; `Kconfig:366-423`; `scripts/build.mk:3-18`; `README.md:152-160` | High |
| `NEMU-GM-002` | Standalone mode is full-system only and not a user-emulation flow. | CONFIRMED | `README.md:42-48,87-94`; official NEMU doc | High |
| `NEMU-GM-003` | The live caller contract is `init -> copy -> exec(1) -> readback/check`. | CONFIRMED | `src/cpu/difftest/dut.c:78-130,143-179`; `tools/ref-so-runner/runner.c:337-385` | High |
| `NEMU-GM-004` | Architectural compare state is one compact blob with explicit CSR/control-state mirror handling. | CONFIRMED | `lib-include/difftest.h:22-44`; `src/isa/riscv64/difftest/ref.c:47-172,196-208` | High |
| `NEMU-GM-005` | Store-commit tuples are first-class diff events with addr/data/mask/pc. | CONFIRMED | `include/memory/paddr.h:101-125`; `src/memory/paddr.c:503-682` | High |
| `NEMU-GM-006` | Query events are optional and currently cover memory accesses. | CONFIRMED | `Kconfig:404-407`; `src/engine/interpreter/rtl-basic.h:125-163`; `src/isa/riscv64/difftest/ref.c:360-377` | High |
| `NEMU-GM-007` | Checkpoint/profiling services are standalone-only and start after workload-loaded unless overridden. | CONFIRMED | `src/monitor/monitor.c:222-230,359-369`; `src/profiling/profiling_control.c:18-23`; `src/isa/riscv64/instr/special.h:36-48`; `src/cpu/cpu-exec.c:317-381` | High |
| `NEMU-GM-008` | Snapshot packages include memory plus reg/control/timer metadata. | CONFIRMED | `src/checkpoint/serializer.cpp:198-240,376-510` | High |
| `NEMU-GM-009` | Flash bootstrap symbol naming is inconsistent in this corpus. | CONFLICTED | `src/cpu/difftest/ref.c:107-113`; `src/cpu/difftest/dut.c:110-113`; `tools/ref-so-runner/runner.c:224-229` | High |
| `NEMU-GM-010` | XiangShan’s actual processor-side diff consumer contract remains outside local evidence. | MISSING | `ref_submodule/xiangshan/README.md:117-122`; `ref/skillref/xiangshan.md:37-45` | High |
| `NEMU-GM-011` | Default ref mode lacks a formal status API and runner reads globals instead. | CONFIRMED | `src/cpu/difftest/ref.c:184-195`; `configs/riscv64-xs-ref_defconfig:219`; `tools/ref-so-runner/runner.c:234-245,358-377` | Medium-High |

### A9. Full Quality Gate

#### Overall Status

- Overall status: `PARTIAL`

#### Evidence Gate

| Check | Result | Notes |
|---|---|---|
| Scope declared | PASS | metadata lists files read/skipped and non-goals |
| Planner focus answered | PASS | all seven extraction questions are answered |
| Evidence attached | PASS | planning-relevant claims cite exact files/lines or official doc URL |
| Claim status used | PASS | `CONFIRMED`, `INFERRED`, `UNCERTAIN`, `CONFLICTED`, `MISSING` are explicit |
| Contradictions reported | PASS | flash symbol mismatch is recorded as `CONFLICTED` |
| Missing contracts reported | PASS | XiangShan external consumer binding is recorded as `MISSING` |
| Handoff actionable | PASS | next actions specify decision, risk, and acceptance test |

#### Readability Gate

| Check | Result | Notes |
|---|---|---|
| Handoff length | PASS | Part A is compact; dense detail moved to appendix sections |
| Findings capped | PASS | six top findings |
| Tables limited | PASS | tables are used where schema/evidence benefit from them |
| Empty sections removed | PASS | only relevant repository sections are kept |
| Decision relevance | PASS | all visible items support GPGPU golden-model planning |
| Appendix separation | PASS | dense API/evidence moved below Part A |

#### Repository Extra Gate

| Topic | Status | Notes |
|---|---|---|
| ISA semantics | not applicable | intentionally excluded except sync/control examples |
| instruction encoding | not applicable | out of shard scope |
| decode path | not applicable | out of shard scope |
| PC / warp state | inferred | PC sync is confirmed; warp-state mapping is a GPGPU transfer |
| active mask | inferred | required GPGPU transfer, not present in CPU NEMU corpus |
| SIMT divergence | not applicable | out of CPU NEMU shard scope |
| register file | confirmed | as part of compact diff state blob |
| scoreboard / hazards | not applicable | not a NEMU golden-model interface topic here |
| issue / execute / writeback | not applicable | out of shard scope |
| memory coalescing | not applicable | GPGPU-only, not in corpus |
| shared memory | not applicable | GPGPU-only, not in corpus |
| barrier semantics | not applicable | GPGPU-only, not in corpus |
| CSR / DCR / config state | confirmed | control-state mirrors are explicitly synced |
| launch protocol | inferred | reset/image/flash bootstrap is the CPU analogue |
| kernel arguments | not applicable | out of shard scope |
| grid/block/warp mapping | inferred | required GPGPU extension, not in CPU NEMU corpus |
| CModel / golden model | confirmed | main subject of this shard |
| trace diff / compare path | confirmed | `difftest_step`, state copy, query/store side channels |
| tests and coverage | missing | no local test suite audited in this shard |
| synthesis / FPGA / PPA evidence | not applicable | not a NEMU repository goal here |

## Quality Gate

- Overall status: PARTIAL
- Evidence status: PARTIAL
- Readability status: PASS
- Safe for GPT-5.5 planning: with caveats
- Full appendix generated: inline
- Biggest evidence gap: actual XiangShan external DiffTest consumer code is not in the local corpus, and the local plan marks `ref_submodule/xiangshan/difftest` as uninitialized
- Biggest readability issue: the consumer/export matrix is dense because the corpus splits ref-side code, generic DUT-side examples, and standalone-mode utilities
- Required next read: `ref_submodule/xiangshan/difftest` or official `OpenXiangShan/difftest`, plus XiangShan simulator-side `--diff` loader/binding code
