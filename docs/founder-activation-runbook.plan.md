# PLAN — Founder-gated model activation runbook

**Status:** 🧭 parked, waiting on Josh · **Owner area:** `docs/`
**Committed:** 2026-08-31 (final parking pass)

Exact steps for Josh to flip each gated capability. Each item lists the action,
the env vars, and the verification. NOTHING here requires code changes — every
gate is already implemented fail-loud (PRs #4–#7).

## 1. FoundationPose (pose tracking, PR #6) — NVIDIA NGC
1. Go to `catalog.ngc.nvidia.com` (org: nvidia, TAO or Isaac FoundationPose).
2. Accept the **NVIDIA Open Model License** on download.
3. Either: `export NGC_API_KEY=nvapi-...` (adapter fetches at runtime), or
   download the checkpoint locally and `export FOUNDATIONPOSE_NGC_DIR=/path`.
4. Verify: `pytest tests/test_reconstruction.py -k founder` style gate flips
   from `FounderActionRequired` to building the workflow.
5. Record the accepted date + model digest in `NOTICE` provenance.

## 2. Safety gate (child-safety, PR #7) — REQUIRED before real user video
1. **OpenAI path:** accept OpenAI commercial terms on the account backing the
   key → `export OPENAI_API_KEY=...`. Hosted moderation becomes the default.
2. **Nemotron path (optional, air-gapped):** deploy the Nemotron Content Safety
   NIM (NVIDIA Open Model License + NIM terms) → `NVIDIA_API_KEY` or
   `NEMOTRON_SAFETY_DIR`. Accept OpenMDW/Gemma component terms if present.
3. Until at least one is configured, the gate rejects every video — this is the
   intended fail-closed posture. Do not ship `TERMINALIA_SAFETY_MOCK=1` to prod.
4. Verify: safe + unsafe canaries through `tests/test_safety.py` real markers
   (see `tests/real-weights-e2e.plan.md`).

## 3. LTX-2 (flythrough, PR #5)
- Current state: attestation-gated. `TERMINALIA_LTX_OK_UNDER_10M=1` attests
  Fractured Crystal Technologies is under $10M annual revenue (free tier).
- **If FCT crosses $10M ARR:** STOP using LTX-2 immediately (Wan2.1 unaffected),
  contact `ltxv-licensing@lightricks.com` for the paid Commercial Use Agreement.
- See `docs/how-it-works/flythrough.ltx2-commercial.plan.md`.

## 4. Cloud compute credits
- Comfy Cloud: `COMFY_CLOUD_API_KEY` (credits) — enables pipeline for
  no-GPU/low-VRAM machines.
- RunPod: `RUNPOD_API_KEY` + `RUNPOD_ENDPOINT_ID` — burst 32GB+/128GB runs
  (fix_anything needs ≥32GB local otherwise).
- Neither has a license gate; pure procurement.

## 5. Attestation checklist (copy into the ops doc when done)
- [ ] NGC terms accepted, key or dir set
- [ ] Safety key configured (OpenAI and/or Nemotron), mock env var absent in prod
- [ ] LTX-2 attestation env set (or LTX-2 intentionally unused)
- [ ] Cloud credits provisioned, cost caps set