"""Cheatsheet Forge — generate beautiful printable cheatsheets from templates."""

import sys
from tools._base import Tool, P_PAPER

CHEATSHEETS = {
    "git": {
        "title": "Git Cheatsheet",
        "sections": {
            "Setup": [
                ("git init", "Initialize a new repo"),
                ("git clone <url>", "Clone a remote repo"),
                ("git config --global user.name", "Set your name"),
            ],
            "Daily Work": [
                ("git status", "See what's changed"),
                ("git add <file>", "Stage changes"),
                ("git commit -m \"msg\"", "Commit staged changes"),
                ("git diff", "See unstaged changes"),
                ("git diff --staged", "See staged changes"),
            ],
            "Branches": [
                ("git branch", "List branches"),
                ("git branch <name>", "Create a branch"),
                ("git checkout <name>", "Switch to a branch"),
                ("git checkout -b <name>", "Create + switch"),
                ("git merge <name>", "Merge branch into current"),
            ],
            "Remote": [
                ("git push origin <branch>", "Push to remote"),
                ("git pull", "Pull from remote"),
                ("git fetch", "Fetch without merging"),
                ("git remote -v", "List remotes"),
            ],
            "History": [
                ("git log --oneline", "Compact log"),
                ("git log --graph", "Visual log"),
                ("git blame <file>", "Who changed what"),
                ("git show <commit>", "Show commit details"),
            ],
            "Fixups": [
                ("git reset HEAD <file>", "Unstage a file"),
                ("git checkout -- <file>", "Discard changes"),
                ("git revert <commit>", "Undo a commit"),
                ("git stash", "Temporarily save changes"),
                ("git stash pop", "Restore stashed changes"),
            ],
        },
    },
    "docker": {
        "title": "Docker Cheatsheet",
        "sections": {
            "Containers": [
                ("docker ps", "List running containers"),
                ("docker ps -a", "List all containers"),
                ("docker run <image>", "Run a container"),
                ("docker run -d <image>", "Run in background"),
                ("docker stop <container>", "Stop a container"),
                ("docker rm <container>", "Remove a container"),
            ],
            "Images": [
                ("docker images", "List images"),
                ("docker pull <image>", "Pull an image"),
                ("docker rmi <image>", "Remove an image"),
                ("docker build -t <tag> .", "Build from Dockerfile"),
            ],
            "Exec": [
                ("docker exec -it <name> sh", "Open shell"),
                ("docker logs <name>", "View logs"),
                ("docker logs -f <name>", "Tail logs"),
            ],
            "Compose": [
                ("docker compose up", "Start services"),
                ("docker compose up -d", "Start in background"),
                ("docker compose down", "Stop services"),
                ("docker compose logs", "View all logs"),
            ],
        },
    },
    "python": {
        "title": "Python Cheatsheet",
        "sections": {
            "Data Types": [
                ("int, float, str, bool", "Primitive types"),
                ("list, tuple, dict, set", "Collection types"),
                ("None", "Null value"),
            ],
            "Control Flow": [
                ("if/elif/else", "Conditional branching"),
                ("for x in iterable:", "Loop over iterable"),
                ("while condition:", "Loop while true"),
                ("break / continue", "Exit/skip iteration"),
            ],
            "Functions": [
                ("def name(args):", "Define function"),
                ("lambda x: x + 1", "Anonymous function"),
                ("*args, **kwargs", "Variable arguments"),
                ("@decorator", "Decorator syntax"),
            ],
            "Common": [
                ("len(), type(), dir()", "Built-in utilities"),
                ("open('file.txt')", "Read/write files"),
                ("try/except/finally", "Exception handling"),
                ("with open(...) as f:", "Context manager"),
            ],
        },
    },
    "sql": {
        "title": "SQL Cheatsheet",
        "sections": {
            "Queries": [
                ("SELECT * FROM table", "Select all"),
                ("SELECT col1, col2 FROM t", "Select specific columns"),
                ("SELECT DISTINCT col FROM t", "Unique values"),
                ("WHERE condition", "Filter rows"),
                ("ORDER BY col ASC/DESC", "Sort results"),
                ("LIMIT n", "Limit results"),
                ("GROUP BY col", "Group rows"),
                ("HAVING condition", "Filter groups"),
            ],
            "Joins": [
                ("INNER JOIN t2 ON t1.id = t2.id", "Only matching rows"),
                ("LEFT JOIN t2 ON t1.id = t2.id", "All from left"),
                ("RIGHT JOIN t2 ON t1.id = t2.id", "All from right"),
            ],
            "Modify": [
                ("INSERT INTO t (col) VALUES (v)", "Insert row"),
                ("UPDATE t SET col=v WHERE c", "Update rows"),
                ("DELETE FROM t WHERE c", "Delete rows"),
                ("CREATE TABLE t (col TYPE)", "Create table"),
            ],
        },
    },
    "vim": {
        "title": "Vim Cheatsheet",
        "sections": {
            "Navigation": [
                ("h j k l", "Left, Down, Up, Right"),
                ("w / b", "Word forward/back"),
                ("0 / $", "Start/end of line"),
                ("gg / G", "First/last line"),
                ("Ctrl+D / Ctrl+U", "Page down/up"),
            ],
            "Editing": [
                ("i / a", "Insert / Append"),
                ("o / O", "Open line below/above"),
                ("dd / yy", "Delete / Yank line"),
                ("p / P", "Paste below/above"),
                ("u / Ctrl+R", "Undo / Redo"),
            ],
            "Search": [
                ("/pattern", "Search forward"),
                ("?pattern", "Search backward"),
                ("n / N", "Next/previous match"),
                (":%s/old/new/g", "Replace all"),
            ],
            "Files": [
                (":w", "Save"),
                (":q", "Quit"),
                (":wq", "Save and quit"),
                (":e <file>", "Open file"),
            ],
        },
    },
}


