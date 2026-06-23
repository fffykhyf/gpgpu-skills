# 调试摘要

## 问题摘要
- 问题类型：performance warning。
- 影响范围：LSQ replay/backpressure 影响 scoreboard wakeup。

## 首次分歧
- cycle：40。
- wavefront：2。
- pc：vector-add load/use window。
- mismatch type：不是 correctness mismatch，是 replay overhead。

## 证据摘要
- trace window：cycle 40-96。
- contract path：`memory_model.request_lifecycle`。
- RTL module：`load_store_queue`。

## 当前判断
- root cause：`MEMORY_SYSTEM_ROOT_CAUSE/MEMORY_REPLAY_OVERHEAD`。
- confidence：high。

## 下一步
- 建议动作：生成 `RTL_PATCH`，重跑 module partial sim、RTL/golden trace diff 和 memory dump compare。

Source AI artifacts: `FIRST_DIVERGENCE_REPORT`, `ROOT_CAUSE_REPORT`, `PERF_ATTRIBUTION_GRAPH`
