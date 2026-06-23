# Contract 冻结摘要

## 本次冻结的内容
- ISA：vector-add 所需 load/add/store/branch/end 指令语义。
- ABI：flat argument buffer，A/B/C pointer 顺序。
- memory model：global memory request lifecycle 和 memory dump range。
- launch model：entry PC、grid/block dim、wavefront size、CSR start/done。
- interface semantics：valid/ready memory request、response tag、loader visibility。
- config ownership：wavefront size、max wavefronts、base addresses 由 contract owner 管理。

## 派生关系
- assembler 从哪里派生：`SYSTEM_CONTRACT_IR.isa_model`。
- disassembler 从哪里派生：同一 ISA model 和 encoding table。
- RTL defines 从哪里派生：contract 派生的 opcode/field truth。
- golden model 从哪里派生：`SYSTEM_CONTRACT_IR`。
- runtime launch 从哪里派生：`SYSTEM_CONTRACT_IR.launch_model`。

## 禁止独立定义的内容
- 禁止项 1：assembler 私自维护 opcode truth。
- 禁止项 2：RTL 或 golden model 私自定义 launch ABI。

## 冻结前检查
| 检查项 | 状态 | 证据 |
|---|---|---|
| ISA truth owner | PASS | `SYSTEM_CONTRACT_IR` |
| golden derived from contract | PASS | `GOLDEN_CONTRACT_MODEL` |
| toolchain derivation path | PASS | `TOOLCHAIN_ARTIFACT_IR` |

## 冻结后影响
- 需要重新生成：assembler/disassembler/program image/runtime launch/loader artifacts。
- 需要重新验证：toolchain smoke、RTL binding、RTL vs golden。

Source AI artifacts: `SYSTEM_CONTRACT_IR`, `GOLDEN_CONTRACT_MODEL`, `CONTRACT_SEMANTICS_REPORT`
