# MIAOW Local Notes For `gpgpu-arch-design`

This file is the local MIAOW reference for the architecture-design skill. It explains what parts of MIAOW matter for staged architecture work, including paper-level scope, RTL anchors, trace/test evidence, FPGA control, and caveats. It is not a request to clone AMD Southern Islands or MIAOW.

Terminology note: this file preserves MIAOW source names such as `wave`, `wavefront`, `wfid`, `workgroup`, and `EXEC`. In the skill contract, map them to `SIMT group`, `simt_group_id`, `CTA/workgroup`, and `active lane mask`; use the MIAOW names only when quoting source behavior.

## What To Learn From MIAOW

MIAOW is useful here because it turns a GPGPU architecture claim into a credible research prototype:

- paper scope: `ref/paper/miaow_hc27.pdf`
- repository entry: `ref_submodule/miaow/README`
- CU integration: `ref_submodule/miaow/src/verilog/rtl/compute_unit/compute_unit.vp`
- global constants: `ref_submodule/miaow/src/verilog/rtl/common/global_definitions.v`
- instruction and trace tests: `ref_submodule/miaow/src/sw/miaow_unit_tests/`, `ref_submodule/miaow/src/verilog/tb/run.pl`
- external golden trace path: `ref_submodule/miaow/src/sw/common/trace_parser.pl`, `ref_submodule/miaow/src/verilog/rtl/tracemon/`
- dispatcher and resource allocation: `ref_submodule/miaow/src/verilog/rtl/dispatcher/`
- FPGA control plane: `ref_submodule/miaow/src/verilog/rtl/fpga/compute_unit_fpga.v`, `ref_submodule/miaow/src/sw/xilinx_sdk/main.c`

The architecture-design takeaway is that a GPGPU proposal should name its scope, implementation anchors, evidence path, and caveats before it becomes a pile of disconnected RTL.

## Paper-Level Scope And Credibility

`ref/paper/miaow_hc27.pdf` presents MIAOW as an open-source implementation of the AMD Southern Islands GPU ISA. The important scope statements are:

- supports 95 instructions
- runs OpenCL programs
- runs OpenCL benchmarks and many Rodinia benchmarks
- targets compute, not graphics
- supports single precision, not a complete graphics GPU
- has ASIC, FPGA, and hybrid FPGA implementation experience

The paper describes the GPU as 32 compute units. Each CU is single issue, supports 40 wavefronts, uses 16-wide vector ALUs, and has an LSU for memory operations. In code, the architectural wavefront mask is still 64 bits, while the CU has multiple SIMD/SIMF units. Treat those as separate architectural and physical quantities:

- architectural wavefront/mask width
- physical vector lane width
- number of parallel SIMD/SIMF units
- test wavefront size

The paper's credibility evidence includes a Virtex-7 FPGA prototype with 1 CU at 50 MHz, around 133K LUTs and 100K registers, and ASIC-style CU estimates around 9.1 mm2 at 32 nm and 1.1 W. Those numbers are useful as prototype evidence, not as a local baseline to copy. The paper also compares against AMD Tahiti, but the comparison has process, method, frequency, and design-goal caveats.

## CU Architecture Anchor

`src/verilog/rtl/compute_unit/compute_unit.vp` is the main architecture anchor. It wires the CU from dispatch to trace-visible retire:

- `fetch`: accepts wavefront dispatch, start PC, base registers, branch redirect, completion, and instruction-buffer request.
- `wavepool`: queues fetched instructions per wavefront and preserves VGPR/SGPR/LDS base metadata.
- `decode`: converts Southern Islands instruction bits into issue fields.
- `issue`: owns valid entries, FU class, data dependencies, memory wait, branch wait, barrier wait, in-flight limits, and arbitration.
- `exec`: owns per-wavefront EXEC, VCC, SCC, and M0 state.
- `salu`: handles scalar/control operations and branch results.
- `simd0` to `simd3`: integer/vector execution.
- `simf0` to `simf3`: single-precision floating execution.
- `rfa`: arbitrates register-file access from execution units.
- `sgpr` and `vgpr`: scalar and vector register files.
- `lsu`: memory instruction decode, address generation, memory request, writeback, and done.
- `tracemon`: external side-effect trace for comparison against a golden trace.

