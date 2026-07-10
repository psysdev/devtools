"""Base tool class that all tools extend."""

from abc import ABC, abstractmethod
from typing import Optional


class Tool(ABC):
    """Base class for all devtools tools.

    Each tool defines:
    - name: CLI command name
    - description: what it does
    - category: "utility" or "flagship"
    - priority: lower number = appears first in listings
    - run(args): handle CLI invocation
    - web_render(): return HTML for the web UI
    """

    name: str = ""
    description: str = ""
    category: str = "utility"  # "utility" or "flagship"
    priority: int = 99  # lower = earlier in listings

    @abstractmethod
    def run(self, args: list[str], stdin: Optional[str] = None) -> str:
        """Handle CLI invocation. Return string output."""
        ...

    def tui(self) -> str:
        """Optional interactive TUI mode. Return HTML-like or rich renderable."""
        return ""

    def web_render(self) -> str:
        """Return HTML for embedding in the web UI."""
        return f"<div class='tool-content'><h2>{self.name}</h2><p>{self.description}</p></div>"

    def cli_help(self) -> str:
        return f"  devtool {self.name:<12}  {self.description}"


# ── Shared priority constants ──────────────────────────────────────
# Lower = appears first

# Utility priority order (most common developer needs first)
P_JSON = 1
P_REGEX = 2
P_BASE64 = 3
P_URL = 4
P_HASH = 5
P_COLOR = 6
P_TS = 7
P_CASE = 8
P_JWT = 9
P_HTML = 10
P_NUM = 11
P_UUID = 12
P_LOREM = 13
P_DIFF = 14
P_SCREENSHOT = 15

# Flagship priority order (most common first)
P_MOCK = 1
P_LENS = 2
P_PAPER = 3
P_BLUEPRINT = 4
P_UNWIND = 5
P_ARCHEO = 6
P_PEEPHOLE = 7
P_RETRO = 8
P_DASH = 9
P_STITCH = 10
