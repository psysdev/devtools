"""Hash Generator — MD5, SHA1, SHA256, SHA512."""

import hashlib
import sys
from tools._base import Tool, P_HASH


class HashTool(Tool):
    name = "hash"
    description = "Generate hashes (md5, sha1, sha256, sha512)"
    category = "utility"
    priority = P_HASH

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = stdin or "".join(sys.stdin)
        if not data:
            return "Usage: echo 'hello' | devtool hash sha256\nSupported: md5, sha1, sha256, sha512"

        algorithm = "sha256"
        if args and args[0] in hashlib.algorithms_available:
            algorithm = args[0]

        data_bytes = data.rstrip("\n").encode()

        try:
            h = hashlib.new(algorithm, data_bytes)
            return h.hexdigest()
        except ValueError:
            return f"Unsupported algorithm: {algorithm}\nAvailable: {', '.join(sorted(hashlib.algorithms_guaranteed))}"

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Hash Generator</h2>
  <div class="tool-layout">
    <div class="tool-input">
      <textarea id="hash-input" rows="4" placeholder="Enter text to hash..."></textarea>
      <button onclick="generateHashes()">Generate</button>
    </div>
    <div class="tool-output">
      <div id="hash-output"></div>
    </div>
  </div>
  <script>
    function generateHashes() {
      fetch('/api/hash', {method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({text:document.getElementById('hash-input').value})
      }).then(r=>r.json()).then(data=>{
        const out = document.getElementById('hash-output');
        out.innerHTML = Object.entries(data).map(([k,v]) =>
          `<div class="hash-row"><span class="hash-label">${k}</span><code onclick="navigator.clipboard.writeText(this.textContent)">${v}</code></div>`
        ).join('');
      });
    }
  </script>
</div>"""


TOOL = HashTool()
