# L1 Cache or Global Adapter Contract

`L1 cache` is a hardware cache term. A capability profile may choose either a
private L1 cache or a direct global adapter.

```yaml
l1_cache_or_global_adapter:
  mode: direct_global_adapter | private_l1_cache
  hit_policy:
  miss_policy:
  mshr_required:
  write_policy:
  response_order_policy:
  visibility_boundary:
```

If `mode: direct_global_adapter`, the contract must still say whether hit/miss,
MSHR, response reorder, and visibility effects exist. Hidden default behavior is
not allowed.
