# Case Gate Reference

Structured cases should describe input artifacts, expected outputs, failure
modes, required gates, forbidden outputs, and patch routing. Legacy
`required_evidence` tokens are allowed during migration, but every new token
should map to a schema field, output field, taxonomy entry, validation gate, or
contract path.

## Allowed Required Gates

- schema_valid
- contract_paths_resolvable
- canonical_hash_present
- canonical_hash_verified
- producer_skill_valid
- consumer_skill_valid
- failure_mode_known
- patch_route_known
- required_revalidation_known
- forbidden_outputs_absent
- pass_evidence_present
- regression_fingerprint_present
- correctness_gate_present
- yosys_profile_known
- backend_claim_boundary_checked

## Patch Route Policy

`patch_route.expected` may be `none` when the case is expected to pass without a
rewrite. Otherwise it must name a route in `shared/tables/revalidation_routing_table.yaml`
or `shared/tables/rewrite_rules.yaml`.

## Evidence Mapping Policy

Each non-legacy evidence token should be resolvable to one of:

- an expected output artifact name
- a field in the expected output schema
- a failure or root-cause taxonomy entry
- an allowed required gate
- a contract path in `SYSTEM_CONTRACT_IR`
