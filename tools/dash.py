"""On-Call Dashboard — configurable terminal dashboard in a TMUX pane."""

import sys
import json
import random
from datetime import datetime
from tools._base import Tool, P_DASH

try:
    import yaml
except ImportError:
    yaml = None

DEFAULT_CONFIG = """panels:
  - type: clock
    title: "Current Time"
    interval: 1s
  - type: quote
    title: "Quote"
  - type: status
    title: "Status"
    items:
      - label: "Backend"
        url: "http://localhost:8000/health"
      - label: "Frontend"
        url: "http://localhost:5173"
"""


class DashTool(Tool):
    name = "dash"
    description = "On-call dashboard — configurable TUI + web monitoring panels"
    category = "flagship"
    priority = P_DASH

    def run(self, args: list[str], stdin: str | None = None) -> str:
        config_path = ""
        export = ""

        i = 0
        while i < len(args):
            if args[i] in ("--config", "-c") and i + 1 < len(args):
                config_path = args[i + 1]; i += 2
            elif args[i] in ("--export", "-e") and i + 1 < len(args):
                export = args[i + 1]; i += 2
            elif args[i] in ("--serve", "-s"):
                return "To start web dashboard: devtool --serve  (then navigate to /dash)"
            else:
                i += 1

        config = {}
        if config_path:
            try:
                with open(config_path) as f:
                    raw = f.read()
                if yaml:
                    config = yaml.safe_load(raw) or {}
                else:
                    config = json.loads(raw)
            except (FileNotFoundError, json.JSONDecodeError, yaml.YAMLError) as e:
                return f"Error loading config: {e}"
        else:
            if yaml:
                config = yaml.safe_load(DEFAULT_CONFIG)
            else:
                # Parse the YAML-like default as a simple dict for non-YAML setups
                config = json.loads('{"panels":[{"type":"clock","title":"Current Time"},{"type":"quote","title":"Quote"},{"type":"status","title":"Status","items":[{"label":"Backend","url":"http://localhost:8000/health"},{"label":"Frontend","url":"http://localhost:5173"}]}]}')

        panels = config.get("panels", [])
        if not panels:
            panels = [{"type": "clock"}]

        if export:
            return self._export_state(panels, export)

        return self._render(panels)

    def _render(self, panels: list) -> str:
        result = []
        result.append("╔══════════════════════════════════════════════╗")
        result.append("║            DASH — On-Call Dashboard         ║")
        result.append("╚══════════════════════════════════════════════╝")
        result.append(f"  Updated: {datetime.now().strftime('%H:%M:%S')}  |  {len(panels)} panel(s)")
        result.append("")

        for p in panels:
            ptype = p.get("type", "info")
            title = p.get("title", ptype)
            result.append(f"  ┌─ {title} ─" + "─" * 30)
            result.append(f"  │")

            if ptype == "clock":
                result.append(f"  │  {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
            elif ptype == "quote":
                quotes = [
                    "It works on my machine",
                    "I'll fix it in the next PR",
                    "Have you tried turning it off and on?",
                    "It's not a bug, it's a feature",
                    "Works in production",
                    "Let me check the logs",
                    "I didn't change anything",
                    "It's a caching issue",
                ]
                result.append(f"  │  \"{random.choice(quotes)}\"")
            elif ptype == "status":
                items = p.get("items", [])
                for item in items:
                    label = item.get("label", "?")
                    result.append(f"  │  ○ {label}  (checking...)")
            elif ptype == "info":
                result.append(f"  │  {p.get('text', 'No info')}")
            else:
                result.append(f"  │  Panel: {ptype}")

            result.append(f"  │")
            result.append(f"  └" + "─" * 40)
            result.append("")

        result.append("  Ctrl+C to exit. Configure via --config=dash.yaml")
        return "\n".join(result)

    def _export_state(self, panels: list, filepath: str) -> str:
        state = {
            "exported_at": datetime.utcnow().isoformat(),
            "panels": len(panels),
            "types": [p.get("type") for p in panels],
        }
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)
        return f"Dashboard state exported to {filepath}"

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>On-Call Dashboard</h2>
  <p>Configurable terminal dashboard that lives in a TMUX pane. Configure via YAML.</p>
  <div class="tool-layout">
    <div class="tool-input">
      <textarea id="dash-config" rows="10" placeholder="Paste dashboard YAML config..." style="width:100%;font-family:monospace;font-size:13px">panels:
  - type: clock
    title: "Current Time"
  - type: quote
    title: "Dev Wisdom"
  - type: info
    title: "System"
    text: "All systems nominal"</textarea>
      <button onclick="renderDash()">Render Dashboard</button>
    </div>
    <div class="tool-output">
      <pre id="dash-output" class="code-output"></pre>
    </div>
  </div>
  <script>
    function renderDash() {
      fetch('/api/dash',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({config:document.getElementById('dash-config').value})
      }).then(r=>r.text()).then(t=>document.getElementById('dash-output').textContent=t);
    }
  </script>
</div>"""


TOOL = DashTool()
