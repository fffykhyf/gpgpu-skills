# Rocket Verification Lessons for GPGPU Skill

## Metadata

- Mode: `repository`
- Depth: `deep`
- Output profile: `model-evidence`
- Repo / subsystem: `ref_submodule/rocket-chip`
- Commit: `55bcad0`
- Planner file: `ref/skillref/rocket.md`
- Assigned write target: `ref/skillref/rocket-reader-reports/rocket_generator_verification_to_gpgpu.md`
- Focus: verification / trace / groundtest / unittest patterns that transfer to a generator-driven GPGPU skill
- Non-goals: Rocket CPU pipeline internals, CSR semantics, frontend/FPU behavior, Linux boot flow
- Files read:
  `ref_submodule/rocket-chip/Makefile`
  `ref_submodule/rocket-chip/regression/Makefile`
  `ref_submodule/rocket-chip/regression/run-test-bucket`
  `ref_submodule/rocket-chip/src/main/scala/unittest/UnitTest.scala`
  `ref_submodule/rocket-chip/src/main/scala/unittest/TestHarness.scala`
  `ref_submodule/rocket-chip/src/main/scala/unittest/TestGenerator.scala`
  `ref_submodule/rocket-chip/src/main/scala/unittest/package.scala`
  `ref_submodule/rocket-chip/src/main/scala/unittest/Configs.scala`
  `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala`
  `ref_submodule/rocket-chip/src/main/scala/system/SimAXIMem.scala`
  `ref_submodule/rocket-chip/src/main/scala/system/ExampleRocketSystem.scala`
  `ref_submodule/rocket-chip/src/main/scala/system/Configs.scala`
  `ref_submodule/rocket-chip/src/main/scala/system/RocketTestSuite.scala`
  `ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala`
  `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala`
  `ref_submodule/rocket-chip/src/main/scala/groundtest/Configs.scala`
  `ref_submodule/rocket-chip/src/main/scala/groundtest/TestHarness.scala`
  `ref_submodule/rocket-chip/src/main/scala/groundtest/GroundTestSubsystem.scala`
  `ref_submodule/rocket-chip/src/main/scala/groundtest/Tile.scala`
  `ref_submodule/rocket-chip/src/main/scala/groundtest/Status.scala`
  `ref_submodule/rocket-chip/src/main/scala/groundtest/Package.scala`
  `ref_submodule/rocket-chip/src/main/scala/groundtest/TraceGen.scala`
  `ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala`
  `ref_submodule/rocket-chip/src/main/scala/tilelink/Fuzzer.scala`
  `ref_submodule/rocket-chip/src/main/scala/tilelink/RAMModel.scala`
  `ref_submodule/rocket-chip/src/main/scala/amba/axi4/Test.scala`
  `ref_submodule/rocket-chip/src/main/scala/formal/FormalUtils.scala`
  `ref_submodule/rocket-chip/src/main/scala/trace/TraceCoreInterface.scala`
  `ref_submodule/rocket-chip/src/main/scala/trace/TraceCoreIngress.scala`
  `ref_submodule/rocket-chip/src/main/scala/trace/TraceEncoder.scala`
  `ref_submodule/rocket-chip/src/main/scala/trace/TraceEncoderController.scala`
  `ref_submodule/rocket-chip/src/main/scala/trace/TraceSink.scala`
  `ref_submodule/rocket-chip/src/main/scala/trace/TraceSinkArbiter.scala`
  `ref_submodule/rocket-chip/src/main/scala/trace/TraceSinkMonitor.scala`
  `ref_submodule/rocket-chip/src/main/resources/vsrc/TraceSinkMonitor.v`
  `ref_submodule/rocket-chip/src/main/resources/csrc/emulator.cc`
  `ref_submodule/rocket-chip/src/main/resources/csrc/debug_rob.cc`
  `ref_submodule/rocket-chip/src/main/resources/csrc/comlog.cc`
  `ref_submodule/rocket-chip/scripts/tracegen.py`
  `ref_submodule/rocket-chip/scripts/tracegen+check.sh`
- Files skipped:
  `ref_submodule/rocket-chip/src/main/scala/rocket/**`
  `ref_submodule/rocket-chip/src/main/scala/tile/**` except groundtest tile wrapper
  `ref_submodule/rocket-chip/src/main/scala/subsystem/**` except external-port traits
