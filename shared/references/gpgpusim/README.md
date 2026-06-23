# GPGPU-Sim Evidence References

This directory is evidence reference, not a design source of truth.

All imported mechanisms must be rewritten into project-owned contracts before
they can affect architecture, golden semantics, runtime ABI, RTL, counters, or
rewrite routing. The raw reader reports live in `raw/`; skill files must cite
the rule they adopt, not paste GPGPU-Sim implementation details as design truth.

Required intake order:

1. `source_map.md`
2. `design_rules.md`
3. `do_not_copy.md`
4. `config_parameter_taxonomy.md`
5. `scheduler_scoreboard_simt.md`
6. `memory_coalescing.md`
7. `l2_noc_dram.md`
8. `atomic_fence_barrier.md`
9. `counter_stall_taxonomy.md`
10. `performance_attribution.md`
11. `power_energy_boundary.md`

Global rule: classify every imported state, parameter, and counter before a
skill uses it.

