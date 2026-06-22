# Repository Mode Template

Use this template for repositories, submodules, RTL, simulators, testbenches, logs, and long implementation code. Do not replace it with a caller-provided ad hoc template. Caller-provided sections may be appended if they do not remove evidence requirements.

For `scan`, keep sections 0, 1, 2, 3, 10, 11, and 12 concise. For `normal`, include all sections with compact tables. For `deep`, include all sections with detailed evidence, contradictions, missing contracts, and concrete next actions.

```markdown
# Repository Architecture Report

## 0. Metadata

- Mode: repository
- Repo:
- Branch / commit if available:
- Task focus:
- Depth: scan / normal / deep
- Files read:
- Files skipped:
- Entry points inspected:
- Confidence: High / Medium / Low

## 1. Executive Handoff for GPT-5.5

Write 5-10 bullets.

Each bullet must include:
- finding
- design implication
- evidence path

## 2. Source-of-Truth Hierarchy

| Layer | Files | Role | Reliability | Notes |
|---|---|---|---|---|
| Project rules | AGENTS.md / docs | | | |
| Spec | spec / docs | | | |
| Golden model | CModel / simulator | | | |
| RTL / implementation | src / rtl | | | |
| Tests | tests / tb | | | |
| Logs / reports | logs / reports | | | |

## 3. Architecture Map

| Module | Responsibility | Inputs | Outputs | State Owned | Owner Files | Tests |
|---|---|---|---|---|---|---|

## 4. Execution Flow

Describe the main flow end-to-end.

For GPGPU / RTL projects, cover:

1. program / kernel launch
2. fetch / decode
3. warp or SIMT-group scheduling
4. operand read
5. execute
6. memory / coalescing / shared memory
7. writeback
8. barrier / synchronization
9. done / result path

## 5. State Contracts

| State | Owner | Updated by | Read by | Reset behavior | Architectural or internal? | Evidence |
|---|---|---|---|---|---|---|
| PC | | | | | | |
| active mask | | | | | | |
| warp / SIMT-group state | | | | | | |
| SIMT stack | | | | | | |
| register file | | | | | | |
| scoreboard | | | | | | |
| memory state | | | | | | |
| CSR / DCR / config | | | | | | |
| launch state | | | | | | |

## 6. Interface Contracts

| Interface | Producer | Consumer | Fields / Signals | Valid-ready / protocol | Backpressure | Evidence |
|---|---|---|---|---|---|---|

## 7. Config / ABI Classification

| Parameter | Meaning | Category | Owner | Visible to software? | Evidence |
|---|---|---|---|---|---|
| | | hardware-private / simulator-private / HW-SW ABI / test-only / debug-only | | | |

## 8. Test and Evidence Map

| Behavior | Test / Log / Trace | What it proves | What it does not prove | Evidence |
|---|---|---|---|---|

## 9. Design Invariants

Use this format for each invariant:

- Invariant:
- Owner:
- Enforced by:
- Tested by:
- Violated if:
- Evidence:
- Confidence:

## 10. Contradictions / Risks

| Issue | Files involved | Why it matters | Severity | Suggested owner |
|---|---|---|---|---|

## 11. Missing Contracts

List missing or under-specified contracts, such as:

- launch done/result ordering
- scoreboard hazard semantics
- memory ordering
- config parameter classification
- test coverage for architectural state

| Missing contract | Evidence gap | Why it matters | Suggested owner |
|---|---|---|---|

## 12. Main Architect Next Actions

Give concrete next actions for GPT-5.5:

1. Decision needed:
2. Files to inspect:
3. Proposed work order:
4. Risk:
5. Acceptance test:

## 13. Compact Handoff Summary

Write a short paragraph for GPT-5.5 that says what was read, what matters most, and what decision this evidence supports or blocks.
```
