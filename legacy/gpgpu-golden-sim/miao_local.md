# MIAOW Local Notes For `gpgpu-golden-sim`

This file is the local MIAOW reference for golden simulator and trace work. MIAOW is valuable here because it shows a working external-oracle flow: Multi2Sim produces functional traces, RTL emits tracemon side effects, and a comparator finds trace divergence per wavefront.

Terminology note: this file preserves MIAOW source names such as `wave`, `wavefront`, `wfid`, `workgroup`, and `EXEC`. In the skill contract, map them to `SIMT group`, `simt_group_id`, `CTA/workgroup`, and `active lane mask`; use the MIAOW names only when quoting source behavior.

## Relevant Source Map

Use these files as the main references:

- `ref_submodule/miaow/src/sw/miaow_unit_tests/run`
- `ref_submodule/miaow/src/sw/common/trace_parser.pl`
- `ref_submodule/miaow/src/verilog/rtl/tracemon/tracemon.h`
- `ref_submodule/miaow/src/verilog/rtl/tracemon/tracemon.c`
- `ref_submodule/miaow/src/verilog/tb/tracefile_cmp.pl`
- `ref_submodule/miaow/src/verilog/tb/run.pl`
- `ref_submodule/miaow/src/sw/miaow_unit_tests/test_*/kernel_0/*_trace_*`
- `ref_submodule/miaow/src/sw/miaow_unit_tests/test_*/unit_test_config.txt`
- `ref_submodule/miaow/src/sw/miaow_unit_tests/test_*/unit_test_instr.mem`
- `ref_submodule/miaow/src/sw/miaow_unit_tests/test_*/unit_test_data.mem`

This flow is a golden trace system, not a module-twin simulator. It is still a useful first correctness loop.

## External Oracle Flow

`src/sw/miaow_unit_tests/run` runs a unit test through Multi2Sim functional mode. It supports Multi2Sim 4.0 and 4.2 paths, copies the OpenCL support library and kernel binary into the test directory, runs `m2s --si-debug-isa`, then invokes `trace_parser.pl`.

`src/sw/common/trace_parser.pl` reads the generated trace, splits streams by `###` tags, creates `kernel_<id>` folders, and moves the corresponding `config_<id>.txt`, `data_<id>.mem`, and `instr_<id>.mem` files into that folder. It then emits per-tag trace files under the kernel folder.

Skill implication:

- external oracle traces must be normalized before comparison
- the command, simulator version, input memory, instruction memory, and config files are part of the golden artifact
- per-wavefront or per-tag traces avoid interleaving hiding the first divergence

## RTL Trace Monitor

`tracemon.h` defines the trace monitor API. The central objects are:

- `Trace_obj`: PC, barrier flag, timestamp, complete bit, and print buffer
- `Bases`: SGPR, VGPR, and LDS base per wavefront
- `MAX_NUM_OF_CU = 4`
- `MAX_WFS_IN_CU = 40`
- `MAX_INSTR_FLIGHT = 20`

`tracemon.c` maintains:

- `objects[MAX_NUM_OF_CU][MAX_WFS_IN_CU][MAX_INSTR_FLIGHT]`
- one output filename per CU/wavefront
- per-wavefront base registers
- a global kernel id

On dispatch, `AddNewWavefront` chooses an output path such as `kernel_0/tracemon_0_0_0.out`. On decode, `AddInstruction` records PC and instruction text in the in-flight object list. On retire, the monitor prints side effects only when prior in-flight instructions are complete, preserving architectural order per wavefront.

Skill implication:

- trace identity needs CU, wfid, PC, and kernel/wavefront tag
- decode/add and retire/print can be separate events
- a trace system should detect "retired PC not found" and "not retired before deschedule"

## Side-Effect Print Coverage

`tracemon.c/h` include print functions for:

- VGPR writes: `PrintVgpr`, `PrintVgprWithVcc`, `PrintVgprF`, `PrintVgprFWithVcc`
- VCC per lane: `PrintVVcc`
- SGPR writes: `PrintSgpr`, `PrintSgprWithScc`, `PrintSgprExecScc`
- special registers: `PrintExec`, `PrintVcc`, `PrintM0`, plus SCC variants
- memory loads: `PrintVgprLoad`, `PrintVgprLoadDS`, `PrintSgprLoad`
- memory stores: `PrintVgprStore`, `PrintVgprStoreDS`
- branch and barrier retire: `PrintAndDeleteOnBranch`, `PrintAndDeleteBarrier`

This is the minimum style to copy: trace architectural side effects, not just final memory. A local trace should show register, lane, value, address, branch/barrier action, and PC.

## Comparator Behavior

`src/verilog/tb/tracefile_cmp.pl`:

- reads a Multi2Sim trace and a tracemon trace
- strips and normalizes Multi2Sim output
- keeps instruction comments and `<=` side-effect lines
- compares normalized golden lines against RTL trace lines
- prints `TEST PASS!`, `TEST FAIL! (Diff)`, or `TEST FAIL! (Hang)`
- writes stripped `.gold` and `.verilog` dumps

The distinction between `Diff` and `Hang` is useful. A content mismatch means a first-divergence problem. A hang/missing trace means the RTL did not retire or did not emit the expected stream.

## Regression Runner

`src/verilog/tb/run.pl` collects available tests, creates `results/<outdir>`, links or copies `simv`, runs each test, compares every `*_trace_*` file against matching `tracemon_*.out`, and writes:

- per-test `run.log`
- wavefront-level compare output
- top-level `summary.txt`
- total test and pass counts

Skill implication:

- a golden loop should produce persistent artifacts
- compare every wavefront, not just every test directory
- record missing trace as a failure, not as skipped output

## How To Apply Locally

Use a staged oracle:

| Stage | MIAOW-inspired artifact |
|---|---|
| tiny instruction | hand-written expected side-effect trace |
| instruction coverage | external ISA simulator trace |
| multi-wavefront RTL | per-wavefront normalized trace |
| module debug | add owner-specific fields such as scoreboard wait, LSU state, branch wait |
| timing study | add cycle/stall fields after functional trace is stable |

For a bug report, capture:

- config file
- instruction memory
- data memory
- launch shape or dispatch fields
- external oracle command/version
- RTL command
- golden trace
- RTL trace
- first divergent line or missing trace

## Caveats

MIAOW's oracle flow does not prove:

- cycle accuracy
- cache/MSHR timing
- scheduler fairness
- power/performance counter correctness
- that RTL module boundaries match a simulator twin

It proves architectural side-effect agreement against an external functional oracle. That is exactly the right first gate for many GPGPU bring-up tasks.
