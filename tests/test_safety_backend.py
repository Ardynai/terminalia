"""Backend translation for the ComfyUI safety node."""
from terminalia.backends import Backend


def test_backend_submits_safety_as_comfy_node(monkeypatch):
    backend = Backend("local-comfy", "http://unused")
    sent = {}

    def post(path, payload):
        sent.update(payload)
        return {"prompt_id": "one"}

    monkeypatch.setattr(backend, "_post", post)
    backend.submit({"terminalia_task": "video_content_safety",
                    "video_path": "video.mp4", "source_sha256": "abc"})
    node = sent["prompt"]["1"]
    assert node["class_type"] == "TerminaliaContentSafety"
    assert node["inputs"] == {"video_path": "video.mp4", "source_sha256": "abc"}
