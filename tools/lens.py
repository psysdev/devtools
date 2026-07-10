"""Schema Detective — infer schema from JSON/CSV data with sample values."""

import sys
import json
from collections import Counter
from tools._base import Tool, P_LENS


def infer_type(values: list) -> dict:
    """Infer the type and stats for a list of values."""
    types = Counter()
    non_null = [v for v in values if v is not None and v != ""]
    null_count = len(values) - len(non_null)

    for v in non_null:
        if isinstance(v, bool):
            types["boolean"] += 1
        elif isinstance(v, int):
            types["integer"] += 1
        elif isinstance(v, float):
            types["float"] += 1
        elif isinstance(v, str):
            # Check if it's a date
            if len(v) == 10 and v[4] == "-" and v[7] == "-":
                types["date"] += 1
            else:
                types["string"] += 1
        elif isinstance(v, dict):
            types["object"] += 1
        elif isinstance(v, list):
            types["array"] += 1
        else:
            types[type(v).__name__] += 1

    dominant = types.most_common(1)
    if not dominant:
        return {"type": "unknown", "nullable": True}

    result = {"type": dominant[0][0]}
    if null_count > 0:
        result["nullable"] = True
        result["null_percent"] = round(null_count / len(values) * 100)

    # Sample values (up to 3, no duplicates)
    seen = set()
    samples = []
    for v in non_null:
        s = str(v)
        if s not in seen and len(seen) < 3:
            seen.add(s)
            samples.append(s[:80])
    if samples:
        result["samples"] = samples

    if result["type"] in ("integer", "float", "boolean"):
        result["unique_count"] = len(set(non_null))

    return result


def infer_schema(data, depth=0, max_depth=5) -> dict:
    """Infer schema from JSON data."""
    if depth > max_depth:
        return {"type": "any"}

    if isinstance(data, dict):
        schema = {"type": "object", "properties": {}}
        for key, value in data.items():
            schema["properties"][key] = infer_schema(value, depth + 1, max_depth)
        return schema

    elif isinstance(data, list):
        if not data:
            return {"type": "array", "items": {"type": "any"}}

        # Collect all items
        all_items = []
        for item in data:
            if isinstance(item, (list, dict)):
                all_items.append(item)
            else:
                all_items.append(item)

        # Infer items schema
        if all(isinstance(v, dict) for v in all_items):
            # Merge all dicts
            merged = {}
            for d in all_items:
                for k, v in d.items():
                    if k not in merged:
                        merged[k] = []
                    merged[k].append(v if not isinstance(v, (list, dict)) else str(v))
            props = {}
            for k, vals in merged.items():
                props[k] = infer_type(vals)
            return {"type": "array", "items": {"type": "object", "properties": props}}
        else:
            types = Counter()
            for v in all_items:
                if isinstance(v, bool):
                    types["boolean"] += 1
                elif isinstance(v, int):
                    types["integer"] += 1
                elif isinstance(v, float):
                    types["float"] += 1
                else:
                    types["string"] += 1
            return {"type": "array", "items": {"type": types.most_common(1)[0][0]}}

    elif isinstance(data, bool):
        return {"type": "boolean"}

    elif isinstance(data, int):
        return {"type": "integer"}

    elif isinstance(data, float):
        return {"type": "float"}

    elif isinstance(data, str):
        if len(data) == 10 and data[4] == "-" and data[7] == "-":
            return {"type": "date"}
        return {"type": "string"}

    return {"type": type(data).__name__}


def schema_to_text(schema: dict, indent: int = 0) -> list:
    """Convert schema dict to readable text."""
    prefix = "  " * indent
    lines = []

    if schema.get("type") == "object":
        props = schema.get("properties", {})
        for name, prop in props.items():
            nullable = prop.get("nullable", False)
            null_str = " (nullable)" if nullable else ""
            type_str = prop.get("type", "unknown")
            samples = prop.get("samples", [])
            sample_str = f" e.g. {samples[0]}" if samples else ""
            lines.append(f"{prefix}  {name}: {type_str}{null_str}{sample_str}")
            if prop.get("properties"):
                lines.extend(schema_to_text(prop, indent + 2))
            if prop.get("items", {}).get("properties"):
                lines.append(f"{prefix}    items:")
                lines.extend(schema_to_text(prop["items"], indent + 3))
    elif schema.get("type") == "array":
        items = schema.get("items", {})
        lines.append(f"{prefix}  array of {items.get('type', 'any')}")
        if items.get("properties"):
            lines.append(f"{prefix}    items:")
            lines.extend(schema_to_text(items, indent + 3))
    else:
        type_str = schema.get("type", "unknown")
        nullable = schema.get("nullable", False)
        null_str = " (nullable)" if nullable else ""
        samples = schema.get("samples", [])
        sample_str = f" e.g. {', '.join(samples)}" if samples else ""
        lines.append(f"{prefix}  {type_str}{null_str}{sample_str}")

    return lines


class LensTool(Tool):
    name = "lens"
    description = "Infer schema from JSON/CSV — see the shape of your data"
    category = "flagship"
    priority = P_LENS

    def run(self, args: list[str], stdin: str | None = None) -> str:
        data = stdin or "".join(sys.stdin)
        if not data:
            return "Usage: cat data.json | devtool lens"

        parsed = None
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            # Try JSON lines
            lines = [l.strip() for l in data.splitlines() if l.strip()]
            if lines:
                try:
                    parsed = [json.loads(l) for l in lines]
                except json.JSONDecodeError:
                    pass

        if parsed is None:
            return "Error: could not parse as JSON"

        if isinstance(parsed, list) and len(parsed) > 1:
            # Multiple records — analyze each field
            merged = {}
            for record in parsed:
                if isinstance(record, dict):
                    for k, v in record.items():
                        if k not in merged:
                            merged[k] = []
                        merged[k].append(v if not isinstance(v, (list, dict)) else str(v))

            result = [f"Schema for {len(parsed)} records ({len(merged)} fields):\n"]
            for name, vals in merged.items():
                info = infer_type(vals)
                result.append(f"  {name}: {info['type']}" +
                    (" (nullable)" if info.get("nullable") else "") +
                    (f" \"{info['samples'][0]}\"" if info.get("samples") else ""))
        else:
            # Single object or small list
            schema = infer_schema(parsed)
            result = ["Inferred schema:\n"]
            result.extend(schema_to_text(schema))

        return "\n".join(result)

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Schema Detective</h2>
  <p>Paste JSON data to infer its schema — field types, nullability, and sample values.</p>
  <textarea id="lens-input" rows="8" placeholder='[{"name": "Alice", "age": 30, "email": "alice@test.com"}]' style="width:100%;font-family:monospace;font-size:13px"></textarea>
  <button onclick="inferSchema()">Infer Schema</button>
  <pre id="lens-output" class="code-output"></pre>
  <script>
    function inferSchema() {
      fetch('/api/lens',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({data:document.getElementById('lens-input').value})
      }).then(r=>r.text()).then(t=>document.getElementById('lens-output').textContent=t);
    }
  </script>
</div>"""


TOOL = LensTool()
