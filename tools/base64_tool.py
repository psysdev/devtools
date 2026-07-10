"""Base64 Encoder/Decoder."""

import base64
import sys
from tools._base import Tool, P_BASE64


class Base64Tool(Tool):
    name = "base64"
    description = "Encode/decode Base64"
    category = "utility"
    priority = P_BASE64

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = stdin or "".join(sys.stdin)
        if not data:
            return "Usage: echo 'hello' | devtool base64 encode\n   or: echo 'aGVsbG8=' | devtool base64 decode"

        action = "encode"
        if args and args[0] in ("decode", "d"):
            action = "decode"

        data = data.rstrip("\n")

        if action == "encode":
            return base64.b64encode(data.encode()).decode()
        else:
            try:
                return base64.b64decode(data).decode()
            except Exception as e:
                return f"Error: {e}"

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Base64 Encoder / Decoder</h2>
  <div class="tool-options">
    <button onclick="setBase64Mode('encode')" id="b64-enc-btn" class="active">Encode</button>
    <button onclick="setBase64Mode('decode')" id="b64-dec-btn">Decode</button>
  </div>
  <div class="tool-layout">
    <div class="tool-input">
      <textarea id="b64-input" rows="6" placeholder="Enter text..."></textarea>
      <button onclick="convertBase64()">Convert</button>
    </div>
    <div class="tool-output">
      <pre id="b64-output" class="code-output"></pre>
      <button onclick="copyOutput('b64-output')">Copy</button>
    </div>
  </div>
  <script>
    let b64Mode = 'encode';
    function setBase64Mode(m) {
      b64Mode = m;
      document.getElementById('b64-enc-btn').className = m==='encode'?'active':'';
      document.getElementById('b64-dec-btn').className = m==='decode'?'active':'';
    }
    function convertBase64() {
      const input = document.getElementById('b64-input').value;
      fetch('/api/base64', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text: input, mode: b64Mode})
      }).then(r => r.text()).then(t => {
        document.getElementById('b64-output').textContent = t;
      });
    }
  </script>
</div>"""


TOOL = Base64Tool()
