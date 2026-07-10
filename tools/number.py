"""Number Base Converter — decimal, binary, octal, hexadecimal."""

import sys
from tools._base import Tool, P_NUM


class NumberTool(Tool):
    name = "num"
    description = "Convert between decimal, binary, octal, hexadecimal"
    category = "utility"
    priority = P_NUM

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = (stdin or " ".join(args)).strip()
        if not data:
            return "Usage: devtool num 255\n   or: devtool num 0xFF\n   or: devtool num 0b11111111"

        # Detect base
        value = None
        base_info = ""

        if data.startswith("0x") or data.startswith("0X"):
            value = int(data, 16)
            base_info = "hex"
        elif data.startswith("0b") or data.startswith("0B"):
            value = int(data, 2)
            base_info = "binary"
        elif data.startswith("0o") or data.startswith("0O"):
            value = int(data, 8)
            base_info = "octal"
        else:
            try:
                value = int(data)
                base_info = "decimal"
            except ValueError:
                try:
                    value = int(data, 16)
                    base_info = "hex (auto-detected)"
                except ValueError:
                    pass

        if value is None:
            return f"Could not parse: {data!r}\nTry: 255, 0xFF, 0b11111111, 0o377"

        return (
            f"Input: {data} ({base_info})\n\n"
            f"  Decimal:    {value:,}\n"
            f"  Hex:        0x{value:X}\n"
            f"  Binary:     0b{value:b}\n"
            f"  Octal:      0o{value:o}\n"
            f"\n"
            f"  Char:       {chr(value) if 32 <= value <= 126 else 'N/A'}\n"
        )

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Number Base Converter</h2>
  <input id="num-input" type="text" placeholder="e.g. 255, 0xFF, 0b11111111" style="width:100%" oninput="convertNum()">
  <div class="tool-output">
    <pre id="num-output" class="code-output"></pre>
  </div>
  <script>
    function convertNum(){
      fetch('/api/num',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({value:document.getElementById('num-input').value})
      }).then(r=>r.text()).then(t=>document.getElementById('num-output').textContent=t);
    }
  </script>
</div>"""


TOOL = NumberTool()
