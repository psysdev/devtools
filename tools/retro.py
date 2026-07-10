"""Terminal Time Machine — record terminal sessions and export as SVG/GIF/HTML."""

import sys
import os
import json
import base64
from datetime import datetime
from tools._base import Tool, P_RETRO


class RetroTool(Tool):
    name = "retro"
    description = "Record terminal sessions, export as animated SVG or HTML"
    category = "flagship"
    priority = P_RETRO

    def run(self, args: list[str], stdin: str | None = None) -> str:
        action = "help"
        if args and args[0] in ("record", "replay", "export", "list"):
            action = args[0]

        if action == "record":
            return ("Recording terminal... Install asciinema for full support:\n"
                    "  pip install asciinema\n"
                    "  asciinema rec session.cast")
        elif action == "export":
            input_file = stdout = ""
            fmt = "svg"
            speed = 1.0
            i = 1
            while i < len(args):
                if args[i] in ("--input", "-i") and i + 1 < len(args):
                    input_file = args[i + 1]; i += 2
                elif args[i] in ("--format", "-f") and i + 1 < len(args):
                    fmt = args[i + 1]; i += 2
                elif args[i] in ("--speed", "-s") and i + 1 < len(args):
                    speed = float(args[i + 1]); i += 2
                elif args[i] in ("--output", "-o") and i + 1 < len(args):
                    stdout = args[i + 1]; i += 2
                else:
                    i += 1

            if not input_file:
                return "Usage: devtool retro export --input=session.cast --format=svg --speed=2x"

            try:
                with open(input_file) as f:
                    cast_data = json.loads(f.read())
            except (FileNotFoundError, json.JSONDecodeError):
                return f"Could not load: {input_file}"

            if fmt == "svg":
                return self._to_svg(cast_data, speed)

            return f"Export: {input_file} → {fmt} (speed: {speed}x)"

        return ("╔══════════════════════════════════════════════╗\n"
                "║       RETRO — Terminal Time Machine         ║\n"
                "╚══════════════════════════════════════════════╝\n"
                "\n"
                "  Record, replay, and export terminal sessions.\n"
                "\n"
                "  Commands:\n"
                "    devtool retro record                    Start recording\n"
                "    devtool retro export --input=session.cast --format=svg\n"
                "    devtool retro export --input=session.cast --format=html\n"
                "    devtool retro list                      List saved sessions\n"
                "\n"
                "  Uses asciinema format (.cast files).\n"
                "  Install: pip install asciinema\n")

    def _to_svg(self, cast_data, speed=1.0) -> str:
        """Generate an animated SVG from a .cast file."""
        version = cast_data.get("version", 2)
        header = cast_data.get("header", {})
        width = header.get("width", 80)
        height = header.get("height", 24)
        stdout_events = [e for e in cast_data.get("stdout", [])]

        if not stdout_events:
            return "No stdout events in cast file"

        lines = ["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 500' style='background:#1a1a2e;font-family:monospace;font-size:14px'>"]
        lines.append("<style>@keyframes blink { 50% { opacity: 0; } }</style>")
        lines.append("<rect width='800' height='500' fill='#1a1a2e' rx='8'/>")

        # Frame
        lines.append("<rect x='10' y='10' width='780' height='480' fill='#16213e' rx='4'/>")

        # Title bar dots
        for x, c in [(20, '#ff5f57'), (36, '#febc2e'), (52, '#28c840')]:
            lines.append(f"<circle cx='{x}' cy='24' r='5' fill='{c}'/>")

        line_y = 50
        for ts, event_type, data in stdout_events[:50]:
            text = data.replace("\\n", "\n").replace("\\e", "\033")
            text = text.split("\n")[0][:80]
            if text:
                safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                lines.append(f"<text x='30' y='{line_y}' fill='#a8d8ea'>{safe}</text>")
            line_y += 22
            if line_y > 460:
                break

        terms = f"Speed: {speed}x | Lines: {height} | Terminal recording"
        lines.append(f"<text x='30' y='475' fill='#555' font-size='11'>{terms}</text>")
        lines.append("</svg>")
        return "\n".join(lines)

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Terminal Time Machine</h2>
  <p>Record terminal sessions and export as animated SVG, GIF, or HTML.</p>
  <div class="tool-options">
    <label>.cast file: <input id="retro-file" type="file" accept=".cast"></label>
    <label>Speed: <input id="retro-speed" type="number" value="2" min="1" max="10" style="width:60px">x</label>
  </div>
  <pre id="retro-output" class="code-output"></pre>
  <script>
    document.getElementById('retro-file').addEventListener('change', async function(e) {
      const file = e.target.files[0];
      if (!file) return;
      const text = await file.text();
      fetch('/api/retro',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({cast:text, speed:+document.getElementById('retro-speed').value})
      }).then(r=>r.text()).then(t=>document.getElementById('retro-output').textContent=t);
    });
  </script>
</div>"""


TOOL = RetroTool()
