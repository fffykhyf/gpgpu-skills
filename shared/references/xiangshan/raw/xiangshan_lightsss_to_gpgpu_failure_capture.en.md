# Repository Architecture Report

## Part A. Human Handoff

### 0. Metadata

- Mode: repository
- Depth: deep
- Output profile: model-evidence
- Repo / subsystem: XiangShan LightSSS + XSPdb failure-capture path
- Branch / commit if available:
  - `ref_submodule/xiangshan`: `5ff19c2`
  - `ref_submodule/xiangshan-nemu`: `75d0019`
- Files read:
  - `ref_submodule/xiangshan/docs/XSPdb/{README.md,design/{fork_backup.md,difftest_snapshot.md,waveform.md,breakpoints.md,watchpoints.md,step.md,cli.md,cli_batch.md,disasm.md,registers.md,trigger_expr_spec.md,trigger_fsm_spec.md},examples/{fork_backup.md,difftest_snapshot.md,waveform.md,disasm.md,registers.md,xspdb_script_example.txt,pc_sequence.fsm}}`
  - `ref_submodule/xiangshan/scripts/{xiangshan.py,pdb-run.py}`
  - `ref_submodule/xiangshan/scripts/xspdb/{cli_parser.py,xspdb.py,xscmd/{cmd_batch.py,cmd_break.py,cmd_difftest.py,cmd_dut.py,cmd_fork_backup.py,cmd_wave.py,cmd_regs.py,cmd_instr.py,cmd_info.py}}`
  - `ref_submodule/xiangshan-nemu/{configs/riscv64-xs-ahead-ref_defconfig,include/cpu/cpu.h,src/{cpu/cpu-exec.c,isa/riscv64/difftest/ref.c,memory/paddr.c,memory/Kconfig}}`
  - Official docs: `https://docs.xiangshan.cc/zh-cn/latest/tools/lightsss/`
- Files skipped:
  - CPU execution/microarchitecture files outside failure-capture scope
  - Missing local submodules: `ref_submodule/xiangshan/{difftest,XSCache,ready-to-run,rocket-chip,utility,yunsuan,...}`
- Entry points inspected:
  - batch/fork capture: `ref_submodule/xiangshan/scripts/xiangshan.py`
  - interactive replay: `ref_submodule/xiangshan/scripts/pdb-run.py`
  - debugger core: `ref_submodule/xiangshan/scripts/xspdb/xspdb.py`
  - fork backup: `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_fork_backup.py`
- Focus:
  - failure-window capture
  - waveform/debug dump policy
  - replay command contract
  - GPGPU transfer only
- Questions answered: 1-7 from the task shard
- Non-goals:
  - CPU frontend/backend details
  - rename/ROB semantics except where they surface failure capture
  - ISA behavior except where needed for replay/debug surfaces
- Appendix: generated at `ref/skillref/xiangshan-reader-reports/xiangshan_lightsss_to_gpgpu_failure_capture.en.md`
- Confidence: Medium

### 1. One-Paragraph Answer

XiangShan exposes two distinct failure-capture layers that should become separate GPGPU skill contracts: `LightSSS` for batch-mode automatic fork-based failure capture around an error, and `XSPdb` for interactive replay with selective waveform, signal/expr/FSM breakpoints, difftest-linked commit state, and reproducible command logs. The transferable lesson is not CPU execution detail; it is that every failing run must emit a bounded replay package instead of only a pass/fail result. Evidence is strong for the local XSPdb mechanics and the official LightSSS semantics, but exact LightSSS config defaults are blocked by the missing local `difftest` submodule. Local docs also drift from the checked-in runtime in a few places, so the GPGPU contract must privilege executable surfaces over stale prose.

### 2. Top Architecture Findings

1. `[CONFIRMED]` XiangShan avoids full-run waveform because only the failure neighborhood matters, while serialized simulator snapshots are expensive and miss non-RTL state such as the reference model and DRAMSim3. Evidence: official LightSSS docs, sections `lightSSS 简介` and `原理` (`https://docs.xiangshan.cc/zh-cn/latest/tools/lightsss/`).
2. `[CONFIRMED]` LightSSS defines the debug window by periodically `fork`ing a lagging child; on failure, the parent wakes the newest child to re-run and dump waveform/debug info. The usable pre-failure window is therefore bounded by the last fork interval, not the whole run. Evidence: official LightSSS docs; `ref_submodule/xiangshan/docs/XSPdb/design/fork_backup.md:4-14`.
3. `[CONFIRMED]` The local interactive path is `XSPdb xstep/xbreak/xwave/xfork_backup`, not the batch `emu.py` path referenced by some docs. `xfork_backup_*` only works on the `xstep` path. Evidence: `ref_submodule/xiangshan/docs/XSPdb/README.md:64-66`; `ref_submodule/xiangshan/docs/XSPdb/design/fork_backup.md:11`; `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_dut.py:41-101`.
4. `[CONFIRMED]` Local waveform policy is selective by design: XSPdb initializes waveform off, turns it on only when requested, supports flush/continue, and fork-backup keeps only the latest two captured wave files. Evidence: `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_wave.py:32-121`; `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_fork_backup.py:41-42,339-362`.
5. `[CONFIRMED]` XSPdb binds replay to failure triggers through signal breakpoints, compiled expressions, and multi-step FSM triggers that all run on clock-edge callbacks; `xstep` polls difftest exit, good trap/loop, and trap-break conditions at step boundaries. Evidence: `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_break.py:31-86,156-187,234-257,298-333`; `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_dut.py:28-69`.
6. `[CONFIRMED]` The reference-side snapshot path in NEMU is not just register copy. With `CONFIG_LIGHTQS`, it snapshots registers/CSR/MMU state, keeps store logs for memory rollback, and maintains a speculative-ahead window (`AHEAD_LENGTH=500`) for replay. Evidence: `ref_submodule/xiangshan-nemu/include/cpu/cpu.h:23,63-94`; `ref_submodule/xiangshan-nemu/src/cpu/cpu-exec.c:525-667,827-922`; `ref_submodule/xiangshan-nemu/src/memory/paddr.c:334-367`; `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:331-340`.

