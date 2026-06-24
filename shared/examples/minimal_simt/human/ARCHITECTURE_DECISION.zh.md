# 架构决策说明

## 本轮选择
- 选择的 preset：`MINIMAL_VERTICAL_SLICE_GPGPU`。
- 核心结构：单 SM、warp scheduler、decode/execute pipeline、register file、scoreboard、LSQ、LDS、global interface。
- 关键参数：1 SM、4 logical warps、小 FPGA 面积优先。

## 选择理由
- 功能理由：能够从 assembly 到 program image，再到 RTL/golden/memory dump 闭环。
- 验证理由：满足 `compile_kernel_to_program_image`、`rtl_sim_smoke_test`、`memory_dump_golden_check`。
- 实现复杂度理由：避免multi-SM 和复杂 cache coherence。
- 性能/面积理由：先保留 LSQ backpressure 可观测性，不追求高吞吐。

## 被拒绝的方案
| 方案 | 拒绝原因 | 后续是否可恢复 |
|---|---|---|
| `MINIMAL_WARP_SM_LEGACY_COMPAT` | 缺少 toolchain/runtime/loader vertical slice | 可恢复 |
| `MULTI_WARP_SINGLE_SM` | 优先级低于 vertical slice 验证目标 | 可恢复 |

## 影响范围
- contract：需要冻结 ISA、launch ABI、memory request lifecycle。
- toolchain：需要派生 assembler/disassembler/program image/runtime launch。
- RTL：需要按模块绑定 scheduler、pipeline、RF、scoreboard、LSQ。
- verification：需要 RTL vs golden、memory dump 和 performance attribution。

## 需要确认的问题
- 问题 1：LSQ replay policy 是否允许后续作为 RTL patch 修复。
- 问题 2：contract freeze 前是否接受 compact system contract。

Source AI artifacts: `ARCH_IR`, `MICRO_CONSTRAINT_ESTIMATE_IR`
