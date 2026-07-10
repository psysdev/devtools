"""devtool Web Server — FastAPI wrapper around all tools."""

import os
import json
import sys
import io
import importlib

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from tools import discover_tools, list_tools, get_tool

app = FastAPI(title="devtools", description="Developer Toolbox")

# Auto-discover tools on startup
discover_tools()


# ── API Models ───────────────────────────────────────────────────────

class JSONRequest(BaseModel):
    pass

class RegexRequest(BaseModel):
    pattern: str = ""
    test_string: str = ""
    flags: str = ""

class DiffRequest(BaseModel):
    text1: str = ""
    text2: str = ""

class Base64Request(BaseModel):
    text: str = ""
    mode: str = "encode"

class URLRequest(BaseModel):
    text: str = ""
    mode: str = "encode"

class HashRequest(BaseModel):
    text: str = ""

class ColorRequest(BaseModel):
    value: str = ""

class CaseRequest(BaseModel):
    text: str = ""
    mode: str = "camel"

class LoremRequest(BaseModel):
    paragraphs: int = 3
    sentences: int = 5

class UUIDRequest(BaseModel):
    version: str = "v4"
    count: int = 1

class JWTRequest(BaseModel):
    token: str = ""

class NumberRequest(BaseModel):
    value: str = ""

class TimeRequest(BaseModel):
    value: str = ""

class HTMLRequest(BaseModel):
    text: str = ""
    mode: str = "encode"

class ScreenshotRequest(BaseModel):
    code: str = ""
    lang: str = "python"
    title: str = "code.py"
    lines: str = ""

class UnwindRequest(BaseModel):
    trace: str = ""

class MockRequest(BaseModel):
    schema_def: str = ""
    count: int = 3
    format: str = "json"

class LensRequest(BaseModel):
    data: str = ""

class PeepholeRequest(BaseModel):
    code: str = ""

class BlueprintRequest(BaseModel):
    yaml: str = ""
    format: str = "ascii"

class PaperRequest(BaseModel):
    topic: str = "git"

class ArcheoRequest(BaseModel):
    file: str = ""
    lines: str = ""

class RetroRequest(BaseModel):
    cast: str = ""
    speed: float = 1.0

class DashRequest(BaseModel):
    config: str = ""

class StitchRequest(BaseModel):
    frames: str = ""
    captions: str = ""


# ── API Routes ───────────────────────────────────────────────────────

def call_tool(name: str, args: list[str], stdin: str | None = None) -> str:
    tool = get_tool(name)
    if not tool:
        return f"Unknown tool: {name}"
    return tool.run(args, stdin) or ""


@app.get("/api/tools")
async def list_api_tools():
    tools = list_tools()
    return [
        {"name": t.name, "description": t.description, "category": t.category}
        for t in tools
    ]


@app.post("/api/json")
async def api_json(req: Request):
    body = await req.json()
    stdin = body.get("text", "")
    if not stdin:
        stdin = json.dumps(body.get("json", {}))
    return Response(content=call_tool("json", ["fmt"], stdin), media_type="text/plain")


@app.post("/api/regex")
async def api_regex(req: RegexRequest):
    args = ["--pattern", req.pattern, "--test", req.test_string]
    if req.flags:
        args.extend(["--flags", req.flags])
    return Response(content=call_tool("regex", args), media_type="text/plain")


@app.post("/api/diff")
async def api_diff(req: DiffRequest):
    stdin = f"{req.text1}\n---SPLIT---\n{req.text2}"
    return Response(content=call_tool("diff", [], stdin), media_type="text/plain")


@app.post("/api/base64")
async def api_base64(req: Base64Request):
    args = [req.mode]
    return Response(content=call_tool("base64", args, req.text), media_type="text/plain")


@app.post("/api/url")
async def api_url(req: URLRequest):
    args = [req.mode]
    return Response(content=call_tool("url", args, req.text), media_type="text/plain")


@app.post("/api/hash")
async def api_hash(req: HashRequest):
    tool = get_tool("hash")
    if not tool:
        return Response(content="Hash tool not found", media_type="text/plain")
    result = {}
    for algo in ("md5", "sha1", "sha256", "sha512"):
        result[algo] = tool.run([algo], req.text).strip()
    return JSONResponse(content=result)


@app.post("/api/color")
async def api_color(req: ColorRequest):
    return Response(content=call_tool("color", [req.value]), media_type="text/plain")


@app.post("/api/case")
async def api_case(req: CaseRequest):
    return Response(content=call_tool("case", [req.mode], req.text), media_type="text/plain")


@app.post("/api/lorem")
async def api_lorem(req: LoremRequest):
    args = ["-p", str(req.paragraphs), "-s", str(req.sentences)]
    return Response(content=call_tool("lorem", args), media_type="text/plain")