- Confidence: `High` for unittest / harness / monitor / regression mapping; `Medium` for trace sink deployment beyond the files read

## Rocket Pattern Summary

| ID | Question | Answer | Status | Evidence |
|---|---|---|---|---|
| Q1 | Smallest hardware unit test contract | The minimal contract is `start` in, `finished` out, plus a local timeout assertion. `UnitTestIO` defines only those two signals; `UnitTest` logs start and asserts `SimpleTimer(timeout, io.start, io.finished)` never expires. `UnitTestSuite` fans one-cycle `start` to all tests and declares success when all `finished` bits are high. `LazyUnitTest` is even smaller: a single `finished` output that can be reduced over a sequence. | CONFIRMED | `ref_submodule/rocket-chip/src/main/scala/unittest/UnitTest.scala:10-35`; `ref_submodule/rocket-chip/src/main/scala/unittest/UnitTest.scala:39-55`; `ref_submodule/rocket-chip/src/main/scala/unittest/TestGenerator.scala:10-18`; `ref_submodule/rocket-chip/src/main/scala/unittest/package.scala:7-11` |
| Q2 | How generated SoC connects to simulation harness | `system.TestHarness` instantiates `ExampleRocketSystem`, fans the harness clock into all DUT clock groups, merges reset with `debug.ndreset`, ties off interrupts, connects declared AXI mem/MMIO ports to `SimAXIMem`, ties off unused slave-side AXI, then routes debug exit into top-level `io.success`. The Verilator C++ harness stops on `dtm->done()`, `jtag->done()`, or `tile->io_success`. | CONFIRMED | `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala:13-41`; `ref_submodule/rocket-chip/src/main/scala/system/ExampleRocketSystem.scala:10-28`; `ref_submodule/rocket-chip/src/main/scala/system/SimAXIMem.scala:15-55`; `ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:54-154`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:195-204`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:221-237`; `ref_submodule/rocket-chip/src/main/resources/csrc/emulator.cc:255-339` |
| Q3 | How named configs link to generated Verilog and tests | Top-level elaboration uses `PROJECT` and `CONFIG`; root `make verilog` defaults to `freechips.rocketchip.system.TestHarness` plus `CONFIG`. Regression suites override `PROJECT`/`CONFIGS` per suite, then stamp per-config build and run targets. Unit-test configs are named `Config` classes that inject concrete `Module(...)` lists through the `UnitTests` field. Groundtest uses separate configs and separate scripts rather than the shared regression makeflow. | CONFIRMED | `ref_submodule/rocket-chip/Makefile:3-9`; `ref_submodule/rocket-chip/regression/Makefile:47-104`; `ref_submodule/rocket-chip/regression/Makefile:112-144`; `ref_submodule/rocket-chip/regression/Makefile:181-253`; `ref_submodule/rocket-chip/src/main/scala/unittest/Configs.scala:21-179`; `ref_submodule/rocket-chip/src/main/scala/groundtest/Configs.scala:16-72`; `ref_submodule/rocket-chip/scripts/tracegen+check.sh:31-39` |
| Q4 | What monitors / fuzzers / final program output each check | `TLMonitor` checks protocol legality against diplomatic parameters, multibeat consistency, source/sink uniqueness, response opcode/size matching, and request watchdog timeout. `TLFuzzer` generates only legal transactions and finishes when all responses retire. `TLRAMModel` shadows memory, tracks overlap races, and asserts exact returned data or CRC when behavior must be defined. AXI tests wrap TL fuzz/model around TL<->AXI adapters. Final test output is consumed in three places: generated `run-*` make rules scan `***...***` and `ASSERTION FAILED`; `emulator.cc` prints pass/fail reason; groundtest scripts count `FINISHED N` and run AXE on converted traces. | CONFIRMED | `ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:35-120`; `ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:606-715`; `ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:826-882`; `ref_submodule/rocket-chip/src/main/scala/tilelink/Fuzzer.scala:80-230`; `ref_submodule/rocket-chip/src/main/scala/tilelink/RAMModel.scala:15-30`; `ref_submodule/rocket-chip/src/main/scala/tilelink/RAMModel.scala:87-177`; `ref_submodule/rocket-chip/src/main/scala/tilelink/RAMModel.scala:241-320`; `ref_submodule/rocket-chip/src/main/scala/amba/axi4/Test.scala:25-95`; `ref_submodule/rocket-chip/src/main/scala/amba/axi4/Test.scala:103-168`; `ref_submodule/rocket-chip/src/main/scala/system/RocketTestSuite.scala:14-31`; `ref_submodule/rocket-chip/src/main/scala/system/RocketTestSuite.scala:64-90`; `ref_submodule/rocket-chip/src/main/resources/csrc/emulator.cc:314-332`; `ref_submodule/rocket-chip/src/main/scala/groundtest/TraceGen.scala:550-607`; `ref_submodule/rocket-chip/scripts/tracegen.py:27-62`; `ref_submodule/rocket-chip/scripts/tracegen+check.sh:114-147` |
| Q5 | Which traces / counters / debug hooks are verification evidence | Verification evidence is not one trace path. Rocket layers multiple hooks: `trace_count` and optional VCD in the emulator, per-request cycle-stamped `TraceGen` logging, a typed architectural trace interface and ingress normalizer, MMIO control for trace encoders, optional byte-stream file sinks, debug ROB buffering for delayed writebacks, and commit-log post-processing into Spike-diffable format. | CONFIRMED | `ref_submodule/rocket-chip/src/main/resources/csrc/emulator.cc:37-49`; `ref_submodule/rocket-chip/src/main/resources/csrc/emulator.cc:65-88`; `ref_submodule/rocket-chip/src/main/resources/csrc/emulator.cc:118-165`; `ref_submodule/rocket-chip/src/main/resources/csrc/emulator.cc:283-331`; `ref_submodule/rocket-chip/src/main/scala/groundtest/TraceGen.scala:323-330`; `ref_submodule/rocket-chip/src/main/scala/groundtest/TraceGen.scala:550-607`; `ref_submodule/rocket-chip/src/main/scala/trace/TraceCoreInterface.scala:28-50`; `ref_submodule/rocket-chip/src/main/scala/trace/TraceCoreIngress.scala:26-52`; `ref_submodule/rocket-chip/src/main/scala/trace/TraceEncoderController.scala:24-84`; `ref_submodule/rocket-chip/src/main/scala/trace/TraceSinkArbiter.scala:35-54`; `ref_submodule/rocket-chip/src/main/resources/vsrc/TraceSinkMonitor.v:1-32`; `ref_submodule/rocket-chip/src/main/resources/csrc/debug_rob.cc:35-125`; `ref_submodule/rocket-chip/src/main/resources/csrc/comlog.cc:7-23`; `ref_submodule/rocket-chip/src/main/resources/csrc/comlog.cc:110-198` |
| Q6 | How regression flow prevents untested config drift | Drift is contained by naming config sets in `regression/Makefile`, materializing per-config build/run stamps, and dedicating a compile-only `Miscellaneous` suite to configs not otherwise executed. CI buckets run suites A/B/C, JTAG suites, and bucket `7` runs `SUITE=Miscellaneous` specifically to keep non-default configs buildable. Groundtest is a separate script flow, so it is covered differently and is not part of the shared regression bucket matrix. | CONFIRMED | `ref_submodule/rocket-chip/regression/Makefile:85-104`; `ref_submodule/rocket-chip/regression/Makefile:112-144`; `ref_submodule/rocket-chip/regression/Makefile:181-253`; `ref_submodule/rocket-chip/regression/run-test-bucket:31-72`; `ref_submodule/rocket-chip/scripts/tracegen+check.sh:19-21` |

