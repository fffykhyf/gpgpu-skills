# MIAOW Local Notes For `gpgpu-config`

This file is the local MIAOW reference for configuration work. MIAOW is useful here because it has real configuration needs spread across RTL, testbench, FPGA software, unit tests, and generators. It is both a source of useful parameter families and a warning about drift.

## Relevant Source Map

Use these files as the main references:

- `ref_submodule/miaow/src/verilog/rtl/common/global_definitions.v`
- `ref_submodule/miaow/src/verilog/rtl/common/issue_definitions.v`
- `ref_submodule/miaow/src/verilog/rtl/decode/decode_definitions.v`
- `ref_submodule/miaow/src/verilog/rtl/alu/alu_definitions.v`
- `ref_submodule/miaow/src/verilog/rtl/lsu/lsu_definitions.v`
- `ref_submodule/miaow/src/verilog/rtl/dispatcher/dispatcher.v`
- `ref_submodule/miaow/src/verilog/tb/dispatcher_wrapper/dispatcher_hard.v`
- `ref_submodule/miaow/src/verilog/rtl/fpga/compute_unit_fpga.v`
- `ref_submodule/miaow/src/sw/xilinx_sdk/main.c`
- `ref_submodule/miaow/src/sw/miaow_unit_tests/test_*/unit_test_config.txt`
- `ref_submodule/miaow/src/sw/siagen/`
- `ref_submodule/miaow/src/sw/miaow_unit_tests/run`

The local lesson is: classify constants before refactoring them. Not every number should become the same kind of macro.

## Global RTL Defines

`src/verilog/rtl/common/global_definitions.v` defines:

- `WF_PER_CU = 40`
- `WG_PER_WF = 40`
- `WF_PER_WG = 16`
- `WF_ID_LENGTH = 6`
- `OPERAND_LENGTH_2WORD = 13`
- `OPERAND_LENGTH_4WORD = 14`
- `VGPR_ADDR_LENGTH = 10`
- `SGPR_ADDR_LENGTH = 9`
- `WORD_LENGTH = 32`
- `NUMBER_VGPR = 1024`
- `NUMBER_SGPR = 512`

Local classification questions:

- Is this an ISA-visible architectural limit?
- Is it a CU physical capacity?
- Is it a field width derived from another value?
- Is it a test fixture assumption?
- Is it a prototype-only value?

Example: `WF_PER_CU` is CU capacity. `WF_ID_LENGTH` is derived from the number of wavefronts and leaks into signal widths. `NUMBER_VGPR` and `NUMBER_SGPR` affect register-file implementation and dispatcher/resource assumptions.

## Stage-Specific Definitions

MIAOW also has local definition files:

- `issue_definitions.v`: issue record layout and dependency metadata
- `decode_definitions.v`: decoded instruction fields
- `alu_definitions.v`: ALU encodings and local control
- `lsu_definitions.v`: memory operation encodings

These are good examples of hardware-private or module-contract constants. They should not leak into runtime headers unless they become ABI.

Skill implication:

- bitfield definitions should have one owner
- derived decode/issue field ranges should not be manually duplicated
- trace decoders and tests need synchronization if they inspect those fields

## Dispatcher Parameters

`src/verilog/rtl/dispatcher/dispatcher.v` defines many resource parameters:

- `NUMBER_CU`
- `CU_ID_WIDTH`
- `WG_ID_WIDTH`
- `WG_SLOT_ID_WIDTH`
- `NUMBER_WF_SLOTS`
- `WF_COUNT_WIDTH`
- `WAVE_ITEM_WIDTH`
- `VGPR_ID_WIDTH`
- `NUMBER_VGPR_SLOTS`
- `SGPR_ID_WIDTH`
- `NUMBER_SGPR_SLOTS`
- `LDS_ID_WIDTH`
- `NUMBER_LDS_SLOTS`
- `GDS_ID_WIDTH`
- `GDS_SIZE`
- `TAG_WIDTH`
- `MEM_ADDR_WIDTH`
- CU-side VGPR/SGPR/LDS/GDS id widths

