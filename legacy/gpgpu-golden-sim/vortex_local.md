# Vortex Local Reference For GPGPU Golden Simulation

This note expands the Vortex references that matter for the `gpgpu-golden-sim`
skill. It is meant to be read before routine simulator, trace, or first
divergence work so you do not need to reopen the whole Vortex tree every time.

Terminology note: this file preserves Vortex source names such as `warp`, `warp ID`, `tmask`, and `CTA`. In the skill contract, map them to `SIMT group`, `simt_group_id`, `active lane mask`, and `CTA/workgroup`; use Vortex names only when quoting source behavior.

## What Vortex Teaches For This Skill

Vortex treats SimX as a modular executable twin of the hardware, not as a
single central interpreter. The simulator owns the same major concepts as the
RTL: scheduler, decode, scoreboard, operands, dispatch, functional units, LSU,
coalescer, caches, local memory, CTA dispatch, and runtime launch state.

For this project, copy the discipline, not the full implementation:

- define the architectural effect before writing the RTL behavior;
- place simulator behavior near the module that owns the corresponding timing;
- include enough trace identity to map a simulator event back to RTL;
- compare first divergent architectural effects before timing details;
- avoid editing the simulator merely to match a suspicious RTL waveform.

## Reference Orientation

Read these Vortex files in this order when the local summary is not enough:

| Path | What to look for |
|---|---|
| `ref/skillref/vortex.md` | The project-level extraction of Vortex lessons: SimX as oracle, trace-first debug, staged memory, runtime/config/PPA separation. |
| `ref_submodule/vortex/docs/simulation.md` | How one workload is run through `simx`, `rtlsim`, and other backends with shared runtime/application paths. |
| `ref_submodule/vortex/docs/debugging.md` | How Vortex uses `run.log`, trace flags, `trace_csv.py`, UUID sorting, and SimX-vs-RTL comparison. |
| `ref_submodule/vortex/docs/designs/simx_simulator_architecture.md` | The main SimX design reference: no central emulator, `SimObject` timing objects, backpressured channels, and module twins. |
| `ref_submodule/vortex/docs/testing.md` | Where regression tests and runtime-facing tests plug into the same simulator/runtime flow. |

## SimX Topology

`ref_submodule/vortex/sim/simx/core.cpp` is the best single code reference for
how Vortex structures a golden simulator as a module twin.

The `Core::Impl` constructor creates a graph of simulator objects that mirrors
the RTL pipeline:

- `Scheduler` owns warp selection, PC, active masks, CTA activation, barrier
  state, and warp suspend/resume.
- `Decoder` and optional `Decompressor` turn fetched instruction words into
  decoded instruction objects.
- `Scoreboard` tracks hazards separately from operand fetch and execution.
- Per-warp `Sequencer` instances model fetch/decode sequencing.
- Per-issue `Operands` objects read source registers.
- Per-FU `Dispatcher` objects route issue slots to ALU, FPU, LSU, SFU, TCU.
- Functional unit objects (`AluUnit`, `FpuUnit`, `LsuUnit`, `SfuUnit`,
  optional `TcuUnit`) own instruction semantics close to the modeled unit.
- The memory path is not hidden inside the core loop: `LocalMem`,
  `LocalMemSwitch`, `MemCoalescer`, `LsuMemAdapter`, optional `Mmu`, and cache
  ports are distinct objects connected through channels.

The lesson for this skill is that a golden simulator should remain debuggable
by ownership. If a bug is in scoreboard wakeup, the simulator should have a
scoreboard owner. If a bug is in LSU response demux, the simulator should have
an LSU/memory owner. A monolithic `execute_instruction()` can be useful for a
first prototype, but it should not become the trusted oracle for RTL timing and
trace alignment.

## Scheduler And Warp State

`ref_submodule/vortex/sim/simx/scheduler.cpp` is the key model for SIMT control
state.

Important details:

- `warp_t` stores `tmask`, `PC`, per-warp `uuid`, `mscratch`, floating/control
  CSRs, and CTA CSRs. Register files live elsewhere, which keeps scheduling
  state separate from operand storage.
- `Scheduler::activate_warp()` installs CTA metadata into the selected warp:
  CTA id/rank/size, thread/block/grid dimensions, kernel entry, local-memory
  address, cluster size, and argument pointer (`mscratch`).
- Reused CTA warps can skip one-time prologue by rewinding the PC to a fixed
  per-CTA dispatch window. This is a runtime/kernel-entry detail that still
  affects the simulator scheduler.
- `schedule()` first lets the CTA dispatcher activate one warp, then handles
  pending `wspawn`, then selects the first active, non-stalled warp allowed by
  the supplied mask.
- A new `instr_trace_t` receives `uuid`, `cid`, `wid`, `cta_id`, `PC`, and
  `tmask` before fetch/decode fills the rest.
- `suspend()` and `resume()` mutate registered next-state (`stalled_warps_next_`)
  so a warp released by decode/commit is not scheduled again in the same cycle.

