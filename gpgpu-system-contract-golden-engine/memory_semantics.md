# Memory Semantics

Memory semantics in `GOLDEN_CONTRACT_MODEL` are executable reference functions derived from `SYSTEM_CONTRACT_IR.memory_model`.

## Required Functions

| Semantics function | Purpose |
|---|---|
| `address_space_resolve` | Map an address to global, shared, local, constant, or invalid space. |
| `coalesce` | Convert lane memory intents into reference memory transactions. |
| `byte_enable` | Compute byte enables from lane mask, access size, and address alignment. |
| `fence_order` | Enforce declared ordering points. |
| `atomic_apply` | Apply atomic operation semantics. |
| `request_lifecycle_step` | Advance issue, stall, response, replay, retire, or fault state. |

## Required Evidence

Each function must cite:

- `contract_path`
- input state fields
- output state fields
- ordering or replay rule id
- failure mode

## Fail Closed Rules

- Reject missing coalescing rules.
- Reject hidden memory ordering defaults.
- Reject duplicate request behavior not declared in the contract.
