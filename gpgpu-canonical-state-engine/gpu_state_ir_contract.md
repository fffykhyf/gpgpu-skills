# GPU_STATE_IR Contract

## Purpose

Populate warp_state, thread_state, pc_state, active_mask_state, scheduler_state, scoreboard_state, register_state, memory_request_state, csr_state, launch_state, pipeline_state, simt_stack_state, and fault_state. Required trace-diff fields include pc_table, exec_mask_table, warp_active, warp_halted, current_fetch_warp, next_fetch_warp, register_pending, pipeline_registers, memory_stall_state, and performance_counters.

## Required Inputs

- Upstream IR named in `SKILL.md`
- Required schema assets
- Required table assets

## Output Contract

- Emit only the IR/report fields owned by the parent skill.
- Preserve consumed IR hashes.
- Record failed fields and missing assets.

## Fail Closed Rule

If a required schema row, table row, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET`. If a field is ambiguous or unsupported, reject instead of inferring.
