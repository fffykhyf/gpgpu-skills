---
name: gpgpu-runtime
description: 用于设计、修改或评审 GPGPU runtime、host/device launch、driver API、command queue、MMIO 或 DCR control、doorbell、DMA、buffer、module、kernel handle、kernel entry、args、grid/block/CTA/workgroup dispatch、event、fence、cache flush 或 synchronization behavior。
---

# GPGPU Runtime Skill

## 1. Objective

把 runtime 拆成 R0 launch ABI definition 和 R1 execution backend，让 host software 把 launch intent 转换成 deterministic GPU launch state，同时不暴露 RTL internals。

## 2. Input Contract

输入是 launch/runtime intent，必须包含 config digest、kernel image expectations、argument model、memory spaces、queue/control-plane needs、target backend，以及 required synchronization/fault behavior。

## 3. Runtime State Model

| Runtime state | Canonical GPU state |
|---|---|
| device/capability state | config-visible limits、memory map、queue limits、feature bits、version |
| module/kernel state | kernel image、entry PC、instruction memory、symbol table、required resources |
| argument state | argument bytes、alignment、pointer mapping、constant/local/shared memory bindings |
| launch state | grid/block dimensions、CTA/workgroup IDs、SIMT group allocation、local memory size |
| queue state | command records、ordering、doorbell/MMIO/DCR writes、backend admission、dependencies |
| execution state | running/completed/faulted kernel、event/fence、timeout、interrupt/status、cache visibility |

## 4. 固定五问

每个 runtime change 必须回答：

1. What state exists? 指明 ABI、queue、launch、memory、completion 或 fault state。
2. Who produces it? Host API、loader、queue builder、MMIO writer、backend 或 device。
3. Who consumes it? Golden sim、RTL dispatcher、memory path、kernel code、event/fence wait 或 PPA。
4. How does it change? 定义 state transition 和 ordering semantics。
5. How do we verify it? 指明 ABI fixture、launch smoke、negative test、trace 或 backend diff。

## 5. R0: Launch ABI Contract

R0 必须先于 backend-specific runtime 工作执行。

| ABI field | Contract |
|---|---|
| kernel image format | image bytes、text/data sections、symbol names、entry PC、required ISA/config version |
| grid/block model | grid dims、block dims、CTA/workgroup IDs、lane/thread IDs、SIMT group partitioning |
| warp dispatch model | simt_group_width、active lane initialization、resident limits、resource allocation |
| argument layout | byte layout、alignment、scalar/pointer encoding、constant memory、local/shared metadata |
| memory space mapping | global、shared/LDS、local、constant、MMIO/uncached spaces、host pointer translation |
| synchronization model | barriers、fences、event semantics、cache flush/visibility、completion/fault reporting |
| capability model | queryable limits、feature bits、memory map、queue count/depth、ABI version |

R0 输出 backend-neutral kernel descriptor，以及 golden sim 和 RTL 都能消费的 argument/memory fixtures。

## 6. R1: Runtime Execution Layer

R1 只能在 R0 稳定后开始。

| Execution component | Contract |
|---|---|
| command queue | command type、order、dependencies、queue full behavior、cancellation/error handling |
| MMIO/DCR/doorbell | register offsets、reset values、side effects、write ordering、capability exposure |
| kernel dispatch engine | resource admission、CTA/workgroup allocation、SIMT group creation、start state |
| DMA/buffer movement | allocation、copy direction、alignment、ownership、cache visibility |
| event/fence system | wait、signal、timeout、interrupt/status、memory-ordering guarantee |
| completion tracking | success、fault code、first fault event、trace identity、cleanup |
| backend HAL | simulator、RTL sim、FPGA 或 device transport，隐藏在同一 runtime state model 后 |

R1 输出 execution timeline：queue admission、launch start、memory visibility events、completion/fault、result readback。

## 7. Transformation Rules

```text
host intent -> R0 ABI descriptor -> backend command -> device launch state -> execution state -> completion/fence state
```

- Host API 不能直接 poke internal PC、register、scoreboard 或 memory signals。
- Kernel descriptor 必须携带 entry PC、launch dims、args pointer、resource limits、config digest、ABI version。
- Queue operations 必须保持 memcpy、launch、event、wait、fence、completion 的 ordering。
- Backend admission 必须拒绝 oversized CTA/workgroup、missing resources、unsupported ISA/config、queue full。
- Fault 必须作为 runtime state 可见，而不是只存在于 simulator logs 或 RTL waveforms。

## 8. State Evolution

| Transition | Producer | Consumer | Verification |
|---|---|---|---|
| `closed -> open` | device open/HAL init | runtime API | capability query test |
| `module bytes -> kernel descriptor` | loader | golden sim/RTL backend | ABI fixture compare |
| `args -> packed argument memory` | host API | kernel code/golden sim | layout unit test |
| `launch descriptor -> queue command` | queue builder | backend scheduler | queue trace |
| `queued -> admitted` | backend admission | dispatch engine | capacity negative test |
| `admitted -> running` | doorbell/MMIO/start command | RTL/golden sim | launch smoke |
| `running -> complete/fault` | backend/device | event/fence wait | completion/fault test |
| `complete -> visible results` | fence/cache flush/readback | host API/PPA | result and trace check |

## 9. Output Contract

- R0 launch ABI document 或 fixture。
- kernel descriptor schema。
- ABI-visible config values 的 generated/runtime header。
- command queue 和 MMIO/DCR contract（若存在 R1）。
- command、launch、admission、completion、fence、fault trace fields。
- invalid kernel、bad args、queue full、timeout、unsupported config 的 negative tests。

## 10. Verification Gate

| Gate | Required proof |
|---|---|
| R0 ABI gate | golden sim 和至少一个 backend fixture 消费相同 descriptor/arg bytes |
| R1 launch gate | 一个 workload 走 public API、queue/doorbell、completion、result readback |
| ordering gate | memcpy/launch/event/wait/fence ordering 出现在 trace |
| capacity gate | oversized launch 或 queue full 产生定义好的 error state |
| fault gate | invalid command、illegal memory、timeout 或 forced fault 报告稳定 runtime state |
| cross-backend gate | simulator 和 RTL backend 使用相同 R0 descriptor |

## 11. Design Evidence Layer

| Evidence | Use |
|---|---|
| GPGPU-Sim | configure-call、argument staging、kernel descriptor、stream operation、backend admission 的 behavioral evidence |
| Rocket Chip | command/response、busy/interrupt/fault、resource exposure、test harness boundaries 的 structural reference |
| Vortex/MIAOW | DCR/MMIO launch control、command processor、FPGA bring-up boundary 的 implementation anchors |
| XiangShan | reproducible run/debug/difftest/checkpoint workflow 的 evidence，不是 GPU ABI template |
| CUDA/PTX | kernel image、args、launch dims、memory spaces、sync 的 ABI constraint |

Framework evidence 只能验证 R0/R1 contract，不能成为独立章节。

## 12. Failure Modes

- launch ABI 和 backend execution 混在一起，导致 simulator/RTL 消费不同 descriptor。
- testbench poke 变成 public runtime API。
- argument layout 改变却不更新 golden sim、RTL、runtime headers 和 tests。
- event/fence 存在但没有 ordering 或 memory-visibility semantics。
- MMIO offsets 缺 reset value、side effect、version 和 negative tests。
- backend logs 显示 fault，但 runtime state 报告 success。
