# Config Drift Guard

Reject rewrite plans when:

- a simulator-private parameter enters a hardware contract;
- CUDA/PTX compatibility fields enter the native ABI;
- fixed latencies become pipeline truth without a project-defined stage;
- queue depths from tested configs become defaults;
- parameter classification is missing.

## XiangShan Runtime DSE Drift Guard

Reject `DSE_EXPERIMENT_MANIFEST` when any `RUNTIME_DSE_KNOB` mutates structural
compile-time or ABI-visible fields. Debug trace knobs must be separated from
performance ranking inputs so enabling full transaction diff or trace DB writes
does not contaminate throughput comparisons.
