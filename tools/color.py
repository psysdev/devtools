"""Color Converter — hex/rgb/hsl conversion with interactive picker."""

import sys
import re
from tools._base import Tool, P_COLOR


def hex_to_rgb(hex_color: str) -> tuple | None:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return None
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def rgb_to_hex(r, g, b) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_hsl(r, g, b) -> tuple:
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    h = s = 0
    l = (mx + mn) / 2
    if mx != mn:
        d = mx - mn
        s = d / (1 - abs(2 * l - 1))
        if mx == r:
            h = ((g - b) / d + (6 if g < b else 0)) / 6
        elif mx == g:
            h = ((b - r) / d + 2) / 6
        else:
            h = ((r - g) / d + 4) / 6
    return (round(h * 360), round(s * 100), round(l * 100))


def hsl_to_rgb(h, s, l) -> tuple:
    h, s, l = h / 360, s / 100, l / 100
    if s == 0:
        return (round(l * 255), round(l * 255), round(l * 255))
    def hue_to_rgb(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    return (
        round(hue_to_rgb(p, q, h + 1/3) * 255),
        round(hue_to_rgb(p, q, h) * 255),
        round(hue_to_rgb(p, q, h - 1/3) * 255),
    )


class ColorTool(Tool):
    name = "color"
    description = "Convert colors between hex, rgb, hsl with preview"
    category = "utility"
    priority = P_COLOR

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = (stdin or " ".join(args)).strip()
        if not data:
            return "Usage: devtool color '#ff5500'\n   or: devtool color 'rgb(255, 85, 0)'\n   or: devtool color 'hsl(20, 100, 50)'"

        rgb = None
        # Try hex
        hex_match = re.search(r'#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})', data)
        if hex_match:
            rgb = hex_to_rgb(hex_match.group(0))

        # Try rgb()
        if not rgb:
            rgb_match = re.search(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', data)
            if rgb_match:
                rgb = (int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3)))

        # Try hsl()
        if not rgb:
            hsl_match = re.search(r'hsl\s*\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)', data)
            if hsl_match:
                rgb = hsl_to_rgb(int(hsl_match.group(1)), int(hsl_match.group(2)), int(hsl_match.group(3)))

        if not rgb:
            return f"Could not parse color: {data!r}\nTry: #ff5500, rgb(255,85,0), hsl(20,100,50)"

        r, g, b = rgb
        hex_val = rgb_to_hex(r, g, b)
        h, s, l = rgb_to_hsl(r, g, b)

        # ANSI color block
        block = f"\033[48;2;{r};{g};{b}m  \033[0m" * 10

        return (
            f"Color: {data}\n\n"
            f"  HEX:  {hex_val}\n"
            f"  RGB:  rgb({r}, {g}, {b})\n"
            f"  HSL:  hsl({h}, {s}%, {l}%)\n"
            f"\n  Preview: {block}\n"
        )

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Color Converter</h2>
  <div class="tool-layout">
    <div class="tool-input">
      <input id="color-picker" type="color" value="#ff5500" onchange="convertColor()" style="width:100%;height:60px">
      <label>Or type hex/rgb/hsl:</label>
      <input id="color-input" type="text" value="#ff5500" placeholder="#ff5500" style="width:100%" oninput="convertColor()">
    </div>
    <div class="tool-output">
      <div id="color-output"></div>
    </div>
  </div>
  <script>
    function convertColor() {
      const val = document.getElementById('color-input').value || document.getElementById('color-picker').value;
      fetch('/api/color', {method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({value: val})
      }).then(r=>r.text()).then(t=>document.getElementById('color-output').textContent=t);
    }
  </script>
</div>"""


TOOL = ColorTool()
