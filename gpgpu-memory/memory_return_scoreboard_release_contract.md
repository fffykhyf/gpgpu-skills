# Memory Return / Scoreboard Release Contract

Return path must preserve:

- request id;
- original warp id;
- destination register;
- response packet id;
- return queue boundary;
- final response event;
- scoreboard release event.

Loads and atomics with destination registers must not release scoreboard before
the final core-visible response.

