# Launch Descriptor Contract

Launch descriptor fields:

- `kernel_id`
- `entry_pc`
- `grid_dim`
- `block_dim`
- `shared_memory_bytes`
- `argument_layout`
- `program_image`
- `constant_memory`
- `global_memory_init`

Do not include CUDA streams, launch latency, compute capability, or OpenCL
object model in the native ABI unless an optional compatibility profile is
selected.

