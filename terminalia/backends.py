"""Terminalia compute backends — local GPU, ComfyUI Cloud, RunPod, any rental.

Every stage (concept image, mesh, video) routes through a Backend that exposes
the same submit/poll/fetch interface. Users without a good GPU run everything
remotely; users with an RTX 6000 or DGX Spark get bigger presets automatically.

Backend selection order (first available wins unless overridden):
  1. local-comfy   — localhost ComfyUI (any port)
  2. comfy-cloud   — cloud.comfy.org (paid credits; X-API-Key auth)
  3. runpod        — serverless ComfyUI endpoint (pay-per-second)
  4. custom        — any HTTP ComfyUI-compatible URL
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from dataclasses import dataclass, field


# --------------------------------------------------------------- profiles --

@dataclass
class GpuProfile:
    """Named hardware profiles. Presets scale to what the GPU can handle."""
    name: str
    vram_gb: float
    mesh_preset: str            # Trellis2 pipeline_type
    mesh_steps: tuple[int, int, int]
    use_tiled_decoder: bool = True
    low_vram: bool = True
    video_engine: str = "wan22"
    video_quant: str = "Q4_K_M"


GPU_PROFILES: dict[str, GpuProfile] = {
    # entry-level / shared rentals
    "rtx-3060-12gb":  GpuProfile("rtx-3060-12gb", 12, "512",
                                 (12, 12, 8), low_vram=True),
    "rtx-4090-24gb":  GpuProfile("rtx-4090-24gb", 24, "1024_cascade",
                                 (30, 16, 16), low_vram=True,
                                 video_quant="Q6_K"),
    "rtx-5090-32gb":  GpuProfile("rtx-5090-32gb", 32, "1536_cascade",
                                 (40, 16, 16), low_vram=False,
                                 video_quant="Q8_0"),
    "rtx-6000-48gb":  GpuProfile("rtx-6000-48gb", 48, "1536_cascade",
                                 (50, 24, 24), low_vram=False,
                                 use_tiled_decoder=False,   # full decode fits
                                 video_quant="fp16"),
    "dgx-spark-128gb": GpuProfile("dgx-spark-128gb", 128, "1536_cascade",
                                  (60, 32, 32), low_vram=False,
                                  use_tiled_decoder=False,
                                  video_quant="bf16"),
}


def profile_for_vram(vram_gb: float) -> GpuProfile:
    """Pick the largest profile whose tier fits, with 5% tolerance on the
    boundary (reported VRAM is often slightly under nominal, e.g. 23.98 on a
    '24GB' card)."""
    effective = vram_gb * 1.05
    best = min(GPU_PROFILES.values(), key=lambda p: p.vram_gb)
    for p in sorted(GPU_PROFILES.values(), key=lambda p: p.vram_gb):
        if p.vram_gb <= effective:
            best = p
    return best


# ---------------------------------------------------------------- backends --

@dataclass
class Backend:
    name: str
    base_url: str
    headers: dict = field(default_factory=dict)
    cost_hint: str = ""
    poll_interval_s: int = 4

    def _post(self, path: str, payload: dict) -> dict:
        req = urllib.request.Request(
            self.base_url + path, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", **self.headers})
        return json.loads(urllib.request.urlopen(req, timeout=120).read())

    def _get(self, path: str, timeout: int = 30):
        req = urllib.request.Request(self.base_url + path, headers=self.headers)
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

    def health(self) -> bool:
        try:
            self._get("/system_stats", timeout=8)
            return True
        except Exception:
            return False

    def submit(self, workflow: dict, client_id: str = "terminalia") -> str:
        body = {"prompt": workflow, "client_id": client_id}
        if "runpod" in self.name:
            # RunPod serverless wraps the payload
            body = {"input": body}
        resp = self._post("/prompt", body)
        return resp.get("prompt_id") or resp.get("id")

    def wait(self, prompt_id: str, timeout_s: int = 1800) -> dict:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            try:
                h = self._get(f"/history/{prompt_id}")
                if prompt_id in h:
                    st = h[prompt_id].get("status", {})
                    if st.get("status_str") == "error":
                        raise RuntimeError("execution error on backend")
                    return h[prompt_id].get("outputs", {})
            except urllib.error.HTTPError as e:
                if e.code == 404 and "runpod" in self.name:
                    pass  # still running
                else:
                    raise
            except Exception:
                if "runpod" in self.name:
                    pass
                else:
                    raise
            time.sleep(self.poll_interval_s)
        raise TimeoutError(f"{prompt_id} on {self.name}")

    def fetch_file_url(self, filename: str, subfolder: str = "") -> str:
        from urllib.parse import quote
        return (f"{self.base_url}/view?filename={quote(filename)}"
                f"&subfolder={quote(subfolder)}&type=output")


def detect_backends(cloud_key: str | None = None,
                    runpod_key: str | None = None,
                    custom_url: str | None = None) -> list[Backend]:
    """Probe in preference order; returns reachable backends only."""
    found: list[Backend] = []

    local_port = os.environ.get("TERMINALIA_COMFY_PORT", "8000")
    local = Backend("local-comfy", f"http://127.0.0.1:{local_port}",
                    cost_hint="free")
    if local.health():
        found.append(local)

    key = cloud_key or os.environ.get("COMFY_CLOUD_API_KEY")
    if key:
        cloud = Backend("comfy-cloud", "https://cloud.comfy.org/api",
                        headers={"X-API-Key": key},
                        cost_hint="credits (~$0.01-0.05/image-tier)")
        if cloud.health():
            found.append(cloud)

    rk = runpod_key or os.environ.get("RUNPOD_API_KEY")
    rp_id = os.environ.get("RUNPOD_ENDPOINT_ID")
    if rk and rp_id:
        rp = Backend(
            "runpod-serverless",
            f"https://api.runpod.ai/v2/{rp_id}",
            headers={"Authorization": f"Bearer {rk}"},
            cost_hint="~$0.00031/s idle + GPU-sec")
        found.append(rp)

    if custom_url:
        cu = Backend("custom", custom_url.rstrip("/"), cost_hint="varies")
        if cu.health():
            found.append(cu)

    return found


def pick_backend(backends: list[Backend], prefer: str | None = None) -> Backend | None:
    if prefer:
        for b in backends:
            if b.name == prefer:
                return b
    return backends[0] if backends else None


def resolve(profile_name: str | None = None, vram_gb: float | None = None,
            prefer_backend: str | None = None,
            allow_cloud: bool = True) -> tuple[Backend, GpuProfile]:
    """One-call setup: detect backends, pick one, resolve the GPU profile.

    Local GPU detected via nvidia-smi when present; otherwise defaults to the
    smallest remote profile and lets the backend's own hardware decide.
    """
    backends = detect_backends()
    if not allow_cloud:
        backends = [b for b in backends if "cloud" not in b.name and "runpod" not in b.name]
    backend = pick_backend(backends, prefer_backend)
    if backend is None:
        raise RuntimeError(
            "No ComfyUI backend reachable. Start local ComfyUI, set "
            "COMFY_CLOUD_API_KEY, or configure RUNPOD_API_KEY+RUNPOD_ENDPOINT_ID.")

    if profile_name and profile_name in GPU_PROFILES:
        return backend, GPU_PROFILES[profile_name]

    if vram_gb is None and backend.name == "local-comfy":
        try:
            stats = json.loads(urllib.request.urlopen(
                backend.base_url + "/system_stats", timeout=10).read())
            for dev in stats.get("devices", []):
                vram_gb = dev.get("vram_total", 0) / (1024 ** 3)
                break
        except Exception:
            vram_gb = None
    if vram_gb is None:
        vram_gb = 24.0  # sensible default for rental instances

    return backend, profile_for_vram(vram_gb)
