# Non-Issue Reason Taxonomy

Use one primary reason per non-issued warp:

- `idle_control`
- `ibuffer_empty`
- `simt_redirect`
- `scoreboard_wait`
- `pipe_unavailable`
- `barrier_wait`
- `membar_wait`
- `atomic_wait`
- `memory_backpressure`

Do not report only low IPC. Low IPC requires a reason distribution and enough
state to prove why each ready-looking warp did not issue.

