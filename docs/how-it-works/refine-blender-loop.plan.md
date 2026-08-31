# PLAN — REFINE: real BlenderMCP place→refine→re-render loop

**Status:** 🧭 parked (not started) · **Owner area:** REFINE / Blender integration
**Committed:** 2026-08-31 (final parking pass — do not lose)

## What's left
The REFINE stage docs describe a BlenderMCP render-inspect-refine loop
(import world → render → agent critique → fix → re-render), and the Blender
character-sheet turntable pipeline was verified manually (2026-08-23, see vault
reference), but the **place→refine→re-render iteration is not end-to-end tested
in-repo**. Nothing in `terminalia/` drives Blender programmatically today.

## Why it matters
REFINE is the quality engine of the pipeline — without the loop, worlds ship
with whatever ASSETS/PLACE produce. This is the single biggest untested gap
between the current pipeline and WorldClaw-class output quality.

## Concrete steps
1. `terminalia/refine_loop.py`: orchestrate BlenderMCP (addon port :9876 on
   Josh's box; headless CYCLES/OPTIX only) — import GLBs, normalize scale,
   camera pass, render N canonical views, return artifact refs into
   `world.refine.render_artifacts` (feeds `fix_anything`).
2. Agent critique hook: render → vision check (floating props, bad lighting,
   material errors) → targeted fix ops → re-render. Bounded iterations (2–3),
   all recorded in `world.refine` history.
3. GpuProfile-aware render presets (resolution, samples, denoiser).
4. Tests with a Blender stub behind the same function boundary; a real-Blender
   smoke marker for local runs.
5. Docs: extend `docs/how-it-works/refinement.md` with the loop contract.

## Trigger to start
When real-weights E2E runs are unblocked (cloud credits / 32GB+ box) and PRs
#4–#7 merge — the loop should iterate on REAL renders, not mocks.

## Founder action
None required (local Blender + MCP addon already installed). Optional: confirm
which box runs headless Blender server-side.