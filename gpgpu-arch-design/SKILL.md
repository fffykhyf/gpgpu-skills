---
name: gpgpu-arch-design
description: Use when planning, staging, or reviewing GPGPU architecture across ISA, SIMT execution, simulator, RTL, runtime launch, configuration, tests, counters, memory hierarchy, PPA, FPGA bring-up, or roadmap decisions.
---

# GPGPU Design Orchestrator Skill

## 1. System Objective

Compile an architecture intent into a verified GPU state-machine contract that stays consistent across config, runtime ABI, semantic oracle, RTL, memory, and PPA evidence.

## 2. Input Contract

Input is an architecture intent with objective, non-goals, target capability, affected GPU state, expected artifacts, evidence constraints, and known risk areas. If the input is only a framework name or a block diagram, first translate it into canonical GPU state.

## 3. Canonical GPU State Model

All architecture knowledge must normalize into these state owners:

| State family | Required fields |
|---|---|
| compute state | PC per SIMT group, active lane mask, predicate state, scalar/vector register file, special registers, CTA/workgroup IDs |
| memory state | address spaces, shared/global/local memory, cache line state, coalescer state, outstanding request table, memory ordering state |
| launch state | kernel image, entry PC, argument layout, grid/block dimensions, resource allocation, command queue entry, completion/fault state |
| scheduling state | resident SIMT groups, ready/waiting/done lifecycle, scoreboard, dependency graph, barrier state, replay state |
| pipeline state | fetch, decode, issue, execute, memory, writeback, retire/trace, stall and flush reasons |
| coherence state | cache ownership/validity when modeled, atomic serialization, fence/flush scope, host/device visibility |

Do not structure designs around frameworks. GPGPU-Sim, Rocket Chip, Vortex, MIAOW, XiangShan, CUDA/PTX, and papers are evidence sources that validate or challenge this canonical state model.

## 3. Mandatory Five Questions

Every orchestrated design artifact must answer:

1. What state exists?
2. Who produces it?
3. Who consumes it?
4. How does it change?
5. How do we verify it?

If any answer is missing, route the work to the narrower skill before implementation.

## 4. Transformation Rules: Design Pipeline DAG

The mandatory flow is:

```text
Arch -> Config -> Runtime(R0) -> Golden Sim -> RTL -> Memory -> Runtime(R1) -> PPA
```

| Stage | Input contract | Transformation | Output contract | Gate |
|---|---|---|---|---|
| Arch | architecture intent | normalize into canonical GPU state | state contract and invariants | five-question checklist |
| Config | state contract | derive typed config IR and generated constants | config.json/config.sv/config.h contract | static legality check |
| Runtime(R0) | config and launch intent | define ABI before backend behavior | launch ABI contract | ABI fixture test |
| Golden Sim | ISA and launch ABI | execute semantic state transitions | oracle traces | first-divergence readiness |
| RTL | oracle trace and config | implement pipeline and dependency FSMs | execution trace | RTL-vs-oracle diff |
| Memory | issue/memory contract | implement memory state machine | memory trace and response contract | hazard/order monitor |
| Runtime(R1) | backend control path | submit, fence, complete, report faults | execution backend contract | host launch smoke |
| PPA | verified variants | compile evidence into causal claims | evidence graph and feedback | baseline/variant audit |

## 5. State Evolution

Architecture state evolves only through explicit artifact handoff. Each pipeline stage consumes the previous stage's output contract, transforms named state, emits a new artifact, and records the verification gate that allows the next stage to proceed.

## 6. Contract Registry

Use these global schemas for cross-skill handoff:

| Contract | Must contain | Producer | Consumer |
|---|---|---|---|
| state contract | PC, SIMT group lifecycle, masks, register files, scoreboard/dependency graph, memory hierarchy, launch state, pipeline state | orchestrator | all skills |
| config contract | typed parameters, derived values, legality checks, ABI visibility, generated artifacts | `gpgpu-config` | runtime, sim, RTL, memory, PPA |
| launch contract | kernel image, entry PC, args, grid/block shape, resource limits, memory spaces, synchronization | `gpgpu-runtime` R0 | golden sim, RTL, runtime R1 |
| instruction contract | opcode semantics, operands, mask behavior, side effects, illegal cases, trace fields | `gpgpu-golden-sim` | RTL, memory, PPA |
| memory contract | op, address space, lane mask, byte mask, data, tag/source, ordering, response, fault | `gpgpu-memory-path` | RTL, golden sim, runtime |
| trace contract | identity, cycle/step, PC, mask, instruction, register effects, memory effects, stall/fault state | golden sim/RTL/memory | PPA, debug |
| evidence contract | baseline, variant, workload, config digest, metrics, counters, causal attribution | `gpgpu-ppa-evaluation` | architecture feedback |

