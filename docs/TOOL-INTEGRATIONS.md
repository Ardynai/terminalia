# World-Gen tool integrations — every tool has a slot, an action, and a trigger

2026-08-30. Grounded on THIS repo's pipeline: **SPEC → TERRAIN → LAYOUT → ASSETS (TRELLIS.2-4B) → PLACE → REFINE (BlenderMCP loop) → EXPORT**, with `world.json` as the single source of truth and swappable compute (local ComfyUI / Comfy Cloud / RunPod). Rule: nothing goes on a vague "watch" — each tool below is either **integrate now**, **spike**, **alternative**, **not-adopting (named reason)**, or **future-gated (named trigger)**.

---

## ASSETS stage (text/image → 3D mesh) — today: TRELLIS.2-4B
**Block3D** — alternative text→mesh generator, block-parallel (~5s/mesh).
- **ACTION: DO NOT INTEGRATE.** Hard reason: **Research-Only RAIL-MS license** (derivative of Cube3D) — not usable in a commercial product. The capability it offers is already covered by TRELLIS.2.
- **What we keep from it:** the *idea* of block-parallel decoding for speed.
- **Trigger to revisit:** Block3D relicenses commercially, OR we train/adopt our own commercially-licensed fast mesh model and want the block-parallel technique. (Logged here so it is not forgotten — it is a licensing block, not a quality doubt.)

## REFINE stage (render-inspect-refine) — today: BlenderMCP loop
**fix-anything** — runtime artifact cleanup on generated 3D (3DGS / NeRF / mesh / point cloud) via a video-diffusion model.
- **ACTION: SPIKE NOW** as a REFINE sub-stage (a `fix_anything` refiner that runs on ASSETS/render output before EXPORT).
- **Why now:** Apache-2.0 (usable), directly lifts output quality, runs on the same compute backends. Cost: needs Wan2.1-I2V-14B (~60GB) → fits the 32GB+/128GB GpuProfiles or Comfy-Cloud/RunPod, so it's gated to those presets.
- **Note (clears a mix-up):** fix-anything is **runtime** cleanup — you run it on outputs. It is NOT a training tool. (Contrast DiffusionOPSD below, which IS training.)

## NEW INPUT PATH — Video → World (ingestion that feeds SPEC / world.json)
**OVOW** ("One Video, One World") — monocular video → instance-level, simulation-ready 4D meshes + physics (URDF).
- **ACTION: DESIGN THE "Video→World" STAGE NOW, and SPIKE it with the released models it's built from — do not idle-wait on OVOW itself.**
- **Why not integrate OVOW directly yet:** their glue code is "under internal review" (unreleased) and the license is unstated — there is literally no code to integrate.
- **Why we don't just wait:** OVOW is a *pipeline over already-released models* (SAM3, Hi3DGen, FoundationPose, VGGT, RoMa v2, Qwen3-VL). We can build "record a space → get a 3D world with physics" now from those parts.
- **Strategic value:** this is the engine behind the "record/scan your business → get a 3D space" onboarding funnel — high-value, so it earns a designed stage, not a bookmark.
- **Trigger to swap in OVOW's own implementation:** they release the code under a permissive license.

## SPEC / agentic layer (prompt → structured world plan) — today: agent-authored functions
**code-world-model** — an agent that writes CODE to generate/simulate a world (compact conditions → deterministic expansion).
- **ACTION: MINE THE PATTERN into our agentic SPEC layer; do NOT take a dependency on their repo.**
- **Why not depend on it:** days-old (44 stars), unclear license, and its output is video simulations — not engine-ready 3D like our pipeline needs.
- **Why it still matters:** it validates our exact direction (code/agent-driven generation) and the "compact conditions → deterministic code expansion" idea is worth folding into our SPEC stage's determinism guarantees.
- **Trigger to adopt their model:** it matures and the license clears. Until then, terminalia already IS agent/code-driven — this is enhancement, not a gap.

## EXPORT / WEBSITE (three.js) — today: glTF export (three.js can load it)
**img2threejs** — single image → animation-ready three.js CODE (hosted service).
- **ACTION: PROTOTYPE it for the LANDING pages** (website Page 3 playable-game / hero scenes). NOT a core world-gen stage.
- **Why not core:** it's a hosted service with unknown terms/pricing and no self-host — fine for prototyping, unsafe as a production dependency. And we already emit glTF that three.js consumes.
- **Trigger to depend on it in production:** confirmed acceptable commercial terms (contact @NickDevFE). Immediate best use: fast landing-scene mockups.

---

## Voice pipeline (separate from world-gen) — for AI players & users
**Gemini 3.5 Transcribe** — speech-to-text: understand voice chat, generate captions, run voice commands.
- **ACTION: ADOPT as the STT provider.** Confirmed intent = STT (understanding voice), not voice generation.
- Slot: a voice-**input** module that pairs with the existing `tts.ts` voice-**output** path. 85+ languages, real-time streaming (Live API, sub-second), WER 2.6% batch / 4.0% streaming.
- Note: if we ever want to *generate* AI-player voices, that's a separate TTS model — different track.

## Train-Our-Own-Model track (v2 — the paid, analytics-optimized tier)
This is the honest home for **"DiffusionOPSD but for world generation."**
**DiffusionOPSD** — training-time reward-guided self-distillation that improves a diffusion model's outputs (2D images today).
- **ACTION: PARK in the v2 "train our own model" track as the quality-post-training technique.** For 2D asset-art now; the same reward-post-training idea generalizes to a 3D/world model if we build one.
- **Why not now:** it is a *training method*, not a runtime tool — it only pays off once we train or fine-tune our own model. Today we compose pretrained models (TRELLIS.2, etc.), we don't train.
- **Trigger:** we commit to training a proprietary asset/world model — which lines up with the stated v2 plan (a paid tier optimized with v1 analytics). When that decision is made, DiffusionOPSD (2D) + its 3D reward-post-training analog is the technique.

---

## Queued so nothing is forgotten
1. **[SPIKE] REFINE:** `fix_anything` refiner sub-stage (Apache-2.0; gated to 32GB+/cloud GpuProfiles).
2. **[SPIKE] INGEST:** "Video→World" stage from SAM3 + Hi3DGen + FoundationPose (OVOW-equivalent, no wait); swap in OVOW on release.
3. **[INTEGRATE] VOICE:** Gemini 3.5 Transcribe STT module (voice chat / commands / captions).
4. **[STUDY] SPEC:** fold code-world-model's compact-conditions→deterministic-code pattern into the agent SPEC layer.
5. **[PROTOTYPE] WEBSITE:** img2threejs for landing scenes; confirm commercial terms.
6. **[GATED] v2:** DiffusionOPSD-style reward post-training — revisit when we train a proprietary model.
7. **[BLOCKED] Block3D:** do not integrate (research-only license); revisit only on relicense.

CI note: the multiverse repo's GitHub Actions is off (billing) until next month; any spike PR is validated locally + planner-corroborated at its SHA until then.
