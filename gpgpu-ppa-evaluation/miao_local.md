# MIAOW Local Notes For `gpgpu-ppa-evaluation`

This file is the local MIAOW reference for PPA evaluation. MIAOW is useful because it shows how an open-source GPGPU prototype can make a credibility claim with functional scope, benchmarks, FPGA data, and ASIC-style area/power estimates while still stating caveats.

## Relevant Source Map

Use these files and artifacts as references:

- `ref/paper/miaow_hc27.pdf`
- `ref_submodule/miaow/README`
- `ref_submodule/miaow/src/verilog/tb/run.pl`
- `ref_submodule/miaow/src/sw/miaow_unit_tests/`
- `ref_submodule/miaow/src/verilog/rtl/tracemon/`
- `ref_submodule/miaow/src/verilog/rtl/fpga/compute_unit_fpga.v`
- `ref_submodule/miaow/src/sw/xilinx_sdk/main.c`
- `ref_submodule/miaow/scripts/xilinx/`

The local lesson is to separate optimization claims from prototype credibility claims.

## What MIAOW Claims

The paper positions MIAOW as an open-source AMD Southern Islands compute GPU implementation. Its credibility evidence includes:

- 95 supported instructions
- OpenCL program support
- OpenCL benchmark support
- many Rodinia benchmarks
- single-precision compute scope
- no graphics focus
- ASIC, FPGA, and hybrid FPGA implementation experience
- 32-CU architecture description at paper level
- CU organization with single issue, 40 wavefronts, 16-wide vector ALUs, and LSU

These are scope and credibility claims. They are not a statement that MIAOW is PPA-optimal.

## FPGA Evidence

The paper reports a Virtex-7 FPGA prototype:

- 1 CU
- 50 MHz
- around 133K LUTs
- around 100K registers

The repository contains the FPGA-related control path:

- `compute_unit_fpga.v`: AXI-Lite slave wrapping the CU and exposing program load, register initialization, start, result, and memory handshake behavior
- `src/sw/xilinx_sdk/main.c`: MicroBlaze-side software that writes MMIO registers, loads instructions and memory, starts execution, polls status, and services LSU memory
- `scripts/xilinx/`: Xilinx support scripts and AXI slave files

Skill implication:

- FPGA evidence should include device, CU count, clock, resource counts, memory/control interface, and workload
- a 1-CU FPGA result must not be extrapolated to a 32-CU GPU without caveats

## ASIC And Industrial Comparison Evidence

The paper reports:

- Tahiti CU area estimate around 5.02 mm2 at 28 nm
- MIAOW CU area around 9.1 mm2 at 32 nm
- Tahiti CU power estimate around 0.52 W
- MIAOW CU power around 1.1 W

Those numbers require caveats:

- process nodes differ
- industrial CU area is estimated, not produced by the same flow
- industrial power is a broad estimate
- MIAOW frequency, physical design, area, and power goals were relaxed
- memory systems, compilers, runtimes, and workloads are not guaranteed apples-to-apples

Skill implication:

- commercial GPU comparisons need a caveat table
- do not imply optimization superiority from a credibility comparison
- report what the data supports and what it cannot support

## Correctness Evidence Before PPA

MIAOW ties performance/prototype credibility to a correctness loop:

- unit tests under `src/sw/miaow_unit_tests/`
- Multi2Sim functional trace generation
- `trace_parser.pl` trace splitting
- RTL `tracemon` side-effect capture
- `tracefile_cmp.pl` comparison
- `run.pl` batch results and `summary.txt`

Skill implication:

- PPA runs should cite correctness status
- an incorrect design's cycles, IPC, or power are not useful design evidence
- trace/benchmark logs should be stored alongside PPA reports

## Credibility Claim Template

For local research prototype claims, record:

| Field | Required content |
|---|---|
| prototype_id | commit, config, backend, tool versions |
| functional scope | ISA subset, precision, memory ops, unsupported features |
| correctness | unit tests, trace comparison, benchmark pass/fail |
| implementation | RTL sim, FPGA, synthesis, ASIC estimate, or hybrid |
| FPGA | device, clock, CU count, LUT/FF/BRAM/DSP, memory/control interface |
| ASIC estimate | node, tool, clock target, area/power method |
| performance | workload, input, launch shape, cycles, baseline |
| caveat | relaxed goals, missing memory hierarchy, different compiler/runtime, estimation limits |
| conclusion | credible prototype, optimization result, or exploratory observation |

## Optimization Claim Template

For local optimization claims, require:

- exact baseline commit/config
- exact variant commit/config
- one intended variable changed
- workload and input size
- backend and tool version
- correctness result
- counters explaining speedup or slowdown
- area/timing/power report if hardware changed
- interpretation that does not exceed the evidence

MIAOW's paper is not mostly an optimization template. Use it more for prototype credibility and comparison discipline.

## Counter And Report Discipline

MIAOW's FPGA and paper numbers should prompt local designs to preserve:

- cycle count or runtime
- instruction count and IPC when available
- wavefront and FU stall counters when evaluating core changes
- load/store counts and memory latency when evaluating LSU changes
- synthesis hierarchy reports for localized RTL changes
- timing target and WNS/Fmax
- power estimation method and activity source

If these counters are missing, state that the result is a hypothesis or credibility data, not a measured optimization.

## Caveats To Keep Visible

MIAOW should not be used as:

- a direct PPA baseline for the local project
- proof that an AMD Southern Islands style ISA is required
- proof that the simple memory model is enough for performance studies
- proof that one FPGA CU predicts many-CU scaling
- proof that relaxed research-prototype timing is production quality

Use MIAOW to write honest PPA claims: what ran, where it ran, what it cost, how it was measured, and what the comparison cannot prove.
