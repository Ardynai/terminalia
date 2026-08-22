# Terminalia

**Agentic 3D open-world generation at scale — built from your own stack.**

Terminalia is a WorldClaw-style (arXiv 2608.05248) pipeline that turns a text prompt into an
explorable, editable 3D world: procedural terrain → LLM-planned layout → generated assets →
physics-placed props → rendered flythroughs → game-engine import. It runs entirely on local
models + the agent itself, no Tencent code required.

```
prompt ──▶ TERRAIN      procedural heightfields from agent-authored masks & noise
       ──▶ LAYOUT       semantic region map + composition plan (image-editing model)
       ──▶ ASSETS       TRELLIS.2-4B image→PBR mesh via ComfyUI
       ──▶ PLACE        segment → reconstruct → ray-cast placement (anti-floating)
       ──▶ REFINE       BlenderMCP render-inspect-refine loop
       ──▶ EXPORT       GLB · UE 5.8 project · Wan/LTX flythrough QA renders
```

## Why "Terminalia"

The terminal is where it's built; the world is what comes out.

## Status

`v0.1.0-alpha` — architecture + terrain engine + scene schema implemented.
Layout/asset/place stages are wired to Hermes agent skills (see `skills/`).

## Requirements

- Windows 11 + RTX 4090 (24GB) — all local models fit
- ComfyUI running on `127.0.0.1:8000` with Trellis2-GGUF nodes
- Blender 5.1 with blender-mcp addon (port 9876)
- Hermes Agent (the orchestrator), or any agent that can run Python + call MCP tools
- Optional: UE 5.8 for import, Wan2GP / LTX-2 for flythrough QA

## Quick start

```powershell
# generate a 2km island world from one line:
python -m terminalia generate --prompt "volcanic island with a ruined temple and pirate cove" --seed 42
```

See [docs/architecture.md](docs/architecture.md) for the full pipeline design.

## License

MIT for Terminalia code. Upstream model licenses apply to generated content
(TRELLIS.2: MIT ✓ · Hunyuan3D-2.x: community · check per asset source).
