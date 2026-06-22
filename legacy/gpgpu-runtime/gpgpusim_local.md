# GPGPU-Sim Local Reference For GPGPU Runtime

This note expands the GPGPU-Sim references that matter for the `gpgpu-runtime` skill. It focuses on CUDA/OpenCL runtime interception, launch stack handling, kernel descriptors, stream operations, functional/performance mode selection, and launch admission into the timing simulator.

Terminology note: this file preserves GPGPU-Sim source names such as `warp`, `CTA`, `kernel_info_t`, `stream`, and `shader`. In the skill contract, map them to `SIMT group`, CTA/workgroup, kernel descriptor, queue/stream, and compute core/CU.

## What GPGPU-Sim Teaches For This Skill

GPGPU-Sim shows a runtime path that can run real CUDA/OpenCL-style applications without testbench pokes:

- runtime API calls are intercepted in `libcuda/` or `libopencl/`;
- launch configuration and arguments are captured before hardware admission;
- `kernel_info_t` becomes the stable kernel descriptor;
- `stream_manager` serializes or orders memcpy, kernel launch, event, and wait operations;
- functional and performance simulation modes share the same runtime launch path;
- launch latency and max concurrent kernels are explicit config-controlled runtime/timing properties.

The local lesson is that runtime is the boundary between workload and backend, not just a convenience script.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/gpgpusim.md` | Runtime lessons and end-to-end launch chain. |
| `ref_submodule/gpgpu-sim/libcuda/cuda_runtime_api.cc` | `cudaConfigureCallInternal`, `cudaSetupArgumentInternal`, `cudaLaunchInternal`. |
| `ref_submodule/gpgpu-sim/libcuda/cuda_api_object.h` | `kernel_config`, `g_cuda_launch_stack`, API object helpers. |
| `ref_submodule/gpgpu-sim/libcuda/gpgpu_context.h` | Runtime/simulator context ownership. |
| `ref_submodule/gpgpu-sim/libopencl/opencl_runtime_api.cc` | OpenCL frontend path. |
| `ref_submodule/gpgpu-sim/src/stream_manager.*` | Stream operations, memcpy, event, wait, kernel launch. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc` | `launch`, `can_start_kernel`, `select_kernel`, CTA issue/admission. |
| `ref_submodule/gpgpu-sim/src/abstract_hardware_model.*` | `kernel_info_t` fields and CTA progression. |

## CUDA Launch Stack Pattern

The CUDA runtime path is:

1. `cudaConfigureCallInternal(gridDim, blockDim, sharedMem, stream)` pushes a `kernel_config`.
2. `cudaSetupArgumentInternal(arg, size, offset)` records argument bytes into that config.
3. `cudaLaunchInternal(hostFun)` checks the launch, resolves the kernel, creates `kernel_info_t`, runs PDOM analysis, and pushes a stream operation.
4. `stream_operation::do_operation()` performs memcpy/event work, or transfers a kernel to functional/performance simulation.
5. Performance simulation waits for `gpu->can_start_kernel()` and launch latency before calling `gpu->launch(m_kernel)`.

Local runtime does not need to mimic CUDA syntax, but it should have equivalent state: launch config, argument staging, kernel lookup, queue operation, backend admission, and completion.

## Stream Operation Lessons

`stream_manager` treats these as first-class operations:

- host-to-device copy;
- device-to-host copy;
- device-to-device copy;
- symbol copy;
- kernel launch;
- event update;
- wait event.

This gives the runtime a single ordering model. A local runtime can start with one queue, but it should still define whether copies, launches, events, waits, fences, and errors are ordered, blocking, or asynchronous.

## Kernel Descriptor Fields

A local `kernel_info_t` equivalent should record:

- kernel name or entry handle;
- entry PC/function pointer;
- argument buffer and sizes;
- grid and block dimensions;
- shared/local memory request;
- stream/queue ID;
- next CTA/workgroup index;
- active/running/done counts;
- launch latency or admission state;
- parent/child relation if dynamic launch exists;
- resource requirements if occupancy is checked.

## Runtime Verification Gates

Borrow these gates from GPGPU-Sim:

- reject empty grid or block dimensions;
- reject CTA size that exceeds configured shader/core capacity;
- test functional and timing/simulator launch through the same descriptor;
- test at least one memcpy plus launch plus copy-back path;
- record stream/queue ID in trace when ordering matters;
- expose launch latency and max concurrent kernels through config, not hidden constants.

## Caveats

- GPGPU-Sim's runtime interception relies on CUDA/OpenCL compatibility and dynamic linking. A local project can use a simpler CLI or C API.
- Do not expose host function pointers or PTX-specific details as the public contract unless they are real project requirements.
- Do not let simulator-only launch shortcuts become the RTL or FPGA runtime ABI.

