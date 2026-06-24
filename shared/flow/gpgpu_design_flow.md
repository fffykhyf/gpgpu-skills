# Compact GPGPU Design Flow

```text
User request/spec
  -> gpgpu-architecture
     outputs DESIGN_INTENT, ARCH candidate, CAPABILITY_PROFILE

  -> gpgpu-contract
     loads memory/interconnect/atomic packs as needed
     freezes SYSTEM_CONTRACT
     derives GOLDEN_CONTRACT_MODEL

  -> gpgpu-toolchain-runtime
     derives assembler/disassembler/program image/loader/runtime launch

  -> gpgpu-rtl
     binds module-by-module RTL to contract paths and negotiated interfaces

  -> gpgpu-flow-yosys
     records Yosys flow/profile/build/report evidence when required

  -> gpgpu-validation
     validates golden vs RTL and collects compact evidence
     expands debug/perf packs only when needed

  -> gpgpu-loop
     routes patches back to architecture/contract/toolchain/RTL/validation
```

Default output is `RUN_STATE.yaml` plus one Chinese human summary.
Expanded artifacts are mode-gated, not always generated.

Current module order:

```text
gpgpu-architecture
  -> gpgpu-contract
  -> gpgpu-toolchain-runtime
  -> gpgpu-rtl
  -> gpgpu-flow-yosys
  -> gpgpu-validation
  -> gpgpu-loop
```

`gpgpu-flow-yosys` is mandatory only when `backend_toolchain` includes Yosys or
the user asks for RTL elaboration, synthesis, PPA, or Yosys-backed build/report
evidence.
