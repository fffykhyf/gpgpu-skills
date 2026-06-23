# ISA Table Derivation

Derive all ISA-facing toolchain artifacts from:

- `SYSTEM_CONTRACT_IR.isa_model.opcodes`
- `SYSTEM_CONTRACT_IR.isa_model.instruction_encodings`
- `SYSTEM_CONTRACT_IR.isa_model.operand_fields`
- `SYSTEM_CONTRACT_IR.isa_model.decode_classes`
- `SYSTEM_CONTRACT_IR.isa_model.assembly_syntax`

Derived artifacts include:

- `tools/isa.py`
- `tools/encoding_table.py`
- `tools/assembler.py`
- `tools/disassembler.py`
- `rtl/defines.svh`
- `rtl/decode.svh`
- `docs/isa.md`

Rules:

- Take every opcode, funct field, operand field, width, signedness, immediate layout, branch offset rule, and alignment rule from `SYSTEM_CONTRACT_IR`.
- Reject hand-written opcode constants in assembler, disassembler, RTL defines, or docs.
- Reject docs or RTL as truth sources.
- Compute `isa_model_hash`, `tools_isa_table_hash`, `assembler_table_hash`, `disassembler_table_hash`, and `rtl_defines_hash`.
- Require `isa_model_hash == tools_isa_table_hash == assembler_table_hash == disassembler_table_hash == rtl_defines_hash`.

Failure modes:

- `ISA_TABLE_DERIVATION_FAIL`
- `ISA_ENCODING_DRIFT`
- `SOURCE_OF_TRUTH_DRIFT`
- `INSUFFICIENT_SKILL_ASSET`
