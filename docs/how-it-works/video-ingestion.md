# Video ingestion

## Owns

The optional `VIDEO INGEST` input path turns a user-provided monocular video
into the same assets and layout records consumed by PLACE and EXPORT. The
validated `world.json` remains the only pipeline state.

## Main flow

`terminalia.ingest.ingest_video(request, backend, profile)` hashes the source
bytes, requires a consent note, and submits a content-safety job before any
reconstruction job. Only an explicit `safe: true` verdict with model
provenance proceeds. Errors, absent fields, unknown verdicts, unsafe content,
zero instances, or missing poses raise; the function never saves a partial
world.

The reconstruction backend returns instance GLB paths, 6DoF pose tracks, and
optional mass/URDF metadata. The stage maps the first pose into the existing
PLACE-compatible `pos_xy`/`z_offset` fields while retaining the full track.
Every backend adapter uses the existing `Backend.submit`/`wait` abstraction and
the selected `GpuProfile`. Tests use that same boundary with deterministic
model stubs; no weights are stored in this repository.

## Determinism and provenance

Raw source bytes are SHA-256 hashed. The caller's seed, hash, backend profile,
model names, versions, licenses, and uploader consent note are recorded or sent
with each job. The stage uses no clock or ambient randomness.

## License and implementation STOPs

- SAM 3 is released under Meta's custom SAM License, which has no blanket
  noncommercial restriction but requires product/legal compliance review.
- Hi3DGen source is MIT, but an official pretrained checkpoint with a clearly
  documented weights license was not identified. No Hi3DGen weights are wired.
- The NVlabs FoundationPose repository license restricts it to noncommercial
  use. It is not wired. NVIDIA's separate commercial NGC artifact requires
  accepting and reviewing NVIDIA terms before an adapter can be added.
- NVIDIA Nemotron 3.5 Content Safety is a possible commercial safety adapter,
  but its OpenMDW/Gemma terms and frame-sampling limitations require acceptance
  and production integration. This spike defines and tests the fail-closed
  adapter contract rather than selecting or shipping those weights.

Official references: [SAM 3](https://github.com/facebookresearch/sam3),
[Hi3DGen](https://github.com/bytedance/Hi3DGen),
[FoundationPose license](https://github.com/NVlabs/FoundationPose/blob/main/LICENSE),
[NVIDIA FoundationPose](https://catalog.ngc.nvidia.com/orgs/nvidia/tao/models/foundationpose/),
and [Nemotron 3.5 Content Safety](https://build.nvidia.com/nvidia/nemotron-3.5-content-safety/modelcard).
