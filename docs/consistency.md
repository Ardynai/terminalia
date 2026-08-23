# Character & Asset Consistency Across Generations

The complete strategy for keeping characters, creatures, and props identical
across videos, renders, and regenerations. All tools verified in this stack.

## The 5-layer consistency stack

### Layer 1 — 3D ground truth (STRONGEST)
Your character lives as a GLB mesh. Renders from any angle are *the same
character by definition*.
- Blender turntable rig (built via MCP, see `patches/` + scripts in repo root):
  studio lighting, 85mm camera at chest height, renders N canonical views
- Views: front / three-quarter / side / back @1024px → ComfyUI `input/charsheet/`
- Re-render anytime; the mesh IS the identity

**Verified**: robot character sheet rendered 4 views via blender-mcp ✓

### Layer 2 — Reference-conditioned generation (image)
- **Qwen-Image-Edit GGUF** (installed): "same character, <new pose/angle>"
  conditioned on the reference — identity carried through edit conditioning
- **InstantID** (just installed): face identity injection for humans
  (`ApplyInstantIDAdvanced`, weight 1.0, insightface CUDA)
- **IPAdapter-class models**: style+identity transfer (add if needed)

Template: `workflows/api/identity_consistency_instantid_api.json`

### Layer 3 — Face swap (post-generation lock)
- **ReActor suite** (15 nodes): swap the canonical face onto ANY generated
  frame where the character appears, CodeFormer restore at 0.5 visibility
- Build one approved face model (`ReActorBuildFaceModel`) and reuse everywhere

Template: `workflows/api/character_face_lock_api.json`

### Layer 4 — Style LoRA (cross-world consistency)
- **ai-toolkit** (UI :8670, CLI configs in config/examples/) trains a LoRA on
  your character sheet renders or world art
- Load with `LoraLoaderModelOnly` in every asset/video workflow
- Deterministic seeds derive from the world seed

### Layer 5 — Prompt discipline
Same descriptive tokens in every prompt ("the rust-colored maintenance robot
with cyan optic stripe") + fixed negative prompts. Weak alone, essential
combined.

## Recommended pipeline order

```
GLB mesh (ground truth)
  → Blender turntable → 4-view sheet @1024
    → ai-toolkit LoRA train on sheet (30-50 imgs equiv)
      → Qwen-Image-Edit for new poses (conditioned on ref)
        → InstantID inject for closeups (humans)
          → ReActor canonical-face lock on final frames
            → Wan 2.2 I2V flythrough (first frame = locked render)
```

## Video generation consistency specifics

1. First/last frame control: Wan FLF2V with locked renders as endpoints
2. Per-shot: render the shot's start frame in Blender (camera at keyframe),
   generate video FROM that frame — camera motion matches the world exactly
3. Multi-character scenes: separate LoRAs per character + regional prompting
