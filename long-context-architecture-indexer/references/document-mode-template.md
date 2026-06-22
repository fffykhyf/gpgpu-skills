# Document Mode Template

Use this template for PDFs, papers, specs, manuals, books, architecture reports, and long Markdown documents. Do not replace it with a caller-provided ad hoc template. Caller-provided sections may be appended if they do not remove evidence requirements.

For `scan`, keep sections 0, 1, 3, 8, 9, 10, and 11 concise. For `normal`, include all sections with compact tables. For `deep`, include all sections with detailed evidence and explicit missing-evidence notes.

```markdown
# Document Reading Report

## 0. Metadata

- Mode: document
- Document name:
- Document type: paper / spec / manual / book / report / unknown
- Version / date if available:
- Pages / sections read:
- Pages / sections skipped:
- Reading goal:
- Focus:
- Depth: scan / normal / deep
- Confidence: High / Medium / Low

## 1. Executive Handoff for GPT-5.5

Write 5-10 bullets only.

Each bullet must include:
- key finding
- why it matters for the user's architecture or design problem
- evidence location

## 2. Document Thesis / Main Argument

- Main claim:
- Supporting claims:
- Non-goals:
- Assumptions:
- Target system / workload:
- Evaluation target:

## 3. Architecture-Relevant Concepts

| Concept | Meaning | Design relevance | Evidence |
|---|---|---|---|

## 4. State / Contract Model

| Contract Type | Content | Who owns it | Evidence | Confidence |
|---|---|---|---|---|
| ISA / ABI | | | | |
| Runtime / launch | | | | |
| Memory model | | | | |
| Pipeline model | | | | |
| Synchronization | | | | |
| Performance model | | | | |

## 5. Mechanism Map

| Mechanism | Input | Output | State used | Dependency | Failure mode | Evidence |
|---|---|---|---|---|---|---|

## 6. Design Rules Extracted

Use this format for each rule:

- Rule:
- Applies when:
- Does not apply when:
- Evidence:
- Effect on GPGPU / accelerator design:
- Confidence:

## 7. Evaluation Pattern

- Metrics:
- Baselines:
- Workloads:
- Ablations:
- Fairness assumptions:
- Missing evidence:

## 8. Contradictions / Ambiguities

| Issue | Location A | Location B | Why it conflicts | Severity |
|---|---|---|---|---|

## 9. Evidence Index

| Claim | Status | Evidence location | Exact artifact | Confidence |
|---|---|---|---|---|

## 10. Open Questions for Main Architect

Only include questions that affect design decisions.

| Question | Why it matters | Evidence gap | Suggested next read |
|---|---|---|---|

## 11. Recommended Next Read

- If continuing this document:
- If applying this to a repo:
- If writing a paper/spec:

## 12. Compact Handoff Summary

Write a short paragraph for GPT-5.5 that says what was read, what matters most, and what decision this evidence supports or blocks.
```
