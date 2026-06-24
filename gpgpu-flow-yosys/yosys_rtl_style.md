# Yosys RTL Style

## Compatibility Purpose

The Yosys RTL compatibility gate determines whether generated RTL is safe to
parse, elaborate, and synthesize through the selected Yosys profile. It is a
backend compatibility gate, not an architecture or contract owner.

## Required Report

Emit `YOSYS_RTL_COMPATIBILITY_REPORT` and `RTL_SYNTH_HYGIENE_REPORT` whenever
Yosys compatibility, elaboration, synthesis, or PPA evidence is requested.

## Fail-Closed Style Rules

Rules are defined in `shared/tables/yosys_rtl_style_rules.yaml`. The gate must
fail closed on:

- top-level unpacked array ports
- large memory reset/init loops without profile gates
- data-dependent while loops in synthesizable regions
- non-constant loop bounds in synthesizable regions
- implicit wires
- combinational ready loops
- dequeue not gated by `valid && ready`
- payload changes while `valid && !ready`
- launch ready gap without inflight register
- done asserted before result/counter stability

## Yosys-Safe Defaults

- Top-level multi-instance ports use flattened packed buses.
- Large memories are not cleared by reset loops by default.
- Register file, shared memory, L2 arrays, metadata caches, and other large
  memories require explicit reset/init profile gates.
- Synthesizable loops use fixed bounds, FSMs, or pipelined reductions.
- Synthesizable regions do not use data-dependent `while` loops.
- Ready/valid side effects use `accept = valid && ready`.
- Dequeue, tag allocation, payload capture, scoreboard release, and response
  wakeup are gated by accepted transactions.
- Payload remains stable while `valid && !ready`.
- Start/busy/done interfaces use an inflight register when inner busy is
  delayed.
- Done/completion asserts only after architectural result and counters are
  latched or stable.

## Verdicts

Allowed verdicts:

- `YOSYS_READY`
- `YOSYS_READY_WITH_LIMITS`
- `YOSYS_UNSAFE_RTL`
- `YOSYS_EVIDENCE_MISSING`

`YOSYS_READY_WITH_LIMITS` must list exact unsupported claims and required
follow-up evidence.
