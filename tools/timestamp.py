"""Timestamp Converter — Unix timestamp ↔ human-readable date."""

import sys
from datetime import datetime, timezone
from tools._base import Tool, P_TS


class TimestampTool(Tool):
    name = "ts"
    description = "Convert Unix timestamps to dates and vice versa"
    category = "utility"
    priority = P_TS

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = (stdin or " ".join(args)).strip()
        if not data:
            return "Usage: devtool ts 1712345678\n   or: devtool ts '2024-04-05 12:00:00'"

        # Try parsing as timestamp
        try:
            ts = float(data)
            if ts > 1e12:  # milliseconds
                dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
                return f"Unix timestamp (ms): {int(ts)}\nUTC: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}\nLocal: {datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                return f"Unix timestamp: {int(ts)}\nUTC: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}\nLocal: {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}"
        except (ValueError, OSError):
            pass

        # Try parsing as date string
        for fmt in [
            "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z",
        ]:
            try:
                dt = datetime.strptime(data.strip(), fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return f"Date: {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}\nUnix timestamp: {int(dt.timestamp())}\nMilliseconds: {int(dt.timestamp() * 1000)}"
            except ValueError:
                continue

        return f"Could not parse: {data!r}\nTry formats: 1712345678, 2024-04-05, 2024-04-05 12:00:00"

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Timestamp Converter</h2>
  <div class="tool-layout">
    <div class="tool-input">
      <label>Unix timestamp or date string:</label>
      <input id="ts-input" type="text" placeholder="e.g. 1712345678 or 2024-04-05 12:00:00" style="width:100%">
      <button onclick="convertTS()" style="margin-top:8px">Convert</button>
    </div>
    <div class="tool-output">
      <pre id="ts-output" class="code-output"></pre>
    </div>
  </div>
  <script>
    function convertTS() {
      fetch('/api/ts', {method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({value:document.getElementById('ts-input').value})
      }).then(r=>r.text()).then(t=>document.getElementById('ts-output').textContent=t);
    }
  </script>
</div>"""


TOOL = TimestampTool()
