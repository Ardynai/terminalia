# Minimal-code discipline (ponytail-style) — applies to every agent that opens this repo.

## Before writing code, stop at the first rung that holds:

1. Does this need to exist?         → no: skip it
2. Already in this codebase?        → reuse it, don't rewrite
3. Standard library does it?        → use it
4. Native platform feature?         → use it
5. Installed dependency does it?    → use it
6. One line?                        → one line
7. Only then: the minimum that works

## Safety carve-out (never trimmed for "less code")

Trust-boundary validation, data-loss handling, error handling, security, and
accessibility are never reduced in the name of minimalism.

## Repo conventions

- `world.json` (pydantic `terminalia.schema.World`) is the single source of truth.
  Every stage reads and writes it; no side-channel state.
- Deterministic given seed: same seed + same ops = same world. Never introduce
  wall-clock or ambient randomness into stages.
- Backends are swappable (`terminalia.backends.Backend`): never hardcode
  localhost or assume a specific GPU.
- Every stage is callable as a plain function with JSON-shaped inputs/outputs so
  agents and humans can drive them equally.

## Docs upkeep

- Every feature PR updates the relevant `docs/how-it-works/<area>.md`.
- A behavior-preserving readability pass runs every ~5 merged feature batches.
