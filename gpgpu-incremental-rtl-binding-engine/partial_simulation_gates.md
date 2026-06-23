# Partial Simulation Gates

The partial simulator validates one module at a time before full-system RTL
simulation. Partial simulation is a module gate, not a replacement for
full-system verification.

## Required Inputs

- module binding record
- selected `MODULE_BINDING_TEMPLATE`
- local trace schema
- `GOLDEN_CONTRACT_MODEL` slice
- `PROGRAM_IMAGE_IR`
- `RUNTIME_LAUNCH_IR`
- `LOADER_CONTRACT_IR`
- `INTERFACE_BINDING_IR` transactions
- local stimulus

## Required Outputs

- `local_trace_hash`
- `local_scoreboard_result`
- `interface_transaction_result`
- `golden_slice_compare_result`
- `timing_feedback_result`
- `verdict`

## Module Case Requirements

`shared/tables/rtl_partial_sim_gate_table.yaml` owns the concrete case list.
At minimum it must cover:

- scoreboard: RAW dependency stall, writeback wakeup, multiple warp independence
- warp scheduler: round-robin fairness, skip stalled warp, no-ready-warp idle
- load/store queue: ready-low payload stable, tag unique, response wakeup, fault
  propagation
- shared memory bank unit: bank conflict stall, lane-mask byte enable,
  aligned/misaligned behavior
- CSR runtime: start, done, fault, kernel entry, arg base
- program image loader interface: program image load, entry PC fetch, first
  instruction decode
- runtime argument buffer interface: argument buffer visible

## Gate Rule

A module with `PARTIAL_SIM_FAIL`, `INTERFACE_PROTOCOL_MISMATCH`,
`GOLDEN_SLICE_MISMATCH`, or `COMBINATIONAL_READY_LOOP` cannot be used in
full-system simulation.

Program-image and runtime partial gates also fail closed on
`PROGRAM_IMAGE_LOAD_FAIL`, `ENTRY_PC_FETCH_FAIL`, `FIRST_INSTRUCTION_DECODE_FAIL`,
or `ARG_BUFFER_VISIBILITY_FAIL`.

## Failure Evidence

Each failed case must report:

- module path
- interface ID when applicable
- contract path
- trace field
- first failing cycle when available
- expected golden slice behavior
- observed local behavior
