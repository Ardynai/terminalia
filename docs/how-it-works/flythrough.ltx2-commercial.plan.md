# PLAN — LTX-2 commercial license path

**Status:** 🧭 parked, attestation-gated · **Owner area:** flythrough (video stage)
**Co-located next to:** `terminalia/video.py`, `workflows/api/flythrough_ltx2_api.json`
**Committed:** 2026-08-31 (final parking pass)

## Current state (per PR #5)
- LTX-2 is wired but requires `TERMINALIA_LTX_OK_UNDER_10M=1` before selection;
  without it, `LicenseAttestationRequired` names the condition.
- License ground truth (verified 2026-08-31): Lightricks community/open-weights
  license — free commercial use for entities **under $10M annual revenue**;
  entities at/above $10M must obtain the paid **Commercial Use Agreement**
  (`ltxv-licensing@lightricks.com`). Breach terms include liquidated damages.
- Default engine remains **Wan2.1-I2V-14B (Apache-2.0)** — unaffected by any of
  this.

## What's left (decision + bookkeeping only, no code)
1. **Now (under $10M):** Josh sets `TERMINALIA_LTX_OK_UNDER_10M=1` in the
   deployment env when he accepts the community-license conditions (no revenue
   cap breach; no training-of-competing-models on LTX-2 outputs). Record the
   acceptance date in ops notes.
2. **Trigger — FCT crosses $10M ARR:** within the license's own terms this
   becomes a paid-license situation. Steps: (a) pause LTX-2 selection (unset the
   env var — code already refuses without it), (b) email
   `ltxv-licensing@lightricks.com` for the Commercial Use Agreement, (c) on
   signature, re-enable; if declined, drop LTX-2 — the pipeline falls back to
   Wan2.1 with zero code changes.
3. Optional follow-up: surface the attestation state in `world.json`
   provenance (extend `ModelRef` with an `attestation` field) so every rendered
   LTX-2 flythrough carries proof of the license tier it ran under.

## Founder action
Only #1 (set the env var when accepting terms) — and the trigger to revisit is
purely ARR-based. No purchase is needed while under $10M.