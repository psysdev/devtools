"""Code Screenshot Generator — VS Code-themed PNG screenshots of code."""

import os
import sys
import io
from tools._base import Tool, P_SCREENSHOT
from pygments import highlight
from pygments.lexers import PythonLexer, get_lexer_by_name, guess_lexer
from pygments.formatter import Formatter
from PIL import Image, ImageDraw, ImageFont


# ── VS Code Dark+ Theme Colors ──
BG_COLOR = (30, 30, 30)
SIDEBAR_COLOR = (37, 37, 38)
TAB_ACTIVE_BG = (30, 30, 30)
TAB_INACTIVE_BG = (37, 37, 38)
ACTIVITY_BAR_BG = (51, 51, 51)
STATUS_BAR_BG = (0, 122, 204)
LINE_NUM_COLOR = (120, 120, 120)
LINE_NUM_HIGHLIGHT = (200, 200, 200)
TEXT_COLOR = (212, 212, 212)
HIGHLIGHT_BG = (40, 45, 55)
FONT_SIZE = 14
LINE_HEIGHT = 22
PADDING_Y = 16
ACTIVITY_BAR_WIDTH = 48
HEADER_HEIGHT = 36
GUTTER_WIDTH = 48

TOKEN_COLORS = {
    "Token.Keyword":          (197, 134, 192),
    "Token.Keyword.Type":     (197, 134, 192),
    "Token.Name.Function":    (220, 220, 170),
    "Token.Name.Class":       (78, 201, 176),
    "Token.Name.Builtin":     (78, 201, 176),
    "Token.Name.Decorator":   (220, 220, 170),
    "Token.String":           (206, 145, 120),
    "Token.String.Doc":       (106, 153, 85),
    "Token.Comment":          (106, 153, 85),
    "Token.Comment.Special":  (106, 153, 85),
    "Token.Number":           (181, 206, 168),
    "Token.Operator":         (212, 212, 212),
    "Token.Punctuation":      (212, 212, 212),
    "Token.Literal.String":   (206, 145, 120),
    "Token.Literal.Number":   (181, 206, 168),
    "Token.Name.Attribute":   (78, 201, 176),
    "Token.Name.Variable":    (212, 212, 212),
    "Token.Name.Namespace":   (78, 201, 176),
    "Token.Name.Constant":    (100, 150, 255),
    "Token.Text":             (212, 212, 212),
}


class VSCodeFormatter(Formatter):
    def __init__(self):
        super().__init__()
        self.tokens = []

    def format(self, tokensource, outfile):
        self.tokens = []
        for ttype, value in tokensource:
            ttype_str = str(ttype)
            for char in value:
                self.tokens.append((ttype_str, char))