Rocket generator lesson:

- Tests are first-class generator products, not post-hoc benches.
- Named configs decide which harness, which DUT topology, which tests, and which CI bucket exist.
- External interface closure is explicit: every optional port is either wired to a simulation model or tied off.
- Protocol legality and reference checking are split: monitors guard interface law; RAMModel/trace flows guard semantic outcomes.
- Compile-only configs are deliberate coverage, not second-class leftovers.

## GPGPU Transfer List Of Generated Artifacts

- `resolved_config.<md|json>`: fully composed named config, test ownership, runtime/debug knobs, and compile/run suite membership. Rocket anchor: named `Config` classes and `PROJECT`/`CONFIG` selection in `Makefile` and `regression/Makefile`.
- `TopHarness-<Config>.sv` and `HarnessPorts-<Config>.md`: explicit closure of DRAM/MMIO/debug/host ports. Rocket anchor: `system.TestHarness`, `groundtest.TestHarness`, `SimAXIMem`, `Ports.scala`.
- `<Config>.plusArgs.h` or equivalent simulator knob manifest: runtime-selectable timeouts, tracing, debug toggles. Rocket anchor: `ElaborationArtefacts.add("plusArgs", ...)` and emulator plusarg parsing.
- `ProtocolMonitor-<iface>.sv`: generated legalizer/timeout checker per fabric edge. Rocket anchor: `tilelink/Monitor.scala` plus `formal/FormalUtils.scala`.
- `ShadowMemoryModel-<iface>.sv` or executable checker: shadow bytes, inflight overlap accounting, exact-value / CRC checks. Rocket anchor: `tilelink/RAMModel.scala`.
- `AdapterFuzz-<path>.sv`: random legal traffic across width/crossing/protocol adapters. Rocket anchor: `tilelink/Fuzzer.scala`, `amba/axi4/Test.scala`.
- `TraceSchema-<rev>.md` and `trace_<target>.{txt,bin}`: typed runtime trace plus file sink. Rocket anchor: `trace/TraceCoreInterface.scala`, `trace/TraceEncoderController.scala`, `TraceSinkMonitor.v`.
- `commitlog-normalizer` and `trace-check` scripts: transform raw runtime evidence into diffable golden inputs. Rocket anchor: `debug_rob.cc`, `comlog.cc`, `tracegen.py`, `tracegen+check.sh`.
- `regression-matrix.yaml` or stamped manifest: executed suites vs compile-only suites. Rocket anchor: `regression/Makefile`, `run-test-bucket`.

