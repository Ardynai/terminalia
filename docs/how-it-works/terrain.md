# How it works — terrain

**Owns:** turning an operator program into a heightmap + region masks.
**Key files:** `terminalia/terrain.py`, `terminalia/schema.py` (Terrain model).
**Start reading:** `build_terrain()`.

## Main flow

1. Agent (or CLI default) writes a **program**: a list of op dicts
   (`{"op": "mountains", "mask": "region0", "height_m": 180}`).
2. `build_terrain(ops, size, mpp, seed)` executes them in order on a
   `TerrainGrid`.
3. Masks are named and reusable — later ops reference earlier masks by key.
4. Output: 16-bit heightmap PNG + per-region mask PNGs; heights in meters.

## Operator catalog

| Op | Effect |
|---|---|
| `voronoi` | n region masks (biome partition) |
| `radial_mask` | smooth radial blob (islands, craters, POI pads) |
| `fbm` / `ridged` | fractal noise fields |
| `raise` / `depress` | add/subtract masked height |
| `mountains` | ridged noise × mask × height |
| `river` | meandering carve between two points |
| `coast` | clamp sea floor to a shelf depth |
| `terraces` | quantize heights inside a mask (rice paddies / mesa) |
| `normalize` | rescale to [min_m, max_m] |

## Gotchas

- Ops are order-sensitive: `coast` after mountains, `normalize` last.
- `river` uses cumulative random walk — same seed reproduces exactly, but
  changing any earlier op shifts it.
- Heights are meters; the grid is square. `meters_per_pixel` converts px→m
  everywhere downstream (placement, exports).

## Where to start reading

`TerrainGrid.__post_init__` → `_value_noise` → the operator methods →
`build_terrain` dispatch.
