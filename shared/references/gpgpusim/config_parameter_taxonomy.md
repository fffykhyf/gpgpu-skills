# Config Parameter Taxonomy

Every external reference parameter must be classified before use:

- `hardware-private`: internal architectural or microarchitectural knob.
- `simulator-private`: simulator mode, calibration, idealization, queue
  artifact, fixed latency, or implementation control.
- `HW/SW ABI`: visible to compiler, runtime, kernel launch, occupancy, or
  compatibility contract.
- `test-only`: regression, benchmark, stopping, or harness control.
- `debug-only`: trace, visualization, print, checkpoint, or debug control.

Exposure policy:

- `Yes`: may become a simple-gpgpu design knob after provenance and range are
  recorded.
- `Guarded`: only under caveat or optional compatibility profile.
- `No`: must stay out of hardware contracts.

Every exposed parameter must include category, default/provenance, legal range
or `unknown`, performance effect, owner skill, and whether it enters a hardware
contract.

Raw basis: `raw/gpgpu-sim-config-parameter-taxonomy.md`.

