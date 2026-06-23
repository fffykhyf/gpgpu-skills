# Differential Correctness Engine

This component is required only in Failure Attribution Mode. It compares RTL,
golden, memory, CSR, fault, and completion evidence to find the earliest
deterministic architectural divergence.

## Compared Signals

- PC and next PC
- decoded instruction
- active mask and predicate mask
- register read values
- register writeback values
- memory request address, size, byte enable, lane mask, and tag
- memory response value, tag, and routing
- CSR update
- barrier state
- scoreboard state
- fault status
- completion status
- final memory dump

## Output

```yaml
first_divergence_report:
  verdict: DIVERGENCE_FOUND | NO_DIVERGENCE_FOUND | INSUFFICIENT_TRACE
  first_divergence_type: PC_MISMATCH | NEXT_PC_MISMATCH | DECODE_MISMATCH | ACTIVE_MASK_MISMATCH | PREDICATE_MASK_MISMATCH | REGISTER_WRITEBACK_MISMATCH | MEMORY_ADDRESS_MISMATCH | MEMORY_VALUE_MISMATCH | MEMORY_BYTE_ENABLE_MISMATCH | RESPONSE_TAG_MISMATCH | CSR_MISMATCH | BARRIER_STATE_MISMATCH | FAULT_STATUS_MISMATCH | COMPLETION_STATUS_MISMATCH
  cycle: optional integer
  step_id: optional integer
  wavefront_id: optional integer
  pc: optional string
  golden_event: object
  rtl_event: object
  contract_paths: list
  rtl_module_paths: list
  toolchain_artifact_paths: list
  precondition_window: list
  postcondition_window: list
  evidence_hashes: list
  confidence: HIGH | MEDIUM | LOW
```

## Ranking Rules

- Prefer the first deterministic architectural divergence.
- Do not report final memory mismatch as root cause. It is a symptom unless it
  is the first observable architectural divergence available.
- Prefer event pairs that share instruction identity, wavefront identity, and
  deterministic order.
- If PC, decode, active mask, and register evidence are all missing, emit
  `INSUFFICIENT_TRACE`.
- If toolchain evidence exists, compare assembler/program image/loader/runtime
  chain before blaming RTL fetch or decode.
