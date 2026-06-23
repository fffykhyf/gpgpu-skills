# Failure Capture Lessons

XiangShan LightSSS/XSPdb teaches that simulation failures should produce a
bounded replayable failure scene instead of full-run wave dumps.

GPGPU abstraction:

- `BATCH_AUTO_CAPTURE` is CI/regression mode for diff fail, assertion fail,
  timeout, and deadlock triggers.
- `INTERACTIVE_REPLAY_SESSION` is human-debug mode with step, break, dump, and
  compare commands.
- `FAILURE_CAPTURE_PACKAGE` contains replay command, trace slice, waveform
  slice or absent reason, config hash, program image hash, golden state, RTL
  state summary, memory store log, counter snapshot, and normalized report.
- `REPLAY_WINDOW` defines pre-failure and post-failure bounds.
- `DEBUG_TRIGGER` describes what caused capture and which context was required.

Rule: if an artifact is missing, the package must record an absent reason.

