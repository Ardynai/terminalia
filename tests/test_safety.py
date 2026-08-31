"""Child-safety gate regression tests; no network or real video decoding."""
import importlib.util

import pytest

from terminalia.backends import GPU_PROFILES
from terminalia.ingest import UnsafeVideoError, ingest_video
from terminalia import safety


class GateBackend:
    name = "test"

    def __init__(self, verdict):
        self.verdict = verdict
        self.jobs = []

    def submit(self, workflow, client_id="terminalia"):
        self.jobs.append(workflow)
        return str(len(self.jobs))

    def wait(self, prompt_id):
        if len(self.jobs) == 1:
            return {"terminalia_result": self.verdict}
        return {"terminalia_result": {"models": [{
            "name": "scene-model", "version": "1", "license": "MIT"}],
            "instances": [{"id": "one", "mesh": "one.glb", "poses": [{
                "frame": 0, "translation": [0, 0, 0],
                "rotation_xyzw": [0, 0, 0, 1]}]}]}}


def request(tmp_path):
    path = tmp_path / "input.mp4"
    path.write_bytes(b"fixture")
    return {"video_path": str(path), "consent_note": "consented", "seed": 9}


@pytest.mark.parametrize("verdict", [
    {"safe": False}, {}, {"safe": True, "model": "garbled"},
    {"safe": True, "model": {"name": "stub", "version": "1", "license": "test"}},
])
def test_unsafe_missing_or_garbled_verdict_stops_before_world(tmp_path, monkeypatch, verdict):
    monkeypatch.setenv("TERMINALIA_SAFETY_MOCK", "1")
    backend = GateBackend(verdict)
    with pytest.raises(UnsafeVideoError):
        ingest_video(request(tmp_path), backend, GPU_PROFILES["rtx-3060-12gb"])
    assert len(backend.jobs) == 1
    assert not (tmp_path / "world.json").exists()


def test_safe_real_model_identity_proceeds(tmp_path, monkeypatch):
    monkeypatch.setenv("TERMINALIA_SAFETY_MOCK", "1")
    model = {"name": "nvidia/nemotron-3.5-content-safety", "version": "3.5",
             "license": "OpenMDW-1.1, Gemma Terms of Use, and Gemma Prohibited Use Policy"}
    world = ingest_video(request(tmp_path), GateBackend({"safe": True, "model": model}),
                         GPU_PROFILES["rtx-3060-12gb"])
    assert world["video_provenance"]["models"][0] == model


def test_no_backend_is_founder_action_reject_all(tmp_path, monkeypatch):
    for key in ("OPENAI_API_KEY", "NVIDIA_API_KEY", "NEMOTRON_SAFETY_DIR",
                "TERMINALIA_SAFETY_MOCK"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(RuntimeError, match="Founder action required"):
        ingest_video(request(tmp_path), GateBackend({"safe": True}),
                     GPU_PROFILES["rtx-3060-12gb"])


def test_uniform_indices_are_deterministic():
    assert safety.sample_frame_indices(101, 5) == [0, 25, 50, 75, 100]
    assert safety.sample_frame_indices(101, 5) == safety.sample_frame_indices(101, 5)


def test_ambiguous_openai_response_is_unsafe(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "not-a-real-key")
    monkeypatch.setattr(safety, "_frames", lambda path: [b"jpeg"])
    monkeypatch.setattr(safety, "_post", lambda *args: {"id": "opaque", "results": [{}]})
    monkeypatch.setattr(safety, "_sha256", lambda path: hashlib.sha256(b"fixture").hexdigest())
    import hashlib
    assert safety.check_video("unused.mp4", hashlib.sha256(b"fixture").hexdigest()).safe is False


def test_node_mock_requires_explicit_opt_in(monkeypatch):
    monkeypatch.delenv("TERMINALIA_SAFETY_MOCK", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("NEMOTRON_SAFETY_DIR", raising=False)
    path = "custom_nodes/terminalia_safety/__init__.py"
    spec = importlib.util.spec_from_file_location("terminalia_safety_node", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with pytest.raises(RuntimeError, match="Founder action required"):
        module.TerminaliaContentSafety().check("unused", "a" * 64)