## Required Test Gates

| Gate | Rocket mechanism | Required evidence | GPGPU transfer |
|---|---|---|---|
| G1 Config elaboration gate | Named configs in `system/Configs.scala`, `unittest/Configs.scala`, `groundtest/Configs.scala`; stamped builds in `regression/Makefile` | Every named config compiles into a harnessed DUT artifact; compile failures are per-config, not hidden in one mega-build | Reject any new feature without a named config fragment and a generated elaboration artifact |
| G2 Smallest module-test gate | `UnitTestIO`, `UnitTest`, `UnitTestSuite`, `LazyUnitTest` | `start`, `finished`, and local timeout assert; suite-level reduction to one completion bit | Every unit testable GPGPU block exposes the same minimal start/finished contract and owns its timeout |
| G3 Harness closure gate | `system/TestHarness`, `groundtest/TestHarness`, `SimAXIMem`, `Debug.connectDebug` | All external ports are simulated or tied off; one top-level success bit feeds the simulator | Forbid floating host/DRAM/debug ports in generated tops |
| G4 Interface-law gate | `tilelink/Monitor.scala`, `formal/FormalUtils.scala` | Protocol legality, multibeat stability, source/sink uniqueness, response matching, timeout | Generate fabric monitors from negotiated interface capabilities, not hand-written ad hoc asserts |
| G5 Semantic-data gate | `tilelink/RAMModel.scala` | Shadow-state comparison, overlap/race detection, CRC for multi-beat atomics, precise mismatch printouts | Any memory/coherence feature must have a reference checker, not only protocol assertions |
| G6 Adapter-randomization gate | `tilelink/Fuzzer.scala`, `amba/axi4/Test.scala` | Random but legal traffic across crossings, width widgets, protocol bridges, error paths | New GPGPU adapters require fuzz wrappers that respect negotiated legality and terminate cleanly |
| G7 Runtime-trace gate | `groundtest/TraceGen.scala`, `tracegen.py`, `tracegen+check.sh`, `trace/*`, `debug_rob.cc`, `comlog.cc` | Machine-readable traces, cycle counters, commit-log repair, external checker integration | New runtime-visible behaviors need a trace schema plus a consumer/checker path, not just printfs |
| G8 Drift-control gate | `regression/Makefile`, `run-test-bucket` | Executed suites plus compile-only suites for the rest | Every unsupported-to-run config still needs a compile gate in CI to prevent configuration rot |

## Rule Candidates For Feature Acceptance

