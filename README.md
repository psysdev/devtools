<br>/> **developer toolbox** — 25 utilities in one CLI + web app.
> Pipe-friendly. Docker-ready. Open source.

---

## ✨ Features

| # | Tool | What it does |
|---|------|-------------|
| 1 | `json` | Format, validate, and pretty-print JSON |
| 2 | `screenshot` | Generate beautiful code screenshots (Pygments + Pillow) |
| 3 | `regex` | Test regex patterns with live matching |
| 4 | `diff` | Side-by-side text diffs |
| 5 | `base64` | Encode / decode base64 |
| 6 | `url` | URL encode / decode |
| 7 | `hash` | Hash generator (MD5, SHA1, SHA256, SHA512) |
| 8 | `ts` | Timestamp converter (Unix ↔ date) |
| 9 | `color` | Color converter (hex, rgb, hsl, name) |
| 10 | `case` | Case converter (camel, snake, kebab, pascal, upper, lower) |
| 11 | `lorem` | Lorem ipsum generator |
| 12 | `uuid` | UUID v4/v7 generator |
| 13 | `jwt` | Decode and inspect JWT tokens |
| 14 | `html` | HTML entity encode / decode |
| 15 | `num` | Number base converter (hex, bin, oct, dec) |
| 16 | `unwind` | ⭐ Stack trace humanizer — promotes the error cause to the top |
| 17 | `archeo` | ⭐ Git archaeology — timeline of changes to a function |
| 18 | `peephole` | ⭐ Code path visualizer — execution tree for nested conditionals |
| 19 | `mock` | ⭐ Data alchemist — `devtool mock --schema='name:string,age:int' --count=10` |
| 20 | `retro` | ⭐ Terminal recording → animated SVG/GIF/HTML |
| 21 | `lens` | ⭐ Schema detective — infer structure from JSON/CSV/YAML |
| 22 | `paper` | ⭐ Cheatsheet forge — `devtool paper git` |
| 23 | `dash` | ⭐ On-call dashboard — configurable TUI panel grid |
| 24 | `blueprint` | ⭐ Architecture diagram generator — YAML → SVG/Mermaid |
| 25 | `stitch` | ⭐ Screenshot storyboard — combine frames with captions |

---

## 🚀 Quick Start

### Option A — Docker (recommended)

```bash
docker pull ghcr.io/franklybreezy/devtools
docker run -p 8080:8080 ghcr.io/franklybreezy/devtools
```

Then open **http://localhost:8080** in your browser.

### Option B — Python (local)

```bash
git clone <repo-url> devtools
cd devtools
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 devtool.py --serve
```

### Option C — Docker Compose

```bash
docker compose up -d
# Open http://localhost:8080
```

---

## 💻 CLI Usage

Pipe data in, get results out. UNIX-style.

```bash
# Format JSON
echo '{"name":"Alice","age":30}' | devtool json

# Base64 encode
echo 'hello world' | devtool base64 encode

# Regex tester
echo 'hello@example.com' | devtool regex --pattern='(\w+)@(\w+)\.(\w+)'

# Color converter
devtool color "#ff5500"

# UUIDs
devtool uuid --count=5

# Stack trace humanizer
cat traceback.txt | devtool unwind

# Mock data
devtool mock --schema='name:string, age:int, email:email, city:city' --count=3

# Architecture diagram
devtool blueprint --file=architecture.yaml --format=mermaid

# List all tools
devtool --help
```

---

## 🌐 Web UI

Start the web server and open `http://localhost:8080`:

```bash
python3 devtool.py --serve
```

The web UI gives you:
- **Tile grid** — all 25 tools at a glance, grouped by category
- **Sidebar navigation** — quick jump between tools
- **Pre-populated examples** — every tool loads with sample data ready to try
- **⌘+⏎ keyboard shortcut** — run any tool from its textarea
- **Copy output** — one-click copy results
- **Dark theme** — matches the psys.dev ecosystem

---

## 🐳 Docker Deployment

### Build locally

```bash
docker build -t devtools .
docker run -p 8080:8080 devtools
```

### Deploy to Render / Koyeb / Fly.io

1. Push this repo to GitHub
2. Create a new Web Service on your hosting platform
3. Point it at the repo — the Dockerfile is auto-detected
4. Set the `PORT` env var to `8080`
5. Deploy

The app reads the `PORT` environment variable, so it works out of the box on most platforms.

---

## 📁 Project Structure

```
devtools/
├── devtool.py          # CLI entry point
├── serve.py            # FastAPI web server (25 API endpoints + static files)
├── Dockerfile          # Multi-stage build (~150 MB)
├── docker-compose.yml  # One-command deploy
├── requirements.txt
├── tools/
│   ├── __init__.py     # Auto-discovers all tools
│   ├── _base.py        # Base Tool class
│   ├── json_tool.py    # & 14 more utility tools
│   ├── unwind.py       # ⭐ & 9 more flagship tools
│   └── ...
└── web/
    ├── index.html      # SPA shell
    ├── style.css       # Dark theme (psys ecosystem)
    └── app.js          # All 25 tool UIs + home tile view
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **CLI** | Python, `argparse`, `rich` |
| **Web server** | FastAPI + uvicorn |
| **Frontend** | Vanilla JS, CSS custom properties |
| **Screenshots** | Pygments + Pillow |
| **Mock data** | Faker |
| **Diagrams** | graphviz |
| **Containers** | Docker, docker-compose |

---

## 📄 License

MIT — do whatever you want with it.
