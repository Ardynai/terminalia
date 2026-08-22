"""Terminalia asset generation — concept image → TRELLIS.2 PBR GLB via ComfyUI.

Reuses the proven wire format from the verified Hermes pipeline runs.
"""
from __future__ import annotations

import json
import shutil
import time
import urllib.request

COMFY = "http://127.0.0.1:8000"
SDXL_WORKFLOW = r"C:\Users\Josh\Documents\ComfyUI\workflows\..\..\..\.hermes"  # unused; built inline


def _submit(workflow: dict, client_id: str) -> str:
    payload = {"prompt": workflow, "client_id": client_id}
    req = urllib.request.Request(
        f"{COMFY}/prompt", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=60)
    return json.loads(resp.read())["prompt_id"]


def _wait(prompt_id: str, timeout_s: int = 900) -> dict:
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        h = json.loads(urllib.request.urlopen(
            f"{COMFY}/history/{prompt_id}", timeout=20).read())
        if prompt_id in h:
            entry = h[prompt_id]
            st = entry.get("status", {})
            if st.get("status_str") == "error":
                err = [m for m in st.get("messages", []) if m[0] == "execution_error"]
                if err:
                    e = err[0][1]
                    raise RuntimeError(f"{e['node_type']}: {e['exception_message']}")
            return entry.get("outputs", {})
        time.sleep(4)
    raise TimeoutError(f"job {prompt_id} timed out")


def generate_concept(name: str, description: str,
                     out_dir: str, seed: int = 42) -> str:
    """SDXL white-background concept render for mesh input."""
    wf_path = os.path.join(os.path.dirname(__file__), "..", "workflows",
                           "sdxl_concept.json")
    with open(wf_path) as f:
        wf = json.load(f)
    wf.pop("_comment", None)  # crashes ComfyUI validation
    wf["6"]["inputs"]["text"] = (
        f"game asset, {description}, full object, centered, "
        "plain solid white background, soft studio lighting, high detail 3d render style")
    wf["7"]["inputs"]["text"] = "background clutter, cropped, blurry, text, watermark"
    wf["3"]["inputs"]["seed"] = seed
    pid = _submit(wf, f"term-concept-{name}")
    outs = _wait(pid)
    for nid, out in outs.items():
        for img in out.get("images", []):
            src = f"/mnt/c/Users/Josh/Documents/ComfyUI/output/{img['filename']}"
            dest = os.path.join(out_dir, f"{name}_concept.png")
            shutil.copy2(src, dest)
            # also copy into ComfyUI input for the mesh stage
            shutil.copy2(dest, "/mnt/c/Users/Josh/Documents/ComfyUI/input/")
            return dest
    raise RuntimeError("no image output")


import os  # noqa: E402


def generate_mesh(concept_filename: str, out_dir: str, name: str,
                  preset: str = "1024_cascade",
                  steps: tuple[int, int, int] = (30, 16, 16),
                  seed: int = 42) -> str:
    """TRELLIS.2-4B: concept PNG (already in ComfyUI input) → textured GLB."""
    wf = {
        "1": {"class_type": "Trellis2LoadImageWithTransparency_GGUF",
              "inputs": {"image": concept_filename}},
        "2": {"class_type": "Trellis2PreProcessImage_GGUF",
              "inputs": {"image": ["1", 0], "padding": 20,
                         "remove_background": True}},
        "3": {"class_type": "Trellis2LoadModel_GGUF",
              "inputs": {"modelname": "TRELLIS.2-4B",
                         "model_format": "GGUF Q4_K_M", "backend": "sdpa",
                         "device": "cuda", "low_vram": True,
                         "keep_models_loaded": True}},
        "4": {"class_type": "Trellis2MeshWithVoxelGenerator_GGUF",
              "inputs": {"pipeline": ["3", 0], "image": ["2", 0], "seed": seed,
                         "pipeline_type": preset,
                         "sparse_structure_steps": steps[0],
                         "shape_steps": steps[1], "texture_steps": steps[2],
                         "max_num_tokens": 999999,
                         "sparse_structure_resolution": 32, "max_views": 1,
                         "generate_texture_slat": True,
                         "use_tiled_decoder": True}},
        "6": {"class_type": "Trellis2MeshWithVoxelToTrimesh_GGUF",
              "inputs": {"mesh": ["4", 0], "reorient_vertices": "90 degrees",
                         "rotate_x": 0.0, "rotate_y": 0.0, "rotate_z": 0.0}},
        "5": {"class_type": "Trellis2ExportMesh_GGUF",
              "inputs": {"trimesh": ["6", 0],
                         "filename_prefix": f"3D/terminalia_{name}",
                         "file_format": "glb"}},
    }
    pid = _submit(wf, f"term-mesh-{name}")
    _wait(pid)
    src = f"/mnt/c/Users/Josh/Documents/ComfyUI/output/3D/terminalia_{name}_00001_.glb"
    dest = os.path.join(out_dir, "mesh.glb")
    shutil.copy2(src, dest)
    return dest
