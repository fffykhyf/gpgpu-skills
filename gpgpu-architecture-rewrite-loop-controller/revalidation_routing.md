# Revalidation Routing

Every patch plan must declare the modules and gates that must rerun.

## Routes

| Patch class | Required route |
|---|---|
| `ARCHITECTURE_PATCH` | Module 1 -> Module 2 -> Module 3 -> Module 4 |
| `CONTRACT_PATCH` | Module 2 -> Module 3 -> Module 4 |
| `RTL_PATCH` | Module 3 -> Module 4 |
| `TEST_EVIDENCE_PATCH` | Module 4 |

## Gate

No rewrite is accepted until its route produces fresh evidence and a new attribution report.
