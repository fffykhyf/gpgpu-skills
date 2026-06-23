# GPGPU-Sim Config Taxonomy Seed

This table seeds imported parameter classification. It is not a default config.

| Parameter | Category | Hardware contract? | Policy | Notes |
|---|---|---:|---|---|
| SM count / cluster count | hardware-private | Yes | classify | May become topology knob with provenance and range. |
| Warp size | HW/SW ABI or hardware-private | Guarded | classify | ABI if compiler/runtime observes it; otherwise private. |
| `-ptx_opcode_latency_*` | simulator-private | No | reject | Timing calibration, not RTL pipeline truth. |
| CUDA compute capability | HW/SW ABI | Guarded | optional profile | Only for CUDA/PTX compatibility. |
| DRAM fixed latency | simulator-private | No | reject | Not a DRAM controller truth. |
| Register/shared memory limit | HW/SW ABI | Yes | contract | Must enter launch and occupancy contract. |
| BookSim allocator/VC knobs | simulator-private or hardware-private | Guarded | classify | Inspiration only; not active SM86 path by default. |
| AerialVision variables | debug-only | No | audit | Stable only after producer-backed counter audit. |
| AccelWattch XML coefficients | simulator-private | No | reject | Power-model calibration, not hardware truth. |

