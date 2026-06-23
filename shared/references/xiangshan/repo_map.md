# XiangShan Repo Map Lessons

XiangShan separates top-level configuration, simulation harness closure,
golden/reference infrastructure, differential testing, debug capture, runtime
constants, structured trace, scripts, and ready-to-run workloads.

GPGPU skill mapping:

- `gpgpu-arch`: tool enablement switchboard and knob classification
- `gpgpu-golden`: executable reference machine and state blobs
- `gpgpu-runtime`: launch descriptors, runtime knobs, debug knobs
- `gpgpu-rtl`: harness closure, probes, trace sinks, counter taps
- `gpgpu-simppa`: diff, capture, trace DB, checkpoint replay, attribution
- `gpgpu-loop`: replay-driven rewrite routing and regression fingerprinting

Rule: generated workflows must produce reproducible scripts such as
`run_correctness.sh`, `run_diff.sh`, `run_replay.sh`,
`run_perf_sampling.sh`, `run_dse.sh`, and `collect_trace_db.sh`.

