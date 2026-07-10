"""Git Archaeology — track changes to specific lines across commits."""

import sys
import os
import subprocess
import re
from datetime import datetime
from tools._base import Tool, P_ARCHEO


def run_git(cmd: list[str], cwd: str = ".") -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=10)
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def find_git_root(path: str = ".") -> str | None:
    """Walk up to find .git directory."""
    current = os.path.abspath(path)
    while current:
        if os.path.isdir(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent
    return None


class ArcheoTool(Tool):
    name = "archeo"
    description = "Git archaeology — track changes to specific lines/functions across commits"
    category = "flagship"
    priority = P_ARCHEO

    def run(self, args: list[str], stdin: str | None = None) -> str:
        filepath = ""
        lines_str = ""
        func_name = ""
        commit_range = ""

        i = 0
        while i < len(args):
            if args[i] in ("--file", "-f") and i + 1 < len(args):
                filepath = args[i + 1]; i += 2
            elif args[i] in ("--lines", "-l") and i + 1 < len(args):
                lines_str = args[i + 1]; i += 2
            elif args[i] in ("--function", "--func", "-fn") and i + 1 < len(args):
                func_name = args[i + 1]; i += 2
            elif args[i] in ("--range", "--from") and i + 1 < len(args):
                commit_range = args[i + 1]; i += 2
            else:
                i += 1

        if stdin and not filepath:
            filepath = stdin.strip()

        if not filepath:
            return "\n".join([
                "Usage: devtool archeo --file=app.py --lines=42-48",
                "   or: devtool archeo --file=app.py --function=calculate",
                "   or: devtool archeo --file=app.py --lines=10-20 --range=HEAD~5..HEAD",
            ])

        git_root = find_git_root(os.path.dirname(filepath) if os.path.exists(filepath) else ".")
        if not git_root:
            return "Error: not in a git repository"

        rel_path = os.path.relpath(filepath, git_root) if os.path.exists(filepath) else filepath

        # Build blame command
        blame_cmd = ["git", "blame", "-w", "--line-porcelain"]
        if lines_str:
            blame_cmd.extend(["-L", lines_str])
        blame_cmd.append("--")
        blame_cmd.append(rel_path)

        blame_out = run_git(blame_cmd, git_root)

        if not blame_out:
            return f"No blame info for {rel_path}"

        result = []
        result.append("╔══════════════════════════════════════════════╗")
        result.append("║     ARCHEO — Git Archaeology Report          ║")
        result.append("╚══════════════════════════════════════════════╝")
        result.append("")
        result.append(f"  File: {rel_path}")
        if lines_str:
            result.append(f"  Lines: {lines_str}")
        if func_name:
            result.append(f"  Function: {func_name}()")
        result.append("")

        # Parse blame output — extract unique commits
        commits = {}
        current_commit = None
        for line in blame_out.splitlines():
            if current_commit is None:
                current_commit = line.split(" ")[0] if " " in line else line
                if current_commit and len(current_commit) >= 8:
                    commits[current_commit] = {"count": 0}
            elif line.startswith("author "):
                if current_commit and current_commit in commits:
                    commits[current_commit]["author"] = line[7:]
            elif line.startswith("author-time "):
                try:
                    ts = int(line[12:])
                    if current_commit and current_commit in commits:
                        commits[current_commit]["date"] = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                except ValueError:
                    pass
            elif line.startswith("summary "):
                if current_commit and current_commit in commits:
                    commits[current_commit]["summary"] = line[8:]
                    current_commit = None

        # Also count lines per commit
        current_commit = None
        for line in blame_out.splitlines():
            if " " in line and len(line.split(" ")[0]) == 40:
                current_commit = line.split(" ")[0]
            if current_commit and current_commit in commits:
                commits[current_commit]["count"] = commits[current_commit].get("count", 0) + 1

        if not commits:
            return f"No git history found for {rel_path}"

        result.append(f"  Contributors: {len(set(c.get('author','?') for c in commits.values()))}")
        result.append(f"  Unique commits touching these lines: {len(commits)}")
        result.append("")

        # Sort by date descending
        sorted_commits = sorted(
            commits.items(),
            key=lambda x: x[1].get("date", ""),
            reverse=True
        )

        result.append("  Timeline (most recent first):")
        result.append("")
        for sha, info in sorted_commits[:10]:
            short_sha = sha[:8]
            author = info.get("author", "?")[:20]
            date = info.get("date", "?")
            summary = info.get("summary", "?")[:60]
            count = info.get("count", 0)
            result.append(f"  └ {short_sha}  {date}  {author:<20}  {summary}")
            result.append(f"      {count} line(s) attributed")
            result.append("")

        # Show source context
        if os.path.exists(filepath):
            result.append(f"  Current source ({rel_path}):")
            try:
                with open(filepath) as f:
                    src_lines = f.readlines()

                if lines_str:
                    parts = lines_str.split("-")
                    start, end = int(parts[0]), int(parts[1]) if len(parts) > 1 else int(parts[0])
                elif func_name:
                    # Find function
                    start, end = 0, 0
                    for i, line in enumerate(src_lines):
                        if f"def {func_name}" in line or f"function {func_name}" in line:
                            start = i + 1
                        elif start > 0 and end == 0 and line.strip() and not line.startswith((" ", "\t")):
                            end = i
                            break
                    if end == 0:
                        end = len(src_lines)
                else:
                    start, end = 1, len(src_lines)

                for i in range(max(0, start - 1), min(len(src_lines), end + 2)):
                    marker = "→" if start <= i + 1 <= end else " "
                    result.append(f"  {marker} {i+1:4d} {src_lines[i].rstrip()}")
            except (FileNotFoundError, IOError):
                result.append("  (source not accessible)")

        return "\n".join(result)

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Git Archaeology</h2>
  <p>Track changes to specific lines across git history. Run from a git repository.</p>
  <div style="display:grid;gap:8px;max-width:500px">
    <label>File path: <input id="archeo-file" type="text" placeholder="app.py" style="width:100%"></label>
    <label>Lines: <input id="archeo-lines" type="text" placeholder="42-48" style="width:100%"></label>
    <button onclick="runArcheo()">Investigate</button>
  </div>
  <pre id="archeo-output" class="code-output"></pre>
  <script>
    function runArcheo() {
      fetch('/api/archeo',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          file:document.getElementById('archeo-file').value,
          lines:document.getElementById('archeo-lines').value
        })
      }).then(r=>r.text()).then(t=>document.getElementById('archeo-output').textContent=t);
    }
  </script>
</div>"""


TOOL = ArcheoTool()
