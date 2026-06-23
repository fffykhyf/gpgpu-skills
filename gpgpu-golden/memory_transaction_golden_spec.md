# Memory Transaction Golden Spec

Golden memory semantics must expose coalescer input before cache timing:

- lane addresses;
- active mask;
- byte mask;
- sector mask;
- access type;
- read/write/atomic class;
- transaction grouping.

The golden model may validate transaction functional content without adopting a
timing cache, MSHR, NoC, or DRAM model.

