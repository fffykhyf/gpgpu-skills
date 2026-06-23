# Simulator-Only Exclusion Rules

Architecture artifacts must reject:

- PTX opcode latency and initiation tables;
- fixed L1/shared/L2/DRAM/kernel launch latency values;
- tested-config queue depths as defaults;
- CUDA stream stack and compute capability as native ABI;
- BookSim `.icnt` knobs as direct fabric truth;
- AccelWattch XML coefficients or object hierarchy;
- AerialVision parser-only variables.

If a rejected item appears in a candidate contract, emit
`FORBIDDEN_PROVENANCE`.

