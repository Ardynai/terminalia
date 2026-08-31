# PLAN — world.json schema evolution

**Status:** 🧭 standing plan (continuous) · **Owner area:** `terminalia/schema.py`
**Committed:** 2026-08-31 (final parking pass)

`world.json` is the single source of truth; the pydantic `World` model evolves
as stages come online. Known upcoming changes, in the order stages will need
them:

1. **v0.3 — ingest refinements:** `video_provenance.models[].attestation`
   (license-tier proof per model, see LTX-2 plan); safety verdict summary
   (categories, sampled frame indices) — currently only in backend outputs.
2. **v0.4 — refine loop:** bounded-iteration history for the BlenderMCP loop
   (`Refinement.iterations[]` with render refs, critique, fix ops) and
   vision-acceptance score per iteration.
3. **v0.5 — audio/characters:** flythrough audio artifacts + canonical character
   bank refs (ReActor face IDs) as first-class entries.
4. **v0.6 — splats/capture:** splat asset kind (`AssetEntry.kind`) +
   SuperSplat edit provenance; multi-region `World` references (tile worlds
   pointing at neighbors).
5. **Cross-cutting rules (unchanged from AGENTS.md):**
   - Every change keeps old worlds loadable (additive fields with defaults;
     `version` bump only when meaning changes, never rename).
   - Stage functions stay JSON-in/JSON-out; no side-channel state.
   - Add a round-trip test in `tests/test_smoke.py` per schema change
     (save → load → equal).
   - Update the JSON-shape docs in `docs/how-it-works/` in the same PR that
     touches the schema.

## Trigger
Each item fires with the stage PR that needs it; no standalone work required.