# ICNT Buffer / Backpressure Contract

Backpressure evidence must distinguish:

- request path `has_buffer` failure;
- response path FIFO full;
- push blocked;
- pop blocked;
- packet volume by class;
- return-to-shader congestion.

Do not report only `NoC slow`.

