# Security Policy

## Reporting

Report vulnerabilities privately to the repository owner via GitHub Security
Advisories. Do not open public issues for exploitable findings.

## Scope

Terminalia executes:
- Local Python (terrain, placement, export)
- HTTP calls to ComfyUI endpoints (local, cloud, rental)
- Generated workflows submitted to those endpoints
- Optionally, Blender via its MCP socket server (arbitrary `bpy` execution)

## Known trust boundaries

1. **Workflow JSON is arbitrary code.** Custom ComfyUI nodes execute Python.
   Only submit workflows to backends you control or trust — same profile as
   `eval`. Terminalia builds its workflows from templates in this repo; inspect
   third-party workflow files before use.
2. **BlenderMCP execute_code is remote code execution by design.** The refine
   loop intentionally runs agent-authored `bpy` code inside Blender. Run it only
   against a local Blender instance you accept code being executed in. The addon
   socket (9876) has no auth — never expose it beyond localhost.
3. **API keys** live in environment variables (`COMFY_CLOUD_API_KEY`,
   `RUNPOD_API_KEY`, `OPENAI_API_KEY`, `NVIDIA_API_KEY`). Never commit them;
   never log full backend headers. Video ingestion rejects all inputs unless a
   real safety provider is configured; `TERMINALIA_SAFETY_MOCK=1` is test-only
   and must never be enabled in production.
4. **Generated content licenses** flow from upstream models — verify before
   commercial redistribution.

## Supported versions

Security fixes target the latest commit on `main`.
