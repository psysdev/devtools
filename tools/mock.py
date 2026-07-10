"""Data Alchemist — generate realistic mock data from a one-line schema."""

import sys
import json
import random
import string
from datetime import datetime, timedelta
from tools._base import Tool, P_MOCK

try:
    from faker import Faker
    fake = Faker()
except ImportError:
    fake = None


FIRST_NAMES = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Iris", "Jack",
               "Kate", "Leo", "Mia", "Noah", "Olivia", "Paul", "Quinn", "Rosa", "Sam", "Tina"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
              "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Martin", "Lee", "Perez", "White", "Harris"]
COMPANIES = ["Acme Corp", "Globex Inc", "Initech", "Hooli", "Stark Industries", "Wayne Enterprises",
             "Cyberdyne Systems", "Umbrella Corp", "Wonka Industries", "Soylent Corp"]
CITIES = ["New York", "San Francisco", "Chicago", "Los Angeles", "Austin", "Seattle", "Boston", "Portland", "Denver", "Miami"]
DOMAINS = ["gmail.com", "outlook.com", "corp.net", "example.com", "startup.io"]
LOREM = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", "sed", "do",
         "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua"]


def gen_value(field_type: str) -> any:
    """Generate a mock value based on the type specification."""
    field_type = field_type.strip().lower()

    if field_type == "string" or field_type == "str":
        return "".join(random.choice(string.ascii_lowercase) for _ in range(random.randint(5, 12)))
    elif field_type == "name":
        return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    elif field_type == "first_name":
        return random.choice(FIRST_NAMES)
    elif field_type == "last_name":
        return random.choice(LAST_NAMES)
    elif field_type == "email":
        name = random.choice(FIRST_NAMES).lower()
        domain = random.choice(DOMAINS)
        return f"{name}.{random.choice(LAST_NAMES).lower()}@{domain}"
    elif field_type == "phone" or field_type == "tel":
        return f"+1 ({random.randint(200, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
    elif field_type == "int" or field_type == "integer":
        return random.randint(0, 1000)
    elif field_type.startswith("int:") or field_type.startswith("int-"):
        parts = field_type.replace(":", "-").split("-")
        if len(parts) >= 3:
            return random.randint(int(parts[1]), int(parts[2]))
        return random.randint(0, 1000)
    elif field_type == "float":
        return round(random.uniform(0, 100), 2)
    elif field_type.startswith("float:"):
        parts = field_type.split(":")[1].split("-")
        if len(parts) == 2:
            return round(random.uniform(float(parts[0]), float(parts[1])), 2)
        return round(random.uniform(0, 100), 2)
    elif field_type == "bool" or field_type == "boolean":
        return random.choice([True, False])
    elif field_type == "date":
        d = datetime.now() - timedelta(days=random.randint(0, 365))
        return d.strftime("%Y-%m-%d")
    elif field_type == "datetime":
        d = datetime.now() - timedelta(days=random.randint(0, 365), hours=random.randint(0, 24))
        return d.strftime("%Y-%m-%d %H:%M:%S")
    elif field_type == "uuid":
        import uuid
        return str(uuid.uuid4())
    elif field_type == "company":
        return random.choice(COMPANIES)
    elif field_type == "city":
        return random.choice(CITIES)
    elif field_type == "zip" or field_type == "zip_code" or field_type == "postcode":
        return f"{random.randint(10000, 99999)}"
    elif field_type == "address":
        return f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Elm', 'Park', 'Lake', 'Hill'])}, {random.choice(CITIES)}"
    elif field_type == "lorem" or field_type == "paragraph":
        words = [random.choice(LOREM) for _ in range(random.randint(5, 20))]
        return " ".join(words).capitalize() + "."
    elif field_type == "url":
        return f"https://{random.choice(COMPANIES).lower().replace(' ', '')}.com/{random.choice(['products', 'about', 'blog', 'docs'])}"
    elif field_type == "color":
        return f"#{random.randint(0, 0xFFFFFF):06x}"
    elif field_type == "ip" or field_type == "ip_address":
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
    elif field_type.startswith("choice:"):
        options = field_type.split(":", 1)[1].split(",")
        return random.choice([o.strip() for o in options])
    else:
        return f"<{field_type}>"


