# World-Gen tool integrations — every tool has a slot, an action, and a trigger

2026-08-30. Grounded on THIS repo's pipeline: **SPEC → TERRAIN → LAYOUT → ASSETS (TRELLIS.2-4B) → PLACE → REFINE (BlenderMCP loop) → EXPORT**, with `world.json` as the single source of truth and swappable compute (local ComfyUI / Comfy Cloud / RunPod). Rule: nothing goes on a vague "watch" — each tool below is either **integrate now**, **spike**, **alternative**, **not-adopting (named reason)**, or **future-gated (named trigger)**.

---

## ASSETS stage (text/image → 3D mesh) — today: TRELLIS.2-4B
**Block3D** — alternative text→mesh generator, block-parallel (~5s/mesh).
- **ACTION: DO NOT INTEGRATE.** Hard reason: **Research-Only RAIL-MS license** (derivative of Cube3D) — not usable in a commercial product. The capability it offers is already covered by TRELLIS.2.
- **What we keep from it:** the *idea* of block-parallel decoding for speed.
- **Trigger to revisit:** Block3D relicenses commercially, OR we train/adopt our own commercially-licensed fast mesh model and want the block-parallel technique.

## REFINE stage (render-inspect-refine) — today: BlenderMCP loop
**fix-anything** — runtime artifact cleanup on generated 3D (3DGS / NeRF / mesh / point cloud) via a video-diffusion model.
- **ACTION: SPIKED** as an optional, backend-routed REFINE sub-stage with deterministic profile gating and `world.json` provenance.
- **Why now:** Apache-2.0 (usable), directly lifts output quality, runs on the same compute backends. Cost: needs Wan2.1-I2V-14B (~60GB) → fits the 32GB+/128GB GpuProfiles or Comfy-Cloud/RunPod.
- **Note:** fix-anything is **runtime** cleanup — NOT a training tool. (Contrast DiffusionOPSD below, which IS training.)

## NEW INPUT PATH — Video → World (ingestion that feeds SPEC / world.json)
**OVOW** ("One Video, One World") — monocular video → instance-level, simulation-ready 4D meshes + physics (URDF).
- **ACTION: IMPLEMENTED** with commercially-clear substitutes: SAM 2 (Apache-2.0), TRELLIS.2-4B (MIT), and NVIDIA NGC FoundationPose (NVIDIA Open Model License).
- **Why not integrate OVOW directly yet:** their glue code is "under internal review" (unreleased); no code to integrate.
- **License boundary:** SAM 3 still needs legal review, Hi3DGen has no clearly licensed official checkpoint, and the non-commercial FoundationPose repository is excluded. The adapter uses only NVIDIA's separately distributed NGC artifact.
- **Strategic value:** the engine behind the "record/scan your business → get a 3D space" onboarding funnel.
- **Trigger to swap in OVOW's own implementation:** they release the code under a permissive license.

## SPEC / agentic layer (prompt → structured world plan) — today: agent-authored functions
**code-world-model** — an agent that writes CODE to generate/simulate a world (compact conditions → deterministic expansion).
- **ACTION: MINE THE PATTERN into our agentic SPEC layer; do NOT take a dependency on their repo.**
- **Why not depend on it:** days-old, unclear license, output is video sims — not engine-ready 3D.
- **Why it still matters:** validates our code/agent-driven direction; the "compact conditions → deterministic code expansion" idea strengthens SPEC determinism.
- **Trigger to adopt their model:** it matures and the license clears.

## EXPORT / WEBSITE (three.js) — today: glTF export (three.js can load it)
**The "single image → live three.js scene" look** (what img2threejs.io *demonstrates*).
- **FOUNDER NOTE (2026-08-30):** do **NOT** use the img2threejs *service* — if it costs money / has unknown hosted terms, we don't want it. The ask was to **copy the capability/look**, not the vendor.
- **ACTION: BUILD OUR OWN, open pipeline.** Target look = a single reference image → an animation-ready three.js scene rendered live in the browser, "no imported meshes." We already own most of it: **ASSETS** (image→mesh via TRELLIS.2 / Hi3DGen) + **EXPORT** (glTF that R3F/three.js loads). The net-new bit is an **EXPORT sub-target: "web/animation-ready three.js scene"** for landing/hero use.
- **Reference (look only, never a dependency):** img2threejs.io.
- **Trigger:** none — build-our-own, start whenever the landing work begins.

---

## LANDING SHOWCASE — playable example worlds (founder idea, 2026-08-30)
On a landing page (the **Globe-of-Windows** Page 2 and/or the **Playable-Game** Page 3), showcase **real, pre-generated example worlds** — made by **us** (terminalia `worlds/` outputs) **and by users** — that visitors can **play around in live**, including **Gaussian-splat ("splatting") worlds**, which are lightweight to render in a browser (ideal for a public, no-login landing).
- **ACTION:** designate an **"example worlds gallery"** as a landing feature, fed by curated terminalia world outputs + an **opt-in** set of user creations.
- **Pipeline tie:** add a **splat / lightweight-web EXPORT target** to EXPORT so a generated world is directly landing-playable.
- **Build home:** the landing spec (multiverse `planning/LANDING-PAGE-SPEC.md` + `NEXT-BUILD-PROMPTS.md §1`). This note keeps it on record from the world-gen side.

---

## Voice pipeline (separate from world-gen) — for AI players & users
**Gemini 3.5 Transcribe** — speech-to-text: understand voice chat, generate captions, run voice commands.
- **ACTION: ADOPT as the STT provider.** Confirmed intent = STT (understanding voice), not voice generation.
- Slot: a voice-**input** module that pairs with the existing `tts.ts` voice-**output** path. 85+ languages, real-time streaming (Live API, sub-second), WER 2.6% batch / 4.0% streaming.

## Train-Our-Own-Model track (v2 — the paid, analytics-optimized tier)
The honest home for **"DiffusionOPSD but for world generation."**
**DiffusionOPSD** — training-time reward-guided self-distillation that improves a diffusion model's outputs (2D images today).
- **ACTION: PARK in the v2 "train our own model" track as the quality-post-training technique.** For 2D asset-art now; generalizes to a 3D/world model if we build one.
- **Why not now:** it is a *training method*, not a runtime tool.
- **Trigger:** we commit to training a proprietary asset/world model (the v2 paid tier optimized with v1 analytics).

---

## Queued so nothing is forgotten
1. **[SPIKED] REFINE:** `fix_anything` refiner sub-stage (Apache-2.0; 32GB+/cloud GpuProfiles).
2. **[IMPLEMENTED] INGEST:** SAM 2 → TRELLIS.2 → NVIDIA NGC FoundationPose, with deterministic mock execution and explicit founder gate.
3. **[BUILD] EXPORT:** our own "image→live three.js scene" web target (the img2threejs *look*, not the service) + a splat/lightweight-web export for landing-playable worlds.
4. **[INTEGRATE] VOICE:** Gemini 3.5 Transcribe STT module (voice chat / commands / captions).
5. **[STUDY] SPEC:** fold code-world-model's compact-conditions→deterministic-code pattern into the agent SPEC layer.
6. **[LANDING] SHOWCASE:** example-worlds gallery (ours + opt-in user splat worlds) on a landing page.
7. **[GATED] v2:** DiffusionOPSD-style reward post-training — revisit when we train a proprietary model.
8. **[BLOCKED] Block3D:** do not integrate (research-only license); revisit only on relicense.

CI note: the multiverse repo's GitHub Actions is off (billing) until next month; any spike PR is validated locally + planner-corroborated at its SHA until then.
