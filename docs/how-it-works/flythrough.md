# Flythrough video

The VIDEO stage turns ordered camera-key renders into a real ComfyUI job through
the same `Backend.submit()` / `wait()` boundary used by other GPU stages. Its
output artifact, engine, model, license, seed, backend, and GPU profile are
recorded in `world.video_provenance`; a `video.flythrough` history entry marks
the completed stage.

## Engines and licenses

`wan21` is the default. It uses Wan2.1-I2V-14B-480P under Apache-2.0 and shares
the exact pinned base-model revision with the FixAnything refiner.

`ltx2` uses LTX-Video 2 under the Lightricks community/open-weights license.
Commercial use is free for entities under USD $10 million annual revenue; an
entity at or above that threshold needs a paid Commercial Use Agreement from
`ltxv-licensing@lightricks.com`. It is never selected by default. Before using
it, the operator must attest to the revenue condition:

```bash
export TERMINALIA_LTX_OK_UNDER_10M=1
```

Without that exact value, selecting `ltx2` raises
`LicenseAttestationRequired` before any backend submission.

Founder STOP: if Fractured Crystal Technologies reaches USD $10 million annual
revenue, stop LTX-2 use and accept a Lightricks Commercial Use Agreement before
re-enabling the attestation.

## GPU profiles and backends

The selected `GpuProfile.video_engine` supplies the default engine and
`video_quant` fills the model loader: 12 GB uses Q4_K_M, 24 GB Q6_K, 32 GB
Q8_0, 48 GB fp16, and 128 GB bf16. Small local profiles remain valid; callers
can supply a Comfy Cloud, RunPod, or custom backend without changing the
workflow. No stage URL or GPU is hardcoded.

## Keyframe contract

Pass one or more ComfyUI-input image paths in camera order. The first image is
the I2V anchor for the current native Wan/LTX templates; retain the ordered list
so future first/last-frame or segmented interpolation templates can consume
more anchors without changing the stage boundary. Paths must already be
reachable by the chosen backend. The caller supplies the world seed, and the
sampler is always seeded explicitly, so identical keyframes, engine, profile,
and seed produce byte-identical prompt JSON.

Templates live in `workflows/api/flythrough_wan21_api.json` and
`workflows/api/flythrough_ltx2_api.json`. Quantized profiles require the
ComfyUI-GGUF loader; fp16/bf16 profiles use native `UNETLoader`. Both workflows
use native conditioning nodes and VideoHelperSuite's `VHS_VideoCombine`.
