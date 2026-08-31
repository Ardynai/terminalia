# PLAN — Swappable compute: production-grade cloud adapters

**Status:** 🧭 parked (abstraction done, production hardening left) · **Owner area:** `terminalia/backends.py`
**Committed:** 2026-08-31 (final parking pass)

## What's left
The `Backend` abstraction + `GpuProfile` tiers + `resolve()` auto-detection are
shipped (v0.3) and used by fix_anything / flythrough / ingest / safety, but the
remote adapters are still thin:

1. **RunPod serverless end-to-end on a real endpoint** — currently the wait loop
   tolerates RunPod's 404-polling semantics, but a real endpoint run (cold
   start, custom worker image with the terminalia custom nodes preinstalled) is
   untested. Steps: build a worker image embedding `custom_nodes/*` + pinned
   weights on demand, deploy, run one fix_anything + one ingestion job, record
   cold-start + cost numbers.
2. **Comfy Cloud paid-tier submission test** — cloud.comfy.org API shape,
   credit burn per 1536_cascade world, artifact fetch through
   `fetch_file_url`.
3. **More backend profiles** — add `GpuProfile` entries for rental SKUs beyond
   the current five (e.g. L40S 48GB, H100 80GB) and verify `profile_for_vram`
   maps them; add a per-backend capability mask (e.g. ltx2 unavailable on
   <24GB) instead of per-call checks.
4. **Cost estimator per world** (already on docs/roadmap.md v0.3): images ×
   meshes × video-seconds per tier → per-backend dollar estimate; feed from the
   E2E run costs gathered in `tests/real-weights-e2e.plan.md`.
5. **Health-probe hardening** — `detect_backends` currently probes
   `/system_stats`; add auth-aware probes (401 vs unreachable) so a bad key
   reports "configured but unauthorized" instead of silently dropping the
   backend.

## Trigger
Founder action #4 in `docs/founder-activation-runbook.plan.md` (credits +
keys provisioned). Steps 1–2 are the first two real-backend E2E runs after
mock-mode coverage is superseded.