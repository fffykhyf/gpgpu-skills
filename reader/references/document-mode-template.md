# Document Mode Template

Use this template for PDFs, papers, specs, manuals, books, architecture reports, and long Markdown documents.

Default behavior: print only Part A in chat. Produce Part B only when `output_profile: model-evidence`, `output_profile: full-audit`, `write_to` is provided, or the planner explicitly asks for the full appendix.

Do not mechanically fill every section. Remove empty sections. Keep visible content decision-oriented.

```markdown
# Document Reading Report

## Part A. Human Handoff

Always print this section.

### 0. Metadata

- Mode: document
- Depth: scan / normal / deep
- Output profile: human-handoff / model-evidence / full-audit
- Document name:
- Document type: paper / spec / manual / book / report / unknown
- Version / date if available:
- Pages / sections read:
- Pages / sections skipped:
- Focus:
- Questions answered:
- Appendix: not generated / generated at `<path>` / printed inline
- Confidence: High / Medium / Low

### 1. One-Paragraph Answer

Summarize what this document is useful for, whether GPT-5.5 should rely on it, and which decision it supports or blocks.

### 2. Top Findings

Include at most 5-7 bullets.

Each bullet must include:

- finding
- why it matters
- evidence location

### 3. Architecture-Relevant Takeaways

Include only takeaways that affect the planner's next decision. Prefer short bullets over tables.

Common categories:

- ISA / ABI
- runtime contract
- memory model
- pipeline model
- synchronization
- performance model
- evaluation pattern

### 4. Risks / Missing Evidence

Include at most 5 items. Use `MISSING`, `UNCERTAIN`, or `CONFLICTED` where appropriate.

### 5. Evidence Snapshot

Include at most 10 claim IDs.

| Claim ID | Status | Short claim | Evidence |
|---|---|---|---|

### 6. Recommended Next Actions for GPT-5.5

Include at most 5 actions. Each action should be concrete and tied to a decision, evidence gap, or next read.

### 7. Compact Quality Gate

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

### A1. Full Document Thesis / Main Argument

- Main claim:
- Supporting claims:
- Non-goals:
- Assumptions:
- Target system / workload:
- Evaluation target:

### A2. Full Concept Index

| Concept | Meaning | Design relevance | Evidence | Confidence |
|---|---|---|---|---|

### A3. Full Contract Model

| Contract Type | Content | Owner | Evidence | Confidence |
|---|---|---|---|---|
| ISA / ABI | | | | |
| Runtime / launch | | | | |
| Memory model | | | | |
| Pipeline model | | | | |
| Synchronization | | | | |
| Performance model | | | | |

### A4. Full Mechanism Map

| Mechanism | Input | Output | State used | Dependency | Failure mode | Evidence |
|---|---|---|---|---|---|---|

### A5. Full Design Rules

Use this shape for each rule:

- Rule:
- Applies when:
- Does not apply when:
- Evidence:
- Effect on GPGPU / accelerator design:
- Confidence:

### A6. Full Evaluation Pattern

- Metrics:
- Baselines:
- Workloads:
- Ablations:
- Fairness assumptions:
- Missing evidence:

### A7. Full Contradictions / Ambiguities

| Issue | Location A | Location B | Why it conflicts | Severity |
|---|---|---|---|---|

### A8. Full Evidence Index

| Claim ID | Claim | Status | Evidence location | Exact artifact | Confidence |
|---|---|---|---|---|---|

### A9. Full Quality Gate

Include the complete checklist results from `references/quality-gate.md`.
```