These values are not all the same class. Some are physical resource quantities. Some are launch fields. Some are resource allocator widths. Some define the CU/dispatcher ABI.

Skill implication:

- dispatch parameters must be checked against CU limits
- tag width is an ABI when used for done/completion
- per-wavefront resource size and total resource size must agree
- allocation failure behavior must be part of the config contract

## FPGA MMIO Registers

`compute_unit_fpga.v` decodes AXI-Lite register addresses for wave ID, base registers, start PC, instruction buffer, GPR writes, memory handshake, and result status.

`src/sw/xilinx_sdk/main.c` defines host-side `NEKO_*` offsets:

- `NEKO_CMD_ADDR`
- `NEKO_BASE_LDS`
- `NEKO_INSTR_ADDR`
- `NEKO_INSTR_VALUE`
- `NEKO_GPR_CMD`
- `NEKO_SGRP_ADDR`
- `NEKO_SGRP_QUAD_0` to `NEKO_SGRP_QUAD_3`
- `NEKO_MEM_OP`
- `NEKO_MEM_RD_DATA`
- `NEKO_MEM_ADDR`
- `NEKO_MEM_WR_DATA`
- `NEKO_MEM_WR_EN`
- `NEKO_MEM_ACK`
- `NEKO_MEM_DONE`
- `NEKO_CYCLE_COUNTER`
- `NEKO_CURRENT_INST_ADDR`

This is the main MIAOW drift warning. The RTL decode and C offsets are separate. A local project should either generate both from one source or add a drift check.

Skill implication:

- MMIO maps are HW/SW ABI
- control register state values are also ABI if software depends on them
- C offsets, RTL decode, docs, and tests must be reviewed together

## Unit-Test Config Format

Each unit test has `unit_test_config.txt`. A typical line encodes:

- kernel or wavefront count fields
- CU/workgroup/wavefront identifiers
- wavefront size
- VGPR/SGPR/LDS sizes or bases
- initial VGPR values per lane
- initial SGPR values
- PC or related final field

The exact format is parsed by MIAOW support code and then used to generate traces and RTL inputs. Treat this as a test ABI. If it changes, the parser, test generator, trace generator, and RTL harness must change together.

## SIAGen And Generated Workloads

`src/sw/siagen/` generates instruction, data, and config files. `main.cpp` calls `parseArgs`, initializes instruction arrays, shuffles instructions, prints instruction streams, writes config files, and writes data memory files.

Skill implication:

- generator arguments are configuration inputs
- generated tests should record the generator version and arguments
- random generation needs a seed story if results are used as evidence

## Conditional Build Flags

`compute_unit.vp` and related files use `FPGA_BUILD` to expose extra dispatch/register ports and remove some simulation-only trace outputs. This is not just a synthesis flag if it changes interfaces.

Classify conditional flags as:

- implementation-only
- debug-only
- test-only
- FPGA prototype interface
- public ABI-changing

## Local Drift Checklist

When changing a config value, inspect:

| If changing | Also inspect |
|---|---|
| wavefront count or id width | fetch, wavepool, issue tables, dispatcher, trace monitor limits |
| VGPR/SGPR count | register files, dispatcher slots, issue dependency tables, test config |
| LDS/GDS size | dispatcher resource tables, LSU address path, runtime/control plane |
| MMIO offset | RTL decode, C constants, scripts, docs, tests |
| unit-test format | parser, generator, trace files, testbench |
| FPGA build flag | interface shape in sim versus FPGA |

## What To Copy Locally

Copy these habits:

- define parameter classes before editing
- derive widths when possible
- treat MMIO maps as ABI
- treat test config formats as ABI
- test at least one small config and one target config

Do not copy the drift. MIAOW's scattered constants are a useful audit target, not a model of a modern unified configuration system.
