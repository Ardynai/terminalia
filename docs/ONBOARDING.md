# Onboarding — first world in 10 minutes

## 0. Prerequisites

- Python 3.11+
- A ComfyUI endpoint: local install, Comfy Cloud key, or RunPod serverless
- (Optional) Blender 5.1 + blender-mcp addon for the refine loop
- (Optional) UE 5.8 / Unity / Godot for engine import

## 1. Install

```bash
git clone <repo-url> terminalia && cd terminalia
pip install -e .
python -m terminalia validate --help   # sanity check
```

## 2. Point at compute

Pick ONE:

```bash
# A. Local ComfyUI (auto-detected on :8000; set port if different)
export TERMINALIA_COMFY_PORT=8000

# B. Comfy Cloud (paid credits)
export COMFY_CLOUD_API_KEY=comfyui-...

# C. RunPod serverless
export RUNPOD_API_KEY=... 
export RUNPOD_ENDPOINT_ID=...
```

## 3. Generate

```bash
python -m terminalia generate \
    --prompt "volcanic island with a ruined temple and pirate cove" \
    --name my-first-world --seed 42
```

Output lands in `worlds/my-first-world/`:
- `world.json` — the whole world state
- `out/terrain/hm.png` + region masks

## 4. Continue the pipeline

Stages after terrain are driven by agent skills (see `docs/skills.md`) or
directly as library calls:

```python
from terminalia import assets, place, layout, video, export

# concept + mesh per object
glb = assets.generate_mesh("hermes_robot.png", out_dir="assets/robot", name="robot")

# placement
from terminalia.place import find_placement
# ... see docs/how-it-works/placement.md

# export to engines
world = {"layout": {"objects": {...}}, "terrain": {...}, "assets": {...}}
export.write_ue_import_script("worlds/my-first-world", world)
```

## 5. Where the tests are

`tests/test_smoke.py` — run from repo root:

```bash
python tests/test_smoke.py   # ALL TESTS PASS expected
```

## Making a safe first change

1. Pick a stage module (`terminalia/*.py`) — each is self-contained.
2. Add/adjust a function with JSON-shaped inputs/outputs.
3. Extend `tests/test_smoke.py` or add `tests/test_<stage>.py`.
4. Update the matching `docs/how-it-works/<stage>.md` in the same PR.

## Conventions

- Deterministic given seed — no ambient randomness in stages.
- Backends via `terminalia.backends`; never hardcode URLs/ports.
- Minimal-code discipline in `AGENTS.md` applies to every contribution.
