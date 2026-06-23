# Atomic Operation Contract

Required fields:

- operation type;
- address;
- lane mask;
- byte mask;
- return-value behavior;
- destination register if any;
- completion event;
- serialization domain;
- scoreboard release condition.

Atomic stalls use `atomic_wait` or `atomic_split_or_replay`, not generic memory
stall.

