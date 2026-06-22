# Minimal SIMT Complete Spec

Design identity: minimal-simt-v4
Source kind: HUMAN_SPEC

- ISA profile: RV32I_SIMT_MINIMAL
- Operation classes: integer ALU, branch, global load, global store, CSR
- Warp width: 8
- Active mask width: 8
- Reconvergence model: stackless single-path teaching model
- SM count: 1
- Max resident warps per SM: 1
- Scheduler policy: ROUND_ROBIN
- Issue width: 1
- Register file: 16 x 32-bit registers per thread
- Address spaces: global, local, constant
- Shared memory: disabled
- Cache policy: NONE
- Launch ABI: SIMPLE_MMIO_DOORBELL_V1
- Completion path: done CSR
- Fault path: fault CSR

Every field above is explicit. No hidden defaults are allowed.
