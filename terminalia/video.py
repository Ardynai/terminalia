"""Terminalia video stage — flythroughs, character lock, consistency.

Integrations:
- Wan2GP / ComfyUI (Wan 2.2, LTX-2): world flythrough I2V from camera-key renders
- ReActor (installed in ComfyUI): face swap onto characters
- Qwen-Image-Edit / Flux Kontext (ComfyUI): character sheet consistency
- OmniDirector-style camera cloning: reference clip → camera path
"""
from __future__ import annotations

import json

COMFY = "http://127.0.0.1:8000"


# ------------------------------------------------------- camera keyframes ---

def camera_keyframes(world: dict, n: int = 8, height_m: float = 25.0) -> list[dict]:
    """Sample the camera path (or auto-orbit POIs) into n keyframe positions."""
    terrain = world.get("terrain", {})
    mpp = terrain.get("meters_per_pixel", 2.0)
    path = world.get("camera", {}).get("waypoints") or []
    if len(path) < 2:
        # auto: circle the layout centroid
        objs = world.get("layout", {}).get("objects", [])
        if objs:
            cx = sum(o["pos_xy"][0] for o in objs.values()) / len(objs) * mpp
            cy = sum(o["pos_xy"][1] for o in objs.values()) / len(objs) * mpp
        else:
            cx = cy = world.get("spec", {}).get("size_hectares", 100) * 50
        import math
        r = max(200, world.get("spec", {}).get("size_hectares", 100))
        path = [(cx + r * math.cos(2*math.pi*i/n),
                 cy + r * math.sin(2*math.pi*i/n)) for i in range(n)]
    keys = []
    for i, (x, y) in enumerate(path[:n]):
        keys.append({
            "frame": i, "x": x, "y": y,
            "z": terrain.get("max_height_m", 220) * 0.3 + height_m,
            "look_at": [cx, cy] if objs else None,
        })
    return keys


# --------------------------------------------------------- character lock ---

def character_lock_workflow(reference_image: str, prompt: str,
                            n_views: int = 4) -> dict:
    """Consistent multi-view character sheet via Qwen-Image-Edit GGUF.

    Returns a ComfyUI workflow dict. The SAME character appears across views:
    view 1 is the reference; each subsequent view is 'same character, <angle>'
    conditioned on view 1 (edit-model conditioning keeps identity).
    """
    angles = ["front view", "three-quarter left", "side profile left",
              "three-quarter right"][:n_views]
    nodes = {}
    prev = "1"
    nodes["1"] = {"class_type": "LoadImage", "inputs": {"image": reference_image}}
    for i, angle in enumerate(angles[1:], start=2):
        nodes[str(i)] = {"class_type": "TextEncodeQwenImageEdit",
                         "inputs": {"clip": ["1", 1], "image": [prev, 0],
                                    "prompt": f"same character, {angle}, "
                                              f"{prompt}, consistent identity"}}
        prev = str(i)
    return {"workflow": nodes, "views": angles}


def face_swap_workflow(source_face: str, target_frame: str) -> dict:
    """ReActor face swap — keep a canonical character face across all shots."""
    return {
        "class_type": "ReActorFaceSwap",
        "inputs": {"source_image": source_face, "input_image": target_frame,
                   "swap_in_source_images": False, "face_restore_model":
                   "codeformer-v0.1.0.pth"},
    }


# ------------------------------------------------------------ flythrough ----

def flythrough_workflow(world_dir: str, keyframe_images: list[str],
                        engine: str = "wan22") -> dict:
    """Keyframe renders → video. Wan2.2 I2V (ComfyUI native) or LTX-2.

    keyframe_images: ordered stills rendered from Blender at camera keys.
    """
    if engine == "wan22":
        return {
            "engine": "wan22-i2v",
            "note": "Use ComfyUI native Wan2.2 I2V template; feed keyframe 1 "
                    "as start image; FLF2V variant accepts last keyframe too",
            "first_frame": keyframe_images[0] if keyframe_images else None,
            "last_frame": keyframe_images[-1] if len(keyframe_images) > 1 else None,
            "recommended": "Wan2.2-I2V-A14B-GGUF Q4_K_M (fits 24GB)",
        }
    if engine == "ltx2":
        return {
            "engine": "ltx2",
            "note": "LTX-2.5 GGUF Q6_K; keyframes as conditioning frames; "
                    "audio+video joint generation",
            "frames": keyframe_images,
        }
    raise ValueError(f"unknown engine: {engine}")


# ------------------------------------------------------------ repo bridges --

REPO_INTEGRATIONS = {
    # repo name (C:\AI\content-creation\) -> role in Terminalia
    "Wan2GP": {
        "role": "video_generation",
        "use": "flythrough QA, cutscene generation; Gradio API callable headless",
        "stage": "video",
    },
    "PermaVid": {
        "role": "consistent_video_edit",
        "use": "identity-consistent multi-shot editing of world cutscenes",
        "stage": "video",
    },
    "MoneyPrinterTurbo": {
        "role": "video_assembly",
        "use": "script→voiceover→subtitles→render for world trailer packaging",
        "stage": "post",
    },
    "omnivoice-studio": {
        "role": "voiceover",
        "use": "narration for flythroughs; character voices",
        "stage": "post",
    },
    "magenta-realtime": {
        "role": "music",
        "use": "live generative score for world exploration videos",
        "stage": "post",
    },
    "ultimate-vocal-remover": {
        "role": "audio_cleanup",
        "use": "stem separation for imported audio",
        "stage": "post",
    },
    "ai-toolkit": {
        "role": "lora_training",
        "use": "train style/character LoRAs for cross-world consistency",
        "stage": "assets",
    },
    "viewdiff": {
        "role": "3d_consistent_t2i",
        "use": "multi-view consistent asset concept sheets",
        "stage": "assets",
    },
    "TeleStyleV2": {
        "role": "style_transfer",
        "use": "unify asset/world art style to one reference",
        "stage": "assets",
    },
    "supersplat": {
        "role": "splat_editor",
        "use": "edit WorldMirror-2.0 splat captures; export optimized ply",
        "stage": "capture",
    },
    "gaussiansplats3d": {
        "role": "splat_viewer",
        "use": "web viewer for world splat captures",
        "stage": "capture",
    },
    "3dgs-render-blender-addon": {
        "role": "splat_render_blender",
        "use": "render splats inside the Blender refine loop",
        "stage": "refine",
    },
    "rembg": {
        "role": "matting",
        "use": "background removal for asset concept images (Trellis2 preprocess "
               "already does this; rembg for batch)",
        "stage": "assets",
    },
    "motion-canvas": {
        "role": "programmatic_video",
        "use": "code-driven camera choreography for flythroughs",
        "stage": "video",
    },
    "remotion-player-sandbox": {
        "role": "programmatic_video",
        "use": "React-based world trailer templating",
        "stage": "post",
    },
    "OpenCut": {
        "role": "final_edit",
        "use": "human-in-the-loop final assembly at localhost:3011",
        "stage": "post",
    },
    "Audio2Face-3D": {
        "role": "facial_animation",
        "use": "audio→facial animation for world NPCs (cloned, needs setup)",
        "stage": "characters",
    },
    "duix-avatar": {
        "role": "talking_avatar",
        "use": "talking-head NPCs from voiceover",
        "stage": "characters",
    },
}
