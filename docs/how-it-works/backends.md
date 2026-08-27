# How it works — compute backends

**Owns:** routing every GPU stage to local ComfyUI, Comfy Cloud, RunPod, or any
HTTP-compatible endpoint; scaling quality presets to available VRAM.
**Key files:** `terminalia/backends.py`.
**Start reading:** `resolve()`.

## Main flow

`resolve()` → `detect_backends()` (health-probes in preference order) →
`pick_backend()` (explicit preference or first reachable) → returns
`(Backend, GpuProfile)`.

## Backends

| Backend | Auth | Cost | Notes |
|---|---|---|---|
| `local-comfy` | none | free | port via `TERMINALIA_COMFY_PORT` (default 8000) |
| `comfy-cloud` | `X-API-Key` | credits | `COMFY_CLOUD_API_KEY`; free tier is read-only |
| `runpod-serverless` | Bearer | $/sec | `RUNPOD_API_KEY` + `RUNPOD_ENDPOINT_ID`; payload wrapped in `{"input": ...}` |
| `custom` | varies | varies | `TERMINALIA_CUSTOM_URL`; anything speaking ComfyUI HTTP |

### Optional local acceleration: SageAttention

[Sage EasyInstall](../references/comfyui-sage-easyinstall.md) is an optional
Windows/ComfyUI-portable operator reference. It installs SageAttention and
Triton and creates a launcher using `--use-sage-attention`; it is **not** a
Terminalia backend, world-model stage, or workflow template.

Use it only for a controlled `local-comfy` installation after an A/B test of the
exact Terminalia workflow. The generated launcher uses ComfyUI's normal port
unless edited, so either set `TERMINALIA_COMFY_PORT=8188` or add `--port 8000`
to the launcher. Keep the ordinary non-Sage launcher as the fallback.

## GpuProfiles

Named hardware tiers (`GPU_PROFILES`) map VRAM → quality: mesh preset
(`pipeline_type`), step counts, tiled-decoder choice, video quantization.
`profile_for_vram()` picks the largest that fits. Local VRAM auto-detected from
`/system_stats` when available.

## Gotchas

- Comfy Cloud free tier cannot execute workflows (403 on `/prompt`) — the health
  probe passes but submission fails; catch `RuntimeError` from `wait()`.
- RunPod serverless has cold starts; first `wait()` may take minutes.
- The 1536_cascade preset with GGUF decoders has hit CUDA illegal-memory-access
  on 24GB cards — profiles ≥32GB disable tiled decode instead.
- SageAttention is model- and version-sensitive. A speedup is not an acceptance
  criterion: disable it if output fidelity, temporal consistency, or stability
  differs from the baseline run.

## Where to start reading

`detect_backends` → `Backend.submit/wait` → `resolve`.
