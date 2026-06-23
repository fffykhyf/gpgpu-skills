# Scheduler-Visible State Contract

Required scheduler-visible state:

- `warp_state`: valid, exited, CTA id, next PC, ibuffer valid, outstanding
  memory and sync waits.
- `SIMT_state`: warp id, PC, active mask, reconvergence PC, call depth,
  divergence event.
- `Scoreboard_state`: warp id, pending destination registers, long-op
  destination registers, reserve event, release event, collision result.
- `pipe_state`: pipe class, availability, selected issue slot, dual-issue
  restriction.

SIMT owns PC/control masks. Scoreboard owns register dependency hazards.