| Axis | Candidate rule | Rocket anchor |
|---|---|---|
| Config | No feature lands until it appears in a named config fragment and in a resolved config manifest that says whether it is executed or compile-only. | `ref_submodule/rocket-chip/src/main/scala/system/Configs.scala:14-107`; `ref_submodule/rocket-chip/src/main/scala/unittest/Configs.scala:172-179`; `ref_submodule/rocket-chip/regression/Makefile:47-104` |
| Interface | Every generated external/internal protocol edge must receive a generated monitor with timeout control and response/source bookkeeping. | `ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:606-715`; `ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:826-882` |
| Golden | Any feature that changes memory-observable results must come with a shadow/reference model or checker, not only directed tests. | `ref_submodule/rocket-chip/src/main/scala/tilelink/RAMModel.scala:87-177`; `ref_submodule/rocket-chip/src/main/scala/tilelink/RAMModel.scala:241-320` |
| RTL | Testable blocks must surface one completion bit and own a local timeout assert; pass/fail cannot depend on simulator-side heuristics alone. | `ref_submodule/rocket-chip/src/main/scala/unittest/UnitTest.scala:28-35`; `ref_submodule/rocket-chip/src/main/scala/unittest/UnitTest.scala:39-55` |
| Runtime | Harness generation must explicitly connect or tie off all external ports and funnel termination into one top-level success signal. | `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala:21-41`; `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:195-204`; `ref_submodule/rocket-chip/src/main/resources/csrc/emulator.cc:283-332` |
| Tests | Random fuzz, deterministic unit tests, and compile-only drift suites are all required; any one of them alone is insufficient. | `ref_submodule/rocket-chip/src/main/scala/tilelink/Fuzzer.scala:80-230`; `ref_submodule/rocket-chip/regression/Makefile:85-104`; `ref_submodule/rocket-chip/regression/run-test-bucket:31-72` |
| Trace | Runtime evidence must be typed, target-selectable, sinkable to files, and consumable by downstream diff/check tools. | `ref_submodule/rocket-chip/src/main/scala/trace/TraceCoreInterface.scala:28-50`; `ref_submodule/rocket-chip/src/main/scala/trace/TraceEncoderController.scala:24-84`; `ref_submodule/rocket-chip/src/main/resources/vsrc/TraceSinkMonitor.v:14-32`; `ref_submodule/rocket-chip/src/main/resources/csrc/comlog.cc:7-23` |
| Counter | Long-running or randomized tests must expose cycle/outstanding watchdog counters in failure text. | `ref_submodule/rocket-chip/src/main/resources/csrc/emulator.cc:314-332`; `ref_submodule/rocket-chip/src/main/scala/groundtest/TraceGen.scala:226-230`; `ref_submodule/rocket-chip/src/main/scala/groundtest/TraceGen.scala:323-330` |

## Required Evidence Table

