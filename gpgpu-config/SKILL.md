---
name: gpgpu-config
description: Use when adding, editing, or reviewing GPGPU parameters, generated config, hardware-private knobs, simulator-private knobs, HW/SW ABI constants, CSR or DCR maps, memory maps, kernel ABI values, device capabilities, backend config drift, or hard-coded core/SIMT-group/thread/cache values.
---

# Config Schema Compiler Skill

## 1. Objective

Compile architecture intent and canonical GPU state into a typed, validated config IR that generates all simulator, RTL, runtime, test, debug, and PPA-facing artifacts.

## 2. Input Contract: Architecture Intent

Input must identify:

- target capability or experiment.
- canonical GPU state affected: PC/SIMT group/mask/register file, memory hierarchy, scoreboard/dependency graph, launch state, pipeline state.
- values intended to be public ABI versus private implementation.
- target backends: golden sim, RTL, runtime, memory model, PPA scripts.
- evidence constraints from references or papers.

Reject config work that starts from a number without naming the state it controls.

## 3. Mandatory Five Questions

For every config field answer:

1. What state exists? Name the GPU state field or generated artifact.
2. Who produces it? Name the config source, derived rule, generator, or capability query.
3. Who consumes it? Name RTL, simulator, runtime, kernel ABI, test, debug, or PPA consumer.
4. How does it change? Name versioning, derivation, legality, and migration rules.
5. How do we verify it? Name static checks, runtime checks, elaboration checks, or trace checks.

## 4. Output Contract: Typed Config IR

Classify every field into exactly one primary class:

| Class | Meaning | Artifact examples |
|---|---|---|
| HW-private | affects implementation only | queue depth, FU latency, cache MSHR count, register-bank count |
| ABI-visible | consumed by software or kernel code | memory map, CSR/DCR/MMIO offsets, warp size, max block size, argument alignment |
| simulator-only | model behavior or observability only | synthetic latency, oracle verbosity, timing-model mode |
| debug-only | trace, assertion, watch, timeout, counters | trace enable, watchdog cycles, checker severity |
| test-only | fixtures and reduced smoke configs | small memory size, single-warp mode, fake backend flag |
| PPA-only | experiment labeling and report binding | benchmark suite ID, activity dump path, power model name |

Public config must generate synchronized artifacts:

```text
config.json -> config.sv + config.h + simulator options + runtime capabilities + PPA config_id
```

## 5. Transformation Rules

Config is compiler IR, not a parameter list. Derive dependent values in one place:

| Source value | Derived values that must not be copied by hand |
|---|---|
| `simt_group_width` | active mask width, lane-valid bits, coalescer lane count, trace mask width, runtime capability |
| resident SIMT groups | simt_group_id width, scheduler table depth, scoreboard rows, outstanding-memory owner width |
| register counts | register address width, scoreboard bitsets, operand read ports, spill/capability limits |
| issue/FU topology | issue packet fields, writeback ports, hazard graph, perf counter groups |
| cache line/beat size | byte-mask width, coalescer segment rules, tag/index bits, memory trace schema |
| memory partitions/source IDs | outstanding table size, request tag width, response demux, monitor ranges |
| MMIO/DCR map | runtime headers, RTL decode, capability version, tests, docs |
| max grid/block/local memory | launch ABI checks, resource allocation, runtime error paths, simulator admission |

When a derived value changes, update the producer, all consumers, and the verification gate in the same patch.

## 6. Consistency Constraints

| Binding | Constraint |
|---|---|
| ISA to config | opcode features, register width, memory spaces, atomics, barriers, and mask width must match instruction semantics |
| RTL to config | generated widths, queue depths, reset values, source IDs, and optional ports must match elaborated hardware |
| runtime to config | ABI constants, memory maps, capabilities, queue limits, and launch limits must match generated headers |
| golden sim to config | oracle must read the same instruction, launch, memory, and mask parameters as RTL |
| memory path to config | cache/coalescer/MSHR/tag/address-space rules must match request/response schema |
| PPA to config | report `config_id` must reconstruct source values, derived topology, backend, workload, and feature flags |

Illegal combinations must fail before simulation or RTL elaboration.

## 7. State Evolution Rules

Config state evolves through explicit versions:

1. Add a source field with class, owner, default, legal range, and description.
2. Add derived rules and generated artifact bindings.
3. Add static validation and one negative validation case.
4. Add runtime/capability version bump when ABI-visible fields change.
5. Add migration note for stale configs or fixtures.
6. Update PPA `config_id` and report labels when measured behavior changes.

Never let debug-only or test-only values become architecture assumptions.

## 8. Verification Gate

| Gate | Must check |
|---|---|
| static check | schema required fields, type/range, power-of-two constraints, cross-field legality, derived values |
| runtime check | capability query, ABI constants, memory map, launch limits, queue limits, version compatibility |
| RTL elaboration check | generated parameter widths, interface fields, optional ports, monitors/assertions |
| simulator check | option dump, canonical trace schema, oracle config digest |
| integration check | at least one small config and one target config produce matching generated artifacts |
| PPA check | config digest/report path is preserved with counters and workload metadata |

## 9. Artifact Output

Each config change should produce or update:

- `config.json`: canonical source and derived values.
- `config.sv`: RTL parameters, typedefs, widths, assertions.
- `config.h`: runtime/kernel ABI constants and capability version.
- simulator option dump: oracle/timing mode and config digest.
- trace schema update when IDs, masks, memory, or pipeline fields change.
- validation log for static/runtime/elaboration gates.

## 10. Design Evidence Layer

Use references only as evidence:

| Evidence | Use |
|---|---|
| GPGPU-Sim | behavioral evidence for grouped runtime/core/memory/power options and compact descriptor pitfalls |
| Rocket Chip | structural reference for typed params, fragments, derived fields, legality checks, generated resources |
| Vortex/MIAOW | implementation anchors for GPU-facing ABI constants, DCR/MMIO maps, dispatch fields, test configs |
| XiangShan | tradeoff justification for large typed parameter surfaces, generated backend/cache widths, audit dumps |
| CUDA/PTX | ABI constraint for warp size, memory spaces, kernel args, synchronization, and capability reporting |

Do not add framework-pattern headings. Convert framework facts into validation constraints or evidence notes.

## 11. Failure Modes

- A public value appears in RTL and runtime but has no single generated source.
- A warp/mask/register/cache width is copied into tests or scripts after generation.
- A simulator-only timing knob silently becomes runtime-visible behavior.
- A config fragment changes topology without updating trace schema and PPA config ID.
- ABI-visible memory maps change without version/capability checks.
- Illegal parameter combinations reach RTL elaboration before failing.
