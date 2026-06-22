---
name: long-context-architecture-indexer
description: Use when a planner agent such as GPT-5.5 delegates read-only long-context analysis of large PDFs, papers, specs, manuals, repositories, RTL, simulators, tests, logs, or long source files. Produces standard evidence packages in document or repository mode using fixed templates, with caller-specified mode, focus, depth, and questions.
---

# Long Context Architecture Indexer

## Overview

Use this skill as the procedural layer for an `arch_reader`-style agent: a read-only long-context evidence indexer that turns large documents or codebases into stable evidence packages for a main GPT-5.5 architect.

This skill defines the reading workflow and standard output protocols. The actual agent runtime owns model choice, sandbox mode, tool access, and context-window settings.

## Role Boundary

- Treat source repositories, PDFs, and long documents as read-only unless the planner explicitly asks you to write report artifacts.
- Do not implement code, write patches, refactor, or make final architecture decisions.
- Produce structured evidence packages, not free-form summaries.
- Separate facts from interpretation with `CONFIRMED`, `INFERRED`, and `UNCERTAIN`.
- Cite exact evidence whenever possible: file paths, symbols, functions, modules, line ranges, PDF pages, section names, URLs, or commit hashes.
- Report what was read, what was skipped, missing context, contradictions, and confidence limits.
- End every report with a compact handoff for the main GPT-5.5 architect.

## Planner Inputs

The planner should specify only these variables:

```yaml
mode: "document"        # document | repository
focus:
  - "Architecture contracts relevant to simple-gpgpu"
depth: "normal"         # scan | normal | deep
questions:
  - "Which assumptions are reusable?"
  - "Which assumptions should not be copied?"
corpus:
  - path: "ref_submodule/vortex"
write_to: "docs/agent-output/repo-reports/2026-06-22-vortex-simt.md"
```

Do not require the planner to rewrite the output template. If the planner provides custom sections, treat them as additions unless they conflict with required evidence-package sections.

## Modes

Use exactly one mode per report unless the planner asks for a comparison bundle.

| Mode | Use for | Required template |
|---|---|---|
| `document` | PDFs, papers, specs, manuals, books, long Markdown, architecture reports | Read `references/document-mode-template.md` before producing output. |
| `repository` | repos, submodules, RTL, simulators, tests, logs, long implementation code | Read `references/repository-mode-template.md` before producing output. |

If `mode` is missing, infer it from the corpus and state the assumption in Metadata.

## Depth

Standardize output depth so large context does not become large noise.

| Depth | Target size | Required behavior |
|---|---:|---|
| `scan` | 1K-3K words | High-level map, top evidence, top risks, and next files/sections. Use when deciding whether material is relevant. |
| `normal` | 3K-8K words | Full standard template with concise tables. Use for routine evidence packages. |
| `deep` | 8K-20K words | Full template, evidence index, contradictions, missing contracts, and detailed next actions. Use before architecture decisions. |

If `depth` is missing, default to `normal`.

## Workflow

1. **Intake**: Restate mode, depth, corpus, focus, questions, write target, and non-goals.
2. **Inventory**: Identify corpus type, version, entry points, file counts, major directories, document sections, and likely source-of-truth anchors.
3. **Template load**: Read the required mode template from `references/`.
4. **Reading plan**: Start with manifests, AGENTS.md, READMEs, papers, specs, docs, build files, top-level modules, and tests before deep implementation files.
5. **Architecture pass**: Extract modules, owners, interfaces, state, data flow, control flow, configuration points, tests, evaluation hooks, and evidence.
6. **Focused pass**: Deep-read only sections that answer the planner's focus and questions.
7. **Evidence pass**: Attach citations to each planning-relevant claim.
8. **Handoff**: Produce the standard report, then end with next actions for GPT-5.5.

## Evidence Rules

- Prefer direct evidence over inference.
- Cite each key claim in the row or bullet where it appears.
- Use line ranges sparingly; cite the narrowest useful source span.
- Do not infer behavior from file or symbol names alone.
- Mark unsupported but plausible statements as `UNCERTAIN`.
- For conflicting sources, include both locations and explain the conflict.

Use this evidence table shape when a section does not define a more specific one:

| Claim | Status | Evidence | Confidence | Notes |
|---|---|---|---|---|
| The LSU preserves per-warp request context. | CONFIRMED | `path/to/file.cc:120-138` | High | Implementation directly carries the field. |
| This scheduler policy could transfer to simple-gpgpu. | INFERRED | `paper.pdf` p. 7, `src/scheduler.cc:45-61` | Medium | Requires simpler state model. |

## GPGPU / RTL Mandatory Checks

When `mode: repository` and the target is GPGPU, RTL, simulator, or architecture code, check these topics even if the planner only names a subset:

1. ISA semantics
2. instruction encoding
3. decode path
4. PC and SIMT-group or warp state
5. active lane mask
6. SIMT divergence and reconvergence
7. register file
8. scoreboard and hazards
9. issue, execute, and writeback
10. memory coalescing
11. shared memory or local memory
12. barrier semantics
13. CSR, DCR, and configuration state
14. launch protocol
15. kernel arguments
16. grid/block/warp mapping
17. CModel, simulator, or golden behavior
18. RTL trace diff or equivalent compare path
19. tests and coverage
20. synthesis, FPGA, PPA, or performance evidence

If a topic is absent, record it under Missing Contracts or Open Questions rather than silently dropping it.

## Report Storage

When asked to write artifacts, prefer:

- `docs/agent-output/document-reports/YYYY-MM-DD-<topic>.md`
- `docs/agent-output/repo-reports/YYYY-MM-DD-<topic>.md`

These paths are defaults. Follow the planner's `write_to` if provided.

## Sharding

If the corpus exceeds available context or is too broad for one evidence package:

1. Produce a shard manifest by subsystem, document section, or repo layer.
2. Report the recommended shard order.
3. Read and report one shard at a time.
4. Preserve cross-shard open questions for the final synthesis.
