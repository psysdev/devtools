"""Stack Trace Humanizer — re-orders stack traces to show the error origin first with source context."""

import sys
import re
import os
from tools._base import Tool, P_UNWIND


class UnwindTool(Tool):
    name = "unwind"
    description = "Humanize stack traces — show error origin first with source context"
    category = "flagship"
    priority = P_UNWIND

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = stdin or "".join(sys.stdin)
        if not data:
            return "Usage: pbpaste | devtool unwind"

        return self._parse_traceback(data)

    def _parse_traceback(self, text: str) -> str:
        lines = text.splitlines()
        if not lines:
            return "Empty input."

        # Detect if it's Python or JS
        is_python = any("Traceback (most recent call last)" in line for line in lines)
        is_js = any(line.strip().startswith("Error") or line.strip().startswith("Uncaught") for line in lines)

        if not is_python and not is_js:
            # Try to auto-detect
            if any("File \"" in line for line in lines):
                is_python = True
            elif any("at " in line for line in lines):
                is_js = True

        if is_python:
            return self._format_python_traceback(lines)
        elif is_js:
            return self._format_js_stack(lines)
        else:
            # Generic fallback
            return self._format_generic(lines)

    def _format_python_traceback(self, lines: list) -> str:
        result = []
        frames = []
        error_line = ""
        error_type = ""
        error_msg = ""

        # Parse frames
        file_re = re.compile(r'  File "([^"]+)", line (\d+)(?:, in (.+))?')
        for i, line in enumerate(lines):
            m = file_re.match(line)
            if m:
                filepath = m.group(1)
                lineno = int(m.group(2))
                func = m.group(3) or "?"
                # Get next line (code line)
                code = lines[i + 1].strip() if i + 1 < len(lines) else ""
                frames.append((filepath, lineno, func, code))

            # Error line
            if "Error:" in line or "Exception:" in line or "Traceback" in line:
                if "Traceback" not in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        error_type = parts[0].strip()
                        error_msg = parts[1].strip()

        if not frames and not error_type:
            return text  # Return as-is if we can't parse

        # Get the last frame (origin)
        last_frame = frames[-1] if frames else None

        result.append("╔══════════════════════════════════════════════╗")
        result.append("║         UNWIND — Stack Trace Humanized      ║")
        result.append("╚══════════════════════════════════════════════╝")
        result.append("")

        if error_type:
            result.append(f"  \033[1;31m{error_type}: {error_msg}\033[0m")
            result.append("")

        if last_frame:
            fp, ln, func, code = last_frame
            result.append(f"  ╭─ \033[1;33mOrigin\033[0m — {os.path.basename(fp)}:{ln} in {func}()")
            if code:
                result.append(f"  ├─ {code}")
            result.append(f"  ╰─ {fp}")
            result.append("")

        # Frame chain
        if len(frames) > 1:
            result.append(f"  \033[1;36mCall chain ({len(frames)} frames):\033[0m")
            for i, (fp, ln, func, code) in enumerate(frames):
                prefix = "  └" if i == len(frames) - 1 else "  ├"
                context = os.path.basename(fp)
                result.append(f"  {prefix} {context}:{ln} → {func}()")
                if code and i < len(frames) - 1:
                    result.append(f"  │  {code}")

        result.append("")
        if last_frame and os.path.exists(last_frame[0]):
            result.append(f"  Source context ({os.path.basename(last_frame[0])}:{last_frame[1]}):")
            try:
                with open(last_frame[0]) as f:
                    src_lines = f.readlines()
                start = max(0, last_frame[1] - 4)
                end = min(len(src_lines), last_frame[1] + 3)
                for i in range(start, end):
                    marker = "→" if i + 1 == last_frame[1] else " "
                    result.append(f"  {marker} {i+1:4d} {src_lines[i].rstrip()}")
            except (FileNotFoundError, IOError):
                result.append(f"  (source file not accessible)")

        return "\n".join(result)

    def _format_js_stack(self, lines: list) -> str:
        result = ["  JS Stack Trace (humanized):", ""]
        at_re = re.compile(r'\s+at\s+(.+)\s+\((.+):(\d+):(\d+)\)')
        for line in lines:
            m = at_re.match(line)
            if m:
                func = m.group(1)
                fp = m.group(2)
                ln = m.group(3)
                col = m.group(4)
                context = os.path.basename(fp) if fp else "<anonymous>"
                result.append(f"  └ {context}:{ln}:{col} → {func}()")
            else:
                result.append(f"  {line}")
        return "\n".join(result)

    def _format_generic(self, lines: list) -> str:
        return "\n".join(f"  {line}" for line in lines)

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Stack Trace Humanizer</h2>
  <p>Paste a Python or JavaScript stack trace — the error origin shows first, with source context.</p>
  <textarea id="unwind-input" rows="10" placeholder="Paste stack trace here..." style="width:100%;font-family:monospace;font-size:13px"></textarea>
  <button onclick="humanizeTrace()">Humanize</button>
  <pre id="unwind-output" class="code-output"></pre>
  <script>
    function humanizeTrace() {
      fetch('/api/unwind',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({trace:document.getElementById('unwind-input').value})
      }).then(r=>r.text()).then(t=>document.getElementById('unwind-output').textContent=t);
    }
  </script>
</div>"""


TOOL = UnwindTool()
