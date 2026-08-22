# Contributing to Terminalia

Thanks for contributing~ Contributions are code, docs, workflows, world
templates, and asset-pipeline integrations.

## Ground rules

1. **Read `AGENTS.md` first** — the minimal-code discipline applies to every PR,
   human or agent authored.
2. **Deterministic stages** — same seed in, same result out. No wall-clock time,
   unseeded RNG, or ambient state inside stage code.
3. **Backends stay swappable** — never hardcode `localhost`, a port, or a GPU
   model. Use `terminalia.backends`.
4. **Schema is contract** — changes to `terminalia/schema.py` need a DECISIONS.md
   entry and a version bump note.

## Docs upkeep (standing rule)

- Every feature PR updates the matching `docs/how-it-works/<area>.md`.
- A full behavior-preserving readability pass runs every ~5 merged feature
  batches: docs, renames, "why" comments only — no logic changes.

## Testing

```bash
python tests/test_smoke.py          # from repo root; ALL TESTS PASS expected
```

New stage? Add `tests/test_<stage>.py` covering the happy path plus one
failure mode.

## What NOT to commit

- Generated worlds (`worlds/*/out/`) — keep only `world.json`
- Asset GLBs (`assets/`) — they're regenerable from seeds + prompts
- Secrets: API keys belong in env vars (`COMFY_CLOUD_API_KEY`,
  `RUNPOD_API_KEY`), never in files

## Model licenses

Generated content inherits upstream model licenses. TRELLIS.2 is MIT;
verify the license of any alternative backend model before shipping outputs.