## 7. Cross-Skill Handoff Rules

| From | To | Required artifact |
|---|---|---|
| orchestrator | config | canonical state model plus visible/private boundary |
| config | runtime R0 | ABI-visible constants, memory map, capability schema |
| config | golden sim and RTL | generated widths, limits, feature flags, trace field schema |
| runtime R0 | golden sim | launch ABI fixture with kernel descriptor and argument bytes |
| golden sim | RTL | instruction, warp, register, memory, and divergence traces |
| RTL | memory | issue packet and memory request/response contract |
| memory | runtime R1 | fence, completion, fault, and visibility semantics |
| runtime R1 | PPA | command timeline, launch latency, completion status, workload metadata |
| PPA | orchestrator/config/RTL/memory/runtime | evidence graph and controlled feedback target |

No skill may consume an implicit contract. If a value or state crosses a boundary, it must appear in the relevant artifact.

## 8. Failure Routing Table

| Failure signal | Route to | Required first check |
|---|---|---|
| ISA or instruction side effect mismatch | `gpgpu-golden-sim` | compare instruction semantic contract and oracle trace |
| PC, active mask, scoreboard, or hazard bug | `gpgpu-rtl-simt-core` | inspect SIMT lifecycle and dependency graph transition |
| memory ordering, coalescing, tag, cache, or fence bug | `gpgpu-memory-path` | inspect memory request/response trace and outstanding table |
| launch, argument, queue, event, or completion bug | `gpgpu-runtime` | split R0 ABI bug from R1 backend execution bug |
| parameter drift or generated width mismatch | `gpgpu-config` | inspect source-of-truth and derived config rules |
| performance claim lacks causal evidence | `gpgpu-ppa-evaluation` | inspect baseline, variant, workload, counters, and attribution |

## 9. Design Invariants

Every GPU design must preserve:

- no deadlocked resident SIMT group unless the kernel intentionally waits on an unsatisfied program condition.
- no illegal memory hazard: every request has valid mask, address space, tag/source lifetime, ordering scope, and response owner.
- scoreboard correctness: dependencies are set before issue, released only by the owning completion, and flushed on kill/reset.
- launch determinism: the same kernel image, config, args, input memory, and launch shape produce the same architectural trace.
- traceability: every committed register or memory side effect can be tied to launch ID, compute core/CU, SIMT group, PC, active mask, and instruction.

## 10. Design Evidence Layer

Evidence validates contracts; it does not define the document structure.

| Evidence type | Source examples | Allowed use |
|---|---|---|
| behavioral evidence | GPGPU-Sim, Accel-Sim, CUDA/PTX traces | validate semantics, launch flow, timing hypotheses, trace fields |
| structural reference | Rocket Chip, Vortex, MIAOW, XiangShan | justify generator discipline, ownership boundaries, monitors, counters, handshakes |
| ISA/ABI constraint | CUDA, PTX, OpenCL, local kernel ABI | constrain image format, argument layout, memory spaces, synchronization |
| empirical justification | papers, benchmark reports, synthesis/PPA reports | justify tradeoffs only after baseline/variant controls are stated |
| implementation anchor | local modules, planned files, tests, traces | bind a claim to code that can be changed or verified |

Use local reference files in this directory only as evidence appendices:
`gpgpusim_local.md`, `rocket_local.md`, `vortex_local.md`, `miao_local.md`, and `xiangshan_local.md`.

## 11. Output Contract

An orchestrated design output must include:

- one-sentence objective and non-goals.
- canonical GPU state table.
- producer/consumer table for each state field.
- transformation rules across the design pipeline DAG.
- generated artifacts expected from each skill.
- verification gates and first failure route.
- evidence layer with source, claim, and limitation.

## 12. Verification Gate

Before an architecture proposal leaves the orchestrator, verify that it has the six contract skeleton sections, the five mandatory questions, the canonical state mapping, a pipeline DAG handoff, a failure route, and an evidence layer whose sources validate contracts rather than define the structure.

## 13. Failure Modes

- Framework chapters replace the canonical state model.
- Runtime launch is treated as a script instead of ABI state.
- Config values are copied instead of derived and generated.
- Simulator traces compare final output only, hiding first divergence.
- RTL owns PC, mask, dependency, and memory state in one untestable block.
- Memory requests drop SIMT group, lane mask, destination, or tag identity.
- PPA claims change multiple variables without a controlled diff.
