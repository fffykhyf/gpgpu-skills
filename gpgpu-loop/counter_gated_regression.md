# Counter-Gated Regression

Functional pass does not imply regression pass.

Trigger rewrite when:

- coalesced transaction count unexpectedly increases;
- scoreboard wait rises without explanation;
- barrier/membar/atomic wait lacks a sync contract;
- cache reservation fail spikes;
- ICNT `has_buffer` fail spikes;
- L2 queue full is misattributed to DRAM;
- a counter lacks producer proof.