def get_font(size=FONT_SIZE):
    candidates = [
        "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
        "/usr/share/fonts/truetype/firacode/FiraCode-Regular.ttf",
        "/usr/share/fonts/truetype/cascadia-code/CascadiaCode-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def get_token_color(ttype_str: str) -> tuple:
    parts = ttype_str.split(".")
    for i in range(len(parts), 0, -1):
        key = ".".join(parts[:i])
        if key in TOKEN_COLORS:
            return TOKEN_COLORS[key]
    return TEXT_COLOR


def highlight_code(code: str, lang: str = "python") -> list:
    lexers = {
        "python": PythonLexer(),
        "py": PythonLexer(),
        "javascript": get_lexer_by_name("javascript"),
        "js": get_lexer_by_name("javascript"),
        "typescript": get_lexer_by_name("typescript"),
        "ts": get_lexer_by_name("typescript"),
        "html": get_lexer_by_name("html"),
        "css": get_lexer_by_name("css"),
        "go": get_lexer_by_name("go"),
        "rust": get_lexer_by_name("rust"),
        "rs": get_lexer_by_name("rust"),
        "java": get_lexer_by_name("java"),
        "yaml": get_lexer_by_name("yaml"),
        "yml": get_lexer_by_name("yaml"),
        "json": get_lexer_by_name("json"),
        "sql": get_lexer_by_name("sql"),
        "bash": get_lexer_by_name("bash"),
        "sh": get_lexer_by_name("bash"),
        "dockerfile": get_lexer_by_name("docker"),
    }
    lexer = lexers.get(lang, guess_lexer(code))
    formatter = VSCodeFormatter()
    highlight(code, lexer, formatter)

    lines = []
    current_line = []
    for ttype_str, char in formatter.tokens:
        color = get_token_color(ttype_str)
        if char == "\n":
            lines.append(current_line)
            current_line = []
        else:
            current_line.append((color, char))
    if current_line:
        lines.append(current_line)
    return lines


def render_screenshot(code: str, title: str = "code.py", lang: str = "python",
                      highlight_lines: list = None, width: int = 960) -> bytes:
    font = get_font()
    small_font = get_font(11)

    hl_lines = highlight_code(code, lang)
    num_lines = len(hl_lines)

    content_height = PADDING_Y * 2 + num_lines * LINE_HEIGHT
    height = min(max(content_height + HEADER_HEIGHT + 24, 120), 4800)

    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([(0, 0), (width, HEADER_HEIGHT)], fill=TAB_INACTIVE_BG)
    for dx, color in [(10, (255, 95, 87)), (26, (255, 189, 46)), (42, (40, 200, 80))]:
        draw.ellipse([(dx, 12), (dx + 10, 22)], fill=color)

    tab_width = min(280, width - 70)
    draw.rectangle([(60, 0), (60 + tab_width, HEADER_HEIGHT)], fill=TAB_ACTIVE_BG)
    draw.text((70, 10), f"  {title}", fill=(180, 180, 180), font=small_font)

    # Activity bar
    draw.rectangle([(0, HEADER_HEIGHT), (ACTIVITY_BAR_WIDTH, height)], fill=ACTIVITY_BAR_BG)
    draw.line([(ACTIVITY_BAR_WIDTH, HEADER_HEIGHT), (ACTIVITY_BAR_WIDTH, height)], fill=(60, 60, 60), width=1)

    # Code
    gutter_right_edge = ACTIVITY_BAR_WIDTH + GUTTER_WIDTH
    y = HEADER_HEIGHT + PADDING_Y
    hl_set = set(highlight_lines or [])
    max_line_width = len(str(num_lines))
    line_num_gutter = max(GUTTER_WIDTH, max_line_width * 10 + 24)

    for i, line in enumerate(hl_lines):
        line_num = i + 1
        if line_num in hl_set:
            draw.rectangle([(ACTIVITY_BAR_WIDTH, y - 2), (width, y + LINE_HEIGHT - 2)], fill=HIGHLIGHT_BG)

        num_text = str(line_num).rjust(max_line_width)
        lnum_color = LINE_NUM_HIGHLIGHT if line_num in hl_set else LINE_NUM_COLOR
        draw.text((ACTIVITY_BAR_WIDTH + line_num_gutter - 8, y - 1), num_text, fill=lnum_color, font=small_font, anchor="ra")

        x = ACTIVITY_BAR_WIDTH + line_num_gutter + 12
        for color, char in line:
            if char == "\t":
                x += FONT_SIZE * 3
                continue
            if char == " ":
                x += FONT_SIZE // 2
                continue
            draw.text((x, y - 1), char, fill=color, font=font)
            bbox = draw.textbbox((0, 0), char, font=font)
            x += bbox[2] - bbox[0] + 0.5
        y += LINE_HEIGHT

    # Status bar
    bar_y = height - 24
    draw.rectangle([(0, bar_y), (width, height)], fill=STATUS_BAR_BG)
    status_text = f"Python 3  |  UTF-8  |  Ln {num_lines}, Col 1"
    draw.text((ACTIVITY_BAR_WIDTH + 12, bar_y + 4), status_text, fill=(255, 255, 255), font=small_font)

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    return img_bytes.getvalue()


class ScreenshotTool(Tool):
    name = "screenshot"
    description = "Generate VS Code-themed code screenshots"
    category = "utility"
    priority = P_SCREENSHOT

    def run(self, args: list[str], stdin: str | None = None) -> str:
        import argparse
        parser = argparse.ArgumentParser(prog="devtool screenshot")
        parser.add_argument("--file", "-f", help="Source file")
        parser.add_argument("--lang", "-l", default="python", help="Language")
        parser.add_argument("--lines", "-n", help="Line numbers to highlight (e.g. 12-18)")
        parser.add_argument("--output", "-o", default="code.png", help="Output file")
        parser.add_argument("--title", "-t", default="code.py", help="Tab title")

        parsed = parser.parse_args(args) if args else parser.parse_args([])

        code = stdin or ""
        if parsed.file:
            with open(parsed.file) as f:
                code = f.read()
        if not code:
            return "Error: provide code via --file, stdin pipe, or paste"

        title = parsed.title or (os.path.basename(parsed.file) if parsed.file else "code")
        lang = parsed.lang or (os.path.splitext(title)[1].lstrip(".") if "." in title else "python")

        hl_lines = []
        if parsed.lines:
            parts = parsed.lines.split("-")
            if len(parts) == 2:
                hl_lines = list(range(int(parts[0]), int(parts[1]) + 1))
            else:
                hl_lines = [int(p) for p in parsed.lines.split(",") if p]

        png_data = render_screenshot(code, title, lang, hl_lines)
        with open(parsed.output, "wb") as f:
            f.write(png_data)
        size_kb = len(png_data) // 1024
        return f"Screenshot saved to {parsed.output} ({size_kb}KB)"

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Code Screenshot Generator</h2>
  <div class="tool-layout">
    <div class="tool-input">
      <div class="tool-options">
        <label>Language: <select id="shot-lang">
          <option value="python">Python</option><option value="javascript">JavaScript</option>
          <option value="typescript">TypeScript</option><option value="html">HTML</option>
          <option value="css">CSS</option><option value="go">Go</option><option value="rust">Rust</option>
          <option value="java">Java</option><option value="yaml">YAML</option><option value="json">JSON</option>
          <option value="sql">SQL</option><option value="bash">Bash</option>
        </select></label>
        <label>Title: <input id="shot-title" value="code.py" style="width:120px"></label>
      </div>
      <textarea id="shot-input" rows="10" placeholder="Paste code here..."></textarea>
      <button onclick="generateScreenshot()">Generate Screenshot</button>
    </div>
    <div class="tool-output">
      <label>Preview:</label>
      <div id="shot-preview" class="preview-area">Click Generate</div>
      <a id="shot-download" style="display:none">Download PNG</a>
    </div>
  </div>
  <script>
    async function generateScreenshot() {
      const code = document.getElementById('shot-input').value;
      const lang = document.getElementById('shot-lang').value;
      const title = document.getElementById('shot-title').value || 'code';
      if (!code) return alert('Paste some code first');
      const resp = await fetch('/api/screenshot', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({code, lang, title})
      });
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const preview = document.getElementById('shot-preview');
      preview.innerHTML = `<img src="${url}" style="max-width:100%;border-radius:4px">`;
      const dl = document.getElementById('shot-download');
      dl.href = url; dl.download = 'screenshot.png'; dl.style.display = 'block';
      dl.textContent = 'Download PNG (' + (blob.size/1024).toFixed(0) + 'KB)';
    }
  </script>
</div>"""

TOOL = ScreenshotTool()
