# Observable Trace Contract

RTL trace must expose, when implemented:

- cycle;
- core id;
- warp id;
- PC;
- active mask;
- issue valid;
- non-issue reason;
- scoreboard collision;
- selected pipe;
- memory transaction count;
- cache status;
- ICNT status;
- L2 queue status;
- DRAM queue status;
- writeback release.

These fields feed `gpgpu-simppa`; they are not optional for performance claims.

