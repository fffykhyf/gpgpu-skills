# Imported Evidence Classification

Before using any external reference, classify each imported item as state,
config, counter, visualization, power, test, debug, or simulator artifact.

Parameters must validate against
`shared/schemas/config_parameter_classification.schema.yaml`.

Reject these as architecture truth unless the project explicitly defines a
replacement contract:

- fixed simulator latency;
- C++ queues and containers;
- CUDA/PTX/SASS capability or runtime stack behavior;
- BookSim and AccelWattch configuration;
- parser-only visualization variables.

## XiangShan DSE Import Rule

XiangShan Constantin evidence may define runtime-DSE mechanics, but not GPU
structure. Accept policy selects, thresholds, already-elaborated feature gates,
trace gates, and counter selection. Reject evidence that would change module
existence, wire width, queue depth, bank count, warp size, ISA/ABI, or MMIO
layout at runtime.
