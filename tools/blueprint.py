"""Architecture Diagram Generator — YAML → ASCII/Mermaid/SVG architecture diagrams."""

import sys
import json
from tools._base import Tool, P_BLUEPRINT

try:
    import yaml
except ImportError:
    yaml = None


def asciidag(services: dict) -> str:
    """Render architecture as ASCII diagram."""
    lines = []
    lines.append("  ┌──────────────────────────────────────┐")
    lines.append("  │         System Architecture          │")
    lines.append("  └──────────────────────────────────────┘")
    lines.append("")

    # Build dependency graph
    deps = {}
    for name, svc in services.items():
        svc_deps = []
        if isinstance(svc, dict):
            svc_deps = svc.get("depends_on", [])
            if isinstance(svc_deps, str):
                svc_deps = [svc_deps]
        deps[name] = svc_deps

    # Group by dependency level (simple layering)
    levels = {}
    remaining = set(deps.keys())

    level = 0
    while remaining:
        current = []
        for name in list(remaining):
            if all(d not in remaining for d in deps.get(name, [])):
                current.append(name)
        if not current:
            current = list(remaining)
        for name in current:
            levels[name] = level
            remaining.remove(name)
        level += 1

    # Render by level
    max_level = max(levels.values()) if levels else 0
    for lvl in range(max_level + 1):
        items = [n for n, l in levels.items() if l == lvl]
        if items:
            lines.append(f"  Level {lvl}:")
            for item in items:
                svc = services.get(item, {})
                if isinstance(svc, dict):
                    stype = svc.get("type", "")
                    stype_str = f" [{stype}]" if stype else ""
                else:
                    stype_str = ""
                lines.append(f"    └ {item}{stype_str}")
                d = deps.get(item, [])
                if d:
                    lines.append(f"        → {', '.join(d)}")
            lines.append("")

    return "\n".join(lines)


def mermaid_diagram(services: dict) -> str:
    """Render architecture as Mermaid graph."""
    parts = ["graph TB"]
    for name, svc in services.items():
        if isinstance(svc, dict):
            stype = svc.get("type", "service")
            parts.append(f"    {name}[{stype}: {name}]")
        else:
            parts.append(f"    {name}[{name}]")

    for name, svc in services.items():
        if isinstance(svc, dict):
            deps = svc.get("depends_on", [])
            if isinstance(deps, str):
                deps = [deps]
            for dep in deps:
                parts.append(f"    {dep} --> {name}")

    return "\n".join(parts)


class BlueprintTool(Tool):
    name = "blueprint"
    description = "Generate architecture diagrams from YAML/JSON definition"
    category = "flagship"
    priority = P_BLUEPRINT

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = stdin or "".join(sys.stdin)
        fmt = "ascii"

        i = 0
        while i < len(args):
            if args[i] in ("--mermaid", "-m"):
                fmt = "mermaid"; i += 1
            elif args[i] in ("--json", "-j"):
                fmt = "json"; i += 1
            elif args[i] in ("--file", "-f") and i + 1 < len(args):
                with open(args[i + 1]) as f:
                    data = f.read()
                i += 2
            else:
                i += 1

        if not data:
            return "Usage: cat architecture.yaml | devtool blueprint [--mermaid]"

        services = None
        # Try YAML first
        if yaml:
            try:
                services = yaml.safe_load(data)
            except yaml.YAMLError:
                pass

        # Try JSON
        if not services:
            try:
                services = json.loads(data)
            except json.JSONDecodeError:
                pass

        if not services:
            return "Error: could not parse as YAML or JSON"

        # Handle nested: services key
        if isinstance(services, dict) and "services" in services:
            services = services["services"]

        if fmt == "mermaid":
            return mermaid_diagram(services)
        elif fmt == "json":
            return json.dumps(services, indent=2)
        else:
            return asciidag(services)

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Architecture Diagram Generator</h2>
  <p>Define your system in YAML, get an architecture diagram.</p>
  <textarea id="bp-input" rows="8" placeholder='services:
  frontend:
    type: react
    depends_on: [api, auth]
  api:
    type: fastapi
    depends_on: [db]
  db:
    type: postgres
  auth:
    type: auth0
' style="width:100%;font-family:monospace;font-size:13px"></textarea>
  <div class="tool-options">
    <select id="bp-format"><option value="ascii">ASCII Diagram</option><option value="mermaid">Mermaid</option></select>
    <button onclick="genBlueprint()">Generate</button>
  </div>
  <pre id="bp-output" class="code-output"></pre>
  <script>
    function genBlueprint() {
      fetch('/api/blueprint',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({yaml:document.getElementById('bp-input').value, format:document.getElementById('bp-format').value})
      }).then(r=>r.text()).then(t=>document.getElementById('bp-output').textContent=t);
    }
  </script>
</div>"""


TOOL = BlueprintTool()
