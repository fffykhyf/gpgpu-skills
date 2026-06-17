# MIAOW Local Notes For `gpgpu-runtime`

This file is the local MIAOW reference for runtime and control-plane work. MIAOW does not provide a Vortex-style full runtime API, but it has three useful early launch/control forms: testbench soft dispatch, hard resource dispatch, and FPGA AXI-lite control.

Terminology note: this file preserves MIAOW source names such as `wave`, `wavefront`, `wfid`, `workgroup`, and `EXEC`. In the skill contract, map them to `SIMT group`, `simt_group_id`, `CTA/workgroup`, and `active lane mask`; use the MIAOW names only when quoting source behavior.

## Relevant Source Map

Use these files as the main references:

- `ref_submodule/miaow/src/verilog/tb/dispatcher_wrapper/dispatcher_soft.v`
- `ref_submodule/miaow/src/verilog/tb/dispatcher_wrapper/dispatcher_hard.v`
- `ref_submodule/miaow/src/verilog/tb/dispatcher_wrapper/dispatcher_hard_host.v`
- `ref_submodule/miaow/src/verilog/rtl/dispatcher/dispatcher.v`
- `ref_submodule/miaow/src/verilog/rtl/dispatcher/gpu_interface.v`
- `ref_submodule/miaow/src/verilog/rtl/dispatcher/cu_handler.v`
- `ref_submodule/miaow/src/verilog/rtl/dispatcher/resource_table.v`
- `ref_submodule/miaow/src/verilog/rtl/dispatcher/global_resource_table.v`
- `ref_submodule/miaow/src/verilog/rtl/dispatcher/wg_resource_table.v`
- `ref_submodule/miaow/src/verilog/rtl/dispatcher/inflight_wg_buffer.v`
- `ref_submodule/miaow/src/verilog/rtl/fpga/compute_unit_fpga.v`
- `ref_submodule/miaow/src/sw/xilinx_sdk/main.c`

Use MIAOW to reason about minimal launch/control contracts, not as a full public runtime API template.

## Testbench Soft Dispatcher

`dispatcher_soft.v` exposes DPI/C-style hooks:

- `ScheduleWavefront`
- `DescheduleWavefront`
- `getCuId`
- `getWfTag`
- `getWfCnt`
- `getWfNumThrds`
- `getVregBase`
- `getVregSize`
- `getSregBase`
- `getSregSize`
- `getLdsBase`
- `getLdsSize`
- `getPC`
- `setVregValue`
- `setSregValue`

It uses those hooks to initialize VGPR/SGPR state, then drives CU dispatch fields:

- `dispatch2cu_wf_dispatch`
- `dispatch2cu_wg_wf_count`
- `dispatch2cu_wf_size_dispatch`
- `dispatch2cu_sgpr_base_dispatch`
- `dispatch2cu_vgpr_base_dispatch`
- `dispatch2cu_wf_tag_dispatch`
- `dispatch2cu_lds_base_dispatch`
- `dispatch2cu_start_pc_dispatch`

When the CU reports `cu2dispatch_wf_done`, the soft dispatcher calls `DescheduleWavefront` with the done tag.

Skill implication:

- direct register pokes are acceptable for fast testbench setup
- they must be labeled test-only
- the dispatch field list is still a useful launch contract
- done and tag return are part of lifecycle, not optional debug

## Hard Dispatcher And Resource Contract

`dispatcher_hard.v` wraps a host generator and the RTL dispatcher. It parameterizes:

- number of CUs
- number of wavefront slots
- workgroup id width
- wavefront count width
- VGPR, SGPR, LDS, and GDS slot sizes
- CU-side VGPR/SGPR/LDS/GDS id widths
- tag width
- memory address width

`dispatcher.v` integrates modules such as:

- `gpu_interface`
- `cu_handler`
- `global_resource_table`
- `resource_table`
- `wg_resource_table`
- `inflight_wg_buffer`
- `allocator`
- `dis_controller`