### 3. Minimal Architecture Map

| Component | XiangShan role | Failure-capture contract | Evidence |
|---|---|---|---|
| `LightSSS` (`./build/emu --enable-fork`) | batch auto-capture around failures | fork snapshot + auto wave/debug dump | official LightSSS docs |
| `scripts/xiangshan.py` | local launcher/build wrapper | build/run policy for `EMU_TRACE`, `--enable-fork`, `--disable-fork` | `ref_submodule/xiangshan/scripts/xiangshan.py:80-81,97,135-157,290-296,784-798` |
| `scripts/pdb-run.py` | XSPdb entrypoint | reproducible interactive/batch replay surface | `ref_submodule/xiangshan/scripts/pdb-run.py:18-26` |
| `XSPdb xstep/xbreak/xwave/xfork_backup` | localized replay and artifact extraction | bounded replay with user-controlled triggers and wave files | `ref_submodule/xiangshan/docs/XSPdb/README.md:3-10,44-64`; `ref_submodule/xiangshan/scripts/xspdb/xscmd/{cmd_dut.py,cmd_break.py,cmd_wave.py,cmd_fork_backup.py}` |
| `XSPdb difftest surface` | REF/DUT synchronized debug state | diff exit detection, commit PC, instruction-step, exported state | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_difftest.py:35-118,158-183,223-255,320-371` |
| `xiangshan-nemu LightQS` | reference-side restore/re-exec | register/CSR/MMU snapshot + memory store-log rollback + ahead re-exec | `ref_submodule/xiangshan-nemu/src/cpu/cpu-exec.c:525-667,909-922`; `ref_submodule/xiangshan-nemu/src/memory/paddr.c:334-367` |

### 4. Top State / Interface Contracts

| Contract | Status | Why it matters | Evidence |
|---|---|---|---|
| Build-time wave capability must exist before batch fork capture | CONFIRMED | `--enable-fork` is insufficient if waveform support was not compiled in | official LightSSS docs, section `运行`; `ref_submodule/xiangshan/scripts/xiangshan.py:80-81,142-143,784-786` |
| Local replay command must separate batch auto-capture from interactive replay | CONFIRMED | LightSSS and XSPdb fork backup are different mechanisms with different trigger surfaces | official LightSSS docs; `ref_submodule/xiangshan/docs/XSPdb/README.md:64-66`; `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_fork_backup.py:44-55` |
| Failure trigger must carry replayable context, not only exit code | INFERRED | local XSPdb exposes commit PC/instr, watch lists, registers, break status, and logs; GPGPU should promote these to required artifacts | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_info.py:236-357`; `ref_submodule/xiangshan/scripts/xspdb/xspdb.py:151-152,602-631,679-686` |
| Reference snapshot must include memory rollback semantics | CONFIRMED | register-only replay is insufficient for memory/atomic/fence failures | `ref_submodule/xiangshan-nemu/src/memory/paddr.c:334-367`; `ref_submodule/xiangshan-nemu/src/isa/riscv64/difftest/ref.c:179-223` |

### 5. Top Risks / Missing Contracts

- `[MISSING]` Exact LightSSS defaults for `FORK_INTERVAL`, `SLOT_SIZE`, and `WAIT_INTERVAL` are not locally verifiable because the docs point to `difftest/config/config.h`, but `ref_submodule/xiangshan/difftest` is uninitialized.
- `[CONFLICTED]` XSPdb docs/examples reference `scripts/emu.py --fork-interval`, but this checkout has no `scripts/emu.py`; the local runnable surfaces are `scripts/xiangshan.py`, `./build/emu`, and `scripts/pdb-run.py`.
- `[CONFLICTED]` `design/difftest_snapshot.md` claims state export is JSON, while local `do_xexpdiffstate` only injects `difftest_stat` into the debugger frame.
- `[UNCERTAIN]` `design/watchpoints.md` claims automatic per-step change reporting for generic `xwatch`, but the local code clearly stores watch signals for display and does not show a dedicated change-delta logger in the files read.
- `[MISSING]` No explicit local artifact packager bundles wave/log/diff/register/disassembly outputs into one reproducible failure package; the user or script must compose it.

### 6. Evidence Snapshot

