# Rocket Generator Reference

This directory records Rocket Chip lessons that are safe to reuse in the GPGPU
skill system. Rocket is used here as a generator, configuration, interface,
MMIO, debug, and verification reference.

Use these lessons for:
- ordered config fragments and resolved config ownership
- system composition roots and generated collateral
- negotiated interface edges, adapters, and protocol monitors
- declarative MMIO register maps and debug/counter blocks
- harness closure, unit-test contracts, fuzzers, trace sinks, and compile-only drift gates

Do not use Rocket as a GPU pipeline reference. Do not copy Rocket scalar
pipeline stages, CLINT or PLIC register layout, TileLink as a mandatory protocol,
or CPU privilege semantics.

Raw reader reports are copied under `raw/`. Curated summaries in this directory
are the preferred AI-facing references for skill rules.
