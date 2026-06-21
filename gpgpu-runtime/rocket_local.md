# Rocket Chip Local Reference For GPGPU Runtime

This note expands the Rocket Chip references that matter for the `gpgpu-runtime` skill. It focuses on RoCC command/response/memory/busy/interrupt patterns, BootROM/reset/debug/resource exposure, ExampleRocketSystem/TestHarness wiring, register/resource maps, and the boundary between debug bring-up and public runtime ABI.

Terminology note: Rocket Chip runtime-facing mechanisms are RISC-V SoC mechanisms, not CUDA/OpenCL/HIP runtime semantics. Preserve names such as BootROM, reset vector, debug module, DMI, JTAG, RoCC, TileLink, and DTS when discussing Rocket. Translate the pattern to GPGPU kernel descriptor, command queue, doorbell, completion, fault, capability, trace, and perf state.

## What Rocket Chip Teaches For This Skill

Rocket's runtime value is control-plane discipline:

- reset and boot resources are explicit;
- debug transport is a first-class SoC interface;
- resources/capabilities are described for software;
- accelerators use command/response/memory/busy/interrupt contracts;
- test harnesses connect public-facing memory/debug/success concepts.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/rocket.md` | Runtime lessons and seven-skill mapping. |
| `ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala` | RoCC instruction, command, response, memory/PTW, busy, interrupt, command router, response arbiter. |
| `ref_submodule/rocket-chip/src/main/scala/system/ExampleRocketSystem.scala` | BootROM, MaskROM, interrupts, AXI memory/MMIO/slave ports. |
| `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala` | Simulation memory, debug, success, serial, and harness connections. |
| `ref_submodule/rocket-chip/src/main/scala/devices/debug/` | Debug module, DMI, JTAG, SBA, debug transport. |
| `ref_submodule/rocket-chip/src/main/scala/resources/` | Device tree, JSON, resource binding, address maps. |
| `ref_submodule/rocket-chip/src/main/scala/regmapper/` | Register field descriptions and memory-mapped register routing. |
| `ref_submodule/rocket-chip/bootrom/` | Boot code and reset-visible resources. |

## RoCC Control-Plane Pattern

`LazyRoCC.scala` defines:

- `RoCCInstruction` fields: opcode, funct, rs1, rs2, rd, xd/xs1/xs2;
- `RoCCCommand` and `RoCCResponse`;
- `RoCCCoreIO`: cmd, resp, mem, busy, interrupt, exception, CSR;
- PTW, FPU response, TileLink client nodes;
- command routing and response arbitration.

For local GPGPU runtime, use the same discipline for:

- command queue entries;
- kernel entry and argument pointer;
- grid/block/CTA/workgroup dimensions;
- resource limits and admission;
- memory access/translation path;
- busy/completion/fault/interrupt/status.

## Resource And Debug Pattern

Rocket exposes BootROM/reset, debug module, DMI/JTAG/SBA, device resources, and test harness wiring. Local GPGPU runtime should:

- separate public launch ABI from debug/test hooks;
- describe MMIO/register fields with reset values and side effects;
- expose version/capability/query data;
- define trace/perf snapshot access;
- ensure simulator and RTL tests use the same public-facing launch concepts.

## TestHarness Lesson

`TestHarness.scala` wires memory, debug, serial, and success signals around the generated system. Local GPGPU tests should have:

- one public launch path;
- deterministic memory setup;
- completion/fault/timeout;
- optional debug/trace/perf enable;
- backend-specific transport hidden behind a stable runtime API.

## Caveats

- Rocket BootROM and RISC-V reset flow are not GPU kernel launch ABI.
- RoCC is not a CUDA/OpenCL runtime.
- Device tree/resource binding is a capability pattern, not a complete GPU driver model.
- Use Vortex/GPGPU-Sim/project runtime rules for actual kernel launch semantics.
