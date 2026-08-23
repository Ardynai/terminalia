# WSL Mirrored-Networking Fixes for OpenMontage / Remotion

Two patches applied to `C:\AI\content-creation\openmontage` on 2026-08-22 to
make Remotion renders work under WSL2 mirrored networking.

## Patch 1 — render_demo.py npx resolution
`find_command("npx.cmd", "npx", "npx.exe")` → reordered to prefer the WSL
native `npx`: `find_command("npx", "npx.cmd", "npx.exe")`.
(Windows .cmd files can't exec from WSL Python.)

## Patch 2 — get-port.js (both dist/get-port.js and esm/index.mjs)
Remotion probes free ports by **connecting** to them. Under WSL mirrored
networking, connects to free ports hang (3s timeout each) instead of failing
fast, so every port in the 3000–3100 range is marked "unavailable" and renders
die with "No available ports found".

Fix: replaced `isPortAvailableOnHost` with a **bind-test** (create a server on
the port; if bind succeeds it's free) and changed multi-host semantics from
ALL-hosts-must-pass to ANY-host-passes.

The fixed file ships here: `remotion-get-port-wsl-fixed.js`. To reapply after a
fresh install:

```bash
cp patches/remotion-get-port-wsl-fixed.js \
   /mnt/c/AI/content-creation/openmontage/remotion-composer/node_modules/@remotion/renderer/dist/get-port.js
```

Note: also keep `render_demo.py`'s find_command order patched (diff included).

## Verified result

`make demo DEMO=focusflow-pitch` → 750/750 frames rendered → 3.7MB MP4 ✓