| Rocket Mechanism | Source Files | Problem Solved in Rocket | Transferable Abstraction | GPGPU Skill Rule | Anti-Pattern to Avoid |
|---|---|---|---|---|---|
| Minimal hardware test contract | `ref_submodule/rocket-chip/src/main/scala/unittest/UnitTest.scala:10-35`<br>`ref_submodule/rocket-chip/src/main/scala/unittest/UnitTest.scala:39-55`<br>`ref_submodule/rocket-chip/src/main/scala/unittest/TestGenerator.scala:10-18` | Gives every hardware test one uniform completion interface and local timeout ownership | `start/finished/timeout` is enough to compose many tests into one generator-level suite | Standardize one tiny test IO for GPGPU blocks; suites may only reduce these bits, not invent custom pass plumbing | Test modules that only print logs or require bespoke simulator glue to decide pass/fail |
| Config-selected test inventories | `ref_submodule/rocket-chip/src/main/scala/unittest/Configs.scala:21-179`<br>`ref_submodule/rocket-chip/src/main/scala/groundtest/Configs.scala:16-72` | Makes test content part of configuration, not an external ad hoc bench list | Named config fragments define both DUT shape and associated verification inventory | Treat config, tests, trace knobs, and runtime knobs as one resolved artifact set | Letting each RTL block secretly pick widths/timeouts/tests locally |
| Harness closure to sim models | `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala:13-41`<br>`ref_submodule/rocket-chip/src/main/scala/system/SimAXIMem.scala:15-55`<br>`ref_submodule/rocket-chip/src/main/scala/subsystem/Ports.scala:54-154` | Prevents generated systems from having dangling memory/MMIO/debug ports in simulation | Generator-owned harness closure for each optional port class | Require explicit sim-model or tieoff policy per GPGPU external port | A “test harness” that depends on manual hand-wiring per config |
| Debug exit wiring | `ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:195-204`<br>`ref_submodule/rocket-chip/src/main/scala/devices/debug/Periphery.scala:221-237`<br>`ref_submodule/rocket-chip/src/main/resources/csrc/emulator.cc:283-332` | Funnels DTM/JTAG/debug completion into one simulator-visible success/failure channel | Unified simulator termination contract | GPGPU runtime/debug flow must export a single top-level completion/failure signal with encoded reason | Multiple unrelated success conditions hidden in logs only |
| Protocol legality monitor | `ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:35-120`<br>`ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:606-715`<br>`ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:826-882`<br>`ref_submodule/rocket-chip/src/main/scala/formal/FormalUtils.scala:10-117` | Catches protocol misuse at the interface boundary before semantic debugging | Generated monitor from negotiated capabilities plus reusable assert/assume/cover wrapper | Emit monitor properties from the interface schema; expose timeout plusargs | Hand-written spot assertions that do not know negotiated widths, IDs, or response classes |
| Random legal traffic generation | `ref_submodule/rocket-chip/src/main/scala/tilelink/Fuzzer.scala:80-230`<br>`ref_submodule/rocket-chip/src/main/scala/amba/axi4/Test.scala:25-95`<br>`ref_submodule/rocket-chip/src/main/scala/amba/axi4/Test.scala:103-168` | Exercises large adapter/crossing state spaces without generating illegal traffic noise | Capability-aware legal fuzzer wrapped around synthesized integration tests | Every new GPGPU adapter/crossbar/crossing path needs a legal-traffic fuzzer and finish condition | Random generators that mostly create illegal packets or never know when they are done |
| Shadow semantic checker | `ref_submodule/rocket-chip/src/main/scala/tilelink/RAMModel.scala:15-30`<br>`ref_submodule/rocket-chip/src/main/scala/tilelink/RAMModel.scala:87-177`<br>`ref_submodule/rocket-chip/src/main/scala/tilelink/RAMModel.scala:241-320` | Distinguishes protocol-correct-but-semantically-wrong memory behavior from legal traffic | Shadow-state reference model with race classification and exact mismatch output | For memory/coherence/atomic features, pair protocol monitors with a semantic checker | Declaring victory because the fabric never deadlocked while data silently mismatched |
| Groundtest trace generation + external checker | `ref_submodule/rocket-chip/src/main/scala/groundtest/TraceGen.scala:212-230`<br>`ref_submodule/rocket-chip/src/main/scala/groundtest/TraceGen.scala:550-607`<br>`ref_submodule/rocket-chip/src/main/scala/groundtest/TraceGen.scala:630-649`<br>`ref_submodule/rocket-chip/scripts/tracegen.py:27-62`<br>`ref_submodule/rocket-chip/scripts/tracegen+check.sh:114-147` | Converts random runtime activity into externally checkable memory-model evidence | Generator-owned trace producer plus consumer script plus formal/golden backend | GPGPU memory-model or scheduler claims need emitted traces and an independent checker pipeline | Free-form trace text with no consumer or stop condition |
| Typed trace sinks and commit-log repair | `ref_submodule/rocket-chip/src/main/scala/trace/TraceCoreInterface.scala:28-50`<br>`ref_submodule/rocket-chip/src/main/scala/trace/TraceCoreIngress.scala:26-52`<br>`ref_submodule/rocket-chip/src/main/scala/trace/TraceEncoderController.scala:24-84`<br>`ref_submodule/rocket-chip/src/main/scala/trace/TraceSinkArbiter.scala:35-54`<br>`ref_submodule/rocket-chip/src/main/resources/vsrc/TraceSinkMonitor.v:14-32`<br>`ref_submodule/rocket-chip/src/main/resources/csrc/debug_rob.cc:35-125`<br>`ref_submodule/rocket-chip/src/main/resources/csrc/comlog.cc:110-198` | Makes runtime evidence targetable, persistable, and diffable even when microarchitectural writeback timing is awkward | Typed trace schema + sink selection + post-processing | Separate architectural trace format from raw microarchitectural timing; supply normalizers | Treating raw simulator print order as the architectural truth |
| Compile-only drift bucket | `ref_submodule/rocket-chip/regression/Makefile:85-104`<br>`ref_submodule/rocket-chip/regression/run-test-bucket:70-72` | Prevents lesser-used configs from silently rotting when they are too expensive or unsuitable to run every time | Explicit compile-only verification tier | Track executed vs compile-only GPGPU configs in CI and fail if either set is missing | “We don’t run that config often” becoming “it no longer elaborates” |

