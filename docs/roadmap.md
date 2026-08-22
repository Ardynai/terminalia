# Roadmap

Honest status markers: ✅ shipped · 🔨 in progress · 🧭 planned · 💡 idea

## v0.1 — Terrain + placement engine ✅
- [x] Scene schema (`world.json`, pydantic)
- [x] Procedural terrain operator engine (fbm/ridged/voronoi/mountains/rivers/
      coasts/terraces)
- [x] Heightmap + region-mask export
- [x] Contact-ratio placement search with slope limits
- [x] Collision pass
- [x] ComfyUI asset bindings (SDXL concept → TRELLIS.2 GLB)
- [x] CLI (generate / validate)

## v0.2 — Engines, video, consistency ✅
- [x] UE 5.x Python import macro
- [x] Unity editor script + manifest
- [x] Godot 4 scene writer
- [x] Generic glTF bundle + manifest
- [x] Camera keyframe sampler + flythrough specs (Wan 2.2 / LTX-2)
- [x] Character lock (Qwen-Image-Edit multi-view sheets)
- [x] Face swap spec (ReActor + CodeFormer)
- [x] Layout stage: flat-area scoring, region-masked site selection
- [x] Repo integrations registry (17 tools mapped to pipeline roles)

## v0.3 — Compute backends 🔨 (this release)
- [x] Backend abstraction (local / Comfy Cloud / RunPod / custom)
- [x] GpuProfile tiers (12GB → 128GB) with automatic preset scaling
- [x] `resolve()` one-call setup with auto-detection
- [ ] RunPod serverless end-to-end test on a real endpoint
- [ ] Comfy Cloud paid-tier submission test
- [ ] Cost estimator per world (images × meshes × video-seconds per backend)

## v0.4 — Agent integration 🧭
- [ ] Hermes skills from docs/skills.md as installable skill pack
- [ ] BlenderMCP refine loop automation (import → render → critique → fix)
- [ ] Vision-based acceptance criteria for refine iterations
- [ ] Layout composition images via Qwen-Image-Edit-GGUF / Flux Kontext

## v0.5 — Video & characters 🧭
- [ ] Wan 2.2 I2V/FLF2V flythrough execution end-to-end
- [ ] LTX-2 joint audio+video cutscenes
- [ ] Character sheet pipeline → canonical face bank → ReActor application
- [ ] Audio2Face-3D NPC facial animation bridge
- [ ] omnivoice/magenta narration+score packaging

## v0.6 — Scale & capture 🧭
- [ ] Multi-region streaming worlds (adjacent tiles, shared borders)
- [ ] Asset LOD baking via Blender decimation
- [ ] WorldMirror 2.0 splat side-channel → SuperSplat edit → re-import
- [ ] Splat→mesh conversion (SuGaR-class) — biggest known gap

## 💡 Ideas parking lot
- Prompt → N candidate worlds → agent ranks and picks
- Biome-aware UE landscape material/splatmap generation
- Community world-template format (share seeds + op programs, not meshes)
- DGX Spark multi-model residency: terrain+asset+video models hot simultaneously
- Terminalia Server: thin web UI over the pipeline for non-technical creators
