# GPGPU Skill

## Summary

本 skill 的目标可以明确拆分为两个核心问题：
1. 如何保证生成结果的正确性与一致性
2. 如何保证生成的 GPGPU 具有良好性能

存在的问题：
gpgpu的生成质量仍然和你提供的 template 强正相关。关键在于如何提升 skill 的上限，而由某 RTL template 决定，而应该由以下三件事共同决定：

template 决定默认质量和稳定性；
contract / property / test 决定正确性；
design space / DSE / benchmark 决定性能上限。


### 1. 如何保证生成结果的正确性与一致性（同一 spec → 相同结果）

**已经做到：**

* 通过 `SYSTEM_CONTRACT_IR` 建立单一语义真源，避免多源语义漂移。
* 强制 `GOLDEN_CONTRACT_MODEL`、toolchain、runtime、RTL 全部从 contract 派生，确保语义一致。
* 引入 validation 证据闭环（trace、hash、fingerprint、first divergence 等），保证结果可验证。
* 使用 rewrite loop 严格限制语义修改路径，避免生成过程中引入隐式变化。
* 引入 deterministic transform、canonical hash、byte-stable 等约束，明确要求生成稳定性。

---

### 2. 如何保证生成的 GPGPU 具有良好性能

**已经做到：**

* 建立完整性能分析框架：`PERFORMANCE_METRIC_IR`、`PERF_ATTRIBUTION_GRAPH`。
* 引入 stall taxonomy、memory/interconnect/atomic/sync attribution。
* 强制性能结论必须绑定 counter 和 trace 证据。
* 定义合理的性能归因路径（从 occupancy 到 DRAM）。
* 引入 counter producer audit，避免错误归因。
* 明确 Yosys PPA 边界，避免虚假性能声明。

**没有做到：**

* 没有明确的性能目标函数（什么叫“性能好”）。
* 没有 benchmark suite 和 workload 定义。
* 没有参数搜索 / DSE 机制。
* 没有 Pareto 优化策略。
* 没有后端 timing/frequency 闭环。
* rewrite loop 只能解释性能问题，不能主动优化设计。

**为什么没有做到：**

* 当前系统偏“分析与验证”，而不是“优化与搜索”。
* 缺少统一的性能目标定义，导致无法驱动优化。
* 缺少 workload，使性能评估不可比较。
* 缺少自动化设计空间探索机制。

**还需要怎么做：**

* 定义 `PERFORMANCE_TARGET_IR`（目标、约束、权重）。
* 构建标准 benchmark suite（覆盖典型 GPGPU workload）。
* 引入 `DSE_PLAN_IR`，支持参数搜索与 Pareto 分析。
* 建立 weighted performance report，用于设计比较。
* 引入 backend timing flow（nextpnr / Vivado / OpenSTA）。
* 扩展 rewrite loop，使其支持“优化动作 + 预期收益 + 回滚条件”。

---

## 已经做到

### 正确性

1. **单一语义真源**：`SYSTEM_CONTRACT_IR` 统一拥有 ISA、execution、state、memory、launch、interface、config 等语义。
2. **Golden model 派生约束**：`GOLDEN_CONTRACT_MODEL` 不是第二套 simulator truth，只是 contract 的可执行视图。
3. **Toolchain/runtime 防漂移**：assembler、disassembler、program image、loader、runtime launch 都要求从 contract 派生，并做 roundtrip/hash equivalence。
4. **RTL binding 结构化**：RTL 不再是松散 wire map，而是 module template、contract path、`INTERFACE_BINDING_IR`、partial sim、trace tap、timing feedback 的组合。
5. **Validation 证据闭环**：correctness gate、pass evidence、trace coverage、regression fingerprint、first divergence、root cause、normalized trace 都已定义。
6. **Rewrite loop 不污染语义**：rewrite 只路由 owner 和 revalidation gate，不直接修改 contract/RTL/toolchain 语义。
7. **Yosys 亲和性已有专门 skill**：`gpgpu-flow-yosys` 和 RTL style gate 已覆盖 top-level unpacked array port、large memory reset loop、data-dependent while、valid/ready hygiene、done 稳定性等问题。

### 性能

1. **性能结论必须有证据**：性能不再是口头判断，而是 `PERFORMANCE_METRIC_IR`、`PERF_ATTRIBUTION_GRAPH`、stall matrix、memory attribution 等结构化对象。
2. **归因顺序合理**：从 launch/occupancy、scheduler、scoreboard、SIMT divergence、coalescing、bank conflict、L1/MSHR、ICNT、L2、DRAM、scoreboard release 逐层排查。
3. **GPGPU 性能关键路径覆盖较全**：memory path、interconnect、atomic/sync packs 覆盖 coalescer、LDS bank、L1/L2/MSHR、NoC、backpressure、atomic serialization、barrier/fence/WSYNC。
4. **counter producer audit 设计正确**：parser-only / visualization-only counter 不能用于稳定 root cause。
5. **Yosys PPA 边界清晰**：Yosys baseline 只能支持 cell count、wire bits、hierarchy size、relative area trend、synthesis hygiene，不能声称 timing closure 或 MHz。

## 没有做到

### 正确性缺口

