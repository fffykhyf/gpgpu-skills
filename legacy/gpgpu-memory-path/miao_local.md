# MIAOW Local Notes For `gpgpu-memory-path`

This file is the local MIAOW reference for the memory-path skill. It explains how MIAOW builds a small but observable LSU and what to copy conceptually before adding coalescing, cache, MSHR, VM, or timing studies.

Terminology note: this file preserves MIAOW source names such as `wave`, `wavefront`, `wfid`, `workgroup`, and `EXEC`. In the skill contract, map them to `SIMT group`, `simt_group_id`, `CTA/workgroup`, and `active lane mask`; use the MIAOW names only when quoting source behavior.

## Relevant Source Map

The main files are:

- `ref_submodule/miaow/src/verilog/rtl/lsu/lsu.v`
- `ref_submodule/miaow/src/verilog/rtl/lsu/lsu_opcode_decoder.v`
- `ref_submodule/miaow/src/verilog/rtl/lsu/lsu_addr_calculator.v`
- `ref_submodule/miaow/src/verilog/rtl/lsu/lsu_op_manager.v`
- `ref_submodule/miaow/src/verilog/rtl/lsu/ds_addr_calc.v`
- `ref_submodule/miaow/src/verilog/rtl/lsu/mtbuf_addr_calc.v`
- `ref_submodule/miaow/src/verilog/rtl/memory/memory.v`
- `ref_submodule/miaow/src/verilog/rtl/tracemon/tracemon.c`
- memory tests under `ref_submodule/miaow/src/sw/miaow_unit_tests/test_200_*`, `test_202_*`, `test_300_*`, `test_301_*`, `test_302_*`, `test_303_*`, `test_304_*`, and `test_305_*`

The MIAOW lesson is not "this is a complete memory hierarchy." It is "even a blocking LSU should expose enough SIMT metadata to debug every lane."

## Opcode Decode

`lsu_opcode_decoder.v` classifies memory instructions and generates control for:

- memory format, including SMRD, DS, and MTBUF
- memory operation count
- read versus write
- SGPR versus VGPR destination
- SGPR/VGPR source reads
- destination address and write mask
- GPR operation depth

Skill implication:

- the LSU frontend should produce a stable memory micro-op contract
- memory format should be trace-visible
- destination class and write mask should be known before response

## Address Generation

`lsu_addr_calculator.v` is the address-generation anchor. It takes:

- vector source data
- scalar source A and B
- opcode
- LDS base
- immediate value

It outputs a 2048-bit address vector and a global/LDS selector. The file handles:

- SMRD: scalar memory read using scalar base and immediate/scalar offset
- DS: LDS address calculation through `ds_addr_calc`
- MTBUF: vector memory address calculation through `mtbuf_addr_calc`
- per-lane thread-id contribution when the scalar descriptor requests it

It also documents an architectural limitation: MTBUF with both offset and index would need two VGPR reads, but this implementation only has one read path for that case. Locally, unsupported address forms should fail explicitly or be marked unsupported, not silently produce plausible data.

Skill implication:

- record scalar base, vector offset, immediate, thread id, and LDS base in the trace plan
- separate global memory and LDS from the start
- state which address modes are unsupported due to register-port or datapath limits

## LSU Operation Manager

`lsu_op_manager.v` is the best local model for a first LSU state machine. It captures:

- `lsu_wfid`
- `instr_pc`
- memory op count
- read/write bit
- SGPR/VGPR destination class
- global/LDS bit
- SGPR write mask
- GPR operation depth
- 64-bit EXEC mask
- 2048-bit per-lane address vector
- memory ack and data
- VGPR store-data source

The FSM states are:

- `IDLE_STATE`
- `ADDR_CALC_STATE`
- `RD_STATE`
- `RD_REG_WR_STATE`
- `WR_REG_INIT_RD_STATE`
- `WR_REG_RD_STATE`
- `WR_STATE`
- `WR_REG_INC_STATE`
- `SIGNAL_DONE_STATE`

The read path issues one memory request at a time, skips inactive VGPR lanes based on the EXEC mask, collects read data into a 2048-bit buffer, then writes back to SGPR or VGPR. The write path reads VGPR data, shifts through lane data, skips inactive lanes, and writes memory. Completion emits done, done wfid, retire PC, destination writeback, and trace memory address.

Skill implication:

- name every LSU state and whether it owns register ports, memory ports, or writeback
- carry wfid and PC from issue to completion
- preserve EXEC mask and per-lane address vector through the operation
- release memory wait only on explicit done with wfid

## Memory Request Contract

MIAOW's LSU-to-memory interface includes:

- `mem_rd_en`
- `mem_wr_en`
- `mem_out_addr`
- `mem_wr_data`
- `mem_tag_req`
- `mem_gm_or_lds`

`mem_tag_req = {current_wfid, mem_rd_en_reg}` in `lsu_op_manager.v`, which is small but important: the response carries enough identity to relate memory behavior to a wavefront. A local design with outstanding requests needs a stronger tag, but the same metadata principle applies.

## Writeback And Trace Contract

The LSU outputs:

- `sgpr_dest_data`, `sgpr_dest_wr_en`, `sgpr_dest_addr`
- `vgpr_dest_data`, `vgpr_dest_wr_en`, `vgpr_wr_mask`, `vgpr_dest_addr`
- `lsu_done`, `lsu_done_wfid`
- `sgpr_instr_done`, `vgpr_instr_done`
- `retire_pc`
- `retire_gm_or_lds`
- `tracemon_mem_addr`

This is the minimum shape local LSU work should preserve. Final memory output alone is too late for debug; trace should show which lanes accessed which addresses and which register writeback followed.

## Simple Memory Model

`src/verilog/rtl/memory/memory.v` is a stub memory:

- byte arrays for data memory and LDS
- single request ack when read or write is asserted
- tag echo through `output_tag`
- no cache, no coalescer, no MSHR, no TLB, no DRAM timing

Use this as a smoke-test memory model only. It is useful for correctness bring-up, but it cannot justify cache, latency, bandwidth, or ordering conclusions.

## Test And Trace Use

The MIAOW memory tests include global buffer loads/stores and LDS reads/writes. They flow through:

1. unit-test config and memory files
2. Multi2Sim functional trace
3. RTL simulation
4. `tracemon` load/store print functions
5. `tracefile_cmp.pl`

The trace print functions in `tracemon.c` include `PrintVgprLoad`, `PrintVgprLoadDS`, `PrintSgprLoad`, `PrintVgprStore`, and `PrintVgprStoreDS`. These distinguish register, lane, address, value, and global/LDS style effects.

## Local Checklist

Before adding a cache or coalescer, prove:

- one SGPR load
- one VGPR load with multiple lanes
- one VGPR store with inactive lanes
- one LDS access
- destination writeback mask
- memory wait set and clear
- trace comparison catches a wrong lane address
- memory model limitations are documented

## Caveats

MIAOW's LSU is not a high-performance memory subsystem. Do not infer:

- coalescing
- cache correctness
- MSHR behavior
- out-of-order response demux
- memory consistency
- address translation
- realistic DRAM latency or bandwidth

Use MIAOW for the first observable LSU and for the discipline of carrying SIMT identity through memory.