| Claim ID | Status | Short claim | Evidence |
|---|---|---|---|
| `XS-LS-001` | CONFIRMED | Full-run wave is intentionally avoided; bounded failure-neighborhood wave is the design target. | official LightSSS docs |
| `XS-LS-002` | CONFIRMED | LightSSS uses periodic forked children; the latest child replays to the failing point. | official LightSSS docs |
| `XS-LS-003` | MISSING | `FORK_INTERVAL` / `SLOT_SIZE` / `WAIT_INTERVAL` exact defaults are not locally available. | official LightSSS docs; missing `ref_submodule/xiangshan/difftest` |
| `XS-LS-004` | CONFIRMED | Local wrapper turns LightSSS off with `--disable-fork` and otherwise injects `--enable-fork`. | `ref_submodule/xiangshan/scripts/xiangshan.py:97,290-296,797` |
| `XS-LS-005` | CONFIRMED | XSPdb fork backup is interactive-only on `xstep`, not the batch `emu.py` loop. | `ref_submodule/xiangshan/docs/XSPdb/README.md:64-66` |
| `XS-LS-006` | CONFIRMED | XSPdb fork backup keeps a waiting child, writes `.fst`, child log, parent log, and retains only the newest two wave files. | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_fork_backup.py:57-92,161-170,192-239,339-362` |
| `XS-LS-007` | CONFIRMED | `xstep` integrates breakpoint checks, fork-backup tick, difftest exit, trap/good-loop exit. | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_dut.py:41-101` |
| `XS-LS-008` | CONFIRMED | `xbreak_expr` and `xbreak_fsm` compile to C++/clock-edge trigger engines. | `ref_submodule/xiangshan/docs/XSPdb/design/trigger_expr_spec.md:5-19`; `ref_submodule/xiangshan/docs/XSPdb/design/trigger_fsm_spec.md:5-16,111-129` |
| `XS-LS-009` | CONFIRMED | Replay logs/scripts are first-class: commands are recorded as `@cmd{...}` and re-executable. | `ref_submodule/xiangshan/scripts/xspdb/xspdb.py:47-54,151-152,602-631,679-686`; `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_batch.py:40-77` |
| `XS-LS-010` | CONFLICTED | `xexpdiffstate` is documented as JSON export, but local code exports a Python object only. | `ref_submodule/xiangshan/docs/XSPdb/design/difftest_snapshot.md:37-40`; `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_difftest.py:363-370` |

### 7. Main Architect Next Actions

1. Decision needed: initialize or separately read `ref_submodule/xiangshan/difftest/config/config.h` for exact LightSSS defaults. Risk: current report cannot pin default fork slot/wait values. Acceptance test: report `FORK_INTERVAL/SLOT_SIZE/WAIT_INTERVAL` with direct code anchors.
2. Decision needed: choose whether the GPGPU skill exposes two modes (`batch_auto`, `interactive_replay`) or one merged abstraction. Risk: mixing them hides different triggers and artifacts. Acceptance test: schema distinguishes automatic fork capture from debugger replay.
3. Decision needed: upgrade GPGPU failure packaging from interactive views to mandatory files. Risk: users can still end with only “test failed”. Acceptance test: skill emits waveform/log/diff/register/disassembly/replay artifacts or explicit reason each one is absent.
4. Decision needed: define cycle-based window semantics for GPGPU even if implementation uses wall-clock fork spacing internally. Risk: wall-clock-only windows are unstable across machines. Acceptance test: schema requires event/cycle window declarations alongside runtime fork/checkpoint policy.
5. Decision needed: validate local XSPdb CLI quirks (`--batch`, missing `emu.py`) before scripting against them. Risk: replay scripts based on stale docs will not run. Acceptance test: replay command template uses only locally verified entrypoints.

### 8. Compact Quality Gate

- Evidence status: PARTIAL
- Readability status: PASS
- Safe for GPT-5.5 planning: yes, with caveats
- Full appendix generated: yes
- Biggest evidence gap: missing local `difftest/config/config.h` for exact LightSSS defaults
- Required next read: initialized `ref_submodule/xiangshan/difftest/config/config.h`

## Part B. Evidence Appendix

### A1. Source-of-Truth Hierarchy

| Layer | Files | Role | Reliability | Notes |
|---|---|---|---|---|
| Project rules | `AGENTS.md`, `ref/skillref/xiangshan.md`, `skill/reader/*` | reader/task contract | High | governs scope and output |
| Official docs | `https://docs.xiangshan.cc/zh-cn/latest/tools/lightsss/` | LightSSS semantics | High | used because local `difftest` submodule is missing |
| Local docs | `ref_submodule/xiangshan/docs/XSPdb/*` | XSPdb command and design intent | Medium | some drift from local runtime |
| Runtime scripts | `ref_submodule/xiangshan/scripts/{xiangshan.py,pdb-run.py,xspdb/*}` | executable local truth for replay/debug flow | High | preferred over stale prose |
| Reference model impl | `ref_submodule/xiangshan-nemu/{include,src}` | snapshot/restore mechanics | High | used only where snapshot support matters |
| Missing local source | `ref_submodule/xiangshan/difftest/*` | exact LightSSS config defaults | Missing | must stay `MISSING` in this shard |

### A2. Corpus Inventory

| Corpus item | Status | Notes |
|---|---|---|
| `ref_submodule/xiangshan` @ `5ff19c2` | present | primary local source |
| `ref_submodule/xiangshan-nemu` @ `75d0019` | present | snapshot-related state source |
| `docs.xiangshan.cc` LightSSS page | present via web | used for official semantics of fork config and runtime policy |
| `ref_submodule/xiangshan/difftest` | missing | blocks exact local LightSSS config verification |
| `scripts/emu.py` | missing | docs/examples mention it; local checkout does not contain it |

