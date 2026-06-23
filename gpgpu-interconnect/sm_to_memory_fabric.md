# SM To Memory Fabric

This contract defines how SM memory requests enter shared cache and DRAM
resources.

## Hierarchy

SM -> L1 -> L2 -> DRAM

Required hierarchy fields:
- `sm_id`
- `l1_instance_id`
- `l2_slice_id`
- `dram_channel_id`
- `request_class`
- `ordering_scope`
- `source_bundle_id`

## Request Merging Across SM

request merging across SM is allowed only when all merged requests have:
- compatible access type
- compatible address range
- compatible byte enables
- compatible memory ordering scope
- no atomic serialization conflict
- no fence drain dependency

Merged requests must retain source SM and warp contributor lists.

## L2 Cache Slicing Policy

L2 cache slicing policy must define:
- address-to-slice function
- source-SM override if present
- slice queue limits
- hit/miss trace fields
- response routing back to source SM

## Trace Contract

Every fabric trace event must include:
- source SM
- route path
- L1 result if modeled
- L2 slice result
- DRAM channel if accessed
- merge group ID if merged
- response target SM

## Acceptance

L4 interconnect passes only if:
- explicit NoC routing exists
- each request has a source SM
- merged requests preserve visibility and response routing
- fabric contention can be attributed to source SM and route segment
