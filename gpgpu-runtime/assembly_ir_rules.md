# Assembly IR Rules

`ASSEMBLY_IR` is the canonical input to assembler generation. It may come from hand-written assembly or a lowered pseudo-assembly frontend. A full CUDA-like frontend is not required for the first vertical slice.

Required fields:

- `contract_hash`
- `source_kind`: `hand_written_asm` or `lowered_frontend`
- `sections`: `.text`, `.data`, `.rodata`
- `symbols`: name, section, offset, visibility
- `instructions`: pc, mnemonic, operands, predicate or active-mask info, source line, contract path
- `data_objects`: name, address, bytes
- `relocations`: symbol, relocation kind, patch site
- `canonical_hash`

Rules:

- Parse mnemonics only from `SYSTEM_CONTRACT_IR.isa_model.opcodes`.
- Parse registers, immediates, labels, sections, and comments only from `SYSTEM_CONTRACT_IR.isa_model.assembly_syntax`.
- Preserve source line and contract path for every instruction so later trace attribution can point back to assembly.
- Reject unresolved labels before program-image emission.

Failure modes:

- `ASM_PARSE_FAIL`
- `ENTRY_SYMBOL_RESOLVE_FAIL`
- `SOURCE_OF_TRUTH_DRIFT`
