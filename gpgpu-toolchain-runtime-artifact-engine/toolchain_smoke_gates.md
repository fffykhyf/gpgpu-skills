# Toolchain Smoke Gates

Run these gates before passing artifacts downstream:

1. ISA table derivation smoke
2. assembler parse smoke
3. assembler encode smoke
4. disassembler decode smoke
5. asm-disasm roundtrip smoke
6. program image layout smoke
7. entry symbol resolve smoke
8. runtime argument encoding smoke
9. loader contract smoke
10. golden program image execution smoke

The golden execution smoke must execute:

```text
PROGRAM_IMAGE_IR -> GOLDEN_CONTRACT_MODEL decode/fetch/execute -> expected memory dump
```

Rules:

- Golden model must not execute only an abstract instruction list for this gate.
- It must fetch bytes from `PROGRAM_IMAGE_IR`, decode with the contract-derived table, and execute.
- Smoke report must keep evidence hashes for each stage and fail closed on missing evidence.

Failure modes:

- `ISA_TABLE_DERIVATION_FAIL`
- `ASM_PARSE_FAIL`
- `ASM_ENCODE_FAIL`
- `DISASM_DECODE_FAIL`
- `DISASM_ROUNDTRIP_FAIL`
- `PROGRAM_IMAGE_LAYOUT_FAIL`
- `ENTRY_SYMBOL_RESOLVE_FAIL`
- `RUNTIME_ARG_ENCODING_FAIL`
- `LOADER_CONTRACT_FAIL`
- `GOLDEN_IMAGE_EXECUTION_FAIL`
