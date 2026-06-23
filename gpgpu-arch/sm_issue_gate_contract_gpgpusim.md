# SM Issue / Non-Issue Contract

Every generated SM design must expose:

- warp valid and exited state;
- barrier, membar, atomic, and memory-backpressure wait state;
- ibuffer valid bit and instruction PC;
- SIMT top PC and active mask;
- scoreboard collision result;
- target pipe availability;
- dual-issue allow/deny result;
- issue event and scoreboard reserve event.

The canonical issue gate order is:

1. warp valid;
2. not waiting at barrier, membar, atomic, or dependency barrier;
3. ibuffer has instruction;
4. SIMT top PC matches instruction PC;
5. scoreboard has no collision;
6. target pipe has a free slot;
7. dual-issue policy allows;
8. issue and reserve scoreboard.

