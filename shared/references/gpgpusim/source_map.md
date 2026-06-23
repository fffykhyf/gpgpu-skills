# GPGPU-Sim Source Map

GPGPU-Sim is a CUDA/OpenCL execution-driven GPU simulator with PTX functional
simulation, shader/cache/interconnect/DRAM timing models, statistics,
visualization, and AccelWattch power estimation.

Use it as:

- functional evidence for PTX-like behavior boundaries;
- timing evidence for scheduler, memory, queue, cache, NoC, DRAM, and counter
  attribution;
- configuration evidence for parameter classification;
- counter evidence only after producer audit.

Do not use it as:

- synthesizable RTL;
- simple-gpgpu ISA or ABI truth;
- default hardware latency, queue depth, or NVIDIA capability source;
- AccelWattch/McPAT module hierarchy;
- AerialVision stable counter list without producer proof.

Raw basis:

- `raw/gpgpu-sim-repo-structure-map.md`
- `raw/gpgpu-sim-simulator-flow-index.md`

