# 设计简报

## 目标
- 本轮目标：设计一个最小 self-correcting SIMT GPGPU vertical slice。
- 目标复杂度：教学级、单 CU、小 FPGA 面积。
- 目标平台：FPGA-oriented prototype。
- 主要 workload：vector-add hand-written assembly。

## 非目标
- 本轮明确不做：完整 CUDA frontend、multi-CU cache coherence、复杂 memory hierarchy。

## 硬约束
- ISA / ABI：ISA 和 launch ABI 必须由 `SYSTEM_CONTRACT_IR` 冻结。
- wavefront / CU：1 个 CU，最多 4 个 logical wavefronts。
- memory：LSQ backpressure 必须可观测。
- RTL / FPGA / ASIC：先跑 vertical slice RTL smoke，不做 ASIC PPA。

## 本轮输出
- 架构候选：`MINIMAL_VERTICAL_SLICE_GPGPU`。
- contract 状态：等待 freeze。
- toolchain 状态：需要 assembler、program image、runtime launch、loader smoke。
- RTL 状态：按模块增量绑定。

## 当前风险
- 风险 1：LSQ replay/backpressure 可能造成 scoreboard wakeup stall。
- 风险 2：program image 和 golden execution 必须证明使用同一 ISA truth。

## 下一步
- 建议动作：进入 contract freeze，并生成 toolchain/runtime artifacts。

Source AI artifacts: `DESIGN_INTENT_IR`, `ARCH_IR`, `MICRO_CONSTRAINT_ESTIMATE_IR`
