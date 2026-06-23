# Config Drift Guard

Reject rewrite plans when:

- a simulator-private parameter enters a hardware contract;
- CUDA/PTX compatibility fields enter the native ABI;
- fixed latencies become pipeline truth without a project-defined stage;
- queue depths from tested configs become defaults;
- parameter classification is missing.

