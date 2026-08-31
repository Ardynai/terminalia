# PLAN — Tool-integration build tickets (from TOOL-INTEGRATIONS.md)

**Status:** 🧭 one plan per mapped-but-unbuilt slot · **Owner area:** beside `docs/TOOL-INTEGRATIONS.md`
**Committed:** 2026-08-31 (final parking pass)
**Rule from TOOL-INTEGRATIONS.md:** nothing idles on a vague "watch" — every
slot is integrate-now / spike / alternative / not-adopting / future-gated. The
spikes that DID run are merged (fix_anything PR #2/#4, video→world PRs #3/#6,
flythrough #5, safety #7). What remains formalized as plans:

## 1. Example-worlds splat gallery (landing showcase) — `splat-gallery.plan.md`
Landing feature: playable pre-generated worlds (ours + opt-in user creations),
Gaussian-splat worlds first (browser-renderable, no login). Needs: a splat /
lightweight-web EXPORT target, curation policy for user submissions, hosting.
Build home is the landing spec (multiverse
`planning/LANDING-PAGE-SPEC.md`); this repo supplies the worlds + export glue.

## 2. Our-own "image → live three.js scene" pipeline — `img2threejs-look.plan.md`
Copy the **look**, never the vendor (img2threejs.io service has paid/unknown
hosted terms — do not use). We own most of it already: ASSETS (TRELLIS.2) +
EXPORT (glTF that three.js/R3F loads). Net-new: an EXPORT sub-target emitting an
animation-ready three.js scene for landing/hero use, "no imported meshes"
where the reference does that.

## 3. Gemini 3.5 Transcribe STT module — `voice-stt-gemini.plan.md`
Voice-INPUT pairing for the existing voice-OUTPUT path: understand voice chat,
captions, voice commands. 85+ languages, live API sub-second, WER 2.6% batch.
Adopt as the STT provider (confirmed intent: understanding, not generation).
Founder action: Google Cloud/AI Studio terms + API key.

## 4. OVOW slot (Video→World upstream) — `ovow-upgrade.plan.md`
Our ingestion (PRs #3/#6) deliberately reimplements the OVOW *capability* from
released models. Swap-in trigger: OVOW releases its glue code under a
permissive license — then evaluate replacing our SAM2/TRELLIS/NGC-FoundationPose
chain where their implementation is better, keeping our license discipline.

## 5. code-world-model pattern — `code-world-spec.plan.md`
Mine the pattern (agent writes CODE to generate/simulate; compact conditions →
deterministic expansion) into the SPEC layer; NO dependency on the repo (days-
old, unclear license, video-sim output). Trigger to adopt the model itself: it
matures AND its license clears.

## 6. Block3D — NOT ADOPTING (standing decision)
Research-only RAIL-MS license. Revisit trigger: commercial relicense, or we
want the block-parallel decoding *technique* for our own mesh model.

## 7. DiffusionOPSD-style training (v2 track) — `train-own-model-v2.plan.md`
Reward-guided self-distillation is a TRAINING method, parked for the v2 paid
tier: train a proprietary asset/world model optimized with v1 analytics. Not
runtime work; starts only if/when the "train our own model" commitment is made
(revisit trigger recorded in TOOL-INTEGRATIONS.md §queued item 7).