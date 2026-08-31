import json

import pytest

from terminalia.backends import Backend, GPU_PROFILES
from terminalia.schema import World, WorldSpec
from terminalia.video import (
    LTX2_LICENSE,
    LicenseAttestationRequired,
    flythrough,
    flythrough_workflow,
)


KEYFRAMES = ["keys/000.png", "keys/007.png"]
PROFILE = GPU_PROFILES["rtx-4090-24gb"]


def test_wan_workflow_is_seeded_comfy_prompt_and_deterministic():
    first = flythrough_workflow(KEYFRAMES, "wan21", PROFILE, seed=123)
    second = flythrough_workflow(KEYFRAMES, "wan21", PROFILE, seed=123)

    assert first["1"]["class_type"] == "LoadImage"
    assert first["12"]["class_type"] == "WanImageToVideo"
    assert first["9"]["class_type"] == "KSampler"
    assert first["9"]["inputs"]["seed"] == 123
    assert first["11"]["class_type"] == "VHS_VideoCombine"
    assert "Q6_K" in first["2"]["inputs"]["unet_name"]
    assert json.dumps(first, sort_keys=True).encode() == json.dumps(second, sort_keys=True).encode()


def test_ltx_requires_attestation(monkeypatch):
    monkeypatch.delenv("TERMINALIA_LTX_OK_UNDER_10M", raising=False)
    with pytest.raises(LicenseAttestationRequired, match="under USD \\$10M"):
        flythrough_workflow(KEYFRAMES, "ltx2", PROFILE)


def test_ltx_workflow_and_license(monkeypatch):
    monkeypatch.setenv("TERMINALIA_LTX_OK_UNDER_10M", "1")
    workflow = flythrough_workflow(KEYFRAMES, "ltx2", PROFILE, seed=9)

    assert workflow["7"]["class_type"] == "LTXVConditioning"
    assert workflow["8"]["class_type"] == "LTXVImgToVideo"
    assert workflow["9"]["inputs"]["seed"] == 9
    assert "under USD $10M annual revenue" in LTX2_LICENSE


class RecordingBackend(Backend):
    def __init__(self):
        super().__init__("stub", "https://stub.invalid")
        self.workflow = None

    def submit(self, workflow, client_id="terminalia"):
        self.workflow = workflow
        return "prompt-1"

    def wait(self, prompt_id, timeout_s=1800):
        assert prompt_id == "prompt-1"
        return {"11": {"videos": [{"filename": "flythrough.mp4", "subfolder": "video"}]}}


def test_execution_records_artifact_and_provenance():
    backend = RecordingBackend()
    world = flythrough(
        World(spec=WorldSpec(prompt="an island", seed=77)),
        KEYFRAMES, backend, PROFILE, "wan21")

    assert backend.workflow["9"]["inputs"]["seed"] == 77
    assert world.video_provenance.engine == "wan21"
    assert world.video_provenance.models[0].license == "Apache-2.0"
    assert world.video_provenance.artifacts[0].uri.endswith(
        "/view?filename=flythrough.mp4&subfolder=video&type=output")
    assert world.history[-1].stage == "video.flythrough"


def test_ltx_execution_records_conditional_license(monkeypatch):
    monkeypatch.setenv("TERMINALIA_LTX_OK_UNDER_10M", "1")
    world = flythrough(
        World(spec=WorldSpec(prompt="a city", seed=5)),
        KEYFRAMES, RecordingBackend(), PROFILE, "ltx2")
    assert world.video_provenance.models[0].license == LTX2_LICENSE
