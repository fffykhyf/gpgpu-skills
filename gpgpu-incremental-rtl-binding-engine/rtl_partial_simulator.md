# RTL Partial Simulator

The partial simulator validates one module at a time before full-system RTL simulation.

## Required Inputs

- module contract
- local trace schema
- `GOLDEN_CONTRACT_MODEL` slice
- interface transactions
- local stimulus

## Required Outputs

- `local_trace_hash`
- `local_scoreboard_result`
- `interface_transaction_result`
- `golden_slice_compare_result`
- `verdict`

## Gate Rule

A module with `PARTIAL_SIM_FAIL` cannot be used in full-system simulation. Partial simulation is a module gate, not a replacement for full-system verification.