## Evidence Snapshot

| Claim ID | Status | Short claim | Evidence |
|---|---|---|---|
| RKT-VER-001 | CONFIRMED | Unit tests reduce to `start`/`finished` plus timeout assert | `ref_submodule/rocket-chip/src/main/scala/unittest/UnitTest.scala:10-35` |
| RKT-VER-002 | CONFIRMED | System harness explicitly closes DRAM, MMIO, debug, and interrupts | `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala:21-41` |
| RKT-VER-003 | CONFIRMED | Config names directly drive per-config build stamps and test targets | `ref_submodule/rocket-chip/regression/Makefile:112-144`; `ref_submodule/rocket-chip/regression/Makefile:181-253` |
| RKT-VER-004 | CONFIRMED | TL monitor checks legality, response/source matching, and timeout | `ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala:606-715` |
| RKT-VER-005 | CONFIRMED | TL fuzzer generates only legal traffic and knows when it finishes | `ref_submodule/rocket-chip/src/main/scala/tilelink/Fuzzer.scala:165-229` |
| RKT-VER-006 | CONFIRMED | RAM model detects semantic memory mismatches, not just protocol errors | `ref_submodule/rocket-chip/src/main/scala/tilelink/RAMModel.scala:279-320` |
| RKT-VER-007 | CONFIRMED | Groundtest success is tile cease reduction; timeout is asserted locally | `ref_submodule/rocket-chip/src/main/scala/groundtest/GroundTestSubsystem.scala:47-51`; `ref_submodule/rocket-chip/src/main/scala/groundtest/TraceGen.scala:642-649` |
| RKT-VER-008 | CONFIRMED | Runtime pass/fail text is simulator-owned and reason-coded | `ref_submodule/rocket-chip/src/main/resources/csrc/emulator.cc:314-332` |
| RKT-VER-009 | CONFIRMED | CI includes a compile-only Miscellaneous bucket to stop config drift | `ref_submodule/rocket-chip/regression/run-test-bucket:70-72` |
| RKT-VER-010 | UNCERTAIN | Groundtest is part of the standard regression matrix | Evidence points the other way: separate scripts exist, but `regression/Makefile` does not name a groundtest suite in the lines read. `ref_submodule/rocket-chip/scripts/tracegen+check.sh:19-21`; `ref_submodule/rocket-chip/regression/Makefile:47-104` |

## Missing Contracts / Risks

- `MISSING`: no single generated manifest in Rocket ties every config class to executed-vs-compile-only policy; the mapping is hand-maintained in `regression/Makefile`.
- `UNCERTAIN`: groundtest `TraceGenConfig` is validated by dedicated scripts, not by the same regression buckets used for `system` and `unittest`; this is a process split GPGPU skills should make explicit.
- `MISSING`: this shard provides no synthesis / FPGA / PPA evidence.
- `NOT APPLICABLE TO THIS SHARD`: ISA/decode/warp/active-mask topics were intentionally not deep-read here; they belong to other Rocket shards, not this verification-only report.
- `CONFLICTED`: none found in the files read.

## Quality Gate

- Overall status: PASS
- Evidence status: PASS
- Readability status: PASS
- Safe for GPT-5.5 planning: yes, with caveats on groundtest-vs-regression split
- Full appendix generated: yes
- Biggest evidence gap: no single source-of-truth manifest for config-to-suite coverage; groundtest uses separate scripts
- Biggest readability issue: none material; citations are dense by design
- Required next read: `ref_submodule/rocket-chip/src/main/scala/subsystem/Configs.scala` and the planner’s diplomacy/system-composition shards if the GPGPU skill needs cross-shard config ownership rules
