"""UUID Generator — v4 and v7."""

import sys
import uuid
import time
from tools._base import Tool, P_UUID


def uuid_v7():
    """Generate a UUID v7 (time-ordered)."""
    # UUID v7: unix_ts_ms (48 bits) | version (4 bits) | rand_a (12 bits) | variant (2 bits) | rand_b (62 bits)
    timestamp = int(time.time() * 1000)
    rand_a = int.from_bytes(uuid.uuid4().bytes[:2], "big") & 0x0FFF
    rand_b = uuid.uuid4().bytes[2:]
    # Combine
    bytes_val = (
        (timestamp >> 40).to_bytes(1, "big")
        + (timestamp >> 32).to_bytes(1, "big")
        + (timestamp >> 24).to_bytes(1, "big")
        + (timestamp >> 16).to_bytes(1, "big")
        + (timestamp >> 8).to_bytes(1, "big")
        + timestamp.to_bytes(1, "big")
        + ((0x7 << 4) | (rand_a >> 8)).to_bytes(1, "big")
        + (rand_a & 0xFF).to_bytes(1, "big")
        + ((0x80 | (rand_b[0] >> 2))).to_bytes(1, "big")
        + rand_b[1:]
    )
    return uuid.UUID(bytes=bytes_val)


class UUIDTool(Tool):
    name = "uuid"
    description = "Generate UUIDs (v4, v7)"
    category = "utility"
    priority = P_UUID

    def run(self, args: list[str], stdin: str | None = None) -> str:
        version = "v4"
        count = 1

        i = 0
        while i < len(args):
            if args[i] in ("v4", "v7"):
                version = args[i]
            elif args[i].isdigit():
                count = int(args[i])
            i += 1

        generator = uuid.uuid4 if version == "v4" else uuid_v7
        ids = [str(generator()) for _ in range(count)]
        if count == 1:
            return ids[0]
        return "\n".join(ids)

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>UUID Generator</h2>
  <div class="tool-options">
    <select id="uuid-version"><option value="v4">UUID v4 (random)</option><option value="v7">UUID v7 (time-ordered)</option></select>
    <label>Count: <input id="uuid-count" type="number" value="1" min="1" max="50" style="width:60px"></label>
    <button onclick="genUUID()">Generate</button>
  </div>
  <pre id="uuid-output" class="code-output"></pre>
  <script>
    function genUUID() {
      fetch('/api/uuid',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({version:document.getElementById('uuid-version').value, count:+document.getElementById('uuid-count').value})
      }).then(r=>r.text()).then(t=>{
        document.getElementById('uuid-output').textContent=t;
        navigator.clipboard.writeText(t.split('\\n')[0]);
      });
    }
  </script>
</div>"""


TOOL = UUIDTool()
