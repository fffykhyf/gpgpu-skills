# Stable Counter Manifest

Every counter must record:

- counter name;
- producer module;
- producer event;
- meaning;
- unit;
- sample window;
- status: `producer-backed`, `defined-only`, or `parser-only`;
- used by;
- stable or debug.

Stable root-cause and regression claims require producer-backed counters.

