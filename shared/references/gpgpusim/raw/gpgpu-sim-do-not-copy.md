# GPGPU-Sim Do Not Copy

Source repo: `ref_submodule/gpgpu-sim`

This file lists boundaries that future agents must preserve.

## Do Not Copy Into RTL

- C++ queue/container implementations from `shader.cc`, `gpu-cache.cc`, `l2cache.cc`, `dram.cc`.
- Fixed latency values such as `-gpgpu_kernel_launch_latency`, `-gpgpu_TB_launch_latency`, `-gpgpu_l1_latency`, `-gpgpu_smem_latency`, `-gpgpu_l2_rop_latency`, `-dram_latency`, and PTX opcode latencies.
- SM86 queue depths such as `-gpgpu_dram_partition_queues`, ICNT buffer sizes, DRAM queue sizes, and response FIFO sizes as default RTL sizes.
- `stream_manager` policy, CUDA stream-zero priority, and CUDA launch stack implementation.
- `mem_fetch_status` enum names as RTL state names without redesign.
- LocalInterconnect one-flit simplification unless intentionally chosen and specified.
- BookSim `.icnt` topology/routing/VC allocator knobs as fabric truth.
- McPAT/AccelWattch object hierarchy or XML coefficients.
- AerialVision parser implementation or parser-only metric list.

## Do Not Copy Into ISA / ABI

- NVIDIA PTX semantics as simple-gpgpu ISA truth.
- SASS/Accel-Sim trace behavior as simple-gpgpu ABI.
- CUDA compute capability fields as native capability fields unless an explicit compatibility profile exists.
- CUDA stack/heap/sync/pending-launch semantics unless simple-gpgpu runtime chooses CUDA-like behavior.
- texture/constant cache behavior as mandatory ABI if the project ISA does not expose those spaces.
- LDGSTS/DEPBAR/CDP details unless the ISA explicitly supports them.

## Do Not Copy Into Performance Model Without Caveat

- SM86 tested config values as general defaults.
- `-gpgpu_coalesce_arch 86` exact coalescing rules as universal memory rules.
- `-gpgpu_perfect_inst_const_cache` as a real cache design.
- `-gpgpu_simple_dram_model` as equivalent to detailed DRAM model.
- `gpgpu_runtime_stat` value without parsing its sample-frequency/flag behavior.
- visualizer names without producer audit.
- defined-but-not-proven-live stall reasons as stable counters.

## What Can Be Copied As Method

- classify every parameter before exposing it.
- separate functional semantics from timing attribution.
- define issue/non-issue reasons.
- model scoreboard reserve/check/release.
- keep SIMT stack state explicit.
- normalize memory request formation before cache/DRAM analysis.
- report memory bottlenecks by queue boundary.
- distinguish cache miss from reservation fail.
- keep NoC packet class and size in the interface.
- report DRAM row locality, queue latency, and bank/chip skew.
- treat power as derived from activity counters.
- require producer-backed counter schema.

## Required Warning Text For Future Reader Agents

Use this warning when summarizing any GPGPU-Sim mechanism:

> This mechanism is simulator evidence. Before updating a simple-gpgpu skill, classify its state, config, and counters. Do not transfer fixed latency, queue depth, CUDA/PTX/SASS behavior, or AccelWattch coefficients into RTL or ISA/ABI without an explicit project contract.

## Legal / Provenance Caution

The top-level repo uses a permissive license, but individual AerialVision files include third-party derivation and non-commercial notices. Future agents should summarize methodology and cite paths; do not copy AerialVision source logic verbatim into project code.
