# How it works — Unity export & control

**Owns:** getting Terminalia worlds into Unity 6, and agent-driven scene control.
**Key files:** `terminalia/export.py` (`write_unity_editor_script`).

## Josh's setup (verified)

- **Unity 6 (6000.4.4f1)** installed: `C:\Program Files\Unity\Hub\Editor\6000.4.4f1\`
- Launcher scripts: `C:\AI\content-creation\unity\launch-unity-hub.ps1`
- His preferred workflow: **agent edits project files directly** (C# scripts,
  assets) — Unity's asset watcher picks up changes on focus. Documented in
  `UNITY_OPENCLAW_AUTOMATION_TEST_PLAN.md` (no test project created yet).
- No plugins installed; stock editor.

## Current export path (works today)

1. `write_unity_editor_script()` generates `TerminaliaWorld.cs` +
   `manifest_unity.json` into the world's export dir
2. Drop both into `<project>/Assets/Editor/`
3. Install **glTFast** or **UnityGLTF** package (Window > Package Manager)
4. Menu **Terminalia → Build World** — imports each GLB, parents under
   `Terminalia_World`, applies positions/rotations from the manifest

This is the "generate → user clicks once" pattern: reliable, no editor plugin
required beyond a glTF importer.

## Agent control options (research in progress)

| Option | Friction | Notes |
|---|---|---|
| File-editing (Josh's plan) | Low | agent writes C# + assets; Unity recompiles on focus |
| Editor MCP plugin | Medium | community servers exist; verify maintenance for Unity 6 |
| `-batchmode -executeMethod` CLI | Medium | headless imports need C# wrapper per op |
| glTFast runtime loading | Low | load GLBs at play-time from manifest; no editor step |

Decision pending the MCP landscape research (v0.7 roadmap item).

## Gotchas

- Unity coordinates are left-handed Y-up (the generated script already converts
  Terminalia's Z-up positions)
- glTF materials may import pink without a URP-compatible shader package
- First editor launch after file edits triggers a full recompile (~30s+)

Related: [[Terminalia]] · [[Content Resource Inventory]]


## DECISION (research complete, Aug 2026)

**Ranked for Terminalia:**

1. **Generated C# importer + one-click menu** (current implementation) — keep.
   Deterministic, offline, no accounts. Upgrade path: extend `TerminaliaWorld.cs`
   to read `world.json` directly via glTFast (first-party `com.unity.cloud.gltfast`).
2. **Headless agent runs**: same dispatcher via `-batchmode -executeMethod` —
   one generic C# dispatcher reading world.json covers ALL ops, not per-op scripts.
3. **Interactive iteration**: MCP for Unity (CoplayDev/unity-mcp, 13.6k stars,
   v10.0 2026-06-30, MIT, actively maintained, Unity 6 supported, 47 tools).
   Install: Package Manager git URL or `openupm add com.coplaydev.unity-mcp`.
   This is the UE-MCP-parity option when Josh wants live agent-in-editor work.
4. **Official Unity MCP + CLI** (beta): ships in `com.unity.ai.assistant`
   package; new official **Unity CLI** (`unity eval` = arbitrary C# against live
   editor, Unite Seoul 2026) is Unity's answer to UE Python macros. Free, but
   Unity 6-only and requires Cloud connection.

## Licensing notes

- Personal: free ≤ $200K revenue/funding; splash optional in Unity 6;
  batchmode allowed on Personal.
- ⚠️ 2026 ToS adds an "Authorized Agentic Access" framework — agents expected
  to connect through Unity-operated channels; third-party MCPs "allowed through
  authorized channels" per staff, community pushback ongoing. Watch this space.

## Sources

- MCP for Unity: https://github.com/CoplayDev/unity-mcp
- Official Unity MCP: https://docs.unity3d.com/Packages/com.unity.ai.assistant@2.0/manual/unity-mcp-overview.html
- Unity CLI: https://docs.unity.com/en-us/hub/unity-cli
