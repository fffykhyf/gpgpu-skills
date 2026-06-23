# XiangShan Reference Library for GPGPU Skills

XiangShan is used as a hardware development-loop reference, not as a CPU
microarchitecture template. The transferable mechanisms are executable golden
reference APIs, layered differential tracing, replayable failure capture, safe
runtime design-space exploration, structured trace databases, and weighted
checkpoint-based performance attribution.

Default skill execution should read `shared/references/xiangshan_lessons.yaml`
and the concise lesson summaries in this directory. Raw reader reports under
`raw/` are lazy-load material for deep investigation only.

## Applies As

- golden reference closure pattern
- trace diff and first-divergence pattern
- bounded failure capture and replay pattern
- runtime-tunable DSE safety pattern
- structured trace DB and query pattern
- representative checkpoint and weighted performance pattern

## Does Not Apply As

- CPU frontend design reference
- branch predictor reference
- rename / ROB reference
- RISC-V privilege or CSR semantics reference
- scalar pipeline template
- XiangShan cache structure template

