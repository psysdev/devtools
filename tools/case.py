"""Case Converter — convert between camelCase, snake_case, kebab-case, etc."""

import sys
import re
from tools._base import Tool, P_CASE


def split_words(text: str) -> list[str]:
    """Split text into words, handling various casing styles."""
    text = text.strip()
    if not text:
        return []
    # Handle camelCase and PascalCase
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', text)
    # Replace separators with spaces
    text = re.sub(r'[_\-\s.]+', ' ', text)
    words = text.lower().split()
    return [w for w in words if w]


def to_camel(words: list[str]) -> str:
    return words[0] + "".join(w.capitalize() for w in words[1:])


def to_pascal(words: list[str]) -> str:
    return "".join(w.capitalize() for w in words)


def to_snake(words: list[str]) -> str:
    return "_".join(words)


def to_kebab(words: list[str]) -> str:
    return "-".join(words)


def to_upper(words: list[str]) -> str:
    return "_".join(w.upper() for w in words)


def to_title(words: list[str]) -> str:
    return " ".join(w.capitalize() for w in words)


def to_dot(words: list[str]) -> str:
    return ".".join(words)


class CaseTool(Tool):
    name = "case"
    description = "Convert between camelCase, snake_case, kebab-case, PascalCase, and more"
    category = "utility"
    priority = P_CASE

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = stdin or "".join(sys.stdin)
        if not data:
            return "Usage: echo 'hello_world' | devtool case camel\nModes: camel, pascal, snake, kebab, upper, title, dot"

        mode = "camel"
        if args and args[0] in ("camel", "pascal", "snake", "kebab", "upper", "title", "dot"):
            mode = args[0]

        words = split_words(data)
        if not words:
            return "Error: no words found in input"

        converters = {
            "camel": to_camel, "pascal": to_pascal, "snake": to_snake,
            "kebab": to_kebab, "upper": to_upper, "title": to_title, "dot": to_dot,
        }

        return converters[mode](words)

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Case Converter</h2>
  <textarea id="case-input" rows="4" placeholder="Type text to convert..." style="width:100%"></textarea>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px">
    <div class="case-mode" onclick="caseConvert('camel')"><strong>camelCase</strong><span id="case-camel"></span></div>
    <div class="case-mode" onclick="caseConvert('pascal')"><strong>PascalCase</strong><span id="case-pascal"></span></div>
    <div class="case-mode" onclick="caseConvert('snake')"><strong>snake_case</strong><span id="case-snake"></span></div>
    <div class="case-mode" onclick="caseConvert('kebab')"><strong>kebab-case</strong><span id="case-kebab"></span></div>
    <div class="case-mode" onclick="caseConvert('upper')"><strong>UPPER_CASE</strong><span id="case-upper"></span></div>
    <div class="case-mode" onclick="caseConvert('title')"><strong>Title Case</strong><span id="case-title"></span></div>
  </div>
  <script>
    function caseConvert(mode) {
      const input = document.getElementById('case-input').value;
      fetch('/api/case',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({text:input, mode})
      }).then(r=>r.text()).then(t=>{
        const el = document.getElementById('case-'+mode);
        el.textContent = ' ' + t;
        navigator.clipboard.writeText(t);
      });
    }
  </script>
</div>"""


TOOL = CaseTool()
