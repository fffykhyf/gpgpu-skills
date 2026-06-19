# XiangShan Local Reference For GPGPU Config

This note expands the XiangShan references that matter for the `gpgpu-config` skill. It focuses on named configs, typed core parameters, derived backend/cache/memory widths, legality checks, generated topology dumps, and config drift prevention.

Terminology note: XiangShan uses CPU terms such as hart, frontend, backend, ROB, CSR, and LSQ. Use those names only when reading the source. In local GPGPU configuration, translate them to compute core/CU, SIMT group, active lane mask, CTA/workgroup, runtime ABI, and memory hierarchy contracts.

## What XiangShan Teaches For This Skill

XiangShan's config surface is large, but it stays usable because values are grouped, derived, checked, and printed. The main local rule is: do not add a knob until its class, owner, derived values, illegal combinations, and public visibility are known.

Use XiangShan to strengthen these config habits:

- named configs for reproducible target/minimal experiments;
- typed parameter objects instead of loose constants;
- derived widths and port counts near the owner;
- config-time checks before generation;
- readable dumps for generated topology;
- synchronization between config, RTL, simulator, runtime, tests, and PPA labels.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/xiangshan.md` | Configuration lessons and seven-skill mapping. |
| `ref_submodule/xiangshan/src/main/scala/top/Configs.scala` | `BaseConfig`, `MinimalConfig`, frontend/backend/cache/TLB/L2 parameter composition. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/Parameters.scala` | `XSCoreParameters` and typed feature/width/queue/memory params. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/BackendParams.scala` | Derived execution-unit counts, issue/read/writeback ports, wakeup configs. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/Backend.scala` | `params.configChecks`, config prints, writeback-port consistency checks. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/dcache/DCacheWrapper.scala` | `DCacheParameters`, derived source/index/tag/ECC/MSHR fields, `require` checks. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/PMParameters.scala` | Perf/HPM configuration surface. |
| `ref/xiangshan.pdf` | Backend, memory, HPM chapters that describe what the parameters control. |

## Named Configs

`top/Configs.scala` defines named configurations rather than anonymous constant edits. `BaseConfig` sets SoC/tile/debug/perf foundations. `MinimalConfig` composes smaller fragments and overrides frontend, backend, memory, DCache, TLB, and L2 parameters.

For local GPGPU work:

- keep `small`, `target`, `experiment`, and `ppa` configs named;
- do not change a default config to run one experiment;
- record the config name or digest in trace and PPA output;
- keep target and smoke configs both valid.

## Typed Core Parameters

`XSCoreParameters` groups:

- ISA and features: XLEN, VLEN, ELEN, FPU, VPU, M extension, H extension, Sv48, CMO, custom CSR/cache ops;
- widths: decode, rename, commit, ROB/RAB commit;
- queues: ROB, RAB, virtual load queue, RAR/RAW/replay queues, store queue, store buffer, issue queues;
- register resources: integer, FP, vector, and special physical register counts;
- memory widths: load/store pipelines, vector load/store pipelines, uncache buffers, prefetch controls;
- TLB, DCache, L2, and prefetcher parameters.

For GPGPU, keep equivalent groups for:

- SIMT group width, physical SIMD width, active mask width;
- resident SIMT groups and CTA/workgroup limits;
- register files, shared memory, barriers, scoreboard entries;
- LSU/coalescer/cache/MSHR/source ID widths;
- runtime-visible ABI constants and capability fields.

## Derived Backend Parameters

`BackendParams.scala` derives FU counts, issue queues, read ports, writeback ports, memory execution units, dispatch widths, wakeup configs, and data-config groupings from configured execution units. `Backend.scala` prints configs and uses `require` to ensure writeback-port configs cover FU writeback requirements.

Local rule:

- never hand-count issue/writeback/operand ports in several files;
- derive them from the execution-unit config;
- fail early if a configured unit cannot issue, read operands, write back, wake dependents, or emit trace/perf events.

## Cache, TLB, And Source IDs

`DCacheWrapper.scala` derives alias bits, source types, request ID widths, MSHR/release/probe/MMIO entry counts, bank/tag/mask fields, ECC widths, uncache IDs, and prefetch source ranges from `DCacheParameters`. It also uses `require` checks for entry counts and SRAM row bits.

For a GPGPU memory hierarchy:

- source/tag width must derive from outstanding requests, coalescer groups, MSHRs, and response queues;
- cacheline, bank, set, way, and mask fields must derive from one source;
- TLB/MMU/prefetch/uncache/MMIO options must have legality checks;
- runtime capability output must change if software can observe the value.

## Config Checklist To Borrow

Before merging a config change, ensure:

- parameter class is known: hardware-private, simulator-private, HW/SW ABI, test-only, or debug-only;
- source value and derived values have one owner;
- illegal combinations fail before generation;
- all consumers are listed: RTL, simulator, runtime, kernel ABI, tests, PPA scripts;
- generated topology can be printed or dumped;
- small and target configs both run through at least a structural validation.

## Caveats

- Do not copy XiangShan CPU feature flags as GPGPU feature flags.
- Do not treat ROB/rename sizes as local SIMT configuration unless the local design explicitly has such structures.
- Do not expose CPU CSR/privileged constants as GPU runtime ABI.
- Do not copy DCache coherence policy without defining the GPGPU memory model.
