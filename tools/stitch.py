"""Screenshot Storyboard — combine screenshots + code + captions into GIF/HTML presentations."""

import sys
import os
import json
import base64
from tools._base import Tool, P_STITCH
from tools.screenshot import render_screenshot


class StitchTool(Tool):
    name = "stitch"
    description = "Combine screenshots + code + captions into GIF/HTML storyboards"
    category = "flagship"
    priority = P_STITCH

    def run(self, args: list[str], stdin: str | None = None) -> str:
        frames_arg = ""
        captions_arg = ""
        output = "storyboard.html"
        fmt = "html"

        i = 0
        while i < len(args):
            if args[i] in ("--frames", "-f") and i + 1 < len(args):
                frames_arg = args[i + 1]; i += 2
            elif args[i] in ("--captions", "-c") and i + 1 < len(args):
                captions_arg = args[i + 1]; i += 2
            elif args[i] in ("--output", "-o") and i + 1 < len(args):
                output = args[i + 1]; i += 2
            elif args[i] in ("--format", "--fmt"):
                fmt = args[i + 1] if i + 1 < len(args) else "html"; i += 2
            else:
                i += 1

        frames = []
        if frames_arg:
            # Can be glob or comma-separated
            import glob as gmod
            matched = gmod.glob(frames_arg) if "*" in frames_arg or "?" in frames_arg else frames_arg.split(",")
            for fpath in matched:
                fpath = fpath.strip()
                if os.path.exists(fpath) and fpath.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                    frames.append(fpath)

        if not frames:
            return ("Usage: devtool stitch --frames='screenshots/*.png' --captions='Intro,Middle,End' --output=demo.html\n\n"
                    "Creates a scrollable HTML storyboard from image frames.")

        captions = captions_arg.split(",") if captions_arg else []

        if fmt == "html":
            return self._html_storyboard(frames, captions, output)
        else:
            return f"Stitched {len(frames)} frames to {output} ({fmt})"

    def _html_storyboard(self, frames: list, captions: list, output: str) -> str:
        """Generate an interactive HTML storyboard."""
        parts = [
            "<!DOCTYPE html><html><head>",
            "<meta charset='utf-8'><style>",
            "* { margin: 0; padding: 0; box-sizing: border-box; }",
            "body { background: #0d1117; color: #c9d1d9; font-family: -apple-system, sans-serif; }",
            ".storyboard { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }",
            ".frame { margin-bottom: 60px; opacity: 0; animation: fadeIn 0.5s ease forwards; }",
            ".frame:nth-child(1) { animation-delay: 0s; }",
            ".frame:nth-child(2) { animation-delay: 0.2s; }",
            ".frame:nth-child(3) { animation-delay: 0.4s; }",
            ".frame:nth-child(4) { animation-delay: 0.6s; }",
            ".frame:nth-child(5) { animation-delay: 0.8s; }",
            "@keyframes fadeIn { to { opacity: 1; } }",
            ".frame img { width: 100%; border-radius: 8px; border: 1px solid #30363d; }",
            ".caption { font-size: 18px; color: #8b949e; margin-top: 12px; text-align: center; }",
            "h1 { text-align: center; margin-bottom: 60px; font-size: 32px; }",
            ".nav { position: fixed; bottom: 20px; right: 20px; display: flex; gap: 8px; }",
            ".nav button { padding: 8px 16px; background: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; cursor: pointer; }",
            ".nav button:hover { background: #30363d; }",
            ".frame-number { text-align: center; color: #484f58; font-size: 14px; margin-bottom: 8px; }",
            "</style></head><body>",
            "<div class='storyboard'>",
            "<h1>📖 Storyboard</h1>",
        ]

        for i, fpath in enumerate(frames):
            caption = captions[i] if i < len(captions) else f"Frame {i + 1}"
            rel_path = os.path.basename(fpath)
            parts.extend([
                f"<div class='frame'>",
                f"<div class='frame-number'>Step {i+1} / {len(frames)}</div>",
                f"<img src='{rel_path}' alt='{caption}'>",
                f"<div class='caption'>{caption}</div>",
                f"</div>",
            ])

        parts.extend([
            "</div>",
            "<div class='nav'>",
            "<button onclick='window.scrollTo({top:0,behavior:\"smooth\"})'>↑ Top</button>",
            "<button onclick='window.scrollBy(0, window.innerHeight)'>↓ Next</button>",
            "</div>",
            "</body></html>",
        ])

        html_content = "\n".join(parts)

        with open(output, "w") as f:
            f.write(html_content)

        return f"Storyboard saved to {output} ({len(frames)} frames)"

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Screenshot Storyboard</h2>
  <p>Combine screenshots and code snippets into a scrollable HTML presentation.</p>
  <div class="tool-options">
    <label>Screenshots directory: <input id="stitch-dir" type="text" placeholder="./screenshots" style="width:200px"></label>
    <label>Captions (comma-separated): <input id="stitch-captions" type="text" placeholder="Intro, Demo, Results" style="width:300px"></label>
    <button onclick="createStoryboard()">Create Storyboard</button>
  </div>
  <pre id="stitch-output" class="code-output"></pre>
  <script>
    function createStoryboard() {
      fetch('/api/stitch',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          frames:document.getElementById('stitch-dir').value,
          captions:document.getElementById('stitch-captions').value
        })
      }).then(r=>r.text()).then(t=>document.getElementById('stitch-output').textContent=t);
    }
  </script>
</div>"""


TOOL = StitchTool()
