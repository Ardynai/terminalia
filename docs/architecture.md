# Terminalia Architecture

## Design principles

1. **Agent as orchestrator, code as tools.** Like WorldClaw, the LLM plans and iterates;
   deterministic Python does geometry. Every stage is a callable tool with a JSON contract.
2. **Explicit world state.** The whole world lives in one `world.json` (scene schema below).
   Any stage can be re-run; the file is the source of truth.
3. **Local-first models.** TRELLIS.2 for assets, ComfyUI diffusion for imagery,
   Wan/LTX for QA video. Cloud APIs are optional accelerators.
4. **Render-inspect-refine.** After placement, render top-down + eye-level views from
   BlenderMCP and let the agent critique before accepting.

## Pipeline stages

### 0. SPEC (`terminalia/spec.py`)
Prompt → structured `WorldSpec` JSON: biomes list, size (hectares), points of interest,
asset themes, time-of-day, camera path intent. The agent writes this; the schema validates it.

### 1. TERRAIN (`terminalia/terrain.py`)
Deterministic, agent-authored:
- Region masks: Voronoi/noise polygons per biome (Red Blob Games style)
- Heightfields: fBm noise × mask weights + geomorphic operators
  (raise_mountains, carve_river, terrace, smooth_coast)
- Output: 16-bit heightmap PNG + region-mask PNGs + splatmaps

The agent composes operators in Python — WorldClaw's key trick — so terrain is
*authored*, not just sampled.

### 2. LAYOUT (`terminalia/layout.py`)
- Render a color-coded **semantic layout map** (each POI = solid color on flat terrain render)
- Pass through image-editing model (Qwen-Image-Edit / Flux Kontext via ComfyUI) to get a
  **composition image** matching the prompt's mood
- Agent decomposes composition into an object list with bounding boxes → world.json

Fallback (no img-edit model): programmatic masks only — paper admits open models are weaker here.

### 3. ASSETS (`terminalia/assets.py`)
- For each object entry: generate concept image (SDXL/Flux, white bg) → TRELLIS.2-4B
  (1024_cascade) → PBR GLB into `assets/<name>/`
- Cache by semantic name; reuse across worlds
- Quality ladder per asset role: hero=1536_cascade(if VRAM ok)/1024_cascade, prop=512

### 4. PLACE (`terminalia/place.py`)
- Ray-cast placement against heightfield: position = surface point, up = normal
- Contact-ratio search: sample k orientations, pick max contact (anti-floating)
- Collision check between placed assets (AABB pass)
- Writes transforms back to world.json

### 5. REFINE (agent loop, BlenderMCP)
- Import GLBs, render top-down + 4 orbit views
- Agent inspects renders (vision), edits placement/scale/material, re-renders
- Max N iterations or until acceptance criteria in spec are met

### 6. EXPORT (`terminalia/export.py`)
- `world.glb` (merged), UE import script (.py macro for UE 5.8),
  flythrough keyframes → Wan 2.2 / LTX-2 image-to-video for QA preview

## Scene schema (world.json)

```jsonc
{
  "version": "0.1",
  "spec": { "prompt": "...", "seed": 42, "size_hectares": 200 },
  "terrain": {
    "heightmap": "out/terrain/hm.png",
    "regions": [ {"name": "volcano", "mask": "...", "biome": "volcanic"} ],
    "operators": ["fbm(seed=42,oct=6)", "raise(volcano,+180m)", "carve_river(...)" ]
  },
  "layout": { "composition_image": "out/layout/comp.png",
              "objects": [ {"id": "temple", "asset": "ruined_temple",
                            "pos": [x,y], "rot_z": 0.7, "scale": 1.2} ] },
  "assets": { "ruined_temple": {"glb": "assets/ruined_temple/mesh.glb", "tris": 12400000} },
  "camera": { "path": [[x,y,z],...] },
  "history": [ {"stage": "place", "at": "...", "notes": "..."} ]
}
```

## Repo layout

```
terminalia/
├── terminalia/           # python package (stages above)
│   ├── cli.py            # `python -m terminalia <cmd>`
│   ├── spec.py  terrain.py  layout.py  assets.py  place.py  refine.py  export.py
│   └── schema.py         # pydantic models = world.json contract
├── skills/               # Hermes agent skill definitions per stage
├── prompts/              # LLM prompts for planning/critique
├── worlds/               # generated worlds (world.json + out/)
├── assets/               # shared asset library (GLB cache)
├── docs/
└── tests/
```

## Relationship to WorldClaw

| WorldClaw | Terminalia |
|---|---|
| Claude Opus planner | Hermes agent (any LLM) |
| GPT-Image-2 layout maps | Qwen-Image-Edit / Flux Kontext / programmatic |
| Hunyuan3D assets | TRELLIS.2-4B (local, MIT) |
| SAM 3 + SAM 3D | TRELLIS.2 direct mesh gen (segmentation optional) |
| BlenderMCP | Same ✓ |
| 4× H20 GPUs | 1× RTX 4090 |

Additions beyond the paper: flythrough QA via Wan/LTX, UE export, splat side-channel
(WorldMirror 2.0) planned for v0.2.
