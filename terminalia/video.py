"""Terminalia video stage — flythroughs, character lock, consistency.

Integrations:
- ComfyUI (Wan2.1, LTX-2): world flythrough I2V from camera-key renders
- ReActor (installed in ComfyUI): face swap onto characters
- Qwen-Image-Edit / Flux Kontext (ComfyUI): character sheet consistency
- OmniDirector-style camera cloning: reference clip → camera path
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .backends import Backend, GPU_PROFILES, GpuProfile
from .refine import FIX_ANYTHING_WEIGHTS
from .schema import ArtifactRef, HistoryEntry, ModelRef, VideoProvenance, World


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
            cx = sum(o["pos_xy"][0] for o in objs) / len(objs) * mpp
            cy = sum(o["pos_xy"][1] for o in objs) / len(objs) * mpp
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

class LicenseAttestationRequired(RuntimeError):
    """Raised when a conditionally licensed model was not attested."""


WAN21_MODEL = ModelRef(
    name="Wan2.1-I2V-14B-480P",
    version=FIX_ANYTHING_WEIGHTS["base"].rsplit("@", 1)[1],
    license="Apache-2.0",
)
LTX2_LICENSE = (
    "Lightricks LTX-Video Community License; commercial use permitted for "
    "entities under USD $10M annual revenue; paid Commercial Use Agreement "
    "required at or above USD $10M annual revenue"
)
LTX2_MODEL = ModelRef(name="LTX-Video-2", version="2.0", license=LTX2_LICENSE)
_TEMPLATES = Path(__file__).parent.parent / "workflows" / "api"


def _model_filename(engine: str, quant: str) -> str:
    if engine == "wan21":
        return (f"wan2.1_i2v_480p_14B_{quant}.safetensors"
                if quant in {"fp16", "bf16"} else
                f"wan2.1-i2v-14b-480p-{quant}.gguf")
    return (f"ltx-video-2-19b-dev-{quant}.safetensors"
            if quant in {"fp16", "bf16"} else
            f"ltx-video-2-19b-dev-{quant}.gguf")


def flythrough_workflow(keyframe_images: list[str], engine: str = "wan21",
                        profile: GpuProfile | None = None, seed: int = 42) -> dict:
    """Build a deterministic ComfyUI API prompt from ordered camera renders."""
    if not keyframe_images:
        raise ValueError("at least one keyframe image is required")
    if engine not in {"wan21", "ltx2"}:
        raise ValueError(f"unknown engine: {engine}")
    if engine == "ltx2" and os.environ.get("TERMINALIA_LTX_OK_UNDER_10M") != "1":
        raise LicenseAttestationRequired(
            "LTX-2 requires TERMINALIA_LTX_OK_UNDER_10M=1 to attest that the "
            "using entity has under USD $10M annual revenue; otherwise obtain "
            "a Commercial Use Agreement from ltxv-licensing@lightricks.com")

    profile = profile or GPU_PROFILES["rtx-4090-24gb"]
    with open(_TEMPLATES / f"flythrough_{engine}_api.json") as f:
        workflow = json.load(f)
    workflow["1"]["inputs"]["image"] = keyframe_images[0]
    workflow["2"]["inputs"]["unet_name"] = _model_filename(engine, profile.video_quant)
    if profile.video_quant not in {"fp16", "bf16"}:
        workflow["2"]["class_type"] = "UnetLoaderGGUF"
    workflow["9"]["inputs"]["seed"] = seed
    workflow["11"]["inputs"]["filename_prefix"] = f"video/terminalia_{engine}_{seed}"
    return workflow


def _video_artifacts(backend: Backend, outputs: dict) -> list[ArtifactRef]:
    artifacts = []
    for node in sorted(outputs):
        for item in outputs[node].get("videos", []):
            artifacts.append(ArtifactRef(
                uri=backend.fetch_file_url(item["filename"], item.get("subfolder", "")),
                kind="video"))
    if not artifacts:
        raise RuntimeError("flythrough backend returned no video artifact")
    return artifacts


def flythrough(world: World, keyframe_images: list[str], backend: Backend,
               profile: GpuProfile, engine: str | None = None) -> World:
    """Execute a flythrough and record its output and provenance in ``world``."""
    engine = engine or profile.video_engine
    workflow = flythrough_workflow(keyframe_images, engine, profile, world.spec.seed)
    prompt_id = backend.submit(workflow, client_id=f"terminalia-flythrough-{world.spec.seed}")
    artifacts = _video_artifacts(backend, backend.wait(prompt_id))
    model = WAN21_MODEL if engine == "wan21" else LTX2_MODEL
    world.video_provenance = VideoProvenance(
        models=[model], engine=engine, seed=world.spec.seed, backend=backend.name,
        profile=profile.name, artifacts=artifacts)
    world.history.append(HistoryEntry(
        stage="video.flythrough", at="", notes=f"{engine}; seed={world.spec.seed}"))
    return world


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
