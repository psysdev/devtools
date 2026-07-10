"""Diff / Text Comparator — side-by-side and unified diffs."""

import difflib
import sys
from tools._base import Tool, P_DIFF


class DiffTool(Tool):
    name = "diff"
    description = "Compare two texts with unified or side-by-side diff"
    category = "utility"
    priority = P_DIFF

    def run(self, args: list[str], stdin: str | None = None) -> str:
        file1 = file2 = ""
        mode = "unified"
        context = 3

        i = 0
        while i < len(args):
            if args[i] in ("-u", "--unified"):
                mode = "unified"
            elif args[i] in ("-s", "--side-by-side"):
                mode = "side-by-side"
            elif args[i] in ("-c", "--context") and i + 1 < len(args):
                context = int(args[i + 1])
                i += 1
            elif not args[i].startswith("-"):
                if not file1:
                    file1 = args[i]
                else:
                    file2 = args[i]
            i += 1

        text1 = text2 = ""
        if file1 and file2:
            try:
                with open(file1) as f: text1 = f.read()
                with open(file2) as f: text2 = f.read()
            except FileNotFoundError as e:
                return f"Error: {e}"
        elif stdin:
            parts = stdin.split("\n---SPLIT---\n")
            if len(parts) >= 2:
                text1, text2 = parts[0], parts[1]
            else:
                return "Error: pipe two texts separated by '---SPLIT---'"
        else:
            return "Usage: devtool diff file1.txt file2.txt\n   or: echo $'text1\\n---SPLIT---\\ntext2' | devtool diff"

        lines1 = text1.splitlines()
        lines2 = text2.splitlines()

        if mode == "unified":
            result = list(difflib.unified_diff(lines1, lines2, fromfile=file1 or "a", tofile=file2 or "b", n=context))
            return "\n".join(result) if result else "Files are identical."
        else:
            return self._side_by_side(lines1, lines2, context)

    def _side_by_side(self, lines1, lines2, context=3) -> str:
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        result = []
        sep = "  │  "
        width = 60

        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == "equal":
                for k in range(i1, i2):
                    if context == 0 or abs(k - i1) < context or abs(k - i2 + 1) <= context or k == i1 or k == i2 - 1:
                        result.append(f"  {lines1[k][:width]:{width}}{sep}{lines2[k][:width]}")
                    elif k == i1 + context:
                        result.append(f"  ...{'':{width}}{sep}...")
            elif op == "replace":
                for k in range(max(i1, i2 - (j2 - j1)), i2):
                    if k < len(lines1):
                        result.append(f"- {lines1[k][:width]:{width}}{sep}")
                for k in range(j1, j2):
                    result.append(f"+ {'':{width}}{sep}{lines2[k][:width]}")
            elif op == "delete":
                for k in range(i1, i2):
                    result.append(f"- {lines1[k][:width]:{width}}{sep}")
            elif op == "insert":
                for k in range(j1, j2):
                    result.append(f"+ {'':{width}}{sep}{lines2[k][:width]}")

        return "\n".join(result) if result else "Files are identical."

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Text Diff</h2>
  <div class="tool-layout tool-layout-2col">
    <div class="tool-input">
      <label>Original text:</label>
      <textarea id="diff-left" rows="8" placeholder="Original..."></textarea>
    </div>
    <div class="tool-input">
      <label>Modified text:</label>
      <textarea id="diff-right" rows="8" placeholder="Modified..."></textarea>
    </div>
  </div>
  <button onclick="runDiff()">Compare</button>
  <div class="tool-output">
    <pre id="diff-output" class="code-output"></pre>
  </div>
  <script>
    function runDiff() {
      const left = document.getElementById('diff-left').value;
      const right = document.getElementById('diff-right').value;
      fetch('/api/diff', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text1: left, text2: right})
      }).then(r => r.text()).then(text => {
        document.getElementById('diff-output').textContent = text;
      });
    }
    document.addEventListener('keydown', function(e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') runDiff();
    });
  </script>
</div>"""


TOOL = DiffTool()
