# Atomic, Fence, and Barrier Rules

Synchronization is not a generic memory stall.

Atomic contracts must define operation type, address, lane mask, byte mask,
return-value behavior, destination register if any, completion event,
serialization domain, and scoreboard release condition.

Fence contracts must define scope, ordering domain, affected memory spaces,
visibility point, completion condition, cache flush or invalidate policy, and
stall reason.

Barrier contracts must define CTA id, expected participant count, arrival mask,
release condition, waiting warp list, and release event.

Important caveat: the GPGPU-Sim atomics/fence notes in this reference set are
timing-side evidence only. Full memory consistency semantics must be defined in
the project-owned golden contract or by a future deeper `cuda-sim/memory.cc`
reader pass.

Raw basis: `raw/gpgpu-sim-atomics-fence-consistency-notes.md`.

