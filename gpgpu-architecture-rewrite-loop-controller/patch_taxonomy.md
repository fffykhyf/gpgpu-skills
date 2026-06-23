# Patch Taxonomy

## Patch Classes

- `ARCHITECTURE_PATCH`
- `CONTRACT_PATCH`
- `RTL_PATCH`
- `TEST_EVIDENCE_PATCH`

## Patch Record

Each patch must include:

- patch target
- owner module
- expected impact
- required revalidation gates
- regression risks
- rejected alternatives

## Forbidden Behavior

The controller must not directly mutate IR. It emits patch plans that route back to the owning module.
