# Refinement

REFINE runs after PLACE and before EXPORT. Its state lives in the typed
`world.refine` section of `world.json`; render inputs must be recorded there
before a refiner runs.

## FixAnything cleanup

`terminalia.refine.fix_anything(world, backend, profile)` sends the recorded
frame folder, rendered video, or mesh render through the backend abstraction.
The backend runtime must provide the `TerminaliaFixAnything` workflow node,
which wraps upstream FixAnything inference and downloads the pinned weights
when absent. A successful pass records its input and cleaned-video references,
seed, backend, GPU profile, and exact weight revisions.

The pass runs on local/custom profiles with at least 32 GB VRAM and on Comfy
Cloud or RunPod, whose runtimes manage their own capacity. Smaller profiles
return normally with `status: "skipped"` and `reason: "insufficient profile"`.
The decision uses only backend/profile data and is deterministic.

FixAnything expects a 61-frame camera-path render, ideally with clean anchor
views at frames 0 and 60. Backend output remains a video cleanup artifact; it
does not mutate the source mesh. EXPORT can select the cleaned artifact from
`world.refine.fix_anything.outputs`.

## Models and license

The integration pins the Apache-2.0 FixAnything LoRA and its Apache-2.0
Wan2.1-I2V-14B-480P base by Hugging Face commit. These total roughly 60 GB and
are fetched by the configured runtime, never stored in this repository. See
the root `NOTICE` for attribution.

## Running the node

Copy or symlink `custom_nodes/terminalia_fixanything` into the ComfyUI
`custom_nodes/` directory, install the upstream FixAnything package and its
pinned DiffSynth dependency in ComfyUI's Python environment, then restart
ComfyUI. `huggingface_hub` is also required. On first real execution the node
downloads the commit-pinned base model and LoRA under
`ComfyUI/models/terminalia/fixanything`; set `HF_TOKEN` if Hugging Face requires
authentication. A failed or unavailable download raises before inference and
does not replace the input or report an output.

Real mode is the default. It uses bf16 weights, tiled decoding, and upstream
sequential CPU/GPU VRAM management so the 480P pipeline fits a 32 GB card. The
input must contain at least 61 frames. Set `TERMINALIA_FIXANYTHING_MOCK=1`, or
send the optional node input `mock: true`, to run a lightweight ffmpeg
denoise/sharpen/re-encode smoke path without importing GPU packages or fetching
weights.

For a fixed input, seed, pinned weights, dependency/CUDA versions, and GPU, the
real node seeds Python, NumPy, Torch, CUDA, and the sampler and requires
deterministic Torch algorithms. It uses no wall-clock or temporal randomness.
GPU/kernel and codec differences mean byte identity is not promised across
hardware or software stacks. Mock output is byte-identical when the same ffmpeg
build is used.
