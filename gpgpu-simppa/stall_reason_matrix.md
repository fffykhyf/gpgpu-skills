# Stall Reason Matrix

Stall matrices must keep dimensions explicit:

- scheduler reason;
- memory access type;
- memory stall reason;
- cache request status;
- reservation fail reason;
- queue boundary;
- sync reason.

Do not collapse `cache_miss`, `cache_reservation_fail`, `mshr_fail`, and
`icnt_req_backpressure`.

