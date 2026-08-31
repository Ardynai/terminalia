# DECISION — Naming collision: terminalia engine vs "Terminalia" multiverse rebrand

**Status:** 🧭 OPEN decision (parked) · **Owner:** Josh (founder) · **Area:** repo identity
**Committed:** 2026-08-31 (final parking pass)

## The collision
Two things currently carry the name:
1. **This repo** — `Ardynai/terminalia`, the world-gen ENGINE (public, MIT,
   Python, the pipeline described in README.md).
2. **"Terminalia" as the public rebrand of multiverse** — the trading-stack /
   platform product (per Notion + multiverse project records).

Search, links, and branding will collide: `github.com/Ardynai/terminalia` ranks
for both meanings; docs, conversations, and package names become ambiguous.

## Options
**A. Rename the engine repo** (e.g. `Ardynai/<new-engine-name>`; candidates
keep the tree theme: `arboreum`, `silvae`, `xylomata`). 
- Pros: engine is young (20 commits, 3 merged PRs, external links minimal);
  rename cost is one-time and low. Multiverse rebrand naming is presumably
  further committed (marketing/public-facing).
- Cons: breaks the growing external reference set (Hermes memory, session
  history, vault notes all say "terminalia repo = engine").

**B. Rebrand multiverse in place** (pick a different public name; leave the
engine as terminalia).
- Pros: zero cost here; engine keeps the name every doc/skill/vault note
  already uses.
- Cons: multiverse rebrand work happens elsewhere and may already be invested.

**C. Disambiguate with qualifiers** (engine = "Terminalia Engine", rebrand =
"Terminalia Platform"), keep both names.
- Pros: zero migration cost either side.
- Cons: weakest fix — the collision persists in search/URLs; docs must
  disambiguate forever.

## Recommendation
 lean **A** (rename the engine) IF the multiverse rebrand is significantly more
invested; else **B**. Decision inputs Josh should weigh: external inbound links
to each, how far the rebrand has propagated, trademark/trust concerns on the
public-product side. Do NOT let this block the parked build plans — they are
written name-neutrally and survive either outcome.

## What a rename entails (if A)
- GitHub rename (redirects old URLs), update `pyproject.toml` name + imports
  via one mechanical PR, README/AGENT/ONBOARDING sweep, vault + Hermes memory
  update (repo paths), Notion repo records.

## Trigger + founder action
**Josh decides.** Default until decided: engine repo stays
`Ardynai/terminalia`; no code changes. Record the verdict here when made.