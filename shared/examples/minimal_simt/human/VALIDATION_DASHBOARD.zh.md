# 验证看板

## 总体状态
- 当前 verdict：correctness pass with performance warning。
- RTL vs golden：pass。
- toolchain smoke：pass。
- runtime launch：pass。
- memory dump：pass。
- performance warning：LSQ replay/backpressure。

## 通过证据
| 项目 | 状态 | 证据摘要 |
|---|---|---|
| assembler roundtrip | PASS | program image hash stable |
| golden image execution | PASS | memory dump hash matched |
| RTL vs golden | PASS | no architectural mismatch |

## 覆盖情况
- contract path coverage：sufficient for vector-add vertical slice。
- feature gate coverage：minimal SIMT path covered。
- trace completeness：sufficient for LSQ replay attribution。

## 性能摘要
- total cycles：96。
- issue utilization：受 memory wait 限制。
- memory stall：scoreboard wait cycles 42。
- scheduler stall：次要。
- top bottleneck：LSQ replay overhead。

## 当前阻塞
- 阻塞项：performance root cause 需要 patch card。
- owner：`gpgpu-loop`。
- 下一步：生成 RTL patch plan。

Source AI artifacts: `CORRECTNESS_GATE_REPORT`, `PASS_EVIDENCE_REPORT`, `PERFORMANCE_METRIC_IR`, `PERF_ATTRIBUTION_GRAPH`
