# Revalidation Routing

Every patch plan must declare the modules and gates that must rerun.

## Routes

| Patch class | Required route |
|---|---|
| `ARCHITECTURE_PATCH` | Module 1 -> Module 2 -> Module 3 -> Module 4 -> Module 5 |
| `CONTRACT_PATCH` | Module 2 -> Module 3 -> Module 4 -> Module 5 |
| `GOLDEN_MODEL_PATCH` | Module 2 -> Module 3 -> Module 5 |
| `TOOLCHAIN_PATCH` | Module 3 -> Module 4 -> Module 5 |
| `RUNTIME_PATCH` | Module 3 -> Module 4 -> Module 5 |
| `RTL_PATCH` | Module 4 -> Module 5 |
| `PASS_EVIDENCE_PATCH` | Module 5 |
| `TEST_EVIDENCE_PATCH` | Module 5 |

`TOOLCHAIN_PATCH` reruns:

- regenerate `TOOLCHAIN_ARTIFACT_IR`
- assembler smoke
- disassembler roundtrip
- program image smoke
- loader contract smoke
- golden image execution
- RTL image-load smoke
- trace diff

`RUNTIME_PATCH` reruns:

- runtime arg encoding
- CSR launch sequence
- completion and fault observation
- RTL/golden trace diff

`PASS_EVIDENCE_PATCH` reruns:

- pass evidence report generation
- trace coverage check
- performance metric extraction
- regression fingerprint generation

## Gate

No rewrite is accepted until its route produces fresh evidence and a new attribution report.
