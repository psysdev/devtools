"""Regex Tester & Visualizer — test patterns, see matches in real-time."""

import re
import sys
from tools._base import Tool, P_REGEX


class RegexTool(Tool):
    name = "regex"
    description = "Test regex patterns with match highlighting"
    category = "utility"
    priority = P_REGEX

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = stdin or "".join(sys.stdin)
        if not args:
            return "Usage: echo 'test string' | devtool regex --pattern='(\\\\w+)@(\\\\w+)' [flags]"

        pattern = ""
        flags = 0
        test_string = data

        i = 0
        while i < len(args):
            if args[i] == "--pattern" and i + 1 < len(args):
                pattern = args[i + 1]
                i += 2
            elif args[i] == "--test" and i + 1 < len(args):
                test_string = args[i + 1]
                i += 2
            elif args[i] == "--flags" and i + 1 < len(args):
                for f in args[i + 1]:
                    if f == 'i': flags |= re.IGNORECASE
                    elif f == 'm': flags |= re.MULTILINE
                    elif f == 's': flags |= re.DOTALL
                    elif f == 'x': flags |= re.VERBOSE
                i += 2
            elif args[i].startswith("-"):
                i += 1
            else:
                i += 1

        if not pattern:
            return "Error: --pattern is required"

        try:
            compiled = re.compile(pattern, flags)
        except re.error as e:
            return f"Regex Error: {e.msg}\n  Pattern: {pattern}\n  {' ' * (e.pos + 10)}^" if hasattr(e, 'pos') else f"Regex Error: {e}"

        match = compiled.search(test_string)
        if not match:
            return f"Pattern: /{pattern}/\nTest string: {test_string!r}\n\nNo match found."

        result = [
            f"Pattern: /{pattern}/",
            f"Test string: {len(test_string)} chars",
            f"Match at position {match.start()}-{match.end()}: {match.group()!r}",
            "",
        ]

        # Show the match visually
        before = test_string[:match.start()]
        matched = test_string[match.start():match.end()]
        after = test_string[match.end():]
        result.append(f"  {before}[{matched}]{after}")
        result.append(f"  {' ' * len(before)}{'^' * len(matched)}")
        result.append("")

        # Groups
        if match.groups():
            result.append(f"Groups ({len(match.groups())}):")
            for i, g in enumerate(match.groups()):
                if g is not None:
                    span = match.span(i + 1)
                    result.append(f"  [{i+1}] '{g}'  (pos {span[0]}-{span[1]})")
                else:
                    result.append(f"  [{i+1}] None")

        if match.groupdict():
            result.append(f"\nNamed groups:")
            for name, val in match.groupdict().items():
                result.append(f"  ?P<{name}> = {val!r}")

        return "\n".join(result)

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Regex Tester</h2>
  <div class="tool-layout">
    <div class="tool-input">
      <label>Pattern:</label>
      <input id="rx-pattern" type="text" placeholder="e.g. (\\\\w+)@(\\\\w+)\\\\.(\\\\w+)" style="width:100%;font-family:monospace">
      <label style="margin-top:8px;display:block">
        Flags: <input id="rx-ignore" type="checkbox"> i <input id="rx-multi" type="checkbox"> m <input id="rx-dotall" type="checkbox"> s
      </label>
      <label style="margin-top:8px;display:block">Test string:</label>
      <textarea id="rx-input" rows="6" placeholder="Enter test string...">hello@example.com</textarea>
      <button onclick="testRegex()">Test</button>
    </div>
    <div class="tool-output">
      <label>Match result:</label>
      <pre id="rx-output" class="code-output"></pre>
    </div>
  </div>
  <script>
    function testRegex() {
      const pattern = document.getElementById('rx-pattern').value;
      const testStr = document.getElementById('rx-input').value;
      let flags = '';
      if (document.getElementById('rx-ignore').checked) flags += 'i';
      if (document.getElementById('rx-multi').checked) flags += 'm';
      if (document.getElementById('rx-dotall').checked) flags += 's';
      fetch('/api/regex', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({pattern, test_string: testStr, flags})
      }).then(r => r.text()).then(text => {
        document.getElementById('rx-output').textContent = text;
      });
    }
    document.addEventListener('keydown', function(e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') testRegex();
    });
  </script>
</div>"""


TOOL = RegexTool()
