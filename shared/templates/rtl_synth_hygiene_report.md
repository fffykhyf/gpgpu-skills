# RTL Synthesis Hygiene Report

## Module List

- module:

## Top Port Style

- flattened_packed_bus:
- unpacked_array_port_findings:

## Memory Reset/Init Style

- large_memory_reset_loops:
- large_memory_init_loops:
- profile_gates:

## Loop Style

- fixed_bound_for_loops:
- data_dependent_while_loops:
- non_constant_loop_bounds:

## Valid/Ready Style

- accept_rule:
- dequeue_gated_by_accept:
- combinational_ready_loop_findings:

## Payload Stability

- payload_stable_while_valid_ready_low:

## Launch Inflight Coverage

- inflight_register_present:
- ready_gap_covered:

## Done/Result/Counter Stability

- result_latched_before_done:
- counters_stable_before_done:

## Verdict

- verdict:
