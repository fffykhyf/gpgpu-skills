# Rocket Repository Map Summary

Raw report: `raw/rocket_repo_map_for_gpgpu.md`

Rocket Chip is useful because it is a parameterized SoC generator, not because it
contains a scalar CPU implementation. The transferable packages are `subsystem`,
`system`, `diplomacy`, `tilelink`, `amba`, `devices`, `regmapper`, `trace`,
`unittest`, and `groundtest`.

Transferable rules:
- Put topology, MMIO address ownership, debug/control planes, and generated
  collateral under one subsystem composition root.
- Declare protocol capabilities before RTL binding and derive concrete widths,
  IDs, masks, and monitors from negotiated edges.
- Generate memory maps, resolved config, interface maps, launch ABI collateral,
  test harnesses, and trace schemas beside RTL.
- Keep SM/cluster wrappers as system integration surfaces, not raw execution
  pipelines.

Do not transfer:
- Rocket scalar pipeline staging, frontend speculation, or CPU decode/control.
- CLINT/PLIC/debug register layouts as fixed GPGPU ABI.
- TileLink as mandatory transport.
- CPU privilege semantics or Rocket coherence assumptions as GPU truth.
