# Vortex Local Reference For GPGPU Config

This note expands the Vortex references that matter for the `gpgpu-config`
skill. It focuses on parameter classification, generated headers, HW/SW ABI
constants, CSR/DCR maps, memory maps, capability reporting, and drift checks.

## What Vortex Teaches For This Skill

Vortex separates hardware-private build configuration from hardware/software
ABI constants:

- `VX_config.toml` describes microarchitecture and implementation knobs.
- `VX_types.toml` describes values shared across hardware and software:
  memory map, CSR/DCR maps, VM format, CTA CSRs, counters, and enums.
- `ci/gen_config.py` generates Verilog headers, C/C++ headers, and C flags from
  TOML.
- `configure` copies the source tree into a build directory and generates
  headers under build-local `hw/` and `sw/`.
- CI guards prevent private config from leaking into public software layers and
  prevent software/simulator/hardware include-boundary drift.

For this project, the key habit is classification before editing a parameter.
Every value is hardware-private, simulator-private, HW/SW ABI, test-only, or
debug-only. Treating all numbers as "just macros" is how config drift starts.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/vortex.md` | Local extraction of config/ABI lessons. |
| `ref_submodule/vortex/docs/designs/build_configuration_system.md` | TOML-driven config flow and hardware/software layering. |
| `ref_submodule/vortex/VX_config.toml` | Hardware-private and simulator/RTL implementation knobs. |
| `ref_submodule/vortex/VX_types.toml` | HW/SW ABI constants: memory map, CSR/DCR maps, counters, enums. |
| `ref_submodule/vortex/ci/gen_config.py` | Generator for Verilog, C/C++, and cflags outputs. |
| `ref_submodule/vortex/configure` | Build-tree setup and generated header creation. |
| `ref_submodule/vortex/ci/check_config_boundary.sh` | Guard that software/tests do not include private `VX_config.h`. |
| `ref_submodule/vortex/ci/check_sw_sim_boundary.sh` | Guard that install-facing software and sim/hw internals stay isolated. |
| `ref_submodule/vortex/sw/runtime/common/caps.h` | Runtime-visible capability decoding from CP registers. |

## `VX_config.toml`: Hardware Build Configuration

`ref_submodule/vortex/VX_config.toml` is the reference for implementation
configuration. It includes values such as:

- platform topology: clusters, cores, socket size;
- cache/local-memory enable bits;
- ISA implementation toggles: M/F/D/C/A/V, TCU, DMA/DXA, texture/raster/OM;
- pipeline parameters: warps, threads, barriers, issue width, SIMD width,
  operand collectors, register-bank counts;
- memory implementation: memory block size, address width, platform banks,
  platform data size, interleave, peak bandwidth, clock rate;
- LSU knobs: lanes, blocks, line size, input queue size, output queue size;
- FPU/TCU implementation type and latency/parallelism knobs;
- cache sizes, ways, replacement policy, writeback, dirty-byte tracking,
  MSHR sizes, request/response queue sizes, bank counts, memory ports;
- local-memory size and bank count;
- VM microarchitecture knobs such as TLB size and pinned-region size.

These are mostly hardware-private or simulator-private. They may affect public
capabilities, but public software should not include the generated private
config header to learn them. Use capability queries or ABI headers when a value
must be visible to software.

## `VX_types.toml`: ABI And Shared Type Configuration

`ref_submodule/vortex/VX_types.toml` is the reference for visible contracts.
It includes:

- global CSR/DCR address widths and MPM CSR bases;
- ISA identity constants;
- memory map:
  - user base;
  - stack base and stack size;
  - local memory base;
  - IO base/end;
  - console buffer layout;
  - exit-code address;
  - page-table base;
- VM page format:
  - page size/log size;
  - address mode (`SV32` or `SV39`);
  - page-table levels;
  - PTE size;
  - page-table size limits;
- DCR maps:
  - base/cache flush/MPM;
  - KMU startup address, kernel entry, args pointer, block/grid dimensions,
    local memory, block size, warp steps, cluster dimensions;
  - DXA, texture, raster, and output-merger state;
- CSR maps:
  - base RISC-V CSRs;
  - FPU/vector CSRs;
  - GPGPU CSRs for thread, warp, core, active warps/threads, num threads,
    num warps, num cores, local memory base, barriers;
  - CTA CSRs for id/rank/size, threadIdx, blockIdx, blockDim, gridDim,
    local-memory address, cluster size, and kernel entry;
- MPM counter classes and counters for core, icache, dcache, l2, l3, memory,
  TLB/PTW, DXA, TCU, texture, raster, and OM;
- enums such as VM address mode.

Treat these as ABI unless proven otherwise. If one changes, check RTL,
simulator, runtime, kernel startup code, tests, documentation, and capability
reporting.

## Config Generator

`ref_submodule/vortex/ci/gen_config.py` is the core generator.

Notable behavior:

- parses ordered TOML with section preservation;
- reads defaults from TOML and applies `--cflags` or trailing `-D...`
  overrides;
- supports `[[enum]]` blocks for enum-typed parameters;
- supports `[[builtin]]` and `[[param]]` blocks for expression-only variables;
- supports `expr:` strings and backtick expressions with `$NAME` references;
- treats lowercase definitions as local/private helper variables that are not
  emitted;
- can emit Verilog header (`-f verilog`), C/C++ header (`-f cpp`), and compiler
  flags (`-f cflags`);
- has unresolved header mode for override-friendly preprocessor definitions;
- uses resolved mode for fully evaluated constants, especially cflags and
  `VX_types`;
- preserves large hex literal widths for Verilog so address constants are not
  truncated by synthesis tools.

For local config work, prefer a generator or single structured source over
copying derived constants by hand across RTL, simulator, runtime, and tests.

## Build Configuration Flow

`ref_submodule/vortex/configure` shows how Vortex creates a configured build
tree:

- reads or defaults `XLEN`, `TOOLDIR`, `OSVERSION`, and `PREFIX`;
- records a `.config.stamp` signature so generated files update when config
  parameters change;
- copies source subdirectories and expands `.in` templates;
- creates build-local `hw/` and `sw/` output directories;
- runs `ci/gen_config.py` for every root TOML file;
- emits Verilog headers to `<build>/hw/<name>.vh`;
- emits C/C++ headers to `<build>/sw/<name>.h`;
- generates `VX_types` in resolved mode because memory-map and VM expressions
  depend on `XLEN`;
- exports `XLEN` for expression resolution.

The lesson is that generated configuration should be build-local. Do not edit
generated headers by hand. Change the source TOML or override flags.

## Include And Layering Boundaries

Vortex has explicit CI guards:

### `ci/check_config_boundary.sh`

This script forbids software and tests from including `VX_config.h`. The reason:
`VX_config.h` is hardware build configuration, private to RTL and simulators.
Software should use:

- `VX_types.h` for ISA/ABI constants;
- `vx_device_query()` / `VX_CAPS_*` for device properties;
- `config.mk` for build parameters;
- generated `-D` flags for compile-time build config when intentionally needed.

### `ci/check_sw_sim_boundary.sh`

This script enforces bidirectional isolation:

- `sw/kernel` and `sw/runtime` must not include or reference `hw/` or `sim/`
  internals;
- `sim/` and `hw/` must not include install-facing `sw/kernel/include` or
  `sw/runtime/include` headers;
- `sw/common` is the internal escape hatch shared across layers.

For local work, use the same boundary thinking. If runtime needs a hardware
fact, either make it ABI, expose it as a capability, or keep it backend-private.
Do not let public software include a private RTL config header.

## Generated Include Points

Useful Vortex include paths:

- `ref_submodule/vortex/hw/rtl/VX_define.vh`: RTL include point that pulls in
  generated Verilog config and derived macros.
- build-local `hw/VX_config.vh` and `hw/VX_types.vh`: generated RTL headers.
- build-local `sw/VX_config.h` and `sw/VX_types.h`: generated C/C++ headers,
  with `VX_config.h` treated as private to non-public layers.
- `ref_submodule/vortex/sw/runtime/common/caps.h`: capability decoding without
  public software including hardware-private config.

If a local parameter is visible through public runtime API, prefer a generated
ABI header or capability query. If it only changes hardware structure, keep it
hardware-private.

## Runtime Capabilities

`ref_submodule/vortex/sw/runtime/common/caps.h` decodes two CP capability words:
`GPU_DEV_CAPS` and `GPU_ISA_CAPS`.

Encoded values include:

- version;
- number of threads;
- number of warps;
- number of cores, sockets, clusters;
- issue width;
- local memory size;
- ISA flags;
- number of memory banks;
- memory bank size.

The helper returns `false` for values the backend must resolve separately, such
as cache line size, global memory size, clock rate, and peak memory bandwidth.

This is a useful pattern when a hardware-private parameter has a runtime-visible
projection. Keep the source private, but expose a stable decoded capability.

## Classification Guide

Use this classification before editing any parameter:

| Class | Vortex examples | Local action |
|---|---|---|
| hardware-private | MSHR size, queue depth, cache bank count, FU latency | Keep in private config; test RTL/sim configs. |
| simulator-private | model-only delay, debug verbosity | Keep out of public ABI. |
| HW/SW ABI | memory map, CSR/DCR numbers, CTA CSRs, kernel entry, counters | Put in shared generated source; update all consumers. |
| test-only | tiny smoke-test memory or input size | Keep in tests; do not leak into architecture. |
| debug-only | trace flags, assertions, watchdog timeouts | Keep optional and non-semantic. |

## Local Change Checklist

For every config change:

- classify the parameter;
- identify the single source of truth;
- list generated outputs and direct consumers;
- decide whether capability/query output changes;
- remove stale hard-coded copies;
- run at least one small config and one target config when parameterized logic
  changes;
- update PPA config ids if evaluation results depend on the value;
- run boundary checks or equivalent greps for illegal includes.

## What Not To Copy

- Do not copy Vortex macro names unless they fit this project's naming style.
- Do not move every value into ABI because software can observe it somewhere in
  Vortex.
- Do not rely on one default config to validate parameterized RTL.
- Do not edit generated headers by hand.
- Do not expose private hardware config in public runtime headers.
