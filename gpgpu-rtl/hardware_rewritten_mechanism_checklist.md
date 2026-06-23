# Hardware-Rewritten Mechanism Checklist

Before binding imported evidence to RTL, confirm:

- state owner is explicit;
- interface fields are structured;
- valid/ready or request/response protocol is checked;
- fixed timing is replaced by a hardware pipeline or queue contract;
- counters have producer tap points;
- simulator-only artifacts are rejected or quarantined in compatibility notes.

