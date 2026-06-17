# Vortex Local Reference For GPGPU Runtime

This note expands the Vortex references that matter for the `gpgpu-runtime`
skill. It focuses on public runtime handles, command submission, module/kernel
loading, kernel entry ABI, command processor control, CTA/KMU dispatch, and
host/device synchronization.

## What Vortex Teaches For This Skill

Vortex separates the user-facing runtime from backend transport and from RTL
internals. The public API talks in device, buffer, queue, event, module, and
kernel handles. The backend owns MMIO/DMA/platform details. The command
processor and KMU turn queue commands into DCR writes, DMA movement, launch,
completion, events, fences, and cache maintenance.

For this project, copy the contract:

- a kernel launch is a state machine, not a testbench poke;
- kernel entry PC and argument pointer are ABI;
- grid/block/CTA dimensions are visible to both runtime and core;
- completion, fence, event, and cache flush must have explicit ordering;
- public runtime headers should not expose private RTL internals.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/vortex.md` | Local extraction of runtime/launch lessons. |
| `ref_submodule/vortex/docs/designs/vortex_runtime_api.md` | Public async runtime API shape: device, buffer, queue, event, module, kernel. |
| `ref_submodule/vortex/docs/designs/command_processor_control_plane.md` | Command rings, doorbells, queue completion, DMA, DCR, launch, fence, event, cache flush. |
| `ref_submodule/vortex/docs/designs/kernel_entry_and_dispatch.md` | Kernel entry PC, multi-entry `.vxbin`, `VXSYMTAB`, argument handoff, startup ABI. |
| `ref_submodule/vortex/docs/designs/cta_clustering_and_dispatch.md` | KMU grid walk, CTA dispatch, cluster dimensions, and CTA-visible state. |
| `ref_submodule/vortex/docs/testing.md` | Runtime-facing tests across simx and rtlsim. |

## Public Runtime Surface

The Vortex runtime headers live under:

- `ref_submodule/vortex/sw/runtime/include/vortex2.h`
- `ref_submodule/vortex/sw/runtime/include/vortex.h`

The important API categories are:

- device handles: open/close, query capabilities, backend state;
- buffer handles: allocate/reserve, map or copy, access permissions, release;
- queue handles: ordered submission and asynchronous completion;
- event handles: completion markers and synchronization;
- module handles: loaded `.vxbin` device image and symbol table;
- kernel handles: resolved kernel entry PC within a module;
- launch arguments: raw argument blob or staged argument buffer;
- synchronization: wait, fence, cache flush, callback/event semantics.

For a smaller runtime, keep the same public/private split. A minimal public API
can be tiny, but it should not require callers to know internal RTL signal names
or CP implementation details.

## Device And Command Processor Runtime

`ref_submodule/vortex/sw/runtime/common/device.cpp` is the common runtime owner
for device-level state and command processor interaction.

Important behavior:

- CP initialization allocates command-ring storage, queue head/completion state,
  and programs command processor registers.
- Device capabilities are read through CP-visible capability words and decoded
  by shared helpers. Runtime-visible capabilities are not guessed from random
  local build flags.
- `cp_submit_cl` writes command-list entries into a ring, uses a release fence
  before the doorbell, rings the CP doorbell, and polls completion sequence
  state such as `Q_SEQNUM`.
- Device write/read paths can route through CP DMA on CP-only-DMA backends, so
  runtime code should not assume direct host access to device memory.

The local lesson is that command submission needs an explicit producer/consumer
protocol: ring space, entry write, ordering fence, doorbell, completion, error
or timeout.

## Queue Launch Path

`ref_submodule/vortex/sw/runtime/common/queue.cpp` is the practical launch path
reference.

The key operation is kernel launch enqueue:

- validate device, queue, kernel, dimensions, and argument inputs;
- retain the kernel/module while the queued work owns it;
- copy or stage the raw argument blob;
- normalize grid, block, and cluster dimensions;
- query device capabilities such as threads, warps, cores, local memory, and
  feature limits;
- compute derived launch parameters such as block size and warp stepping;
- write launch DCRs for startup address, kernel entry, startup argument,
  block/grid dimensions, local memory size, block size, warp steps, and cluster
  dimensions;
- submit the command list through the queue/CP path;
- release staged resources after completion or failure.

For local runtime work, do not skip the DCR/launch record even if the first
backend is a simulator. That record is what lets sim and RTL share the same
conceptual launch ABI.

## Module And Kernel Loading

`ref_submodule/vortex/sw/runtime/common/module.cpp` describes the `.vxbin`
module format and kernel resolution.

`.vxbin` layout:

- 8-byte little-endian `min_vma`;
- 8-byte little-endian `max_vma`;
- binary payload;
- optional symbol-table footer:
  - concatenated string blob;
  - entries of `{ name_off, name_len, pad, pc }`;
  - `n_symbols`;
  - magic bytes `VXSYMTAB`.

`Module::load_bytes()`:

- validates the header and VMA range;
- detects and parses the optional `VXSYMTAB` footer from the end of the file;
- reserves the image VMA range as a device buffer;
- marks code/data read-only and BSS read-write;
- uploads the binary payload with `dev_write`;
- zeroes the BSS region;
- exposes footer entries as named kernel symbols;
- falls back to a single `main` entry at `min_vma` when no footer exists;
- also exposes `main` for single-entry footer images when useful for legacy
  tests.

`Kernel` caches the resolved PC and holds a reference to the module. It can also
query max block size from device capabilities. The key local lesson: kernel
entry resolution is runtime state, not a compile-time constant in a testbench.

## Kernel Binary Tooling

`ref_submodule/vortex/sw/kernel/scripts/vxbin.py` creates `.vxbin` files from
ELF images.

It:

- uses `readelf -l` to find the minimum and maximum loadable VMA;
- reads `_edata` and `_end` to include initialized data and BSS extent;
- uses `objcopy -O binary` to extract the loadable binary payload;
- pads payload to `_edata` so the runtime can distinguish binary data from BSS;
- writes `min_vma`, `max_vma`, payload, and optional `VXSYMTAB`;
- finds kernel entry stubs named `__vx_kentry_<kernel>`;
- maps `kernel_main` to public name `main`;
- writes each footer entry as name offset/length and PC.

If this project introduces multi-kernel modules, use the same idea: a module
format that lets the runtime resolve named kernel entry PCs without hard-coded
host knowledge.

## Kernel Startup ABI

`ref_submodule/vortex/sw/kernel/src/vx_start.S` is the kernel entry ABI
reference.

Under KMU-enabled launch:

- `_start` aliases `__vx_cta_entry`;
- the KMU launches every CTA/warp at a startup address;
- `__vx_cta_entry` configures SATP when VM is enabled;
- it initializes `gp`, stack pointer, optional TLS, and global constructors;
- it reads the selected kernel entry PC from `VX_CSR_CTA_ENTRY`;
- it reads the kernel-argument pointer from `VX_CSR_MSCRATCH`;
- it calls the selected kernel through `jalr`;
- it drains pending work with `wsync`;
- it shuts down the warp with `tmc x0`;
- reused CTA warps re-enter a fixed per-CTA dispatch window that reloads entry
  and args.

For a local runtime, the minimum kernel ABI is:

- where the kernel starts;
- how args reach the kernel;
- how stack/TLS/global init is handled or intentionally omitted;
- how a warp/thread terminates;
- which CSRs or equivalent state expose CTA IDs and dimensions.

## Command Processor RTL

The command processor RTL is under `ref_submodule/vortex/hw/rtl/cp/`.

Useful files:

- `VX_cp_pkg.sv`: command opcodes, command structures, queue state, register
  offsets, and shared CP types.
- `VX_cp_core.sv`: CP regfile, command fetch, command execution engines,
  arbiters, host/device AXI interactions, GPU interface, queue progress, and
  completion signaling.

The command processor design document explains the command classes:

- register/DCR writes;
- DMA transfers;
- kernel launch;
- fence/wait;
- event operations;
- cache flush;
- queue completion and doorbell.

Do not require a full Vortex CP for an early local project, but keep the same
logical roles. A tiny runtime can submit a single launch command directly, but
it still needs start, completion, error, and ordering semantics.

## KMU And CTA Dispatch

Launch commands eventually reach:

- `ref_submodule/vortex/hw/rtl/VX_kmu.sv`
- `ref_submodule/vortex/hw/rtl/core/VX_cta_dispatch.sv`

The KMU holds DCR-programmed launch state:

- startup address;
- kernel entry address;
- argument pointer;
- block dimensions;
- grid dimensions;
- local memory size;
- block size;
- warp stepping in X/Y/Z;
- cluster dimensions.

CTA dispatch maps grid/block/cluster state into warp records visible to the
core. SimX mirrors this in `sim/simx/scheduler.cpp` by copying CTA metadata into
per-warp CSR state during activation.

For local work, this is the boundary between runtime and SIMT core. If a kernel
sees wrong `blockIdx`, `threadIdx`, `gridDim`, or args, debug the launch/DCR/CTA
path before blaming the core ALU or memory pipeline.

## Capability And Config Boundary

`ref_submodule/vortex/sw/runtime/common/caps.h` decodes runtime-visible
capability words read from the CP register file:

- number of threads, warps, cores, sockets, clusters;
- issue width;
- local memory size;
- ISA flags;
- memory bank count/size.

Some caps are not encoded and must be resolved by the backend: cache line size,
global memory size, clock rate, and peak memory bandwidth.

This is important for runtime design because software should query visible
capabilities instead of including private hardware config headers.

## Local Transfer Checklist

- Define public handles first: device, buffer, queue, event, module, kernel.
- Define backend transport separately: register read/write, DMA, host memory,
  simulator callback, or RTL bridge.
- Define module format and kernel entry resolution before adding multi-kernel
  launch features.
- Define argument staging and lifetime.
- Define DCR/MMIO launch records for grid/block/local memory/entry/args.
- Define completion, timeout, fence, event, and cache flush behavior.
- Add at least one workload that runs through the public runtime path for both
  simulator and RTL-style backend when available.

## What Not To Copy

- Do not expose internal RTL wires as a public API.
- Do not import the full Vortex CP if a smaller explicit launch command is
  enough for the current milestone.
- Do not hard-code kernel entry PC in tests once modules/kernels exist.
- Do not add asynchronous queues or events without ordering and completion
  semantics.
- Do not let runtime include private hardware config headers when a capability
  query or generated ABI header is the correct boundary.
