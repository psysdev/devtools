"""Lorem Ipsum Generator — generate placeholder text."""

import sys
import random
from tools._base import Tool, P_LOREM

LOREM_WORDS = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore "
    "et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut "
    "aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit esse "
    "cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt in "
    "culpa qui officia deserunt mollit anim id est laborum"
).split()


def generate_sentence(word_count: int = None) -> str:
    if word_count is None:
        word_count = random.randint(5, 15)
    words = [random.choice(LOREM_WORDS) for _ in range(word_count)]
    sentence = " ".join(words).capitalize() + "."
    return sentence


def generate_paragraph(sentences: int = None) -> str:
    if sentences is None:
        sentences = random.randint(3, 7)
    return " ".join(generate_sentence() for _ in range(sentences))


class LoremTool(Tool):
    name = "lorem"
    description = "Generate lorem ipsum placeholder text"
    category = "utility"
    priority = P_LOREM

    def run(self, args: list[str], stdin: str | None = None) -> str:
        paragraphs = 3
        sentences = 5
        words = 0
        fmt = "plain"

        i = 0
        while i < len(args):
            if args[i] in ("-p", "--paragraphs") and i + 1 < len(args):
                paragraphs = int(args[i + 1]); i += 2
            elif args[i] in ("-s", "--sentences") and i + 1 < len(args):
                sentences = int(args[i + 1]); i += 2
            elif args[i] in ("-w", "--words") and i + 1 < len(args):
                words = int(args[i + 1]); i += 2
            elif args[i] in ("--html",):
                fmt = "html"; i += 1
            elif args[i] in ("--markdown", "--md"):
                fmt = "markdown"; i += 1
            else:
                i += 1

        result = []
        if words > 0:
            result.append(" ".join(random.choice(LOREM_WORDS) for _ in range(words)))
        else:
            for _ in range(paragraphs if paragraphs > 0 else 1):
                p = generate_paragraph(sentences)
                if fmt == "html":
                    result.append(f"<p>{p}</p>")
                elif fmt == "markdown":
                    result.append(f"\n{p}\n")
                else:
                    result.append(p + "\n")

        return "\n".join(result).strip()

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Lorem Ipsum Generator</h2>
  <div class="tool-options">
    <label>Paragraphs: <input id="lorem-p" type="number" value="3" min="1" max="20" style="width:60px"></label>
    <label>Sentences: <input id="lorem-s" type="number" value="5" min="1" max="30" style="width:60px"></label>
  </div>
  <button onclick="genLorem()">Generate</button>
  <div class="tool-output">
    <pre id="lorem-output" class="code-output"></pre>
    <button onclick="copyOutput('lorem-output')">Copy</button>
  </div>
  <script>
    function genLorem() {
      fetch('/api/lorem',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({paragraphs:+document.getElementById('lorem-p').value, sentences:+document.getElementById('lorem-s').value})
      }).then(r=>r.text()).then(t=>document.getElementById('lorem-output').textContent=t);
    }
  </script>
</div>"""


TOOL = LoremTool()
