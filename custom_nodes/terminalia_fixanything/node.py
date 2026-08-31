"""Runtime implementation of the ``TerminaliaFixAnything`` ComfyUI node."""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

from .constants import FIX_ANYTHING_WEIGHTS

_HF_REF = re.compile(r"^hf://(?P<repo>[^@]+)@(?P<revision>[0-9a-f]{40})(?:/(?P<file>.+))?$")


def _parse_hf_ref(value: str) -> tuple[str, str, str | None]:
    match = _HF_REF.fullmatch(value)
    if not match:
        raise ValueError(f"expected a commit-pinned Hugging Face reference, got {value!r}")
    return match.group("repo"), match.group("revision"), match.group("file")


def _output_directory() -> Path:
    try:
        import folder_paths
        return Path(folder_paths.get_output_directory()) / "terminalia"
    except ImportError:
        return Path(os.environ.get("TERMINALIA_COMFY_OUTPUT", tempfile.gettempdir())) / "terminalia"


def _model_directory() -> Path:
    try:
        import folder_paths
        return Path(folder_paths.models_dir) / "terminalia" / "fixanything"
    except ImportError:
        return Path(os.environ.get("TERMINALIA_FIXANYTHING_MODELS", "models/terminalia/fixanything"))


def _artifact_path(artifacts: list[dict], temporary: Path) -> Path:
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("artifacts must be a non-empty list")
    artifact = artifacts[0]
    if not isinstance(artifact, dict) or artifact.get("kind") not in {"video", "frames"}:
        raise ValueError("each artifact must contain uri and kind ('video' or 'frames')")
    uri = artifact.get("uri")
    if not isinstance(uri, str) or not uri:
        raise ValueError("artifact uri must be a non-empty string")
    parsed = urllib.parse.urlparse(uri)
    if parsed.scheme in {"http", "https"}:
        target = temporary / (Path(parsed.path).name or "input.mp4")
        try:
            with urllib.request.urlopen(uri, timeout=300) as source, target.open("wb") as dest:
                shutil.copyfileobj(source, dest)
        except Exception as exc:
            raise RuntimeError(f"could not fetch input artifact {uri!r}") from exc
        return target
    if parsed.scheme == "file":
        path = Path(urllib.request.url2pathname(parsed.path))
    elif parsed.scheme:
        raise ValueError(f"unsupported artifact URI scheme: {parsed.scheme}")
    else:
        path = Path(uri)
    if not path.exists():
        raise FileNotFoundError(f"input artifact not found: {path}")
    return path


def _seed_everything(seed: int) -> None:
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import numpy
        numpy.random.seed(seed % (2**32))
    except ImportError:
        pass
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.use_deterministic_algorithms(True)
        torch.backends.cudnn.benchmark = False
    except ImportError:
        pass


