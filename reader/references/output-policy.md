# Output Policy

## Concepts

`depth` controls how deeply the corpus is read.

`output_profile` controls how much is written back and who the output is optimized for.

The default is:

```yaml
depth: normal
output_profile: human-handoff
```

This means: read at normal depth, but return a concise decision handoff.

## Output Profiles

### human-handoff

Default profile.

Use when the report is meant for a human and GPT-5.5 planner.

Visible output targets:

- `scan`: 500-1200 words
- `normal`: 1000-2500 words
- `deep`: 2000-4000 words

Visible output rules:

- no full evidence tables
- no full contract tables
- no table wider than 5 columns
- max 7 top findings for `normal`
- max 10 top findings for `deep`
- max 10 visible evidence claims for `normal`
- max 20 visible evidence claims for `deep`
- max 5 risks
- max 5 next actions

### model-evidence

Use when GPT-5.5 needs more evidence than the visible handoff can carry.

Visible output:

- compact handoff only
- appendix path and status
- compact quality gate

Appendix:

- full architecture or document map
- full state contracts
- full interface contracts
- full evidence index
- missing contracts
- quality gate

### full-audit

Use only for deep review or audit.

Output:

- full handoff
- full appendix
- full claim index
- full contradiction analysis
- full quality gate

This profile may print long material in chat only when explicitly requested. Prefer writing the appendix to `write_to`.

## Depth Limits

### scan

Purpose:

- triage relevance
- decide whether to continue reading

Visible output:

- 500-1200 words
- max 5 findings
- max 5 evidence claims
- max 5 open questions
- no full tables

### normal

Purpose:

- routine GPT-5.5 handoff
- enough evidence for next-step planning

Visible output:

- 1000-2500 words
- max 7 findings
- max 10 evidence claims
- max 5 risks
- max 5 next actions

Appendix:

- optional, only if `write_to` is provided or `output_profile: model-evidence`

### deep

Purpose:

- support design decision or architecture review
- verify state contracts, interface contracts, and contradictions

Visible output:

- 2000-4000 words
- max 10 findings
- max 20 visible evidence claims

Appendix:

- recommended
- required for `output_profile: model-evidence` or `output_profile: full-audit`

## Universal Rules

1. Do not mechanically fill templates.
2. Do not output empty tables.
3. Move full tables to appendix.
4. Keep the first page decision-oriented.
5. Every visible item must help GPT-5.5 decide what to do next.
6. Prefer bullets over wide tables in Part A.
7. If evidence is important but bulky, cite the appendix rather than printing it.
8. If a report would exceed the selected profile, shard or write an appendix.
