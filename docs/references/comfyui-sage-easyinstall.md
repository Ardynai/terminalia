# ComfyUI Sage EasyInstall — optional local acceleration reference

**Status:** optional operator reference; not a Terminalia dependency  
**Scope:** Windows 10/11, NVIDIA GPU, ComfyUI portable only  
**Assessed upstream revision:** `mickmumpitz/ComfyUI-Sage-EasyInstall@297c4b0a03bcea55bc3f4cc810ef138000b9cb77`

## Fit decision

This project is **not another world-generation workflow**. It is an installer for
SageAttention, `triton-windows`, embedded-Python headers/libraries, an optional
Blackwell fp16 compatibility node, and a ComfyUI launcher that adds
`--use-sage-attention`.

Terminalia must not vendor it, import it, or make it part of `world.json`.
Terminalia's source-of-truth and deterministic stages remain unchanged:

```text
world.json
→ terrain
→ layout
→ asset generation through a Backend
→ placement
→ refine
→ export / video
```

The useful placement is narrower: an operator may use it to accelerate a
**separate local ComfyUI portable instance** that executes Terminalia's existing
API-format workflows. The most relevant candidate is Wan-based flythrough/video
sampling. Treat speed as an optimization, never as a workflow or quality gate.

## Why it stays outside the core

- It is Windows- and ComfyUI-portable-specific; Terminalia also supports Linux,
  Apple Silicon through remote backends, Comfy Cloud, RunPod, and custom HTTP.
- It mutates the ComfyUI embedded Python environment and installs binary wheels.
- It does not define Terminalia world specifications, terrain operators, layout,
  placement, assets, engine exports, or artifact provenance.
- SageAttention compatibility varies by model, ComfyUI version, Torch/CUDA
  combination, and custom nodes.
- Terminalia's backend API already treats the local ComfyUI process as opaque;
  no Python code change is required for SageAttention.

## Recommended operating profile

1. Make a disposable copy of a known-good ComfyUI portable installation.
2. Pin and inspect the upstream release or commit before running any batch file.
3. Prefer `install-sage-only.bat`.
4. Do not enable ComfyUI Manager or network `--listen` through the broader setup
   installer unless separately reviewed and intentionally required.
5. Keep the normal non-Sage launcher for immediate rollback.
6. The generated launcher normally uses ComfyUI's default port. Either:
   - set `TERMINALIA_COMFY_PORT=8188`, or
   - append `--port 8000` so it matches Terminalia's default local backend.
7. On an RTX 4090, skip the optional RTX 50-series/Blackwell fp16 fix unless a
   separately reproduced issue proves it is needed.
8. Never expose the ComfyUI API or custom-node surface beyond a trusted host.

## Acceptance test

Run one representative Terminalia workflow twice with identical inputs:

```text
baseline launcher + same workflow + same seed
Sage launcher    + same workflow + same seed
```

Record:

- ComfyUI commit;
- workflow hash;
- model and LoRA hashes;
- Torch, CUDA, Triton, and SageAttention versions;
- GPU and driver;
- wall-clock duration and peak VRAM;
- output hashes where deterministic;
- image/video quality review;
- temporal flicker, black frames, NaNs, crashes, or node fallback warnings.

Promote the Sage launcher only when the exact workflow is faster **and** all
quality and stability checks match the baseline. Disable SageAttention and use
the ordinary launcher if any regression appears.

## Workflow-specific posture

| Terminalia stage | Posture |
|---|---|
| Terrain, masks, layout, placement, collision, export | No effect; pure Python/engine-neutral |
| TRELLIS.2 asset workflow | Experimental only; validate carefully and keep a baseline launcher |
| Qwen/Flux concept or edit workflows | Experimental only; no blanket enablement |
| Wan 2.2 flythrough/video | Best candidate for measured acceleration, but validate temporal consistency |
| LTX video | Experimental; validate the exact model and node path |
| Cloud/RunPod/custom backends | Not applicable unless that image already provides SageAttention |

## Security and rollback

The installer is an executable supply-chain surface. It can install packages,
copy headers/libraries, add a custom node, and create launch scripts. Run it only
inside a controlled ComfyUI clone, preserve the original environment, and never
commit the installed wheels or modified embedded-Python tree to Terminalia.

Rollback is operational, not a Terminalia code change: stop the Sage launcher
and start the ordinary ComfyUI launcher. If the portable environment was
mutated incompatibly, discard the clone and restore the known-good copy.

## Upstream

- Repository: <https://github.com/mickmumpitz/ComfyUI-Sage-EasyInstall>
- Upstream SageAttention: <https://github.com/thu-ml/SageAttention>

Reassess compatibility before every major ComfyUI, Torch, CUDA, or model-stack
upgrade. Do not treat an earlier successful test as a permanent compatibility
guarantee.