The module exposes explicit signals for dispatch, instruction fetch, memory requests, SGPR/VGPR writeback, special-register writeback, retire PC, branch, barrier, waitcnt, and trace data. This is the implementation pattern to preserve locally: architecture state should have named owners and trace-visible effects.

## State And Resource Contract

`src/verilog/rtl/common/global_definitions.v` defines basic CU sizes:

- `WF_PER_CU = 40`
- `WF_PER_WG = 16`
- `WF_ID_LENGTH = 6`
- `VGPR_ADDR_LENGTH = 10`
- `SGPR_ADDR_LENGTH = 9`
- `NUMBER_VGPR = 1024`
- `NUMBER_SGPR = 512`

These are architecture-design prompts, not magic constants. For a local architecture design, classify each similar value:

- architectural limit visible to ISA/runtime
- physical microarchitecture resource
- dispatcher allocation unit
- FPGA prototype constraint
- test fixture value

MIAOW's dispatcher also has `NUMBER_CU`, `NUMBER_WF_SLOTS`, VGPR/SGPR/LDS/GDS resource sizes, tag width, and start-PC width. Those values become launch and resource contracts when a runtime or dispatcher exists.

## Trace And Test Evidence

MIAOW's correctness loop is a strong architecture reference:

1. `src/sw/miaow_unit_tests/run` runs unit tests through Multi2Sim functional mode and emits Southern Islands ISA traces.
2. `src/sw/common/trace_parser.pl` splits traces into `kernel_*` folders and moves `config_*.txt`, `data_*.mem`, and `instr_*.mem`.
3. RTL simulation uses `tracemon.c/h` to collect architectural side effects per CU and wavefront.
4. `src/verilog/tb/tracefile_cmp.pl` normalizes Multi2Sim traces and compares them with `tracemon_*.out`.
5. `src/verilog/tb/run.pl` batches tests, runs simulation, compares every wavefront trace, and writes `summary.txt`.

The architectural lesson is that "supports an instruction" means more than decode exists. It needs an input configuration, an executable reference trace, an RTL trace, a comparator, and a regression artifact.

## Runtime And FPGA Architecture Boundary

MIAOW has a smaller runtime/control-plane story than Vortex, but it is still useful:

- `dispatcher_soft.v` drives wavefront launch through C hooks and initializes SGPR/VGPR state for testbench runs.
- `dispatcher.v` and supporting dispatcher modules allocate CU, wavefront slots, VGPR, SGPR, LDS, and GDS resources.
- `compute_unit_fpga.v` wraps a CU in an AXI-Lite slave with registers for wave ID, base VGPR/SGPR/LDS, wave count, start PC, instruction buffer writes, GPR writes, start, result, and memory handshake.
- `xilinx_sdk/main.c` writes these MMIO registers, loads instructions and memory, starts execution, polls status, and services LSU memory requests.

This is not a complete handle-based runtime API. It is still an architecture boundary because it defines how code, registers, memory, dispatch, done, and result observation happen.

## Skill Implications

For architecture work, require this minimum table:

| Architecture claim | MIAOW-style question |
|---|---|
| ISA support | Which instruction tests and golden traces prove it? |
| SIMT state | Which module owns PC, mask, wavefront state, and special registers? |
| CU organization | What is architectural wavefront width versus physical SIMD width? |
| Memory support | Is the LSU path traceable per lane and per wavefront? |
| Runtime launch | Is this a testbench hook, dispatcher contract, or hardware MMIO path? |
| Config | Which constants are ABI, resource, prototype, or test-only values? |
| PPA | Is the claim optimization, prototype credibility, or exploration? |

## Limitations To Preserve

MIAOW should not be treated as proof that the local project should:

- copy AMD Southern Islands ISA
- copy 32 CUs, 40 wavefronts, or the exact SIMD/SIMF organization
- treat the simple `memory.v` as a real cache hierarchy
- use testbench C hooks as a permanent runtime API
- treat Hot Chips area/power/performance numbers as local baselines
- skip a local simulator or golden trace because MIAOW used Multi2Sim

Use MIAOW to make local architecture claims concrete, observable, and honest about scope.
