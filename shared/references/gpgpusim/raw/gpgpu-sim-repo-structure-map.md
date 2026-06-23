# GPGPU-Sim Repository Structure Map

Source repo: `ref_submodule/gpgpu-sim`

Reader basis: 5 parallel reader-agent passes over repo flow, shader core, memory hierarchy, taxonomy, visualization/power/regression. The repo was read as a simulator evidence source, not an RTL source.

## Positioning

GPGPU-Sim is best classified as:

- CUDA/OpenCL execution-driven GPU simulator.
- PTX functional simulator and instruction-level golden-model reference for NVIDIA PTX behavior.
- Cycle-level timing model for shader core, cache, interconnect, memory partition, and DRAM.
- Statistics, visualization, and power-analysis framework through AerialVision and AccelWattch.
- Regression/benchmark framework through tested configs and external benchmark harnesses.

It is not:

- synthesizable RTL;
- a final simple-gpgpu ISA/ABI specification;
- a source for copying fixed latency, queue depth, CUDA behavior, or NVIDIA-specific SASS/PTX behavior into RTL contracts.

## Main Directory Map

| Path | Responsibility | Classification |
|---|---|---|
| `README.md` | Project positioning, usage, simulator features, AerialVision and AccelWattch pointers | source of truth |
| `configs/tested-cfgs/` | GPU-like tested profiles, including `SM86_RTX3070` | configuration, mixed hardware/simulator |
| `libcuda/` | CUDA runtime interception, fatbin/function registration, launch argument handling | HW/SW ABI relevant, simulator frontend |
| `libopencl/` | OpenCL runtime interception and launch path | HW/SW ABI relevant, simulator frontend |
| `src/gpgpusim_entrypoint.cc` | simulator initialization, option registration, config parse, stream manager creation | simulator control plane |
| `src/stream_manager.*` | stream operations, memcpy/event/kernel dispatch, functional-vs-timing launch branch | simulator runtime |
| `src/abstract_hardware_model.*` | shared `kernel_info_t`, `warp_inst_t`, `simt_stack`, `mem_access_t`, coalescing | hardware-relevant model schema |
| `src/cuda-sim/` | PTX parser/IR/functional execution/thread/memory model | functional simulation |
| `src/gpgpu-sim/` | timing model for GPU top, shader core, scoreboard, cache, L2, ICNT, DRAM, stats, power bridge | timing simulation |
| `src/intersim2/` | BookSim/Intersim2 NoC backend | simulator-only NoC backend |
| `aerialvision/` | visualization parser and variable taxonomy | stats/visualization |
| `src/accelwattch/` | McPAT-derived power/energy model and XML/counter binding | power model |
| `short-tests*.sh`, `.github/workflows/` | regression entry points and config matrix | test-only/support |
| `debug_tools/`, `checkpoint.md` | debug/checkpoint utilities | debug-only |

## Functional, Timing, Configuration, Power Boundaries

Functional simulation:

- `src/cuda-sim/*`
- `src/abstract_hardware_model.*`
- `libcuda/*`, `libopencl/*`
- `src/stream_manager.cc` when `stream_operation::do_operation()` takes the functional branch.

Timing simulation:

- `src/gpgpu-sim/gpu-sim.*`
- `src/gpgpu-sim/shader.*`
- `src/gpgpu-sim/scoreboard.*`
- `src/gpgpu-sim/gpu-cache.*`
- `src/gpgpu-sim/l2cache.*`
- `src/gpgpu-sim/icnt_wrapper.*`, `local_interconnect.*`, `src/intersim2/*`
- `src/gpgpu-sim/dram.*`, `dram_sched.*`

Configuration:

- parser creation in `src/gpgpusim_entrypoint.cc:gpgpu_context::gpgpu_ptx_sim_init_perf`;
- uarch option registration in `src/gpgpu-sim/gpu-sim.cc:gpgpu_sim_config::reg_options`;
- shader/memory/DRAM options in `src/gpgpu-sim/gpu-sim.cc`;
- concrete seed config in `configs/tested-cfgs/SM86_RTX3070/gpgpusim.config`;
- BookSim config seed in `configs/tested-cfgs/SM86_RTX3070/config_ampere_islip.icnt`, but SM86 active path uses `-network_mode 2` local xbar, not this BookSim file.

Statistics, visualization, and power:

- `src/gpgpu-sim/stats.h` defines memory-stage access and stall enums.
- `src/gpgpu-sim/stat-tool.*`, `mem_latency_stat.*`, `traffic_breakdown.*`, `visualizer.*` emit/aggregate counters.
- `aerialvision/variableclasses.py` and `aerialvision/lexyacc.py` parse visualizer variables; some variables are parser-only and need producer audit.
- `src/gpgpu-sim/power_interface.*`, `power_stat.*`, and `src/accelwattch/*` map simulator counters into power estimates.

## Source-Of-Truth Files To Read First

P0 source files for future reader agents:

- `README.md`
- `configs/tested-cfgs/SM86_RTX3070/gpgpusim.config`
- `configs/tested-cfgs/SM86_RTX3070/config_ampere_islip.icnt`
- `src/gpgpusim_entrypoint.cc`
- `src/stream_manager.cc`
- `libcuda/cuda_runtime_api.cc`
- `libopencl/opencl_runtime_api.cc`
- `src/abstract_hardware_model.{h,cc}`
- `src/cuda-sim/{cuda-sim.*,ptx_ir.*,ptx_sim.*,instructions.cc,memory.*}`
- `src/gpgpu-sim/{gpu-sim.*,shader.*,scoreboard.*,stats.h,gpu-cache.*,mem_fetch.*,l2cache.*,icnt_wrapper.*,local_interconnect.*,dram.*,dram_sched.*,addrdec.*}`
- `src/gpgpu-sim/{stat-tool.*,mem_latency_stat.*,traffic_breakdown.*,visualizer.*,power_interface.*,power_stat.*}`
- `aerialvision/{README,variableclasses.py,lexyacc.py}`
- `src/accelwattch/{README,gpgpu_sim_wrapper.*,XML_Parse.*}`

## Design Rule

Rule name: classify before copying

Problem solved: prevents simulator C++ choices from becoming accidental RTL or skill contracts.

Required state contract: every extracted mechanism must be tagged as functional, timing, config, counter, visualization, power, test, or debug.

Required config contract: every parameter must be classified as `hardware-private`, `simulator-private`, `HW/SW ABI`, `test-only`, or `debug-only`.

Applicable skill: `gpgpu-arch`, `gpgpu-memory`, `gpgpu-interconnect`, `gpgpu-simppa`, `gpgpu-golden`, `gpgpu-runtime`, `gpgpu-rtl`.

Implementation anchor: `ref/skillref/gpgpusim.md` and this report directory.
