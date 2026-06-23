# Atomic / Fence / Barrier Golden Spec

Atomic semantics must define request issue, lane participation, return value,
destination register, serialization domain, completion event, and scoreboard
release condition.

Fence semantics must define scope, ordering domain, affected memory spaces,
visibility point, completion condition, and cache flush/invalidate policy.

Barrier semantics must define CTA id, participant count, arrival mask, waiting
warp list, release condition, and release event.

GPGPU-Sim timing notes are not a complete memory consistency model.

