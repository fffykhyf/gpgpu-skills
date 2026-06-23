# Power and Energy Boundary

Power/energy evidence is derived from activity counters. It cannot prove a
performance bottleneck by itself.

Any power report must record:

- source mode: `sim`, `hw`, or `hybrid`;
- XML/config provenance when a model is used;
- sampling window and aggregation policy;
- activity counters consumed by each bucket;
- whether the producing counters are producer-backed.

Do not copy AccelWattch XML coefficients, McPAT object hierarchy, constant-power
terms, or hybrid CSV substitution as RTL or validation truth.

Raw basis: `raw/gpgpu-sim-power-energy-model-notes.md`.

