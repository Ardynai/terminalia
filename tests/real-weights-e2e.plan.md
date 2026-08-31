# PLAN — Real-weights E2E for fix_anything + safety gate

**Status:** 🧭 parked, blocked on founder actions · **Owner area:** `tests/`
**Committed:** 2026-08-31 (final parking pass)

## What's left
PRs #4 (FixAnything node) and #7 (safety gate) ship **mock-mode E2E only**
(verified transforms / stubbed verdicts). The real-weights paths are implemented
but unexercised in CI-less local runs:
- fix_anything: real Wan2.1-I2V-14B + FixAnything LoRA (~60GB, Apache-2.0) on a
  32GB+/128GB profile or cloud backend.
- video_content_safety: real OpenAI `omni-moderation-latest` or Nemotron
  Content Safety run against unsafe + safe sample videos.

## Why gated
No cloud credits / API keys configured yet (`COMFY_CLOUD_API_KEY`,
`RUNPOD_API_KEY`, `OPENAI_API_KEY`, `NGC_API_KEY` all absent from env). Child-
safety posture: until a real safety backend + key exists, the gate stays HARD
fail-closed (reject everything) — that is correct behavior, not a bug.

## Concrete steps
1. `tests/test_real_weights_fixanything.py` — marked `@pytest.mark.real_weights`
   (skipped unless `TERMINALIA_REAL_E2E=1`): sample render → real cleanup →
   perceptual-diff assertion (cleaned ≠ input, structure preserved).
2. `tests/test_real_safety.py` (same marker): unsafe canary video → rejected;
   safe canary → passes with real ModelRef provenance.
3. Backend matrix: local 32GB+ run + one Comfy Cloud run + one RunPod run;
   record cost per run in the test output for the cost-estimator work.
4. Wire a GitHub Actions nightly (Actions billing resumes next month) —
   marker-gated so PR CI stays free/mocked.

## Trigger
Founder actions land (see `docs/founder-activation-runbook.plan.md`) AND cloud
credits/keys exist. Nothing to build before then.

## Founder action
See runbook: NVIDIA NGC terms + `NGC_API_KEY`, `OPENAI_API_KEY` (safety),
Comfy Cloud or RunPod credits.