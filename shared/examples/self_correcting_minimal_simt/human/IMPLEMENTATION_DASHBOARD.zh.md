# 实现看板

## 总体状态
- 当前 verdict：局部 RTL binding 可继续。
- 已绑定模块：scheduler、decode/execute pipeline、register file、scoreboard、LSQ、global interface。
- 局部仿真：关键模块有 partial sim gate。

## 模块绑定状态
| 模块 | 状态 | 证据摘要 |
|---|---|---|
| warp_scheduler | PASS | scheduler contract paths 已绑定 |
| load_store_queue | WARNING | replay/backpressure 需要 performance evidence |
| cache_global_interface | PASS | request/response path 已绑定 |

## 接口风险
- 风险：LSQ replay 可能延迟 scoreboard wakeup。

## 局部仿真
- 已通过：valid/ready stability、response wakeup、loader visibility。
- 未通过：无确定 fail，存在 performance warning。

## 当前阻塞
- 阻塞项：无 correctness blocker。
- owner：`gpgpu-rtl`。

## 下一步
- 建议动作：进入 validation dashboard，检查 memory replay overhead。

Source AI artifacts: `INCREMENTAL_RTL_MAP`, `MODULE_INTERFACE_REPORT`, `RTL_PARTIAL_SIM_REPORT`