### A3. Failure-Capture Flow

1. Batch auto-capture (`LightSSS`)
   - Build emulator with waveform capability (`EMU_TRACE`).
   - Run `./build/emu ... --enable-fork`.
   - Parent periodically forks lagging child snapshots.
   - On failure, parent wakes newest child.
   - Child re-runs to failure and emits wave/debug output.
2. Interactive replay (`XSPdb`)
   - Launch `python3 scripts/pdb-run.py`.
   - Load image, REF `.so`, optional flash/memory overrides.
   - Arm `xbreak` / `xbreak_expr` / `xbreak_fsm` / `xwatch_commit_pc`.
   - Step with `xstep` / `xistep`.
   - Turn wave on only near the suspect region or use `xfork_backup_on`.
   - Preserve command log / script for replay.
3. Reference restore (`NEMU LightQS`)
   - Save stable register snapshot and store log.
   - Run ahead (`AHEAD_LENGTH=500`) and take speculative snapshot.
   - On restore, roll back memory via store log, restore registers/CSR/MMU state, and re-execute remaining instructions.

### A4. GPGPU Failure Capture Schema

```yaml
failure_capture:
  enabled: true
  modes:
    - name: batch_auto
      source: fork_snapshot
      purpose: "CI/regression failure auto-capture"
      required_build_flags:
        - EMU_TRACE
      required_run_flags:
        - --enable-fork
    - name: interactive_replay
      source: debugger_replay
      purpose: "localize failure with manual/triggered stepping"
      required_entrypoint:
        - python3 scripts/pdb-run.py
      required_triggers:
        - xbreak
        - xbreak_expr
        - xbreak_fsm
        - xwatch_commit_pc
  triggers:
    - trace_mismatch
    - assertion_failure
    - timeout
    - illegal_state
    - performance_regression_gate
  failure_event:
    required_fields:
      - kind
      - cycle
      - event
      - field
      - rtl_value
      - golden_value
      - context
      - suspected_modules
  window:
    pre_failure:
      required: true
      basis: cycle|instruction|wallclock
    post_failure:
      required: false
      basis: cycle|instruction|wallclock
    fork_or_checkpoint_interval:
      required: true
      notes:
        - "LightSSS and local XSPdb fork backup both expose wall-clock windows"
        - "GPGPU contract should also declare logical cycle/instruction windows"
    replay_boundary:
      required: true
      choices:
        - failing_event
        - trigger_match
        - commit_boundary
  artifacts:
    required:
      - replay_command
      - failure_script_or_replay_log
      - mismatch_report
      - diff_status
      - waveform_or_reason_missing
      - register_snapshot
      - disassembly_window
      - pc_or_commit_window
      - suspected_module_list
    conditional:
      - scoreboard_trace
      - coalescer_trace
      - barrier_trace
      - atomic_order_trace
      - outstanding_transaction_trace
      - counter_snapshot
  policy:
    never_emit_only:
      - "test failed"
    must_emit:
      - failing_event
      - suspected_modules
      - required_trace_windows
      - replay_command
```

### A5. Why XiangShan Avoids Full-Run Waveform

| Observation | Status | Evidence | GPGPU rule |
|---|---|---|---|
| Only the failure-neighborhood waveform is needed. | CONFIRMED | official LightSSS docs | Do not default to whole-run wave dumps. |
| Serialized snapshot files miss non-RTL state such as REF/DRAMSim3 and are costly on large designs. | CONFIRMED | official LightSSS docs | Failure capture must preserve non-RTL debug state or explicitly log it separately. |
| Local XSPdb docs also warn wave files grow large and should be enabled only when needed. | CONFIRMED | `ref_submodule/xiangshan/docs/XSPdb/design/waveform.md:39-40` | Selective wave must be a first-class control surface. |

### A6. Debug-Window Contract

