# Terminalia ComfyUI Workflows

Ready-to-run API-format workflow templates. Copy into
`C:\Users\Josh\Documents\ComfyUI\user\default\workflows\` (or submit via the API)
and fill in your file names.

All templates were validated against Josh's live ComfyUI 0.27.x node set.

| Template | Purpose | Key nodes |
|---|---|---|
| `world_asset_trellis2_api.json` | Concept image → textured GLB asset with cleanup chain | Trellis2-GGUF, FillHoles, Simplify |
| `video_to_frames_api.json` | Video → frame PNGs (fps override, sampling) | VHS_LoadVideo, SaveImage |
| `character_face_lock_api.json` | Swap canonical character face onto renders | ReActor + CodeFormer |
| `identity_consistency_instantid_api.json` | Identity-consistent generations from one ref image | InstantID |
| `background_removal_birefnet_api.json` | Clean alpha cutouts for mesh input | BiRefNetRMBG / RMBG |
| `upscale_4x_api.json` | 4× upscale of world renders | 4x-UltraSharp |
| `flythrough_wan22_stub_api.json` | Keyframe inputs stub — pair with native Wan 2.2 I2V template | LoadImage |

## Optional ComfyUI runtime references

- [ComfyUI Sage EasyInstall](../docs/references/comfyui-sage-easyinstall.md) —
  optional Windows-portable SageAttention/Triton installer for accelerating
  compatible local ComfyUI runs. It does not contain a world-generation
  workflow and is not part of Terminalia's deterministic world model. Use it as
  a local runtime optimization only after same-seed A/B validation.

## Gotchas encoded in these templates

1. **No top-level `_comment` strings** — crashes ComfyUI 0.27.x validation.
2. **VHS_LoadVideo requires ALL params** even when schema shows defaults.
3. **Trellis2 `rotate_x/y/z` required** on VoxelToTrimesh even at 0.0.
4. **`remove_background: true` is mandatory** before TRELLIS generation.

## Node pack prerequisites

- ComfyUI-VideoHelperSuite ✓ installed
- comfyui-reactor ✓ installed (15 nodes incl. face models)
- ComfyUI_InstantID ✓ installed (+ insightface, onnxruntime)
- ComfyUI-RMBG (BiRefNet) ✓ installed
- ComfyUI-Trellis2-GGUF ✓ installed
