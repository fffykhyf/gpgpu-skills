# Memory Ordering Litmus Tests

Minimum litmus coverage:

- atomic return-value ordering;
- same-address atomic serialization;
- fence visibility point;
- CTA barrier release;
- store/fence/load ordering by scope;
- scoreboard release after atomic or load completion.

GPGPU-Sim timing-side notes are insufficient as a full memory consistency model.