def _run(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError as exc:
        raise RuntimeError(f"required executable not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode(errors="replace").strip()
        raise RuntimeError(f"{command[0]} failed: {detail}") from exc


def _mock_transform(source: Path, output: Path, seed: int) -> None:
    """Apply a deterministic cleanup-like denoise/sharpen transform."""
    if source.is_dir():
        frames = sorted(p for p in source.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"})
        if not frames:
            raise ValueError(f"frame artifact contains no images: {source}")
        manifest = output.parent / "frames.txt"
        manifest.write_text("".join(f"file '{p.resolve().as_posix()}'\nduration 0.0666666667\n" for p in frames)
                            + f"file '{frames[-1].resolve().as_posix()}'\n")
        input_args = ["-f", "concat", "-safe", "0", "-i", str(manifest)]
    else:
        input_args = ["-i", str(source)]
    # Seed selects a stable, subtle sharpening strength; no stochastic filter is used.
    amount = 0.35 + (seed % 11) / 100
    _run(["ffmpeg", "-y", "-loglevel", "error", *input_args, "-map_metadata", "-1",
          "-vf", f"hqdn3d=1.5:1.5:6:6,unsharp=5:5:{amount:.2f}:5:5:0",
          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
          "-an", "-threads", "1", str(output)])


def _download_weights(base_ref: str, lora_ref: str, root: Path) -> tuple[Path, Path]:
    try:
        from huggingface_hub import hf_hub_download, snapshot_download
    except ImportError as exc:
        raise RuntimeError("real mode requires huggingface_hub and the upstream fix-anything package") from exc
    base_repo, base_revision, base_file = _parse_hf_ref(base_ref)
    lora_repo, lora_revision, lora_file = _parse_hf_ref(lora_ref)
    if base_file is not None or lora_file is None:
        raise ValueError("base_weights must name a repository and lora_weights must name a file")
    root.mkdir(parents=True, exist_ok=True)
    try:
        base = Path(snapshot_download(base_repo, revision=base_revision, local_dir=root / base_repo))
        lora = Path(hf_hub_download(lora_repo, lora_file, revision=lora_revision,
                                    local_dir=root / lora_repo))
    except Exception as exc:
        raise RuntimeError("FixAnything model files are absent and could not be fetched") from exc
    return base, lora


def _real_transform(source: Path, output: Path, seed: int, base_ref: str,
                    lora_ref: str, clean_frame_indices: list[int]) -> None:
    try:
        import torch
        from diffsynth.utils import ModelConfig
        from fixanything.data import load_frames, save_video
        from fixanything.pipelines import WanVideoPipeline
    except ImportError as exc:
        raise RuntimeError("real mode requires torch, DiffSynth-Studio, and upstream fix-anything") from exc

    base, lora = _download_weights(base_ref, lora_ref, _model_directory())
    patterns = ["diffusion_pytorch_model*.safetensors", "models_t5_umt5-xxl-enc-bf16.pth",
                "Wan2.1_VAE.pth", "models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth"]
    model_root = base.parents[1]
    base_repo, _, _ = _parse_hf_ref(base_ref)
    configs = [ModelConfig(model_id=base_repo, origin_file_pattern=pattern,
                           local_model_path=str(model_root), download_resource="huggingface",
                           skip_download=True, offload_device="cpu") for pattern in patterns]
    tokenizer = ModelConfig(model_id=base_repo, origin_file_pattern="google/*",
                            local_model_path=str(model_root), download_resource="huggingface",
                            skip_download=True)
    pipe = WanVideoPipeline.from_pretrained(torch_dtype=torch.bfloat16, device="cuda",
                                             model_configs=configs, tokenizer_config=tokenizer,
                                             redirect_common_files=False)
    pipe.load_lora(pipe.dit, str(lora), alpha=1.0)
    pipe.enable_vram_management()
    frames, _ = load_frames(str(source), 480, 832, num_frames=61)
    if len(frames) < 61:
        raise ValueError(f"FixAnything requires 61 input frames, got {len(frames)}")
    reference = frames[:61] + [frames[60]] * 4
    clean = set(int(i) for i in clean_frame_indices)
    if 60 in clean:
        clean.update(range(61, 65))
    generated = pipe(
        prompt="A clean, high-quality, photorealistic video with sharp details, smooth motion, and natural lighting.",
        negative_prompt="色调艳丽，过曝，静态，细节模糊不清，字幕，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，畸形的，毁容",
        input_image=reference[0], reference_video=reference,
        clean_frame_indices=sorted(clean), num_frames=65, height=480, width=832,
        seed=seed, tiled=True, num_inference_steps=10, cfg_scale=5.0)
    save_video(generated[:61], str(output), fps=15)


class TerminaliaFixAnything:
    """Refine a render with pinned Wan2.1 + FixAnything weights.

    Determinism contract: a fixed input, seed, pinned weights, package/CUDA stack,
    and hardware produces the same frames. Python, NumPy, Torch, and CUDA RNGs are
    seeded; deterministic Torch algorithms are required; the sampler receives the
    seed directly; and no time-based or temporal randomness is used. Cross-device
    or cross-version byte identity is not promised because GPU kernels and video
    codecs may differ. Mock mode is byte-identical on the same ffmpeg build.
    """

    OUTPUT_NODE = True
    RETURN_TYPES = ()
    FUNCTION = "execute"
    CATEGORY = "Terminalia/refinement"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "artifacts": ("TERMINALIA_ARTIFACTS",),
                "seed": ("INT", {"default": 1, "min": 0, "max": 2**63 - 1}),
                "base_weights": ("STRING", {"default": FIX_ANYTHING_WEIGHTS["base"]}),
                "lora_weights": ("STRING", {"default": FIX_ANYTHING_WEIGHTS["lora"]}),
                "clean_frame_indices": ("TERMINALIA_FRAME_INDICES",),
            },
            "optional": {"mock": ("BOOLEAN", {"default": False})},
        }

    def execute(self, artifacts, seed, base_weights, lora_weights,
                clean_frame_indices, mock=False):
        if base_weights != FIX_ANYTHING_WEIGHTS["base"] or lora_weights != FIX_ANYTHING_WEIGHTS["lora"]:
            raise ValueError("TerminaliaFixAnything only accepts Terminalia's pinned model revisions")
        seed = int(seed)
        if not 0 <= seed <= 2**63 - 1:
            raise ValueError("seed must be between 0 and 2^63-1")
        _seed_everything(seed)
        output_dir = _output_directory()
        output_dir.mkdir(parents=True, exist_ok=True)
        identity = json.dumps([seed, artifacts], sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(identity.encode()).hexdigest()[:16]
        filename = f"fixanything-{digest}.mp4"
        output = output_dir / filename
        with tempfile.TemporaryDirectory(prefix="terminalia-fixanything-") as temp:
            temporary = Path(temp)
            source = _artifact_path(artifacts, temporary)
            staged_output = temporary / "output.mp4"
            use_mock = mock or os.environ.get("TERMINALIA_FIXANYTHING_MOCK") == "1"
            if use_mock:
                _mock_transform(source, staged_output, seed)
            else:
                _real_transform(source, staged_output, seed, base_weights, lora_weights,
                                list(clean_frame_indices))
            os.replace(staged_output, output)
        return {"ui": {"videos": [{"filename": filename, "subfolder": "terminalia", "type": "output"}]},
                "result": ()}
