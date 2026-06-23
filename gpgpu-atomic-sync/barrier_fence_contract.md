# Barrier and Fence Contract

This contract defines hierarchical barrier and fence semantics.

## Barrier Scopes

Supported barrier scopes:
- warp barrier
- wavefront barrier
- CU barrier
- grid barrier

`warp barrier` appears only for compatibility with legacy wording. The canonical
execution unit is `wavefront barrier`.

## Wavefront Barrier

A wavefront barrier synchronizes active lanes inside one wavefront. It must
define:
- participating lane mask
- release condition
- interaction with EXEC mask
- trace event

## CU Barrier

A CU barrier synchronizes wavefronts resident in one CU or one workgroup mapped
to one CU. It must define:
- participant wavefront set
- arrival bitmap
- release bitmap
- timeout or unsupported condition
- LDS visibility rule

## Grid Barrier

A grid barrier synchronizes across CUs. It must define:
- participant CU set
- global arrival count
- memory visibility rule
- unsupported fallback if the hardware/runtime cannot guarantee it

## Fence Ordering Semantics

fence ordering semantics must define:
- scope: wavefront, CU, device, or system
- affected memory spaces
- request drain condition
- cache visibility action
- atomic interaction
- completion event

## Hierarchical Rule

hierarchical barrier and fence semantics:
- wavefront barrier must not imply CU barrier
- CU barrier must not imply grid barrier unless explicitly declared
- fence scope must be at least as large as the memory visibility claim
- grid barrier requires fabric and memory-system participation

## Failure Modes

Failures include:
- barrier participant mismatch
- fence drain incomplete
- missing memory visibility action
- grid barrier used when unsupported
- barrier/fence trace missing scope
