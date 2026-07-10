"""JSON Formatter & Validator — prettify, validate, collapsible tree view."""

import json
import sys
from tools._base import Tool, P_JSON


class JSONTool(Tool):
    name = "json"
    description = "Format, validate, and prettify JSON"
    category = "utility"
    priority = P_JSON

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = stdin or sys.stdin.read()
        if not data:
            return "Error: no input (pipe JSON or provide --file)"

        indent = 2
        if args and args[0] in ("fmt", "format"):
            if len(args) > 1 and args[1].isdigit():
                indent = int(args[1])

        try:
            parsed = json.loads(data)
            return json.dumps(parsed, indent=indent, sort_keys=False, ensure_ascii=False)
        except json.JSONDecodeError as e:
            # Try to show where the error is
            lines = data.split("\n")
            line_no = e.lineno or 1
            col_no = e.colno or 1
            context = "\n".join(lines[max(0,line_no-3):line_no])
            marker = " " * (col_no - 1) + "^"
            return f"JSON Error: {e.msg}\n  Line {line_no}, Column {col_no}\n\n{context}\n{marker}"

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>JSON Formatter</h2>
  <div class="tool-layout">
    <div class="tool-input">
      <label>Paste JSON:</label>
      <textarea id="json-input" rows="10" placeholder='{"key": "value", "array": [1, 2, 3]}'></textarea>
      <button onclick="formatJSON()">Format</button>
    </div>
    <div class="tool-output">
      <label>Output:</label>
      <pre id="json-output" class="code-output"></pre>
      <button onclick="copyOutput('json-output')">Copy</button>
    </div>
  </div>
  <script>
    function formatJSON() {
      const input = document.getElementById('json-input').value;
      const output = document.getElementById('json-output');
      try {
        const parsed = JSON.parse(input);
        output.textContent = JSON.stringify(parsed, null, 2);
        output.className = 'code-output valid';
      } catch(e) {
        output.textContent = 'Error: ' + e.message;
        output.className = 'code-output error';
      }
    }
    document.addEventListener('keydown', function(e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') formatJSON();
    });
  </script>
</div>"""


TOOL = JSONTool()
