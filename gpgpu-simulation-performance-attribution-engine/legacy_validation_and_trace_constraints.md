# Legacy Validation and Trace Constraints

This reference migrates the useful constraints from the removed
`gpgpu-runtime-validator`, the validation portions of `gpgpu-memory-subsystem`,
and the trace and RTL/golden comparison portions of
`gpgpu-implementation-validator`, plus the useful evidence behavior from legacy
`gpgpu-runtime`, `gpgpu-memory-path`, `gpgpu-golden-sim`,
`gpgpu-rtl-simt-core`, and `gpgpu-causal-trace-analyzer`.

## Runtime Validation Evidence

Runtime evidence must be normalized into `NORMALIZED_TRACE_IR`. Useful migrated
checks include:

- frontend subset compile or parse smoke
- assembler smoke
- program image or hex load smoke
- kernel test application evidence
- launch argument encoding
- grid, block, and thread mapping
- queue and doorbell behavior
- CSR synchronization
- completion observation
- fault observation
- golden output comparison

These checks validate behavior against `GOLDEN_CONTRACT_MODEL`; they must not
define launch or memory truth themselves.

The final cross-run output for this engine is `PERF_ATTRIBUTION_GRAPH`, with
supporting `ROOT_CAUSE_REPORT` and normalized trace evidence.

Runtime validation must not infer scheduler policy, allocate warps absent from
the contract, optimize memory visibility, modify config defaults, or treat the
backend transport as the launch ABI.

## Memory Correctness Evidence

Memory validation must compare trace evidence against contract paths and RTL
module paths. It must cover the applicable subset of:

- request lifecycle
- address-space selection
- coalescing result
- lane mask and byte enable behavior
- load/store queue ordering
- duplicate-request prevention
- request replay policy
- shared-memory bank conflict behavior
- cache miss and global response behavior
- atomic and fence ordering
- fault propagation
- scoreboard wakeup
- stall and backpressure behavior
- memory dump comparison

Any memory conclusion without cycle, warp, memory event, contract path, and RTL
module evidence is insufficient.

## RTL and Golden Trace Comparison

The engine must preserve the old implementation-validator discipline:

- collect RTL simulation trace
- collect waveform-derived trace when available
- collect golden contract trace derived from `GOLDEN_CONTRACT_MODEL`
- normalize field names and time bases
- compare PC, active mask, register writes, memory transactions, CSR changes,
  completion, and faults
- report first divergence with minimal trace window

Trace comparison must identify both contract path and module path whenever the
data allows it. A mismatch without enough evidence becomes
`INSUFFICIENT_TRACE_EVIDENCE`, not a guessed root cause.

## Causal Attribution Requirement

Performance and correctness reports must become a causal graph, not a flat
report. The graph should connect:

```text
cycle
  -> warp
  -> scoreboard or scheduler state
  -> memory request or execution pipeline event
  -> cache miss, bank conflict, replay, dependency, or pipeline bubble
  -> RTL module path
  -> SYSTEM_CONTRACT_IR path
```

Root cause classes include contract violation, RTL structural issue, memory
imbalance, scheduling inefficiency, missing evidence, and test-evidence drift.

The migrated causal trace analyzer rule is mandatory: metrics are not enough.
Every root cause must cite trace evidence, a failed gate, and a path to either
`SYSTEM_CONTRACT_IR` or `INCREMENTAL_RTL_MAP`. If multiple root causes cannot be
ranked deterministically, emit `ROOT_CAUSE_AMBIGUOUS`.
