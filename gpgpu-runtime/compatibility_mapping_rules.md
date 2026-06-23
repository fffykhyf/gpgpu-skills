# Optional CUDA/OpenCL Compatibility Mapping

CUDA and OpenCL frontends may map into the native launch descriptor, but their
object models must not leak into the base ABI.

Compatibility-only fields include:

- CUDA stream stack and stream policy;
- kernel launch latency;
- compute capability;
- OpenCL object handles;
- PTX capability and memory-space quirks.

Native runtime output remains `PROGRAM_IMAGE_IR`, `RUNTIME_LAUNCH_IR`, and
`LOADER_CONTRACT_IR` derived from `SYSTEM_CONTRACT_IR`.