1. **还没有全局 deterministic generation contract**
   文档要求 byte-stable，但没有统一规定 spec normalization、字段排序、ID 命名、module/signal/file naming、volatile 字段排除和双跑 diff。

2. **旧 preset 名称和新 preset 名称混用**
   新表中统一使用 `MINIMAL_SIMT_CORE`、`SINGLE_SM_WARP_PIPELINE`、`TOOLCHAIN_RUNTIME_VERTICAL_SLICE` 等 preset；旧 preset 名称必须由 forbidden-token gate 阻止回归。否则会破坏同 spec 稳定选择。

3. **schema 还不是强可执行规范**
   很多 schema 字段仍是 `map`、`any` 或自然语言 rule。当前能指导 LLM，但还不能完全机械验证 enum、cross-field invariant、contract path existence、hash equivalence。

4. **测试脚本主要验证资产完整性，不等于端到端正确性**
   当前脚本通过说明 skill 打包健康，但还没有证明 assembler/disassembler 真实 roundtrip、golden 真执行、RTL 真仿真、trace 真 diff、Yosys 真 elaborate/synth。

5. **formal/property 层还不足**
   还缺少系统化 SVA / SymbiYosys / smtbmc 属性包，例如 valid/ready 无丢包、tag uniqueness、scoreboard release、coalescer restore、barrier/fence/atomic litmus。

### 性能缺口

1. **没有明确性能目标函数**
   “性能好”需要定义 workload、metric、threshold、资源预算和权重。当前有 metric 和 attribution，但缺少强制的 `PERFORMANCE_TARGET_IR`。

2. **缺少 benchmark suite / workload profile**
   需要固定 vector add、SAXPY、reduction、stencil、histogram、scatter/gather、divergence、bank conflict、multi-SM memory streaming 等测试，否则无法比较不同生成结果的性能好坏。

3. **缺少 DSE / 参数搜索机制**
   当前 micro-constraint estimator 是可行性估算，不是优化器。它没有定义参数搜索空间、搜索算法、停止条件、Pareto frontier。

4. **缺少后端 timing/frequency 闭环**
   Yosys 可以做 generic synth hygiene 和面积趋势，但不能证明 Fmax。若目标是 FPGA/高频，需要 nextpnr/Vivado/OpenSTA 等后端证据。

5. **rewrite 还偏归因，不是主动优化生成**
   目前能找出为什么慢、路由 patch，但缺少“候选优化动作 + 预期 metric movement + 回滚条件”的系统规则。

## 优先修改建议

### P0：先修 determinism 基础

1. 统一 preset 命名，删除旧名称残留。
2. 更新 `enum_table.yaml`，与 capability profile 和 architecture decision rules 保持一致。
3. 确保 interface/golden mismatch failure mode 拼写由 forbidden-token gate 阻止回归。
4. 新增 `canonical_generation_rules.md`：字段排序、stable ID、module/signal/file naming、hash 计算、volatile 字段排除。
5. 新增 `DETERMINISM_MANIFEST_IR`：记录 input spec hash、normalized spec hash、artifact hash、volatile fields、comparison policy。
6. 新增 determinism CI：同一 spec 连续生成两次，剥离 volatile 字段后 diff。

### P1：让 schema 和 case 变成可执行门禁

1. 将关键 schema 转为严格 JSON Schema / Pydantic / Cerberus。
2. 所有 expected YAML 跑 schema validation。
3. 所有 contract path 必须能在 `SYSTEM_CONTRACT_IR` 中解析。
4. 所有 hash 必须按 canonical serialization 真实计算。
5. case 不只检查 token，还要检查输入、输出、failure mode、patch route、required gates。

### P2：补齐正确性验证上限

1. 新增 formal/assertion pack。
2. 新增 Yosys/SymbiYosys/smtbmc profile。
3. 新增 end-to-end vertical slice runner：assemble → program image → golden execute → RTL sim → trace normalize → diff → Yosys elaborate/synth。
4. 把 `PASS_EVIDENCE_REPORT` 和 `REGRESSION_FINGERPRINT` 接入真实 CI。

### P3：把性能从“可解释”推进到“可优化”

1. 新增 `PERFORMANCE_TARGET_IR`。
2. 新增 `BENCHMARK_SUITE_IR`。
3. 新增 `DSE_PLAN_IR`。
4. 新增默认 `WEIGHTED_PERF_REPORT`。
5. 新增 backend timing flow 边界。
6. 扩展 rewrite rules，从“瓶颈归因”增加到“候选优化动作 + 预期 metric movement + 回滚条件”。

## 结论

这版 skill 的正确性框架已经比较强，适合作为“从 0 到可信 vertical slice GPGPU”的流程骨架。它知道谁是真源、谁是派生物、谁负责语义、谁负责 RTL、谁负责验证、谁负责 patch routing，也引入了 trace、hash、provenance、fail-closed、Yosys compatibility 和 regression fingerprint。

它的主要短板不是缺少模块，而是缺少**全局可执行闭环**：同 spec 双跑 diff、严格 schema validator、真实 end-to-end runner、formal/property gate、benchmark/DSE/performance target。补齐这些之后，它才会从“指导 LLM 正确设计 GPGPU 的 skill”提升为“能持续产出可重复、可验证、可优化 GPGPU 设计的工程系统”。