def render_cheatsheet(name: str, theme: str = "dark") -> str:
    """Render a cheatsheet as ANSI-colored text."""
    cs = CHEATSHEETS.get(name)
    if not cs:
        available = ", ".join(sorted(CHEATSHEETS.keys()))
        return f"Unknown cheatsheet: {name}\nAvailable: {available}"

    lines = []
    header_color = "\033[1;36m" if theme == "dark" else "\033[1;34m"
    section_color = "\033[1;33m" if theme == "dark" else "\033[1;31m"
    cmd_color = "\033[0;32m" if theme == "dark" else "\033[0;34m"
    desc_color = "\033[0;37m" if theme == "dark" else "\033[0;30m"
    reset = "\033[0m"

    title = cs["title"]
    lines.append(f"{header_color}╔════════════════════════════════════╗{reset}")
    lines.append(f"{header_color}║  {title:^35} ║{reset}")
    lines.append(f"{header_color}╚════════════════════════════════════╝{reset}")
    lines.append("")

    for section_name, items in cs["sections"].items():
        lines.append(f"{section_color}── {section_name} ──{reset}")
        lines.append("")
        for cmd, desc in items:
            lines.append(f"  {cmd_color}{cmd:<30}{reset}  {desc_color}{desc}{reset}")
        lines.append("")

    return "\n".join(lines)


class PaperTool(Tool):
    name = "paper"
    description = "Generate printable cheatsheets (git, docker, python, sql, vim)"
    category = "flagship"
    priority = P_PAPER

    def run(self, args: list[str], stdin: str | None = None) -> str:
        topic = "git"
        theme = "dark"

        i = 0
        while i < len(args):
            if args[i] in CHEATSHEETS:
                topic = args[i]
            elif args[i] in ("--light",):
                theme = "light"
            elif args[i] in ("--list", "-l"):
                return "Available: " + ", ".join(sorted(CHEATSHEETS.keys()))
            i += 1

        if stdin and stdin.strip() in CHEATSHEETS:
            topic = stdin.strip()

        return render_cheatsheet(topic, theme)

    def web_render(self) -> str:
        topics = "', '".join(sorted(CHEATSHEETS.keys()))
        return f"""<div class="tool-content">
  <h2>Cheatsheet Forge</h2>
  <div class="tool-options">
    <label>Topic:
      <select id="paper-topic">
        {''.join(f'<option value="{k}">{k.title()}</option>' for k in sorted(CHEATSHEETS.keys()))}
      </select>
    </label>
    <button onclick="genCheatsheet()">Generate</button>
  </div>
  <pre id="paper-output" class="code-output"></pre>
  <script>
    function genCheatsheet() {{
      fetch('/api/paper',{{method:'POST',headers:{{'Content-Type':'application/json'}},
        body:JSON.stringify({{topic:document.getElementById('paper-topic').value}})
      }}).then(r=>r.text()).then(t=>document.getElementById('paper-output').textContent=t);
    }}
  </script>
</div>"""


TOOL = PaperTool()
