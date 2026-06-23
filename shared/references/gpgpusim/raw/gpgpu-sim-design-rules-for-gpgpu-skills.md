# GPGPU-Sim Design Rules For GPGPU Skills

Source repo: `ref_submodule/gpgpu-sim`

These rules are extracted from reader-agent evidence. They are not direct implementation patches.

## Design Rules

### Rule 1: Classify Before Copying

- Problem solved: avoids copying simulator-only artifacts.
- Required config contract: every parameter is `hardware-private`, `simulator-private`, `HW/SW ABI`, `test-only`, or `debug-only`.
- Applicable skill: `gpgpu-arch`, `gpgpu-memory`, `gpgpu-interconnect`, `gpgpu-simppa`.
- Implementation anchor: `src/gpgpusim_entrypoint.cc`, `src/gpgpu-sim/gpu-sim.cc`, SM86 config.

### Rule 2: Separate Functional Semantics From Timing

- Problem solved: timing stalls should not define correctness.
- Required state contract: functional instruction effects and timing issue/memory events are separate.
- Applicable skill: `gpgpu-golden`, `gpgpu-runtime`, `gpgpu-rtl`.
- Implementation anchor: `src/stream_manager.cc`, `src/cuda-sim/*`, `src/gpgpu-sim/*`.

### Rule 3: Issue Must Explain Non-Issue

- Problem solved: low IPC reports need actionable causes.
- Required counter/stall reason: control/ibuffer, scoreboard, pipe unavailable, barrier/membar/atomic wait, memory backpressure.
- Applicable skill: `gpgpu-arch`, `gpgpu-simppa`, `gpgpu-rtl`.
- Implementation anchor: `src/gpgpu-sim/shader.cc:scheduler_unit::cycle`.

### Rule 4: Scoreboard And SIMT Are Separate Contracts

- Problem solved: data hazards and control divergence need independent state.
- Required state contract: SIMT PC/active mask/reconvergence; scoreboard pending destinations/long ops.
- Applicable skill: `gpgpu-arch`, `gpgpu-rtl`, `gpgpu-golden`.
- Implementation anchor: `src/abstract_hardware_model.h:simt_stack`, `scoreboard.cc`.

### Rule 5: Memory Request Formation Is A First-Class Boundary

- Problem solved: cache/DRAM cannot be analyzed before coalescing is known.
- Required state contract: per-lane addresses, active mask, byte mask, sector mask, transaction list.
- Applicable skill: `gpgpu-memory`, `gpgpu-runtime`, `gpgpu-rtl`.
- Implementation anchor: `src/abstract_hardware_model.cc:warp_inst_t::generate_mem_accesses`.

### Rule 6: Memory Stalls Are Layered

- Problem solved: avoids blaming all memory stalls on DRAM.
- Required attribution method: classify formation, shared/L1 bank, cache, MSHR, ICNT, L2, DRAM, return path, scoreboard release.
- Applicable skill: `gpgpu-memory`, `gpgpu-interconnect`, `gpgpu-simppa`.
- Implementation anchor: `stats.h`, `shader.cc`, `gpu-cache.cc`, `l2cache.cc`, `dram.cc`.

### Rule 7: Cache Miss And Reservation Failure Are Different

- Problem solved: distinguishes locality problems from structural queue/MSHR pressure.
- Required counter: `cache_request_status` plus fail reason.
- Applicable skill: `gpgpu-memory`, `gpgpu-simppa`.
- Implementation anchor: `src/gpgpu-sim/gpu-cache.h`.

### Rule 8: NoC Contract Must Preserve Packet Class And Size

- Problem solved: local xbar and BookSim paths differ materially.
- Required state contract: source, destination, request/reply class, size/flits, buffer availability.
- Applicable skill: `gpgpu-interconnect`.
- Implementation anchor: `src/gpgpu-sim/icnt_wrapper.*`, `local_interconnect.*`, `src/intersim2/*`.

### Rule 9: DRAM Tuning Requires Address Mapping Evidence

- Problem solved: row locality and bank skew can dominate before raw timing.
- Required counter/stall reason: row locality, bank/chip skew, queue latency, utilization, efficiency.
- Applicable skill: `gpgpu-memory`, `gpgpu-simppa`.
- Implementation anchor: `addrdec.cc`, `dram.cc`, `dram_sched.cc`, `mem_latency_stat.cc`.

### Rule 10: Synchronization Is Not Just A Stall

- Problem solved: atomics/fence/barrier semantics need separate correctness and timing contracts.
- Required state contract: atomic completion, fence scope, barrier arrival/release.
- Applicable skill: `gpgpu-golden`, `gpgpu-memory`, `gpgpu-rtl`.
- Implementation anchor: `shader.cc`, `mem_fetch.cc`, future read `cuda-sim/memory.cc`.

### Rule 11: Visualization Variables Need Producer Audit

- Problem solved: AerialVision parser declares names that may not be produced.
- Required counter contract: producer-backed / parser-only / defined-only classification.
- Applicable skill: `gpgpu-simppa`.
- Implementation anchor: `visualizer.cc`, `shader.cc`, `l2cache.cc`, `dram.cc`, `aerialvision/lexyacc.py`.

### Rule 12: Power Is Derivative Of Activity

- Problem solved: prevents power estimates from becoming independent evidence.
- Required counter contract: every power bucket lists consumed activity counters and source mode.
- Applicable skill: `gpgpu-simppa`, `gpgpu-loop`.
- Implementation anchor: `power_interface.cc`, `power_stat.h`, `accelwattch/*`.

### Rule 13: Tested Configs Are Profiles, Not Defaults

- Problem solved: avoids copying RTX3070-like values into simple-gpgpu.
- Required config contract: provenance, category, legal range if known, exposure policy.
- Applicable skill: all architecture and implementation skills.
- Implementation anchor: `configs/tested-cfgs/*`.

### Rule 14: Regression Must Gate Counters, Not Only Functional Pass

- Problem solved: performance work can regress attribution even if outputs are correct.
- Required test gate: functional result, cycle/perf counters, memory stall taxonomy, config snapshot.
- Applicable skill: `gpgpu-loop`, `gpgpu-simppa`, `gpgpu-golden`.
- Implementation anchor: `short-tests*.sh`, `.github/workflows/*`.

### Rule 15: NVIDIA-Specific Behavior Requires Optional Profile

- Problem solved: prevents CUDA/PTX/SASS behavior from silently becoming simple-gpgpu ABI.
- Required config contract: optional compatibility profile.
- Applicable skill: `gpgpu-runtime`, `gpgpu-golden`, `gpgpu-rtl`.
- Implementation anchor: `libcuda/*`, `libopencl/*`, `src/cuda-sim/*`.
