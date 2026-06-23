# Toolchain Trace Attribution

This component aligns attribution with
`gpgpu-toolchain-runtime-artifact-engine`. It checks the chain from assembly to
RTL fetch/decode before blaming RTL decode or execution.

## Checked Chain

```text
assembly
  -> encoded bytes
  -> disassembly
  -> program image
  -> loader
  -> runtime launch
  -> RTL fetch/decode
```

## Distinctions

The attribution must distinguish:
- assembler parse failure
- assembler encoding mismatch
- disassembler roundtrip mismatch
- program image layout mismatch
- entry PC or symbol resolution mismatch
- loader initialization mismatch
- runtime arg buffer mismatch
- RTL fetch mismatch
- RTL decode mismatch
- golden decode mismatch

## Output

```yaml
toolchain_attribution_report:
  verdict: TOOLCHAIN_PASS | TOOLCHAIN_ROOT_CAUSE_FOUND | TOOLCHAIN_TRACE_INSUFFICIENT
  checked_chain:
    assembly_ir_hash: string
    assembler_output_hash: string
    disassembly_hash: string
    program_image_hash: string
    loader_contract_hash: string
    runtime_launch_hash: string
    rtl_first_fetch_hash: string
  failure_point: ASM_PARSE | ASM_ENCODE | DISASM_DECODE | ROUNDTRIP | PROGRAM_IMAGE_LAYOUT | ENTRY_SYMBOL_RESOLUTION | LOADER_INIT | RUNTIME_ARG_ENCODING | RTL_FETCH | RTL_DECODE
  related_contract_paths:
    - isa_model.instruction_encodings
    - launch_model.program_image_format
    - launch_model.argument_buffer_layout
    - launch_model.loader_contract
  related_artifacts:
    - tools/assembler.py
    - tools/disassembler.py
    - tools/program_image.py
    - tools/runtime_launch.py
    - tools/loader.py
```

## Attribution Rules

- If assembler bytes mismatch ISA encoding truth, classify
  `TOOLCHAIN_ROOT_CAUSE/ASM_ENCODE_MISMATCH`.
- If disassembly does not roundtrip, classify
  `TOOLCHAIN_ROOT_CAUSE/DISASM_ROUNDTRIP_MISMATCH`.
- If image layout or entry PC mismatches loader contract, classify
  `TOOLCHAIN_ROOT_CAUSE/PROGRAM_IMAGE_LAYOUT_MISMATCH` or
  `ENTRY_SYMBOL_RESOLVE_MISMATCH`.
- If runtime launch config, arg buffer, CSR start, completion, or fault
  observation mismatches, classify `RUNTIME_LAUNCH_ROOT_CAUSE`.
- If toolchain chain passes and RTL first fetch/decode diverges, continue to
  RTL functional attribution.
