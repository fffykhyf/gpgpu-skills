# 设计简报

## 目标

构建最小 SIMT GPGPU 垂直切片，覆盖 warp 执行、基础内存路径和运行时启动绑定。

## 非目标

不覆盖多 SM 一致性、完整缓存替换策略、功耗模型或供应商级 ISA 兼容性。

## 硬约束

架构、契约、RTL 绑定和验证产物必须从同一组 IR 派生，禁止在文档中独立定义 ISA 或内存语义。

## 本轮输出

生成 DESIGN_INTENT_IR、ARCH_IR、MICRO_CONSTRAINT_ESTIMATE_IR，并为后续 contract/RTL/validation 阶段提供输入。

## 当前风险

示例仅代表 compact skill 的最小闭环，不能替代完整工具链或完整仿真回归。

## 下一步

冻结 SYSTEM_CONTRACT_IR 和 GOLDEN_CONTRACT_MODEL，然后派生 RTL 绑定与验证窗口。
