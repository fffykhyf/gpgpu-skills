# SM Issue Gate Contract

## Gate Order

1. warp valid
2. not waiting at barrier, membar, atomic, or dependency barrier
3. ibuffer has instruction
4. SIMT top PC matches instruction PC
5. scoreboard has no collision
6. target pipe has free slot
7. dual-issue policy allows
8. issue and reserve scoreboard

## Observable State

| Field | Producer | Consumer |
|---|---|---|
| warp valid | RTL scheduler | simppa |
| SIMT top PC | SIMT state | scheduler |
| active mask | SIMT state | execution lanes |
| scoreboard collision | scoreboard | scheduler |
| pipe availability | execution pipe | scheduler |
| non-issue reason | scheduler | simppa/loop |

## Required Rule

Every non-issued warp must produce exactly one primary `non_issue_reason`.

