# Trace Normalizer

The trace normalizer converts RTL, waveform-derived, golden contract, runtime, memory, and module partial-sim traces into `NORMALIZED_TRACE_IR`.

## Normalized Event Fields

- `event_id`
- `cycle`
- `warp_id`
- `instruction_id`
- `contract_path`
- `rtl_module_path`
- `event_type`
- `dependencies`
- `evidence_source`

## Rules

- Every event must identify its evidence source.
- Golden events must derive from `GOLDEN_CONTRACT_MODEL`.
- RTL events must identify a module path from `INCREMENTAL_RTL_MAP`.
- Events without cycle information must provide a deterministic ordering key.
