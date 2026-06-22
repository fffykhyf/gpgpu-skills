# Sharding Protocol

## When to Shard

Shard if:

- the corpus does not fit safely in context
- the corpus is over 200 dense pages
- the repo has more than 5 major subsystems
- the planner asks for cross-document or cross-repo comparison
- a single report would exceed the selected output profile

## Shard Types

### Document Shards

Use:

- one paper per shard
- 30-80 pages per shard for books or manuals
- section-based shards for ISA manuals, architecture specs, and long standards

### Repository Shards

Prefer semantic shards:

1. project rules and source-of-truth docs
2. specs and architecture docs
3. golden model / simulator
4. ISA / decode / frontend
5. scheduler / scoreboard / SIMT state
6. memory path
7. runtime / launch / ABI
8. tests / traces / logs
9. synthesis / PPA / performance

## Shard IDs

Use stable IDs:

- `DOC-001`
- `REPO-001`
- `SYN-001`

## Claim IDs

Use stable claim IDs:

- `DOC-001-C001`
- `REPO-003-C014`
- `SYN-001-C007`

Claim status:

- `CONFIRMED`
- `INFERRED`
- `UNCERTAIN`
- `CONFLICTED`
- `MISSING`

## Per-Shard Output Rule

Each shard visible output must be short:

- max 5 findings
- max 5 evidence claims
- max 3 open questions
- max 3 next-shard dependencies

Full shard evidence goes to appendix only if `write_to` is provided or the planner requests `model-evidence` / `full-audit`.

## Shard Manifest

Before reading shards, produce:

| Shard ID | Scope | Files / Pages | Purpose | Depends on | Expected Output |
|---|---|---|---|---|---|

## Cross-Shard Synthesis

Do not concatenate shard reports.

Instead, produce one consolidated synthesis:

- executive handoff
- consolidated claim index
- consolidated architecture map
- contradictions
- missing contracts
- GPT-5.5 decisions needed
- quality gate

The consolidated synthesis follows `output-policy.md`; long evidence stays in appendix.
