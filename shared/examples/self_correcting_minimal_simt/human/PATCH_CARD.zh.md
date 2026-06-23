# 修复卡片

## 问题摘要
- 问题类型：memory replay overhead。
- 首次发现位置：cycle 40-96 的 LSQ replay window。
- 影响范围：scoreboard wakeup 延迟，降低 issue utilization。

## 证据
- trace window：40-96。
- contract path：`memory_model.request_lifecycle`。
- RTL module：`load_store_queue`。
- toolchain artifact：无 toolchain mismatch。
- confidence：high。

## 判断
- root cause：`MEMORY_SYSTEM_ROOT_CAUSE/MEMORY_REPLAY_OVERHEAD`。
- 选择的 patch 类型：`RTL_PATCH`。
- owner module：`gpgpu-rtl`。

## 修复计划
- 修改目标：`load_store_queue.replay_policy` 和 queue depth。
- 预期效果：减少 wavefront stall cycles。
- 不修改的内容：不修改 ISA、ABI、program image 或 golden semantics。

## 重新验证
- 必须重跑：module partial sim、RTL/golden trace diff、memory dump compare。
- 可选重跑：performance metric extraction。

## 回归风险
- 风险 1：interface latency change。
- 风险 2：duplicate memory request。

Source AI artifacts: `ROOT_CAUSE_REPORT`, `ARCH_REWRITE_PLAN`, `REWRITE_DECISION_REPORT`
