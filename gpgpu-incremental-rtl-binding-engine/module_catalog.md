# Module Catalog

The catalog enumerates required RTL modules for a minimal self-correcting SIMT GPGPU.

| Module | Required responsibility |
|---|---|
| `sm_core` | Own SM-level control and dispatch boundaries. |
| `warp_scheduler` | Bind scheduler contract to selected warp. |
| `decode_execute_pipeline` | Bind ISA decode, execute, and writeback paths. |
| `register_file` | Bind register read/write ports and hazards. |
| `scoreboard` | Bind dependency tracking and wakeup behavior. |
| `load_store_queue` | Bind memory request issue, replay, and retire. |
| `shared_memory` | Bind bank behavior and shared memory access. |
| `cache_global_interface` | Bind cache/global request-response interface. |
| `interconnect` | Bind module-to-module transport. |
| `csr_runtime_interface` | Bind runtime-visible control/status interface. |

Every catalog entry must have a contract path, interface definition, local trace schema, and partial simulation gate.
