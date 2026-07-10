"""URL Encoder/Decoder."""

import sys
import urllib.parse
from tools._base import Tool, P_URL


class URLTool(Tool):
    name = "url"
    description = "Encode/decode URL components"
    category = "utility"
    priority = P_URL

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = stdin or "".join(sys.stdin)
        if not data:
            return "Usage: echo 'hello world' | devtool url encode\n   or: echo 'hello+world' | devtool url decode"

        action = "encode"
        if args and args[0] in ("decode", "d"):
            action = "decode"

        data = data.rstrip("\n")

        if action == "encode":
            return urllib.parse.quote(data)
        else:
            return urllib.parse.unquote(data)

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>URL Encoder / Decoder</h2>
  <div class="tool-options">
    <button onclick="setURLMode('encode')" id="url-enc-btn" class="active">Encode</button>
    <button onclick="setURLMode('decode')" id="url-dec-btn">Decode</button>
  </div>
  <div class="tool-layout">
    <div class="tool-input">
      <textarea id="url-input" rows="4" placeholder="Enter text..."></textarea>
      <button onclick="convertURL()">Convert</button>
    </div>
    <div class="tool-output">
      <pre id="url-output" class="code-output"></pre>
      <button onclick="copyOutput('url-output')">Copy</button>
    </div>
  </div>
  <script>
    let urlMode = 'encode';
    function setURLMode(m) { urlMode=m;
      document.getElementById('url-enc-btn').className=m==='encode'?'active':'';
      document.getElementById('url-dec-btn').className=m==='decode'?'active':'';
    }
    function convertURL() {
      fetch('/api/url', {method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({text:document.getElementById('url-input').value, mode:urlMode})
      }).then(r=>r.text()).then(t=>document.getElementById('url-output').textContent=t);
    }
  </script>
</div>"""


TOOL = URLTool()