@app.post("/api/uuid")
async def api_uuid(req: UUIDRequest):
    args = [req.version, str(req.count)]
    return Response(content=call_tool("uuid", args), media_type="text/plain")


@app.post("/api/jwt")
async def api_jwt(req: JWTRequest):
    return Response(content=call_tool("jwt", [], req.token), media_type="text/plain")


@app.post("/api/num")
async def api_num(req: NumberRequest):
    return Response(content=call_tool("num", [req.value]), media_type="text/plain")


@app.post("/api/ts")
async def api_ts(req: TimeRequest):
    return Response(content=call_tool("ts", [req.value]), media_type="text/plain")


@app.post("/api/html")
async def api_html(req: HTMLRequest):
    args = [req.mode]
    return Response(content=call_tool("html", args, req.text), media_type="text/plain")


@app.post("/api/screenshot")
async def api_screenshot(req: ScreenshotRequest):
    from tools.screenshot import render_screenshot
    hl_lines = []
    if req.lines:
        parts = req.lines.split("-")
        if len(parts) == 2:
            hl_lines = list(range(int(parts[0]), int(parts[1]) + 1))
        elif len(parts) == 1 and parts[0].isdigit():
            hl_lines = [int(parts[0])]
    png_data = render_screenshot(
        code=req.code,
        title=req.title or "code.py",
        lang=req.lang or "python",
        highlight_lines=hl_lines
    )
    return Response(content=png_data, media_type="image/png")


@app.post("/api/unwind")
async def api_unwind(req: UnwindRequest):
    return Response(content=call_tool("unwind", [], req.trace), media_type="text/plain")


@app.post("/api/mock")
async def api_mock(req: MockRequest):
    args = ["--schema", req.schema_def, "-n", str(req.count)]
    if req.format != "json":
        args.append(f"--{req.format}")
    return Response(content=call_tool("mock", args), media_type="text/plain")


@app.post("/api/lens")
async def api_lens(req: LensRequest):
    return Response(content=call_tool("lens", [], req.data), media_type="text/plain")


@app.post("/api/peephole")
async def api_peephole(req: PeepholeRequest):
    return Response(content=call_tool("peephole", [], req.code), media_type="text/plain")


@app.post("/api/blueprint")
async def api_blueprint(req: BlueprintRequest):
    args = [f"--{req.format}"] if req.format != "ascii" else []
    return Response(content=call_tool("blueprint", args, req.yaml), media_type="text/plain")


@app.post("/api/paper")
async def api_paper(req: PaperRequest):
    return Response(content=call_tool("paper", [req.topic]), media_type="text/plain")


@app.post("/api/archeo")
async def api_archeo(req: ArcheoRequest):
    args = ["--file", req.file]
    if req.lines:
        args.extend(["--lines", req.lines])
    return Response(content=call_tool("archeo", args), media_type="text/plain")


@app.post("/api/retro")
async def api_retro(req: RetroRequest):
    args = ["export", "--speed", str(req.speed)]
    return Response(content=call_tool("retro", args, req.cast), media_type="text/plain")


@app.post("/api/dash")
async def api_dash(req: DashRequest):
    return Response(content=call_tool("dash", [], req.config), media_type="text/plain")


@app.post("/api/stitch")
async def api_stitch(req: StitchRequest):
    args = ["--frames", req.frames]
    if req.captions:
        args.extend(["--captions", req.captions])
    return Response(content=call_tool("stitch", args), media_type="text/plain")


# ── Web UI ───────────────────────────────────────────────────────────

STATIC_DIR = os.path.join(os.path.dirname(__file__), "web")


@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path) as f:
            return f.read()
    return HTMLResponse("<h1>devtools</h1><p>Web UI not found. Run from the project directory.</p>")


@app.get("/app.js", response_class=Response)
async def app_js():
    js_path = os.path.join(STATIC_DIR, "app.js")
    if os.path.exists(js_path):
        with open(js_path) as f:
            return Response(content=f.read(), media_type="application/javascript")
    return Response(content="", media_type="application/javascript")


@app.get("/style.css", response_class=Response)
async def style_css():
    css_path = os.path.join(STATIC_DIR, "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            return Response(content=f.read(), media_type="text/css")
    return Response(content="", media_type="text/css")


def run_server(host: str = "127.0.0.1", port: int = None):
    import uvicorn
    # Allow PORT env var override (for cloud deployment)
    env_port = os.environ.get("PORT")
    if env_port:
        port = int(env_port)
    if port is None:
        port = 8080
    print(f"\n  ╔═══════════════════════════════════════════════╗")
    print(f"  ║   devtool — Developer Toolbox                ║")
    print(f"  ║   Web UI: http://{host}:{port}              ║")
    print(f"  ║   {len(list_tools()) if list_tools() else 25} tools available                ║")
    print(f"  ╚═══════════════════════════════════════════════╝\n")
    uvicorn.run(app, host=host, port=port, log_level="warning")
