# Coalescer Input Trace Generation

Runtime/toolchain output must generate enough memory-bundle information for
coalescer input traces:

- instruction id;
- warp id when known;
- access type;
- memory space;
- lane address expression or vector;
- active mask;
- byte enables;
- ordering scope;
- coalescing policy reference.

This trace is input to memory formation, not a cache or DRAM timing result.

