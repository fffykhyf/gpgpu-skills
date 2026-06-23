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

## Store Commit Channel

Every committed store must be observable through `STORE_COMMIT_EVENT` with
cycle or step, SM, warp, lane mask, address, byte enable, data hash, and commit
sequence. Store mismatch localization must use this channel before falling back
to final memory dumps.