| Mechanism | Window basis | Window definition | Status | Evidence |
|---|---|---|---|---|
| LightSSS batch fork | wall-clock seconds | recoverable pre-failure region is bounded by last `FORK_INTERVAL` child snapshot | CONFIRMED | official LightSSS docs |
| XSPdb `xfork_backup_on <window_sec>` | wall-clock seconds | parent spawns one waiting child every `window_sec`; on break, child re-runs to same break and dumps `.fst` | CONFIRMED | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_fork_backup.py:44-55,364-397` |
| NEMU LightQS stable/spec snapshot | instructions | stable snapshot + speculative-ahead snapshot (`AHEAD_LENGTH=500`) for re-exec after restore | CONFIRMED | `ref_submodule/xiangshan-nemu/include/cpu/cpu.h:23`; `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c:331-340` |
| XSPdb docs `--fork-interval (emu.py)` | runtime CLI | documented, but local surface absent in this checkout | CONFLICTED | `ref_submodule/xiangshan/docs/XSPdb/design/difftest_snapshot.md:35`; missing `scripts/emu.py` |

### A7. LightSSS / Waveform / Replay Knobs

| Item | Meaning | Where defined | Local status | GPGPU transfer rule |
|---|---|---|---|---|
| `FORK_INTERVAL` | how often to fork child snapshots | official LightSSS docs, points to `difftest/config/config.h` | semantics CONFIRMED; local default MISSING | expose fork/checkpoint interval explicitly |
| `SLOT_SIZE` | max simultaneous child processes | official LightSSS docs | semantics CONFIRMED; local default MISSING | bound retained snapshots/waves; make retention visible |
| `WAIT_INTERVAL` | child polling interval for parent signal | official LightSSS docs | semantics CONFIRMED; local default MISSING | expose wake latency or use blocking wake with explicit note |
| `--enable-fork` | enable LightSSS at runtime | official LightSSS docs; `scripts/xiangshan.py` | CONFIRMED | failure capture needs an explicit runtime on/off knob |
| `EMU_TRACE` | build-time wave support required for LightSSS wave dump | official LightSSS docs; `scripts/xiangshan.py` | CONFIRMED | replay contract must distinguish build prerequisites from run flags |
| waveform output policy | wave saved to build dir in LightSSS; local XSPdb waves default to cwd and `.fst`; XSPdb fork backup keeps latest 2 | official docs; local scripts | CONFIRMED | artifact package must record output directory, retention, and format |
| `--fork-interval` | snapshot workflow CLI mentioned in XSPdb docs | local docs only | CONFLICTED | do not script against undocumented/absent local entrypoints |

Notes:

- `scripts/xiangshan.py` auto-enables `EMU_TRACE` when fork capture is active unless `--disable-fork` or `--trace-fst` changes the mode (`ref_submodule/xiangshan/scripts/xiangshan.py:80-81,142-143`).
- XSPdb waveform control is off at init, resume/pause based, and requires absolute paths for explicit files (`ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_wave.py:32-81`).

### A8. Interactive Debug Surface: Failures to Replay

| Surface | What it does | How it connects to failure capture | Evidence |
|---|---|---|---|
| `xbreak` | break on signal condition via clock callback | direct hardware trigger for replay boundary | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_break.py:31-86` |
| `xbreak_expr` | compiled boolean/time-window trigger | trigger on multi-signal conditions without Python per-cycle overhead | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_break.py:156-187`; `ref_submodule/xiangshan/docs/XSPdb/design/trigger_expr_spec.md:12-20,76-83` |
| `xbreak_fsm` | multi-step sequence trigger | encode failure signatures such as PC/order sequences | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_break.py:234-257`; `ref_submodule/xiangshan/docs/XSPdb/design/trigger_fsm_spec.md:11-16,111-129`; `ref_submodule/xiangshan/docs/XSPdb/examples/pc_sequence.fsm:1-23` |
| `xwatch_commit_pc` | commit-boundary PC watch | stop near targeted commit address | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_difftest.py:371-412` |
| `xstep` | cycle stepping with break/diff/trap polling | main interactive replay loop | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_dut.py:41-101,202-223` |
| `xistep` | instruction stepping from commit-PC changes | align replay to commit events instead of raw cycles | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_difftest.py:223-255,257-318` |
| `xdifftest_turn_on_with_ref` | arm REF comparison | couples replay to mismatch detection | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_difftest.py:344-359` |
| `xexpdiffstate` | export current difftest state to debugger frame | manual inspection point, but not a file artifact in this checkout | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_difftest.py:363-370` |
| `xpc` | print commit PCs/instructions | lightweight commit window view | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_difftest.py:175-183` |
| `xwave_on/off/flush/continue` | selective wave lifecycle | replay wave only around suspect region | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_wave.py:56-162` |
| `xfork_backup_on/off/status` | waiting child `.fst` capture on trigger | bounded interactive pre-failure wave around `xbreak` | `ref_submodule/xiangshan/scripts/xspdb/xscmd/cmd_fork_backup.py:364-435` |
| `--script` / `--replay` / `--cmds` | reproducible command injection | make failure localization rerunnable | `ref_submodule/xiangshan/scripts/xspdb/cli_parser.py:67-96`; `ref_submodule/xiangshan/scripts/xspdb/xspdb.py:41-54,191-196,228-248,602-686` |

### A9. Artifact Package Contract

| Artifact | XiangShan support | Status | Evidence | GPGPU contract consequence |
|---|---|---|---|---|
| waveform (`.fst`) | LightSSS child dump; XSPdb selective wave; XSPdb fork wave | CONFIRMED | official LightSSS docs; `cmd_wave.py`; `cmd_fork_backup.py:189,229-239` | required or explicit reason why unavailable |
| child log | `fork_backup.log` | CONFIRMED | `ref_submodule/xiangshan/docs/XSPdb/design/fork_backup.md:9`; `cmd_fork_backup.py:295-316` | required for replay provenance |
| parent log | `fork_backup_parent.log` | CONFIRMED | `cmd_fork_backup.py:319-325,377,396` | required for wake/reap provenance |
| difftest exit status | runtime diff exit code from `GetDifftestStat()` | CONFIRMED | `cmd_difftest.py:104-118` | capture mismatch status and reason in report |
| register/CSR snapshot | interactive summary from `difftest_stat`; flash init/load helpers | CONFIRMED | `cmd_info.py:236-277`; `cmd_regs.py:144-179`; `docs/XSPdb/examples/registers.md:4-16` | promote to explicit saved file in GPGPU tool |
| disassembly window | `xdasm*`, symbol-aware window, cache | CONFIRMED | `docs/XSPdb/design/disasm.md:15-42`; `docs/XSPdb/examples/disasm.md:3-13` | required around failing PC/event |
| PC/commit window | `xpc`, commit list, watched commit PC, FSM PC sequence trigger | CONFIRMED | `cmd_difftest.py:158-183,371-412`; `cmd_info.py:253-256,300-317`; `examples/pc_sequence.fsm` | required around failing warp/CTA boundary |
| command script | `--script`, `xload_script`, example `.txt` | CONFIRMED | `cli_parser.py:67-72`; `cmd_batch.py:67-118`; `examples/xspdb_script_example.txt:1-8` | required for exact replay |
| replay log | `--replay`, `xload_log`, `@cmd{...}` markers | CONFIRMED | `xspdb.py:47-54,151-152,602-686` | required when debugging from recorded session |
| JSON diff snapshot file | doc says yes; code says no | CONFLICTED | `design/difftest_snapshot.md:37-40`; `cmd_difftest.py:363-370` | do not promise file export unless implemented |
| packaged tarball of all debug artifacts | not in pass-3 local surfaces read | MISSING | no bundle script in requested corpus | GPGPU skill must add explicit bundling |

### A10. Mismatch-to-Debug-Window Table

| Mismatch type | Failing event to report | Suspected modules | Required debug window | Required artifacts |
|---|---|---|---|---|
| wrong register value | `WarpInstrCommit` or `LaneRegWriteback` | lane regfile, writeback mux, scoreboard, replay/flush path | commit window + lane writeback + regfile + scoreboard | replay command, commit trace, writeback trace, register snapshot, disassembly |
| wrong memory value | `MemoryTransaction` | coalescer, address generator, cache/L1/L2/NoC, LSU replay | failing memory event + prior coalescer/transaction path | replay command, transaction trace, waveform, commit window, outstanding txn view |
| barrier hang | `Timeout` or `IllegalState` on stalled barrier | warp scheduler, barrier unit, active-mask state, scoreboard | pre-timeout scheduler + barrier queue + active-mask evolution | replay command, timeout counters, PC/commit window, barrier trace |
| atomic mismatch | `MemoryTransaction(op=atomic)` | atomic unit, serialization point, memory ordering, outstanding txn table | atomic issue-to-retire window | replay command, atomic trace, outstanding txn trace, waveform |
| fence mismatch | `FenceRetire` / ordering violation | memory ordering logic, LSU drain, scoreboard | drain window before/after fence | replay command, commit trace, outstanding txn trace, memory ordering trace |
| timeout/deadlock | `Timeout` | scheduler, outstanding memory, deadlock watchdog, barrier/atomic queues | bounded pre-timeout window + last forward-progress event | replay command, counter snapshot, PC/commit window, suspected-module list, waveform |

Rule:

```text
The rewrite-loop-controller must never report only "test failed".
It must produce a bounded failure package with failing event, suspected modules,
required trace windows, and a replay command.
```

### A11. Minimal Replay Command Contract

Required fields:

- exact launcher: `./build/emu` or `python3 scripts/pdb-run.py`
- workload image or checkpoint path
- reference shared object path (`--diff`) when diff-based localization is required
- trigger source: script (`--script`) or replay log (`--replay`) or injected commands (`--cmds`)
- any non-default memory / flash / first-instruction overrides
- waveform destination/window when wave is required
- fork/checkpoint mode selection when using batch auto-capture

Locally verified replay templates:

```bash
$NOOP_HOME/build/emu \
  -i /abs/path/to/image-or-checkpoint \
  --diff /abs/path/to/riscv64-nemu-interpreter-so \
  --enable-fork
