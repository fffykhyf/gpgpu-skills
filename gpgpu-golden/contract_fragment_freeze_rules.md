# Contract Fragment Freeze Rules

`gpgpu-interconnect`, `gpgpu-memory`, and `gpgpu-atomic-sync` produce
`contract_fragment_ir`. `gpgpu-golden` is the only skill that freezes those
fragments into `SYSTEM_CONTRACT_IR`.

Rules:

1. Fragment-producing skills do not create a second semantic truth source.
2. `SYSTEM_CONTRACT_IR` is the only frozen truth source.
3. The executable golden model derives only from `SYSTEM_CONTRACT_IR`.
4. `GOLDEN_CONTRACT_MODEL` derives only from `SYSTEM_CONTRACT_IR`.
5. SimX-style module twin trace also derives only from `SYSTEM_CONTRACT_IR`.
6. Any fragment conflict fails closed with owner skill and contract path.

The executable golden model must be constructed only from SYSTEM_CONTRACT_IR;
it must not read side contracts directly after freeze.

Required frozen fragments:

- fabric request/response and L2 route fragment;
- LSU lane format and coalescer response restore fragment;
- L1 cache or global adapter and L2 cache slice fragment;
- MSHR replay and deadlock guard fragment;
- atomic serialization, fence visibility, barrier phase, and WSYNC drain fragment.