For a smaller local simulator, keep the same explicit state categories even if
the policy is simpler: active warps, stalled warps, PC, active mask, CTA/kernel
state, and trace identity.

## Instruction Trace Schema

`ref_submodule/vortex/sim/simx/instr_trace.h` is the most useful trace schema
reference. Vortex's `instr_trace_t` carries enough context to connect fetch,
decode, issue, FU behavior, memory, and writeback.

Fields worth preserving conceptually:

- identity: `uuid`, `cid`, `wid`, `cta_id`;
- control: `tmask`, `PC`, raw `code`, decoded instruction pointer;
- writeback: `wb`, `dst_reg`, `dst_data`, `dst_bytesel`;
- operands: `src_regs`, `src_data`;
- execution class: `fu_type`, `op_type`;
- packetization/timing: `pid`, `sop`, `eop`, `num_pkts`, `issue_time`;
- scheduler/debug flags: `fetch_stall`, `resume_warp`.

The `operator<<` prints core/warp/CTA, mask, PC, writeback, destination/source
registers, execution type, packet markers, and UUID. That is the minimum shape
you want from a trace that will be compared against RTL.

Do not overfit the local trace to Vortex field names. Keep the categories:
identity, control, operands, execution class, writeback, memory, and scheduling
reason. Add fields only when they help localize a first divergence.

## Memory Trace Payloads

`ref_submodule/vortex/sim/simx/types.h` defines the memory event payloads used
by SimX:

- `MemReq` carries operation, address, optional data block, byte enable, tag,
  hart id, UUID, and flags. It exposes helpers for write/read and address type.
- `MemRsp` carries tag, hart id, UUID, and optional data block.

This is important for golden simulation because memory correctness is not only
about final memory contents. A useful memory trace must preserve lane mask,
byte enables, original SIMT context, request tag, response ordering, and the
writeback destination. If a simulator only logs `load addr -> value`, it will be
hard to debug coalescing, partial responses, or divergent warp memory behavior.

## LSU Model As Golden Reference

`ref_submodule/vortex/sim/simx/lsu_unit.cpp` gives a practical example of a
unit-level golden model that is more detailed than a pure ISA interpreter.

Useful behaviors:

- `compute_addrs()` implements the AGU formula from decoded operands and
  instruction arguments. It records per-thread address, size, thread id, and
  store/AMO data while respecting the active mask.
- `ingest_inputs()` makes the request queue a real one-cycle stage. A while
  loop would collapse simulated latency and hide timing bugs.
- Fences are held until older per-block requests drain. This is a model of
  ordering, not just a no-op instruction.
- `process_request_step()` emits one memory-side batch per call, allocates
  pending entries for loads/AMOs, saves lane metadata, and tracks whether the
  request is the end of packet.
- `process_response_step()` uses the response tag to recover the pending entry,
  formats signed/unsigned/float load data, applies byte-selection and NaN-boxing,
  then only forwards to writeback when the terminal response arrives.
- Perf counters such as loads, stores, and load latency are updated in the same
  place as the modeled behavior.

The local rule: if an RTL LSU can have outstanding requests, the simulator must
have an explicit pending table or equivalent traceable routing state.

## First-Divergence Workflow In Vortex Terms

Vortex's debugging docs and `ci/trace_csv.py` support a workflow you can reuse:

1. Run the same workload, backend config, input memory, and launch shape on the
   golden simulator and the implementation under test.
2. Emit trace lines with a stable instruction or memory UUID where possible.
3. Sanitize logs into comparable rows. Vortex's `trace_csv.py` is a reference
   for converting noisy logs into sortable trace records.
4. Compare committed architectural effects first: PC, active mask, destination
   register, writeback data, memory write, exception/termination.
5. Only after architectural effects match, compare timing fields such as stall
   reasons, issue cycle, cache latency, or queue occupancy.
6. Classify the first mismatch as simulator bug, RTL bug, runtime/launch bug,
   memory model bug, or test harness mismatch.

## Local Transfer Checklist

- Map every non-trivial RTL module to a simulator owner or explicitly state why
  it is not modeled yet.
- Keep trace identity stable across simulator and RTL. UUID is ideal; a
  deterministic sequence id is acceptable early.
- Make memory requests self-describing: op, address, mask, byte enable, data,
  tag, destination, SIMT context.
- Put instruction semantics near the modeled unit. Do not hide LSU, barrier, or
  scheduler behavior inside a generic interpreter.
- Require a first-divergence report before changing RTL to match simulator or
  simulator to match RTL.
- For bring-up, start with a functional trace, then add timing fields only when
  they answer a specific debug question.

## What Not To Copy

- Do not import every Vortex simulator object if this project has a smaller core.
- Do not require cycle-exact agreement before the architectural trace is stable.
- Do not use Vortex queue sizes, cache sizes, or extension behavior as defaults
  without a local reason.
- Do not let trace format grow without a comparison purpose.