The dispatcher accepts host workgroup fields including workgroup id, number of wavefronts, wavefront size, VGPR/SGPR/LDS/GDS total size, per-wavefront register size, and start PC. It outputs CU dispatch fields and tracks wavefront completion/deallocation.

Skill implication:

- runtime launch is also resource allocation
- VGPR/SGPR/LDS/GDS totals and per-wavefront sizes need explicit failure behavior
- tag width and done tag form an ABI between CU and dispatcher
- dispatcher capacity must match CU capacity and config

## FPGA AXI-Lite Control Plane

`compute_unit_fpga.v` wraps the CU as an AXI-Lite slave. The control plane includes:

- execution FSM: `IDLE_STATE`, `EXECUTE_STATE`, `RESULT_STATE`
- write to start command register to begin execution
- result-ready behavior when `cu2dispatch_wf_done` fires
- wave ID, base VGPR, base SGPR, base LDS, wave count, and start PC registers
- instruction buffer address and value registers
- SGPR quad write registers
- VGPR vector base, per-lane data registers, and write mask
- FPGA memory request/ack/done handshake

The RTL decodes AXI address slices such as:

- `9'h001`: wave ID
- `9'h002`: base VGPR
- `9'h003`: base SGPR
- `9'h004`: base LDS
- `9'h005`: wave count
- `9'h006`: start PC
- `9'h007`: instruction address
- `9'h008`: instruction value
- `9'h0C0`: GPR command
- `9'h0C1` to `9'h0C5`: scalar register write fields
- `9'h0C6` and above: vector register write fields

Skill implication:

- even a small FPGA bring-up path is a runtime/control plane
- MMIO register names, offsets, and state transitions must be documented
- result ready and done tag are the hardware-visible completion path

## Xilinx SDK Host Control

`src/sw/xilinx_sdk/main.c` is the matching software side. It defines `NEKO_*` offsets using `XPAR_AXI_SLAVE_0_S00_AXI_BASEADDR`, including:

- `NEKO_CMD_ADDR`
- `NEKO_BASE_LDS`
- `NEKO_INSTR_ADDR`
- `NEKO_INSTR_VALUE`
- `NEKO_GPR_CMD`
- SGPR quad offsets
- memory op, address, read data, write data, ack, and done offsets
- cycle/current-instruction read offsets

The SDK code uses UART commands and `XIo_Out32`/`XIo_In32` to:

- load instruction words
- load memory data
- reset instruction and memory counters
- start kernel execution
- poll execution status
- read cycle/current instruction counters
- service LSU memory read/write handshakes
- send kernel-done notification

Skill implication:

- the host-side state machine is part of the runtime contract
- a memory service loop can be a valid early backend transport
- C offsets and RTL decode must stay synchronized

## Local Runtime Contract Template

For a local runtime/control-plane change, specify:

| Stage | Required fields |
|---|---|
| program load | instruction address, instruction data, endian/order, PC base |
| state init | SGPR values, VGPR lane values, LDS/data memory, masks |
| dispatch | CU id, wfid or tag, start PC, wavefront size, workgroup wavefront count, base registers |
| execution | start command, accepted/idle condition, busy status |
| memory service | request op, address, data, ack, done, read/write direction |
| completion | done flag, done tag, result-ready read, timeout behavior |
| cleanup | deschedule, resource release, buffer lifetime |

## Boundaries And Caveats

Do not promote MIAOW's testbench hooks into a public API. They are useful for unit tests because they write internal register state directly.

Do not assume MIAOW's FPGA MMIO path is a complete runtime. It lacks handle-based devices, buffers, queues, modules, kernels, events, fences, and cache-flush semantics.

Do copy these principles:

- launch is a contract, even in a testbench
- resource allocation is part of runtime behavior
- MMIO offsets are ABI
- memory service and completion must be observable
- test-only and public interfaces must be separate
