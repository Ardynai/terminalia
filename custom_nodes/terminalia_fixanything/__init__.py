"""ComfyUI node for Terminalia's FixAnything refinement pass."""

from .node import TerminaliaFixAnything

NODE_CLASS_MAPPINGS = {"TerminaliaFixAnything": TerminaliaFixAnything}
NODE_DISPLAY_NAME_MAPPINGS = {"TerminaliaFixAnything": "Terminalia FixAnything"}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "TerminaliaFixAnything"]
