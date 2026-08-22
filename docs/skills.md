# Terminalia agent skills

Each pipeline stage maps to a Hermes agent skill. The agent orchestrates; these define
the contracts.

## terminalia-terrain
Author a terrain operator program for a WorldSpec.
- Input: WorldSpec JSON (biomes, POIs, size)
- Output: ops list consumed by `terminalia.terrain.build_terrain`
- Guidance: 1 radial/voronoi mask per biome; ridged mountains on highlands;
  carve rivers from peaks to coast; always end with `coast` + `normalize`.
- Verify: render heightmap preview, check silhouette against prompt mood.

## terminalia-layout
Decompose the world into placed objects.
- Read heightmap + region masks → pick POI sites (flat areas, region centers, coastlines)
- Optionally generate composition image via ComfyUI img-edit (Qwen-Image-Edit GGUF)
- Emit `layout.objects[]` with roles: hero / prop / foliage / terrain_feature

## terminalia-assets
Fill the asset library via ComfyUI + TRELLIS.2 (`terminalia.assets`).
- Concept: SDXL white-bg render per object description
- Mesh: TRELLIS.2-4B, preset by role — hero:1024_cascade, prop:512
- Cache hits skip generation. Record tris count in world.json.

## terminalia-place
Run placement search (`terminalia.place`) for every layout object against the heightmap.
- Water objects (ships/boats): min_contact 0.4, slope_limit 50°
- Structures: min_contact 0.7, slope_limit 25°
- Run collision pass; nudge or re-search failures; update world.json transforms

## terminalia-refine
BlenderMCP loop:
1. Import all GLBs at their placements (bpy.ops.import_scene.gltf)
2. Render top-down + 4 orbit views
3. Agent vision-critique: floating? overlaps? scale mismatch vs spec?
4. Fix via execute_code (transform edits) and repeat ≤3 iterations

## terminalia-export
- Merge to single GLB export
- Generate UE 5.8 import python macro
- Camera path → Wan 2.2 I2V flythrough renders for review