```

Build precondition for the command above:

```bash
make emu EMU_TRACE=1
```

Interactive/batch replay template using only local XSPdb surfaces:

```bash
python3 scripts/pdb-run.py \
  --batch 1 \
  -i /abs/path/to/image-or-checkpoint \
  --diff /abs/path/to/riscv64-nemu-interpreter-so \
  -s /abs/path/to/failure_replay.txt \
  --wave-path /abs/path/to/replay.fst \
  --mem-base-address 0x80000000 \
  --diff-first-inst-address 0x80000000
```

Local caveats:

- `--script` / `--replay` are handled only in batch mode (`ref_submodule/xiangshan/scripts/xspdb/xspdb.py:310-315`).
- In this checkout `--batch` is parsed as a valued argument, not a `store_true` flag (`ref_submodule/xiangshan/scripts/xspdb/cli_parser.py:61-62`), so a truthy token such as `1` is the locally safe form.
- Do **not** use `python3 scripts/emu.py --fork-interval ...` as the “minimal local replay command”; that file is absent here.

### A12. Required Evidence Table

| XiangShan Mechanism | Source Files / Docs | Problem Solved | Transferable GPGPU Abstraction | Skill Rule | Required Schema | Anti-Pattern to Avoid |
|---|---|---|---|---|---|---|
| `[CONFIRMED]` LightSSS periodic fork snapshot | official LightSSS docs | avoid full-run wave; preserve failure-neighborhood state without serialized checkpoint files | two-tier failure capture: fork/checkpoint window + replay-on-failure | every regression failure must have a bounded replay window | `failure_capture.window`, `failure_capture.modes.batch_auto` | always-on whole-run waveform |
| `[CONFIRMED]` build-time `EMU_TRACE` + runtime `--enable-fork` | official LightSSS docs; `ref_submodule/xiangshan/scripts/xiangshan.py:80-81,142-143,290-296` | separates build prerequisites from runtime capture | split GPGPU debug knobs into compile-time and run-time requirements | replay command must include both prerequisites and runtime flags | `failure_capture.modes.batch_auto.required_*` | runtime flag that silently does nothing because build lacked trace support |
| `[CONFIRMED]` XSPdb `xfork_backup_*` interactive fork wave | `ref_submodule/xiangshan/docs/XSPdb/{README.md,design/fork_backup.md,examples/fork_backup.md}`; `cmd_fork_backup.py` | capture short interactive pre-failure wave around an `xbreak` | debugger-local bounded replay mode | local debug must support trigger-bound wave capture independent of CI mode | `failure_capture.modes.interactive_replay`, `artifacts.waveform_or_reason_missing` | conflating CI auto-capture with human-driven replay |
| `[CONFIRMED]` selective waveform lifecycle (`xwave_on/off/flush/continue`) | `design/waveform.md`; `cmd_wave.py`; `examples/waveform.md` | keep wave cost low and reuse captured windows | explicit wave lifecycle for GPGPU replay | traces must be enableable near the suspect region only | `artifact_policy.waveform`, `replay.wave_control` | dumping wave from reset to failure by default |
| `[CONFIRMED]` signal / expr / FSM triggers | `cmd_break.py`; `design/{breakpoints.md,trigger_expr_spec.md,trigger_fsm_spec.md}` | localize failure to event signatures, not only cycle counts | trigger DSL for warp/memory/barrier sequences | every hard-to-hit failure may define a trigger expression or FSM | `trigger`, `failure_signature`, `suspected_modules` | CPU-specific trigger names hardcoded into a generic skill |
| `[CONFIRMED]` difftest-linked commit stepping and state views | `cmd_difftest.py`; `cmd_info.py` | align replay to commit boundaries and export synchronized debug state | event-boundary replay and summary views | mismatch reports must cite event boundary, PC/commit context, and ref status | `mismatch`, `context`, `pc_or_commit_window` | reporting only cycle number with no event context |
| `[CONFIRMED]` NEMU LightQS register+memory rollback | `ref_submodule/xiangshan-nemu/{include/cpu/cpu.h,src/cpu/cpu-exec.c,src/memory/paddr.c,src/isa/riscv64/difftest/ref.c}` | restore replayable reference state including memory effects | failure capture must include state rollback semantics, not just RTL signals | ref/golden replay must support restore of architectural state and memory history | `golden_snapshot`, `restore_contract`, `memory_transaction_trace` | register-only replay for memory/atomic/fence bugs |
| `[CONFIRMED]` replayable command logs via `@cmd{...}` | `xspdb.py:47-54,151-152,602-686`; `cmd_batch.py:40-77` | make debug sessions reproducible | command-log-as-artifact | every failure package must include a replay script or replay log | `replay_command`, `failure_script_or_replay_log` | screenshots/manual notes instead of machine-runnable replay |
| `[CONFLICTED]` docs/runtime drift (`emu.py`, JSON export) | `design/difftest_snapshot.md:35,37-40`; missing `scripts/emu.py`; `cmd_difftest.py:363-370` | prevents false assumptions about artifact surfaces | skill must privilege executable surfaces over stale docs | if docs and runtime disagree, mark conflict and prefer local executable truth | `evidence_status`, `runtime_surface` | silently copying stale documentation into the skill |

### A13. Claim Index

| Claim ID | Claim | Status | Evidence | Confidence |
|---|---|---|---|---|
| `XS-LS-C001` | LightSSS exists to save only the waveform/debug region near failure instead of whole-run wave. | CONFIRMED | official LightSSS docs | High |
| `XS-LS-C002` | LightSSS fork captures whole-process state, addressing the limitation of RTL-only serialized snapshots. | CONFIRMED | official LightSSS docs | High |
| `XS-LS-C003` | `FORK_INTERVAL`, `SLOT_SIZE`, `WAIT_INTERVAL` semantics are documented, but exact local values are unavailable in this checkout. | MISSING | official LightSSS docs; missing local `difftest` submodule | High |
| `XS-LS-C004` | Local `scripts/xiangshan.py` injects `--enable-fork` and auto-configures trace-related make variables for fork capture. | CONFIRMED | `ref_submodule/xiangshan/scripts/xiangshan.py:80-81,97,135-157,290-296` | High |
| `XS-LS-C005` | XSPdb fork backup is an interactive `xstep`-path feature, not the batch emu loop. | CONFIRMED | `ref_submodule/xiangshan/docs/XSPdb/README.md:64-66`; `design/fork_backup.md:11` | High |
| `XS-LS-C006` | XSPdb fork backup uses one waiting child, wake-by-break, `.fst` output, child/parent logs, and a two-wave retention policy. | CONFIRMED | `cmd_fork_backup.py:27-42,57-92,161-170,339-362` | High |
| `XS-LS-C007` | `xstep` is the place where breakpoints, fork tick, difftest exit, and trap/good-loop exits converge. | CONFIRMED | `cmd_dut.py:41-101` | High |
| `XS-LS-C008` | XSPdb trigger engines run on clock-edge callbacks and support multi-step FSM signatures. | CONFIRMED | `cmd_break.py:31-86,156-187,234-257`; trigger specs | High |
| `XS-LS-C009` | NEMU LightQS snapshot/restore includes registers, CSR, MMU state, and memory rollback logs. | CONFIRMED | `cpu-exec.c:525-667`; `paddr.c:334-367` | High |
| `XS-LS-C010` | The local replay surface is `pdb-run.py` + XSPdb batch/interactive controls; `scripts/emu.py` is absent. | CONFLICTED | missing file; `cli_parser.py`; `xspdb.py:310-315` | High |
| `XS-LS-C011` | Local `xexpdiffstate` is not a JSON file export. | CONFLICTED | `design/difftest_snapshot.md:37-40`; `cmd_difftest.py:363-370` | High |
| `XS-LS-C012` | GPGPU should require replay scripts/logs, waveform policy, and trace-window declarations in every failure package. | INFERRED | derived from confirmed XiangShan mechanisms above | Medium |

### A14. Full Contradictions / Missing Contracts

| Issue | Files involved | Why it matters | Severity | Suggested owner |
|---|---|---|---|---|
| `emu.py --fork-interval` documented but absent locally | `docs/XSPdb/design/difftest_snapshot.md`, `docs/XSPdb/examples/difftest_snapshot.md`, missing `scripts/emu.py` | local replay instructions can fail immediately | High | XiangShan docs / local tooling owner |
| JSON diff-state export documented but not implemented in local command | `design/difftest_snapshot.md`, `scripts/xspdb/xscmd/cmd_difftest.py` | artifact expectations become wrong | Medium | XSPdb docs/runtime owner |
| exact LightSSS config defaults unavailable | official docs + missing `ref_submodule/xiangshan/difftest` | prevents exact tuning/retention defaults in contract | High | repo setup / submodule owner |
| generic `xwatch` auto-report behavior unclear from local code | `design/watchpoints.md`, `cmd_dut.py`, `cmd_info.py` | do not over-promise watchpoint artifact behavior | Low | XSPdb docs/runtime owner |
| no bundled failure package artifact writer in the inspected local surfaces | requested corpus | leaves users to assemble artifacts manually | Medium | downstream skill/tooling owner |

### A15. Full Quality Gate

Evidence checklist:

| Check | Result | Notes |
|---|---|---|
| Scope declared | PASS | mode, depth, focus, non-goals, files read/skipped listed |
| Planner focus answered | PASS | all 7 extraction questions addressed |
| Evidence attached | PASS | each planning-relevant claim cites file/URL anchors |
| Claim status used | PASS | `CONFIRMED`, `INFERRED`, `UNCERTAIN`, `CONFLICTED`, `MISSING` used explicitly |
| Contradictions reported | PASS | `emu.py`, JSON export, watch behavior surfaced |
| Missing contracts reported | PASS | missing local `difftest` config surfaced |
| Handoff actionable | PASS | next actions specify exact missing reads and contract decisions |

Readability checklist:

| Check | Result | Notes |
|---|---|---|
| Handoff length | PASS | chat can stay compact; details moved to appendix |
| Findings capped | PASS | top findings kept concise |
| Tables limited | PASS | tables are in appendix where bulk is expected |
| Empty sections removed | PASS | only relevant repository sections retained |
| Decision relevance | PASS | all sections target failure-capture contract decisions |
| Appendix separation | PASS | full evidence retained here; chat handoff can stay short |

Repository extra gate:

| Topic | Status | Notes |
|---|---|---|
| ISA semantics | not applicable | intentionally out of shard scope |
| instruction encoding | not applicable | intentionally out of shard scope |
| decode path | not applicable | intentionally out of shard scope |
| PC / warp state | inferred | only as replay-context requirement for GPGPU |
| active mask | inferred | required in GPGPU mismatch context, not XiangShan-local pass |
| SIMT divergence | not applicable | CPU-specific repo, not a pass-3 topic |
| register file | confirmed | only insofar as debug summary / snapshot exports it |
| scoreboard / hazards | inferred | required GPGPU transfer for failure windows |
| issue / execute / writeback | not applicable | only commit-step boundary used |
| memory coalescing | inferred | GPGPU transfer target, not XiangShan-local mechanism |
| shared memory | inferred | GPGPU transfer target |
| barrier semantics | inferred | GPGPU transfer target for timeout/hang capture |
| CSR / DCR / config state | confirmed | NEMU/XSPdb snapshot exposes control state |
| launch protocol | not applicable | CPU repo |
| kernel arguments | not applicable | CPU repo |
| grid/block/warp mapping | inferred | GPGPU transfer target only |
| CModel / golden model | confirmed | difftest/NEMU surfaces inspected |
| trace diff / compare path | confirmed | XSPdb difftest integration inspected |
| tests and coverage | missing | no pass-3 failure-capture tests were inspected |
| synthesis / FPGA / PPA evidence | not applicable | out of shard scope |

## Quality Gate

- Overall status: PARTIAL
- Evidence status: PARTIAL
- Readability status: PASS
- Safe for GPT-5.5 planning: yes, with caveats
- Full appendix generated: yes
- Biggest evidence gap: missing local `ref_submodule/xiangshan/difftest/config/config.h` for exact `FORK_INTERVAL` / `SLOT_SIZE` / `WAIT_INTERVAL` defaults
- Biggest readability issue: XiangShan uses two different fork-based failure-capture surfaces (`LightSSS` batch auto-capture vs `XSPdb` interactive fork backup) and they must not be collapsed into one ambiguous rule
- Required next read: initialized `ref_submodule/xiangshan/difftest/config/config.h` from the matching XiangShan revision
