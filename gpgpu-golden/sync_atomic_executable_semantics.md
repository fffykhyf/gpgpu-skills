# Synchronization and Atomic Executable Semantics

Golden synchronization semantics must distinguish atomic, fence, barrier, and
WSYNC behavior.

Required functions:

- `execute_atomic_serialization()`
- `execute_fence_drain()`
- `execute_barrier_arrive_wait_release()`
- `execute_wsync_drain()`

Rules:

- Atomic visibility is not fence visibility.
- Fence is not barrier arrival.
- Barrier release does not imply memory visibility unless explicitly frozen.
- WSYNC drains prior work and is not a scoreboard hazard.
