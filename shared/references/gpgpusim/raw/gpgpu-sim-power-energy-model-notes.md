# GPGPU-Sim Power / Energy Model Notes

Source repo: `ref_submodule/gpgpu-sim`

Primary files:

- `src/gpgpu-sim/power_interface.{h,cc}`
- `src/gpgpu-sim/power_stat.{h,cc}`
- `src/accelwattch/gpgpu_sim_wrapper.{h,cc}`
- `src/accelwattch/XML_Parse.*`
- `src/accelwattch/README`
- `configs/tested-cfgs/SM86_RTX3070/gpgpusim.config`

## Model Boundary

AccelWattch in this repo is a counter-to-power model. It is not an independent hardware measurement and not RTL.

Observed controls:

- `-power_simulation_enabled`
- `-accelwattch_xml_file`
- `-hw_perf_file_name`
- `-power_simulation_mode`
- hybrid per-counter selectors such as `-accelwattch_hybrid_perfsim_*`

SM86 config sets power disabled and comments that a real energy model is still needed.

## Counter Sources

`power_interface.cc` consumes `power_stat_t` and calls wrapper setters for:

- total instructions;
- integer/floating/double/SFU/tensor/texture access counts;
- committed instructions;
- register file reads/writes and non-register operands;
- instruction cache hits/misses;
- constant cache and texture cache accesses;
- shared-memory accesses;
- L1D read/write hits/misses;
- L2 read/write hits/misses;
- active SMs;
- average pipeline duty cycle;
- DRAM read/write/precharge;
- active threads and active lanes;
- ICNT flits from SIMT to memory and memory to SIMT.

## AccelWattch Wrapper

`gpgpu_sim_wrapper` maps counters into:

- McPAT-style `p->sys.*` fields;
- `sample_perf_counters[]`;
- component power buckets.

Important caveats:

- XML scaling coefficients are calibration data, not design truth.
- hybrid mode can substitute hardware CSV counters for simulated counters.
- homogeneous aggregation assumptions from McPAT/AccelWattch are methodology, not RTL evidence.

## Component Buckets

Reader agent identified component buckets in `gpgpu_sim_wrapper.cc:update_components_power`, including:

- instruction buffer / pipeline style buckets;
- register file;
- execution units;
- cache components;
- NoC;
- DRAM/memory controller;
- static power.

Use these as energy-report categories, not RTL module boundaries.

## What To Copy Into Skills

Good:

- define energy estimation as a derived report from named activity counters;
- require counter provenance: simulator, hardware, or hybrid;
- require per-window sampling frequency and aggregation mode;
- keep power attribution aligned with performance bottlenecks;
- document model coefficients and source file.

Do not copy:

- XML coefficients;
- McPAT object hierarchy as RTL module hierarchy;
- `constant_power` or regression terms as hardware truth;
- power numbers from disabled configs as evidence;
- hybrid CSV substitution as simulator validation unless separately checked.

## Design Rule

Rule name: power is derivative of activity

Problem solved: prevents energy estimates from being treated as primary evidence.

Required state contract:

- activity counters per component per sampling window.

Required config contract:

- model mode: `sim`, `hw`, or `hybrid`;
- XML/config provenance;
- sampling frequency;
- aggregation policy.

Required counter/stall reason:

- every power bucket must list the performance counters it consumes.

Applicable skill:

- `gpgpu-simppa`
- `gpgpu-loop`
- `gpgpu-rtl` only for counter tap placement, not for power model internals.

Implementation anchor:

- `src/gpgpu-sim/power_interface.cc:mcpat_cycle`
- `src/gpgpu-sim/power_interface.cc:calculate_hw_mcpat`
- `src/accelwattch/gpgpu_sim_wrapper.cc`
