# PLAN — Fabric sidecar connection (public repo boundary)

**Status:** 🧭 parked · **Owner area:** integration layer (new `terminalia/integrations/`)
**Committed:** 2026-08-31 (final parking pass)

## Boundary rule (hard constraint)
Terminalia is a **public** repo. It must NEVER import the private
`ardyn` core / image packages or any private GHCR image. The fabric sidecar is
reached **over HTTP only**:

- Transport: `FABRIC_TRANSPORT_D_URL` + bearer token from env
  (`FABRIC_TRANSPORT_D_TOKEN`, never committed).
- **Fail-closed:** sidecar unreachable / unauthorized / malformed response →
  stage raises; no degraded or stubbed fallback that fakes success.
- Package access: `ardyn` / terminalia private-package access is intentionally
  NOT granted to this repo — no vendoring, no import, no dev-dependency on the
  private core/image. HTTP is the only coupling.
- Same posture as `SECURITY.md` already demands for workflow JSON: the sidecar
  is a code-execution-adjacent surface — localhost/loopback by default, explicit
  opt-in for remote.

## Concrete steps (when fabric transport-d is ready to consume)
1. `terminalia/integrations/fabric.py`: thin HTTP client (stdlib `urllib`, no
   new deps) — health probe, submit job, bounded poll, artifact fetch; bearer in
   `Authorization`, URL+token via env only.
2. Capability probe returns the sidecar's exposed world-gen tools; anything
   absent → fail-closed (same philosophy as the safety gate).
3. Wire as an optional Backend-adjacent integration — world.json stays the only
   state contract; sidecar jobs are invoked through the same stage-function
   boundaries.
4. Tests: env-absent → skip/fail-closed; mock HTTP server tests for
   success/auth-fail/malformed responses; a real-sidecar smoke marker gated on
   the env vars being present.
5. Docs: `docs/how-it-works/fabric.md` + `SECURITY.md` note confirming no
   private package imports and no secrets in repo.

## Trigger
When Josh wants terminalia jobs dispatched through the fabric sidecar instead
of (or in addition to) direct ComfyUI backends. No prerequisite inside this
repo; founder action is provisioning the transport URL + token.