# Roadmap

## v0.1 — Terrain + placement engine ✅ (this release)
- [x] Scene schema (world.json, pydantic)
- [x] Procedural terrain: fbm/ridged/voronoi masks, raise/depress/mountains,
      river carving, coast smoothing, terraces, normalize
- [x] Heightmap + mask export
- [x] Contact-ratio placement search with slope limits
- [x] Collision pass
- [x] ComfyUI asset generation bindings (concept → TRELLIS.2 GLB)
- [x] CLI: generate / validate

## v0.2 — Agent integration
- [ ] Hermes skills from docs/skills.md as installable skills
- [ ] Layout stage: composition image via Qwen-Image-Edit-GGUF (installed)
- [ ] BlenderMCP refine loop automation
- [ ] Asset cache shared across worlds

## v0.3 — Video QA + engine export
- [ ] Wan 2.2 I2V flythrough renders (Wan2GP integration)
- [ ] UE 5.8 import macro generator
- [ ] WorldMirror 2.0 splat side-channel (video → 3DGS overlay)

## v0.4 — Scale
- [ ] Multi-region streaming (adjacent world tiles)
- [ ] Asset LOD baking (Blender decimate via MCP)
- [ ] Splat→mesh bridge (SuGaR-class) for photo-real regions

## Ideas
- Biome-aware texture splatmaps for UE landscape material
- Prompt → multiple candidate worlds → agent picks best
- Community asset pack format
