# Optional CUDA/PTX Compatibility Profile

CUDA/PTX fields are optional compatibility metadata, not native simple-gpgpu
truth.

Only a selected compatibility profile may expose:

- CUDA compute capability;
- PTX capability limits;
- CUDA stack/heap/dynamic parallelism limits;
- texture/constant memory behavior;
- PTX-specific atomic or fence behavior.

Without the profile, native ISA/ABI contracts must define their own behavior.

