---
name: gpgpu-rtl-simt-core
description: 用于从 GPU_STATE 和 kernel 执行 pure GPGPU SIMT hardware model，产生 cycle-level simulation、hardware trace、pipeline events、stalls 或 writeback traces。
---

# GPGPU RTL SIMT Pure Hardware Execution Model

## Objective

执行 `GPU_STATE` 所规定的 hardware model。

```text
input:  GPU_STATE + kernel
output: cycle_level_simulation + hardware_trace
```

本 skill 是 pure implementation layer。禁止 reinterpret architecture、modify canonical state、choose scheduling policy、alter memory hierarchy 或发明 transform-engine 未输出的 RTL structures。

## Input Contract

输入必须包含：

- `GPU_STATE` snapshot and hash。
- kernel image and launch identity。
- 来自 `gpgpu-deterministic-transform-engine` 的 RTL mapping artifact。
- fixed trace schema。

拒绝 direct prose specs、unlocked `SPEC_IR` 或 missing transform-engine mappings。

## Output Contract

输出：

```text
hardware_trace = {
  cycle,
  warp_id,
  pc,
  active_mask,
  scheduler_event,
  pipeline_stage_events,
  scoreboard_events,
  execution_unit_events,
  memory_interface_events,
  writeback_events,
  fault_events
}
```

cycle-level summary counters 只能作为 trace-derived data 输出。

## Execution Rules

| Hardware area | Rule |
|---|---|
| scheduler | 执行 `GPU_STATE.scheduler_state` 的 fixed scheduler mapping |
| pipeline | 遵循 mapped fetch/decode/issue/execute/writeback FSM |
| scoreboard | 应用 `GPU_STATE.register_state` 的 dependency rules |
| execution units | 使用 transform artifact 中 fixed latency/port mapping |
| memory interface | emit memory events，不选择 memory behavior |
| CSR/fault | report state-defined control/status behavior |

## Forbidden Behavior

- Reinterpreting architecture。
- Modifying `GPU_STATE`。
- Selecting alternate implementations。
- 从 common RTL practice 补 missing state。
- 把 waveform convenience 当 semantic truth。

## Verification Gate

- 每个 hardware trace event 映射到 `GPU_STATE` field 和 transform table entry。
- 同一 input 的 cycle evolution deterministic。
- scheduler 和 memory behavior 是 consumed，不是 invented。
- hardware trace 可被 `gpgpu-causal-trace-analyzer` 消费。

## Failure Modes

- 因 RTL 更容易实现而改变 state。
- 添加 untracked stall causes。
- 输出 transform-engine 未声明的 trace fields。
- 把 cycle-level events 折叠成 final output only。
- 用 prose explanation 替代 hardware trace debug。
