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
