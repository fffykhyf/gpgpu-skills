# Argument Layout Contract

Argument layout must derive from `SYSTEM_CONTRACT_IR.launch_model` and record:

- argument name or ordinal;
- byte offset;
- size;
- alignment;
- signedness or pointer class when relevant;
- constant/global/shared-memory binding.

Runtime artifacts must round-trip this layout through assembler, loader, and
golden image execution.

