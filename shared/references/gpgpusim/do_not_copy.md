# GPGPU-Sim Do-Not-Copy Boundary

Never copy these into RTL:

- C++ queue/container implementations;
- fixed simulator latencies;
- SM86 queue depths or response FIFO sizes as defaults;
- CUDA stream stack or stream-zero policy;
- BookSim allocator, VC, topology, or routing knobs as fabric truth;
- AccelWattch object hierarchy, XML coefficients, or McPAT terms;
- AerialVision parser logic or parser-only metric names.

Never copy these into ISA or ABI:

- NVIDIA PTX/SASS semantics as native simple-gpgpu ISA truth;
- CUDA compute capability as a native field unless a compatibility profile is
  explicitly selected;
- CUDA stack, heap, dynamic parallelism, stream, or object model behavior;
- texture/constant cache behavior unless exposed by the project ISA.

Safe methodology to import:

- parameter classification;
- functional/timing separation;
- issue and non-issue reason contracts;
- scoreboard reserve/check/release;
- SIMT PC and active-mask state;
- memory transaction normalization;
- queue-boundary memory attribution;
- producer-backed counter manifests.

Raw basis: `raw/gpgpu-sim-do-not-copy.md`.

