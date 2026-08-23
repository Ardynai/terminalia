# How it works — frames (video → images)

**Owns:** extracting still frames from any video for use as asset references,
I2V conditioning, or analysis.
**Key files:** ComfyUI VideoHelperSuite nodes (installed) — no new dependency.

## Verified working pipeline (2026-08-22)

```jsonc
{
  "1": {"class_type": "VHS_LoadVideo",
        "inputs": {"video": "<file.mp4>",   // file in ComfyUI input dir
                    "force_rate": 2,          // fps override (0 = native)
                    "custom_width": 0,        // 0 = native
                    "custom_height": 0,
                    "frame_load_cap": 6,      // max frames (0 = all)
                    "skip_first_frames": 0,
                    "select_every_nth": 1}},
  "2": {"class_type": "SaveImage",
        "inputs": {"images": ["1", 0], "filename_prefix": "frames/x"}}
}
```

Gotcha: ALL VHS_LoadVideo params are REQUIRED in API format even when the
schema shows defaults — omit `custom_width/height` and you get a silent
"required input missing" validation error.

Alternatives on the same box:
- `VHS_LoadVideoFFmpeg` — same but with start_time seeking, uses ffmpeg directly
- `GetVideoComponents` — splits VIDEO into IMAGE + AUDIO + mask
- Plain `ffmpeg -i x.mp4 frames/%04d.png` outside ComfyUI

## OpenCut relationship

OpenCut edits timelines; it does not export raw frame sequences as a primary
feature. For frame extraction inside the Terminalia pipeline, use the VHS
nodes above. OpenCut is for human final assembly.
