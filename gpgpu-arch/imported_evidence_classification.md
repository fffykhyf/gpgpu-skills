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

