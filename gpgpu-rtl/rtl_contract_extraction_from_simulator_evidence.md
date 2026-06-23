# RTL Contract Extraction From Simulator Evidence

Rewrite simulator mechanisms into hardware contracts before binding RTL.

Can become RTL contracts:

- scoreboard pending register bitset;
- SIMT PC, active mask, and reconvergence state;
- issue gate;
- memory request interface;
- coalescer output interface;
- packet interface;
- cache status output;
- counter tap points.

Must not become RTL directly:

- C++ queue/container implementation;
- `std::set` scoreboard;
- BookSim config;
- AccelWattch object model;
- CUDA stream stack;
- fixed simulator latency;
- SM86 queue depth;
- PTX opcode latency table.

