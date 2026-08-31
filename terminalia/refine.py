"""REFINE sub-stages."""
from __future__ import annotations

from .backends import Backend, GpuProfile
from .schema import ArtifactRef, FixAnythingPass, World

FIX_ANYTHING_WEIGHTS = {
    "lora": "hf://kvuong2711/fix-anything@f6a13d034eb9015be4140d8d34fa82c89da2ab7a/fixanything_lora.safetensors",
    "base": "hf://Wan-AI/Wan2.1-I2V-14B-480P@f28b0cfee1e6c330ca5dd5227f8ba0d23ee5a4db",
}
_REMOTE_BACKENDS = {"comfy-cloud", "runpod-serverless"}


def can_run_fix_anything(backend: Backend, profile: GpuProfile) -> bool:
    """Cloud runtimes manage capacity; local/custom runtimes need 32GB+."""
    return backend.name in _REMOTE_BACKENDS or profile.vram_gb >= 32


def _output_artifacts(backend: Backend, outputs: dict) -> list[ArtifactRef]:
    artifacts = []
    for node in sorted(outputs):
        for item in outputs[node].get("videos", []):
            artifacts.append(ArtifactRef(
                uri=backend.fetch_file_url(item["filename"], item.get("subfolder", "")),
                kind="video"))
    if not artifacts:
        raise RuntimeError("fix-anything backend returned no video artifact")
    return artifacts


def fix_anything(world: World, backend: Backend, profile: GpuProfile) -> World:
    """Clean the render artifacts already recorded in ``world``."""
    inputs = world.refine.render_artifacts
    if not inputs:
        raise ValueError("world.refine.render_artifacts must contain a render")

    if not can_run_fix_anything(backend, profile):
        world.refine.fix_anything = FixAnythingPass(
            status="skipped", inputs=inputs, seed=world.spec.seed,
            backend=backend.name, profile=profile.name,
            weights=FIX_ANYTHING_WEIGHTS,
            reason="insufficient profile")
        return world

    workflow = {
        "fix_anything": {
            "class_type": "TerminaliaFixAnything",
            "inputs": {
                "artifacts": [a.model_dump() for a in inputs],
                "seed": world.spec.seed,
                "base_weights": FIX_ANYTHING_WEIGHTS["base"],
                "lora_weights": FIX_ANYTHING_WEIGHTS["lora"],
                "clean_frame_indices": [0, 60],
            },
        },
    }
    prompt_id = backend.submit(workflow, client_id=f"terminalia-fix-anything-{world.spec.seed}")
    cleaned = _output_artifacts(backend, backend.wait(prompt_id))
    world.refine.fix_anything = FixAnythingPass(
        status="ran", inputs=inputs, outputs=cleaned, seed=world.spec.seed,
        backend=backend.name, profile=profile.name,
        weights=FIX_ANYTHING_WEIGHTS)
    return world
