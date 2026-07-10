#!/usr/bin/env python3
"""devtool — Developer Toolbox.

CLI + Web developer utilities. Pipe-friendly, UNIX-style.

Usage:
    devtool <tool> [args...]
    devtool --serve
    echo '{"a":1}' | devtool json
"""

import argparse
import sys
import textwrap

from tools import discover_tools, list_tools, get_tool


def main():
    discover_tools()

    parser = argparse.ArgumentParser(
        prog="devtool",
        description="Developer Toolbox — CLI + Web developer utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              devtool json fmt < data.json
              echo '{"a":1}' | devtool json
              devtool color "#ff5500"
              devtool unwind < traceback.txt
              devtool --serve           # Start web UI
        """),
    )

    parser.add_argument("--serve", action="store_true", help="Start web UI")
    parser.add_argument("--port", type=int, default=8080, help="Web UI port")
    parser.add_argument("--host", default="127.0.0.1", help="Web UI host")
    parser.add_argument("tool", nargs="?", help="Tool name")
    parser.add_argument("tool_args", nargs=argparse.REMAINDER, help="Tool arguments")

    args = parser.parse_args()

    if args.serve:
        return _serve(args.host, args.port)

    if not args.tool:
        _show_tools()
        return

    tool = get_tool(args.tool)
    if not tool:
        print(f"Unknown tool: {args.tool}")
        print(f"Run 'devtool' to see available tools.")
        sys.exit(1)

    stdin = sys.stdin.read() if not sys.stdin.isatty() else None
    result = tool.run(args.tool_args, stdin)
    if result:
        print(result, end="" if result.endswith("\n") else "\n")


def _show_tools():
    print(textwrap.dedent("""\
        ╔══════════════════════════════════════════════╗
        ║              devtool — Toolbox               ║
        ╚══════════════════════════════════════════════╝
    """))

    tools = list_tools()
    utilities = [t for t in tools if t.category == "utility"]
    flagships = [t for t in tools if t.category == "flagship"]

    print("  ── Utilities ──")
    for t in utilities:
        print(t.cli_help())

    print()
    print("  ── Flagship Tools ──")
    for t in flagships:
        print(t.cli_help())

    print()
    print("  devtool --serve           Start web UI on port 8080")
    print()


def _serve(host: str, port: int):
    """Start the web UI server."""
    from serve import run_server
    run_server(host, port)


if __name__ == "__main__":
    main()
