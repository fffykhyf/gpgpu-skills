# Self-Correcting Minimal SIMT Request

Design a minimal teaching SIMT GPGPU that can run a CUDA-like vector-add kernel through a frontend, assembler, program image, RTL partial simulation, full trace comparison, memory dump, and golden contract check.

Target constraints:

- one CU
- small FPGA-oriented area budget
- 4 logical wavefronts maximum
- memory pressure must be estimated before contract freeze
- LSQ backpressure must be observable
- failures must produce an architecture, contract, or RTL rewrite plan
