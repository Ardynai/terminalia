"""ComfyUI node exposing Terminalia's real video safety gate."""
from terminalia.safety import check_video


class TerminaliaContentSafety:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"video_path": ("STRING",), "source_sha256": ("STRING",)}}

    RETURN_TYPES = ()
    FUNCTION = "check"
    CATEGORY = "Terminalia"
    OUTPUT_NODE = True

    def check(self, video_path: str, source_sha256: str):
        verdict = check_video(video_path, source_sha256).model_dump()
        return {"ui": {"terminalia_result": verdict}, "result": ()}


NODE_CLASS_MAPPINGS = {"TerminaliaContentSafety": TerminaliaContentSafety}
NODE_DISPLAY_NAME_MAPPINGS = {"TerminaliaContentSafety": "Terminalia Content Safety"}
