# Repository Mode Template

Use this template for repositories, submodules, RTL, simulators, testbenches, logs, and long implementation code.

Default behavior: print only Part A in chat. Produce Part B only when `output_profile: model-evidence`, `output_profile: full-audit`, `write_to` is provided, or the planner explicitly asks for the full appendix.

Do not mechanically fill every section. Remove empty sections. Keep visible content decision-oriented. Repository mode should surface the top confirmed facts, the riskiest missing contracts, and the next files GPT-5.5 should inspect.

```markdown
# Repository Architecture Report

## Part A. Human Handoff

Always print this section.

### 0. Metadata

- Mode: repository
- Depth: scan / normal / deep
- Output profile: human-handoff / model-evidence / full-audit
- Repo / subsystem:
- Branch / commit if available:
- Files read:
- Files skipped:
- Entry points inspected:
- Focus:
- Questions answered:
- Appendix: not generated / generated at `<path>` / printed inline
- Confidence: High / Medium / Low

### 1. One-Paragraph Answer

Explain what this repo or subsystem contains, whether it is usable as architecture evidence, and which GPT-5.5 decision it supports or blocks.

### 2. Top Architecture Findings

Include at most 5-7 findings.

Each finding must include:

- confirmed fact
- design implication
- evidence path

### 3. Minimal Architecture Map

Do not list every module. Include only:

- top-level flow
- 3-7 most important modules
- missing or risky subsystem boundaries

### 4. Top State / Interface Contracts

Include only the most important confirmed or missing contracts.

Common GPGPU / RTL examples:

- PC / warp state
- active mask
- scheduler / scoreboard
- memory path
- launch state
- golden model relation

### 5. Top Risks / Missing Contracts

Include at most 5 risks. Use `MISSING`, `UNCERTAIN`, or `CONFLICTED` where appropriate.

### 6. Evidence Snapshot

Include at most 10 claim IDs.

| Claim ID | Status | Short claim | Evidence |
|---|---|---|---|

### 7. Main Architect Next Actions

Include at most 5 actions.

Each action should include:

- decision needed
- files to inspect
- risk
- acceptance test

### 8. Compact Quality Gate

- Evidence status: PASS / PARTIAL / FAIL
- Readability status: PASS / PARTIAL / FAIL
- Safe for GPT-5.5 planning: yes / no / with caveats
- Full appendix generated: yes / no / inline
- Biggest evidence gap:
- Required next read:

## Part B. Evidence Appendix

Only print or write this section when:

- `output_profile: model-evidence`
- `output_profile: full-audit`
- `write_to` is provided
- the planner explicitly asks for the full appendix

When `write_to` is provided, write Part B to that path and do not duplicate it in chat unless `output_profile: full-audit`.

### A1. Source-of-Truth Hierarchy

| Layer | Files | Role | Reliability | Notes |
|---|---|---|---|---|
| Project rules | AGENTS.md / docs | | | |
| Spec | spec / docs | | | |
| Golden model | CModel / simulator | | | |
| RTL / implementation | src / rtl | | | |
| Tests | tests / tb | | | |
| Logs / reports | logs / reports | | | |

### A2. Full Architecture Map

| Module | Responsibility | Inputs | Outputs | State Owned | Owner Files | Tests |
|---|---|---|---|---|---|---|

### A3. Full Execution Flow

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

### A4. Full State Contracts

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

### A5. Full Interface Contracts

| Interface | Producer | Consumer | Fields / Signals | Valid-ready / protocol | Backpressure | Evidence |
|---|---|---|---|---|---|---|

### A6. Full Config / ABI Classification

| Parameter | Meaning | Category | Owner | Visible to software? | Evidence |
|---|---|---|---|---|---|

Categories: hardware-private / simulator-private / HW-SW ABI / test-only / debug-only.

### A7. Full Test and Evidence Map

| Behavior | Test / Log / Trace | What it proves | What it does not prove | Evidence |
|---|---|---|---|---|

### A8. Full Design Invariants

Use this shape for each invariant:

- Invariant:
- Owner:
- Enforced by:
- Tested by:
- Violated if:
- Evidence:
- Confidence:

### A9. Full Contradictions / Risks

| Issue | Files involved | Why it matters | Severity | Suggested owner |
|---|---|---|---|---|

### A10. Full Missing Contracts

| Missing contract | Evidence gap | Why it matters | Suggested owner |
|---|---|---|---|

### A11. Full Main Architect Next Actions

Use this shape for each action:

- Decision needed:
- Files to inspect:
- Proposed work order:
- Risk:
- Acceptance test:

### A12. Full Quality Gate

Include the complete checklist results from `references/quality-gate.md`.
```
