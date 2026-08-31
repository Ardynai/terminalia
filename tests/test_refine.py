from terminalia.backends import Backend, GPU_PROFILES
from terminalia.refine import FIX_ANYTHING_WEIGHTS, fix_anything
from terminalia.schema import ArtifactRef, World, WorldSpec


class StubBackend(Backend):
    def __init__(self, name="local-comfy"):
        super().__init__(name, "https://compute.example")
        self.submissions = []

    def submit(self, workflow, client_id="terminalia"):
        self.submissions.append((workflow, client_id))
        return "job-1"

    def wait(self, prompt_id, timeout_s=1800):
        assert prompt_id == "job-1"
        return {"fix_anything": {"videos": [{"filename": "cleaned.mp4"}]}}


def sample_world(seed=7):
    world = World(spec=WorldSpec(prompt="sample mesh render", seed=seed))
    world.refine.render_artifacts = [
        ArtifactRef(uri="renders/orbit-frames", kind="frames")]
    return world


def test_fix_anything_runs_and_records_artifact():
    backend = StubBackend()
    world = fix_anything(sample_world(), backend, GPU_PROFILES["rtx-5090-32gb"])

    result = world.refine.fix_anything
    assert result.status == "ran"
    assert result.outputs[0].uri.endswith("filename=cleaned.mp4&subfolder=&type=output")
    assert result.weights == FIX_ANYTHING_WEIGHTS
    workflow = backend.submissions[0][0]["fix_anything"]["inputs"]
    assert workflow["seed"] == 7
    assert workflow["artifacts"] == [{"uri": "renders/orbit-frames", "kind": "frames"}]


def test_fix_anything_skips_insufficient_profile_without_submission(tmp_path):
    backend = StubBackend()
    world = fix_anything(sample_world(), backend, GPU_PROFILES["rtx-4090-24gb"])

    assert world.refine.fix_anything.status == "skipped"
    assert world.refine.fix_anything.reason == "insufficient profile"
    assert backend.submissions == []
    path = tmp_path / "world.json"
    world.save(str(path))
    assert World.load(str(path)).refine.fix_anything.reason == "insufficient profile"


def test_cloud_backends_run_regardless_of_reported_profile():
    for name in ("comfy-cloud", "runpod-serverless"):
        backend = StubBackend(name)
        result = fix_anything(
            sample_world(), backend, GPU_PROFILES["rtx-3060-12gb"])
        assert result.refine.fix_anything.status == "ran"


def test_decision_and_workflow_are_deterministic():
    runs = []
    for _ in range(2):
        backend = StubBackend()
        world = fix_anything(sample_world(), backend, GPU_PROFILES["dgx-spark-128gb"])
        runs.append((world.model_dump(), backend.submissions))
    assert runs[0] == runs[1]
