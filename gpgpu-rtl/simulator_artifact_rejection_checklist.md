# Simulator Artifact Rejection Checklist

Reject or quarantine:

- CUDA stream stack;
- PTX opcode latency tables;
- fixed simulator latencies;
- BookSim and local-xbar simulator assumptions;
- AccelWattch XML/object hierarchy;
- AerialVision parser-only variables;
- SM86 tested-config queue depth values.

Emit `SIMULATOR_ARTIFACT_REJECTION_REPORT` when such evidence appears.

