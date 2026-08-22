# How it works — placement

**Owns:** finding physically-plausible positions/rotations for every layout
object on the heightmap.
**Key files:** `terminalia/place.py`, `terminalia/layout.py` (site pre-selection).
**Start reading:** `find_placement()`.

## Main flow

1. `layout.select_sites()` scores flatness (integral-image local std) inside
   each region mask and proposes sites, honoring min separation.
2. `find_placement()` samples candidate spots around the requested center:
   - slope gate: rejects spots steeper than `slope_limit_deg`
   - contact-ratio search: 9 footprint probes per rotation, best of 6 rotations
3. `resolve_collisions()` runs an AABB pass; overlapping ids are reported for
   nudging or re-search.

## Contact ratio

Fraction of footprint ring samples whose terrain height is within tolerance of
the base plane. 1.0 = perfectly seated. Defaults: structures ≥0.7, foliage ≥0.4,
water vehicles ≥0.4 with wider slope limits.

## Gotchas

- Water objects fail strict search — lower `min_contact` and widen
  `slope_limit_deg` (ships sit "on" water planes, not terrain).
- Very large heroes may need multiple searches at different centers; the agent
  iterates rather than one call solving everything.

## Where to start reading

`estimate_contact_ratio` → `find_placement` → `resolve_collisions`.
