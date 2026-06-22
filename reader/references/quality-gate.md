# Quality Gate

Every report must end with a compact quality gate in visible output.

Use the full checklist in the appendix when `output_profile: model-evidence`, `output_profile: full-audit`, or `write_to` is provided.

## Overall Status

Choose one:

- `PASS`
- `PARTIAL`
- `FAIL`

## Evidence Gate

| Check | PASS condition |
|---|---|
| Scope declared | Files/pages read and skipped are listed |
| Planner focus answered | Focus and questions are addressed |
| Evidence attached | Key claims have exact evidence locations |
| Claim status used | CONFIRMED / INFERRED / UNCERTAIN / CONFLICTED / MISSING are used correctly |
| Contradictions reported | Conflicts are listed or explicitly not found |
| Missing contracts reported | Missing mandatory topics are recorded |
| Handoff actionable | GPT-5.5 next actions are concrete |

## Readability Gate

| Check | PASS condition |
|---|---|
| Handoff length | Visible output follows selected output profile |
| Findings capped | Top findings are capped |
| Tables limited | No full tables in human-handoff |
| Empty sections removed | No mechanical template filling |
| Decision relevance | Every visible item affects planner decision |
| Appendix separation | Detailed evidence is moved to appendix |

## Repository Extra Gate

For GPGPU / RTL repositories, mark each topic as confirmed, inferred, missing, conflicted, or not applicable:

- ISA semantics
- instruction encoding
- decode path
- PC / warp state
- active mask
- SIMT divergence
- register file
- scoreboard / hazards
- issue / execute / writeback
- memory coalescing
- shared memory
- barrier semantics
- CSR / DCR / config state
- launch protocol
- kernel arguments
- grid/block/warp mapping
- CModel / golden model
- trace diff / compare path
- tests and coverage
- synthesis / FPGA / PPA evidence

## Required Visible Footer

```markdown
## Quality Gate

- Overall status:
- Evidence status:
- Readability status:
- Safe for GPT-5.5 planning:
- Full appendix generated:
- Biggest evidence gap:
- Biggest readability issue:
- Required next read:
```