def parse_schema(schema: str) -> tuple:
    """Parse a schema string into field definitions.
    Supports: name:string, age:int, items:[{name:string, qty:int}], nested:{field:type}
    """
    fields = []
    i = 0
    schema = schema.strip()

    while i < len(schema):
        # Skip whitespace and commas
        if schema[i] in ", ":
            i += 1
            continue

        # Parse field name
        name_start = i
        while i < len(schema) and schema[i] not in ":, ":
            i += 1
        field_name = schema[name_start:i]

        if i < len(schema) and schema[i] == ":":
            i += 1  # skip ':'

        # Parse field type
        if i < len(schema) and schema[i] == "{":
            # Nested object
            depth = 1
            type_start = i
            i += 1
            while i < len(schema) and depth > 0:
                if schema[i] == "{": depth += 1
                elif schema[i] == "}": depth -= 1
                i += 1
            nested_schema = schema[type_start:i]
            fields.append((field_name, "object", nested_schema))
        elif i < len(schema) and schema[i] == "[":
            # Array
            type_start = i
            i += 1
            depth = 1
            while i < len(schema) and depth > 0:
                if schema[i] == "[": depth += 1
                elif schema[i] == "]": depth -= 1
                i += 1
            array_spec = schema[type_start:i]
            # Determine if it's array of primitives or objects
            inner = array_spec[1:-1].strip()
            if inner.startswith("{"):
                fields.append((field_name, "array_object", inner))
            else:
                fields.append((field_name, "array", inner))
        else:
            while i < len(schema) and schema[i] not in ", ":
                i += 1
            field_type = schema[name_start+len(field_name)+1:i].strip()
            fields.append((field_name, "simple", field_type))

    return fields


def gen_record(fields: list, count: int = 1) -> list:
    """Generate mock records from parsed field definitions."""
    records = []
    for _ in range(count):
        record = {}
        for name, kind, spec in fields:
            if kind == "simple":
                record[name] = gen_value(spec)
            elif kind == "object":
                subfields = parse_schema(spec[1:-1])
                record[name] = gen_record(subfields, 1)[0]
            elif kind == "array":
                arr_count = random.randint(1, 3)
                record[name] = [gen_value(spec) for _ in range(arr_count)]
            elif kind == "array_object":
                subfields = parse_schema(spec[1:-1])
                arr_count = random.randint(1, 2)
                record[name] = gen_record(subfields, arr_count)
        records.append(record)
    return records


class MockTool(Tool):
    name = "mock"
    description = "Generate realistic mock data from a one-line schema"
    category = "flagship"
    priority = P_MOCK

    def run(self, args: list[str], stdin: str | None = None) -> str:
        schema = ""
        count = 1
        fmt = "json"

        i = 0
        while i < len(args):
            if args[i] in ("-s", "--schema") and i + 1 < len(args):
                schema = args[i + 1]; i += 2
            elif args[i] in ("-n", "--count") and i + 1 < len(args):
                count = int(args[i + 1]); i += 2
            elif args[i] in ("--csv",):
                fmt = "csv"; i += 1
            elif args[i] in ("--sql",):
                fmt = "sql"; i += 1
            elif args[i] in ("--md", "--markdown"):
                fmt = "markdown"; i += 1
            elif not args[i].startswith("-") and not schema:
                schema = args[i]; i += 1
            else:
                i += 1

        if not schema and stdin:
            schema = stdin.strip()

        if not schema:
            return "Usage: devtool mock --schema='name:string,age:int,email:email' --count=3"

        fields = parse_schema(schema)
        records = gen_record(fields, count)

        if fmt == "csv":
            if not records:
                return ""
            headers = list(records[0].keys())
            rows = [",".join(headers)]
            for r in records:
                rows.append(",".join(str(r.get(h, "")).replace(",", ";") for h in headers))
            return "\n".join(rows)
        elif fmt == "sql":
            if not records:
                return ""
            table = "mock_data"
            headers = list(records[0].keys())
            stmts = []
            for r in records:
                cols = ", ".join(headers)
                vals = ", ".join(f"'{str(r.get(h, ''))}'" for h in headers)
                stmts.append(f"INSERT INTO {table} ({cols}) VALUES ({vals});")
            return "\n".join(stmts)
        elif fmt == "markdown":
            if not records:
                return ""
            headers = list(records[0].keys())
            rows = ["| " + " | ".join(headers) + " |"]
            rows.append("| " + " | ".join("---" for _ in headers) + " |")
            for r in records:
                rows.append("| " + " | ".join(str(r.get(h, "")) for h in headers) + " |")
            return "\n".join(rows)
        else:
            return json.dumps(records if count > 1 else records[0], indent=2, default=str)

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>Mock Data Generator</h2>
  <div class="tool-options">
    <input id="mock-schema" type="text" placeholder="name:string, age:int, email:email" style="width:70%">
    <label>Count: <input id="mock-count" type="number" value="3" min="1" max="50" style="width:60px"></label>
    <select id="mock-format"><option value="json">JSON</option><option value="csv">CSV</option><option value="sql">SQL</option><option value="markdown">Markdown</option></select>
  </div>
  <button onclick="genMock()">Generate</button>
  <pre id="mock-output" class="code-output"></pre>
  <button onclick="copyOutput('mock-output')" style="margin-top:4px">Copy</button>
  <script>
    function genMock() {
      fetch('/api/mock',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          schema_def:document.getElementById('mock-schema').value,
          count:+document.getElementById('mock-count').value,
          format:document.getElementById('mock-format').value
        })
      }).then(r=>r.text()).then(t=>document.getElementById('mock-output').textContent=t);
    }
  </script>
</div>"""


TOOL = MockTool()
