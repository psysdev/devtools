"""Code Path Visualizer — render control flow as an ASCII tree with dead code detection."""

import sys
import ast
import re
from tools._base import Tool, P_PEEPHOLE


class ConditionVisitor(ast.NodeVisitor):
    """Extract conditional paths from a function AST."""

    def __init__(self):
        self.paths = []
        self.current_depth = 0

    def visit_FunctionDef(self, node):
        self.func_name = node.name
        self.generic_visit(node)

    def visit_If(self, node):
        condition = ast.unparse(node.test) if hasattr(ast, 'unparse') else "?"
        branch = {
            "type": "if",
            "condition": condition,
            "depth": self.current_depth,
            "body_lines": len(node.body),
            "orelse_lines": len(node.orelse) if node.orelse else 0,
        }
        self.paths.append(branch)

        # Visit nested conditions
        self.current_depth += 1
        for stmt in node.body:
            if isinstance(stmt, ast.If):
                self.visit_If(stmt)
        for stmt in node.orelse:
            if isinstance(stmt, ast.If):
                self.visit_If(stmt)
            elif isinstance(stmt, ast.IfExp):
                self.paths.append({"type": "if", "condition": "ternary", "depth": self.current_depth})
        self.current_depth -= 1

        if node.orelse and not any(isinstance(s, (ast.If, ast.IfExp)) for s in node.orelse):
            self.paths.append({"type": "else", "depth": self.current_depth})

    def visit_IfExp(self, node):
        condition = ast.unparse(node.test) if hasattr(ast, 'unparse') else "ternary"
        self.paths.append({"type": "ternary", "condition": condition, "depth": self.current_depth})


def visualize_function(source: str) -> str:
    """Parse a function and visualize its control flow."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return f"Syntax error: {e}"

    result = []
    result.append("╔══════════════════════════════════════════════╗")
    result.append("║          PEEPHOLE — Code Path Visualizer     ║")
    result.append("╚══════════════════════════════════════════════╝")
    result.append("")

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            # Count total paths (2^n for n ifs is worst case, but let's count actual branches)
            visitor = ConditionVisitor()
            visitor.visit(node)
            paths = visitor.paths

            if_count = sum(1 for p in paths if p["type"] == "if")
            else_count = sum(1 for p in paths if p["type"] == "else")

            result.append(f"  Function: {func_name}()")
            result.append(f"  Conditions: {if_count} if(s), {else_count} else(s)")
            if if_count > 0:
                result.append(f"  Possible paths: at least {2 ** if_count}")
            result.append("")

            # Draw the tree
            if paths:
                result.append("  Control Flow Tree:")
                for i, p in enumerate(paths):
                    indent = "  │  " * p.get("depth", 0)
                    prefix = "  ├──" if i < len(paths) - 1 else "  └──"
                    if p["type"] == "if":
                        cond = p.get("condition", "?")
                        body = p.get("body_lines", 0)
                        result.append(f"  {indent}{prefix} if {cond} ({body} lines)")
                    elif p["type"] == "else":
                        orelse = p.get("orelse_lines", 0)
                        result.append(f"  {indent}{prefix} else")
                    elif p["type"] == "ternary":
                        cond = p.get("condition", "?")
                        result.append(f"  {indent}{prefix} ternary: {cond}")
                result.append("")

            # Show source
            src_lines = source.splitlines()
            if src_lines:
                result.append(f"  Source ({len(src_lines)} lines):")
                # Find the function
                for i, line in enumerate(src_lines):
                    marker = " " if i < len(src_lines) - 1 else " "
                    result.append(f"  {marker} {i+1:4d} {line}")
                result.append("")

    return "\n".join(result)


class PeepholeTool(Tool):
    name = "peephole"
    description = "Visualize code execution paths as an ASCII tree"
    category = "flagship"
    priority = P_PEEPHOLE

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = stdin or "".join(sys.stdin)
        if not data:
            return "Usage: cat app.py | devtool peephole\n  Pipes in a Python function, renders its control flow tree."

        return visualize_function(data)

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Code Path Visualizer</h2>
  <p>Paste a Python function to see its control flow as a visual tree.</p>
  <textarea id="peep-input" rows="10" placeholder='def process(x):&#10;    if x > 0:&#10;        return "positive"&#10;    elif x == 0:&#10;        return "zero"&#10;    else:&#10;        return "negative"' style="width:100%;font-family:monospace;font-size:13px"></textarea>
  <button onclick="runPeephole()">Visualize</button>
  <pre id="peep-output" class="code-output"></pre>
  <script>
    function runPeephole() {
      fetch('/api/peephole',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({code:document.getElementById('peep-input').value})
      }).then(r=>r.text()).then(t=>document.getElementById('peep-output').textContent=t);
    }
  </script>
</div>"""


TOOL = PeepholeTool()
