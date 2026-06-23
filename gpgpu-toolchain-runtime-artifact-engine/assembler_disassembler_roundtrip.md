# Assembler/Disassembler Round Trip

## Gate A: Encode

Input: `ASSEMBLY_IR`.

Output: encoded instruction bytes.

Check:

- mnemonic exists in `SYSTEM_CONTRACT_IR.isa_model.opcodes`
- operand count matches `SYSTEM_CONTRACT_IR.isa_model.operand_fields`
- operand width and signedness match contract fields
- immediate value is encodable
- branch offset follows alignment and range rules
- unsupported instruction is rejected or trapped according to `unsupported_instruction_behavior`

Failure: `ASM_ENCODE_FAIL`.

## Gate B: Decode

Input: encoded instruction bytes.

Output: `DISASSEMBLY_IR`.

Check:

- opcode table derives from the same `SYSTEM_CONTRACT_IR`
- decode class is correct
- operand field extraction is correct
- unsupported encoding behavior matches contract

Failure: `DISASM_DECODE_FAIL`.

## Gate C: Round Trip

Path:

```text
ASM -> bytes -> DISASM -> bytes
```

Require byte-equivalent output when formatting is canonical. Allow semantic-equivalent output only when the contract declares aliases or pseudo-instruction expansion rules.

Failure modes:

- `DISASM_ROUNDTRIP_FAIL`
- `UNSUPPORTED_INSTRUCTION_BEHAVIOR_MISMATCH`
- `SOURCE_OF_TRUTH_DRIFT`
