# MIAOW Local Notes For `gpgpu-rtl-simt-core`

This file is the local MIAOW reference for the RTL SIMT core skill. It summarizes the MIAOW CU implementation details that matter when designing fetch, wavefront state, decode, issue, dependency tracking, special registers, execution units, writeback, and trace.

## Core RTL Path

The main entry is `ref_submodule/miaow/src/verilog/rtl/compute_unit/compute_unit.vp`. The useful mental model is:

```text
dispatch -> fetch -> wavepool -> decode -> issue/scoreboard
         -> rfa/register files -> SALU/SIMD/SIMF/LSU
         -> exec/special state -> writeback -> tracemon/retire
```

MIAOW does not hide the CU in one module. Its top level exposes interfaces for:

- wavefront dispatch and done
- instruction buffer request and response
- branch redirect
- wavefront base registers
- decoded issue fields
- FU select signals
- SGPR/VGPR read and writeback
- EXEC, VCC, SCC, M0 read/write state
- LSU memory request/response
- retire PC and tracemon side effects

The local design rule is to name state ownership before writing RTL. If PC, active mask, dependency readiness, branch wait, barrier wait, or writeback ownership cannot be assigned to a module, the boundary is still unclear.

## Fetch And Wavefront Residency

`src/verilog/rtl/fetch/fetch.v` accepts:

- `dispatch2cu_wf_dispatch`
- wavefront tag
- start PC
- VGPR, SGPR, and LDS base
- wavefront size
- workgroup wavefront count
- branch redirect from SALU
- completion from issue

It allocates a wfid with `wfid_generator`, records workgroup metadata with `wavegrp_info`, initializes the EXEC mask with `mask_gen`, and drives instruction-buffer address/tag requests through `pc_block` and `round_robin`.

`src/verilog/rtl/wavepool/wavepool.vp` receives instruction-buffer responses and feeds decode. It stores per-wavefront instruction queues, base-register metadata, stop-fetch signals, and reset behavior for halt/branch/completion. Its `reg_40x35b_1r_1w` base-register table stores `{vgpr_base, sgpr_base, lds_base}` by wfid.

Skill implication:

- dispatch metadata is resident wavefront state, not testbench noise
- start PC, current PC, base registers, wavefront size, tag, and workgroup wavefront count must survive until retire or deschedule
- stop-fetch and branch redirect need explicit ownership

## Issue Readiness

`src/verilog/rtl/issue/issue.v` is the most important SIMT RTL reference. It splits readiness into multiple per-wavefront arrays:

- `valid_entry_out`
- `fu_lsu`, `fu_salu`, `fu_simd`, `fu_simf`
- `ready_array_data_dependencies`
- `mem_wait_arry`
- `pending_branches_arry`
- `barrier_wait_arry`
- `max_instr_inflight_array`

The actual ready equations are explicit:

```text
salu_ready = fu_salu & valid & deps_ready & ~max_inflight & ~branch_wait & ~barrier_wait
simd_ready = fu_simd & valid & deps_ready & ~max_inflight & ~branch_wait & ~barrier_wait
simf_ready = fu_simf & valid & deps_ready & ~max_inflight & ~branch_wait & ~barrier_wait
lsu_ready  = fu_lsu  & valid & deps_ready & ~max_inflight & ~mem_wait & ~branch_wait & ~barrier_wait
```

`instruction_arbiter.v` then combines those ready arrays with FU availability signals such as `simd0_alu_ready`, `salu_alu_ready`, and `lsu_ready`.

Skill implication:

- never reduce issue to `decode_valid && fu_ready`
- every wait condition needs set, clear, reset, and trace/debug rules
- LSU readiness must include memory wait, not just FU availability

## Scoreboard And Dependencies

`src/verilog/rtl/issue/scoreboard.v` stores decoded instruction records in `instr_info_table`. It derives issued instruction operands and destinations from the stored record rather than rereading decode wires.

The dependency logic is separated:

- `busy_gpr_table` identifies busy source/destination fields.
- `vgpr_comparator` and `sgpr_comparator` compare retired writebacks against waiting instruction fields.
- `gpr_dependency_table.vp` tracks VGPR/SGPR readiness per wavefront.
- `spr_dependency_table.v` tracks special-register hazards for EXEC, VCC, SCC, and M0.
- `ready_array_data_dependencies = ready_arry_spr & ready_arry_gpr`.

Skill implication:

- GPR and SPR hazards are different owners
- special registers are not "just SGPR aliases" in issue logic
- a decoded instruction should become a stable issue record before arbitration
- writeback-done wfid and destination-valid mask are part of the hazard-clear contract

## Wait Tables

MIAOW uses separate modules for waits:

- `mem_wait.v`: set on LSU issue, clear on `lsu_done` plus `lsu_done_wfid`.
- `branch_wait.v`: set when a branch issues, clear when SALU reports branch completion for the wfid.
- `barrier_wait.v`: holds wavefronts at workgroup barriers and emits barrier retire trace information.
- `finished_wf.v`: handles halt/done and maximum in-flight protection.
- `valid_entry.v`: records which resident issue entries are valid and removes them on issue, halt, waitcnt, branch, or barrier cases.

Skill implication:

- branch, barrier, memory, and in-flight waits are not interchangeable stalls
- each wait needs a release event and a deadlock check
- barrier logic needs workgroup membership, not only a single wfid

## Special State

`src/verilog/rtl/exec/exec.v` owns per-wavefront special state:

- M0: 32-bit
- SCC: 1-bit
- VCC: 64-bit
- EXEC: 64-bit active mask

Fetch initializes EXEC from wavefront size through `fetch_init_wf_en`, `fetch_init_wf_id`, and `fetch_init_value`. SALU can write EXEC, VCC, SCC, and M0. SIMD/SIMF can write VCC through a mux selected by RFA.

Skill implication:

- active mask is architectural state, not a temporary datapath bit
- the owner of EXEC initialization and update must be named
- VCC writes from vector units and SALU need arbitration and hazard feedback

## Execution Units And Register Files

The CU instantiates:

- `salu/salu.vp` and `salu/scalar_alu.v` for scalar/control behavior
- four `simd/simd.v` units for integer/vector behavior
- four `simf/simf.v` units for floating behavior
- `rfa/rfa.v` for register-file access arbitration
- `sgpr/sgpr.v` and `vgpr/vgpr.v` for scalar/vector storage

The top-level trace-visible writebacks include destination address, data, write enable, write mask, instr_done, done wfid, and retire PC. Preserve this shape in local RTL so a failure can be traced to issue, operand, FU, register file, or retire.

## Bring-Up Sequence

A MIAOW-inspired local bring-up can be:

1. Dispatch one wavefront into fetch and initialize EXEC.
2. Fetch instructions by PC and push them through wavepool.
3. Decode one ALU instruction into a stable issue record.
4. Issue through one FU and write SGPR/VGPR result.
5. Add GPR dependency clear on writeback.
6. Add EXEC/VCC/SCC/M0 dependency handling.
7. Add branch wait and branch redirect.
8. Add barrier wait with workgroup membership.
9. Add LSU issue and memory wait release.
10. Add multi-FU arbitration and retire trace alignment.

## Caveats

MIAOW's RTL is a valuable reference, but local designs should not blindly copy:

- AMD Southern Islands encodings
- exact 40-wavefront CU capacity
- exact 4 SIMD plus 4 SIMF layout
- generated `.vp` style
- lack of a modern valid-ready interface in some legacy modules

Copy the discipline: explicit state tables, explicit waits, explicit writeback, and traceable retire.
