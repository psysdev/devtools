"""Tool registry — auto-discovers all tool modules and registers them."""

import importlib
import os
import pkgutil
from typing import Optional


_registry = {}


def discover_tools():
    """Import all tool modules in the tools package and register them."""
    package_dir = os.path.dirname(__file__)
    for importer, modname, ispkg in pkgutil.iter_modules([package_dir]):
        if modname.startswith("_") or modname == "cli":
            continue
        module = importlib.import_module(f"tools.{modname}")
        if hasattr(module, "TOOL"):
            tool = module.TOOL
            _registry[tool.name] = tool


def get_tool(name: str) -> Optional[object]:
    return _registry.get(name)


def list_tools():
    # Sort by category (utility first), then by priority, then by name
    return sorted(
        _registry.values(),
        key=lambda t: (0 if t.category == "utility" else 1, t.priority, t.name),
    )


def get_tools_by_category(category: str):
    return [t for t in list_tools() if t.category == category]
