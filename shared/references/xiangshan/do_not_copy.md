# XiangShan Material Not To Copy

Do not migrate XiangShan CPU microarchitecture into GPGPU skills.

Forbidden transfers:

- CPU frontend, fetch queue, branch predictor, FTQ, RAS, TAGE, SC, or uBTB structure
- rename, ROB, scalar commit, CPU issue queue, or scalar pipeline semantics
- RISC-V privilege, exception, interrupt, PMP/PMA, CSR, CLINT, PLIC, or debug-module details
- XiangShan-specific cache hierarchy internals as mandatory GPGPU cache structure
- XiangShan workload assumptions as GPGPU workload defaults

Allowed transfer:

- development closure mechanics that keep RTL, golden reference, traces,
  replay, counters, and performance evidence synchronized.

