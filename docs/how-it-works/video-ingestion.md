# Video ingestion

## Owns

The optional `VIDEO INGEST` path turns a consented monocular video into the
assets and layout records consumed by PLACE and EXPORT. Validated `world.json`
remains the only pipeline state.

## Implemented flow

`terminalia.ingest.ingest_video(request, backend, profile)` hashes the source,
requires a consent note, and runs the fail-closed content-safety job before it
submits reconstruction. The reconstruction graph connects two custom packages:

1. `terminalia_segment` uses SAM 2 video segmentation and tracking to produce
   per-instance masks and bounding boxes.
2. `terminalia_reconstruct` crops each track, creates its CAD-reference mesh
   with TRELLIS.2-4B, then tracks 6DoF poses with NVIDIA FoundationPose from
   NGC. FoundationPose is model-based: each generated object mesh is its pose
   track's required CAD reference.

The backend returns relative GLB paths, triangle counts, bounds, pose tracks,
and optional physics. Ingestion validates the contract and maps the first pose
to PLACE-compatible coordinates without discarding the full track.

## Models, licenses, and runtime setup

| Model | License recorded in provenance | Runtime source |
|---|---|---|
| SAM 2 | Apache-2.0 | Hugging Face revision pinned in `reconstruction.py` |
| TRELLIS.2-4B | MIT | Hugging Face revision pinned in `reconstruction.py` |
| FoundationPose (NVIDIA NGC) | NVIDIA Open Model License | `NGC_API_KEY` or `FOUNDATIONPOSE_NGC_DIR` |

No weights are committed. The two node packages import-guard their GPU/model
dependencies. Backends install those dependencies and fetch the pinned model
artifacts. Missing FoundationPose credentials fail the pose stage with:

> Founder action required: accept the NVIDIA Open Model License and set
> `NGC_API_KEY`, or download FoundationPose from NVIDIA NGC and set
> `FOUNDATIONPOSE_NGC_DIR`.

For dependency-free orchestration tests, set
`TERMINALIA_RECONSTRUCT_MOCK=1`. Mock execution writes deterministic simple
GLBs and fixed pose tracks from the source hash and seed; real execution is the
default.

SAM 3 is deliberately not implemented: its custom Meta license requires legal
review before it can replace Apache-2.0 SAM 2. Hi3DGen weights are not wired
because no clearly licensed official checkpoint was identified.

## Determinism and provenance

Source bytes are SHA-256 hashed. Seed, hash, backend profile, pinned model
versions, exact license strings, and uploader consent are carried through the
jobs and `world.json`. The stage uses no clock or ambient randomness.
