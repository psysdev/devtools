"""HTML Entity Encoder/Decoder."""

import sys
import html
from tools._base import Tool, P_HTML


class HTMLTool(Tool):
    name = "html"
    description = "Encode/decode HTML entities"
    category = "utility"
    priority = P_HTML

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = stdin or "".join(sys.stdin)
        if not data:
            return "Usage: echo '<div class=\"foo\">' | devtool html encode\n   or: echo '&lt;div&gt;' | devtool html decode"

        action = "encode"
        if args and args[0] in ("decode", "d"):
            action = "decode"

        data = data.rstrip("\n")

        if action == "encode":
            return html.escape(data, quote=True)
        else:
            return html.unescape(data)

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>HTML Entity Encoder / Decoder</h2>
  <div class="tool-options">
    <button onclick="setHTMLMode('encode')" id="html-enc-btn" class="active">Encode</button>
    <button onclick="setHTMLMode('decode')" id="html-dec-btn">Decode</button>
  </div>
  <textarea id="html-input" rows="4" placeholder="Enter text..." style="width:100%"></textarea>
  <button onclick="convertHTML()">Convert</button>
  <pre id="html-output" class="code-output"></pre>
  <script>
    let htmlMode='encode';
    function setHTMLMode(m){htmlMode=m;
      document.getElementById('html-enc-btn').className=m==='encode'?'active':'';
      document.getElementById('html-dec-btn').className=m==='decode'?'active':'';
    }
    function convertHTML(){
      fetch('/api/html',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({text:document.getElementById('html-input').value,mode:htmlMode})
      }).then(r=>r.text()).then(t=>document.getElementById('html-output').textContent=t);
    }
  </script>
</div>"""


TOOL = HTMLTool()
