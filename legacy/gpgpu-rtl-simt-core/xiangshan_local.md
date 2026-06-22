# XiangShan Local Reference For GPGPU RTL SIMT Core

This note expands the XiangShan references that matter for the `gpgpu-rtl-simt-core` skill. It focuses on backend state ownership, derived execution-unit ports, writeback consistency checks, recovery/control state, vector metadata, trace/perf hooks, and memory replay boundaries.

Terminology note: XiangShan is an out-of-order CPU. Do not translate rename, ROB, RAB, precise commit, or branch prediction directly into SIMT design. Use XiangShan only as a checklist for ownership, generated checks, and debug/perf visibility.

## What XiangShan Teaches For This Skill

XiangShan's backend is valuable because it avoids hiding everything in one module. It separates control, datapath, issue, execution units, function units, register files, writeback, trace, CSR/debug, and TopDown event generation.

For a local SIMT core, this maps to:

- SIMT group lifecycle owner;
- active lane mask and divergence owner;
- scheduler readiness equation;
- scoreboard dependency owner;
- operand/register-bank owner;
- FU issue and writeback owners;
- LSU replay/wakeup boundary;
- trace and perf owners.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/xiangshan.md` | RTL SIMT lessons and seven-skill mapping. |
| `ref/xiangshan.pdf` | Backend chapters: CtrlBlock, DataPath, Schedule and Issue, ExuBlock, FunctionUnit, VFPU, Debug, HPM. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/Backend.scala` | Backend composition, config checks, CtrlBlock/regions/TopDown wiring. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/BackendParams.scala` | Derived scheduler, issue, FU, read/write port, wakeup, and writeback params. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/CtrlBlock.scala` | Control block, redirect/recovery, frontend/backend control boundary. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/TopDownGen.scala` | Local bottleneck and perf event generation. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/MemBlock.scala` | Backend-to-memory ports, wakeup/writeback/violation boundary. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/lsqueue/LoadQueueReplay.scala` | Replay causes, priority, wakeup, debugTopDown events. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/vector/` | Vector LSU metadata and lane/element style state. |

## Backend Ownership To Borrow

`Backend.scala` derives execution unit configuration, checks consistency, prints generated config, and composes CtrlBlock plus execution regions. The local SIMT rule is:

- do not let scheduler own register dependencies implicitly;
- do not let operand read hide scoreboard behavior;
- do not let LSU completion update random tables directly;
- do not add trace/perf as an afterthought far from event owners.

Each SIMT pipeline stage should state:

- input and output packet fields;
- valid/ready and backpressure;
- kill/flush/replay handling;
- state updates;
- trace event and counter owner.

## Derived Ports And Writeback Checks

`BackendParams.scala` computes FU counts, issue queue counts, load/store execution units, read ports, write ports, and wakeup configurations from execution-unit descriptions. `Backend.scala` checks writeback port configurations against FU writeback requirements.

For local RTL SIMT:

- derive register file read ports from configured issue lanes and FU source requirements;
- derive writeback ports from ALU/FPU/SFU/LSU/TCU result paths;
- derive wakeup and scoreboard-release paths from FU latency and result class;
- fail generation if a configured unit cannot write back, wake dependents, or be traced.

## CtrlBlock And Recovery

XiangShan's CtrlBlock handles CPU redirects, recovery, trace, CSR, exception, and commit-related control. Local SIMT should not copy CPU snapshot recovery directly. Translate the concept into:

- branch/divergence/reconvergence owner;
- active lane mask update;
- SIMT group kill/replay state;
- barrier wait and release;
- memory replay recovery;
- fault and launch-visible status.

## Vector Metadata

XiangShan VFPU and vector LSU references are useful because they carry element/mask/exception/merge metadata through vector-like pipelines. This is closer to GPGPU lane behavior than scalar CPU issue, but it is still not SIMT semantics.

Borrow:

- per-element or per-lane mask propagation;
- merge-buffer and offset metadata;
- exception aggregation;
- writeback mask handling;
- replay metadata.

Do not call XiangShan vector elements "warps" or use vector length as SIMT group residency.

## Memory Replay Boundary

`MemBlock.scala` and `LoadQueueReplay.scala` show that memory wakeup, replay, violation, and writeback are not hidden inside a FU. Local SIMT cores should route LSU events through explicit fields:

- simt_group_id;
- active lane mask;
- destination registers and masks;
- replay cause;
- fault metadata;
- wakeup/writeback validity;
- perf/debug event.

## Caveats

- Do not add rename, ROB, RAB, or precise CPU commit to the SIMT core unless the local architecture explicitly requires them.
- Do not copy XiangShan branch predictor or frontend pipeline as a SIMT fetch model.
- Do not use CPU CSR/debug semantics as GPU runtime ABI.
- Do not treat TopDown CPU event categories as GPU categories without remapping to scheduler, SIMT divergence, LSU, cache, barrier, and runtime events.
