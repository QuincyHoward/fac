#!/usr/bin/env python3
"""Read-only MCP-style context server for the FAC project.

The server speaks JSON-RPC 2.0 over stdio and deliberately exposes only
read-only context tools. It never writes files or executes shell commands.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
MAX_CHARS = 200_000
SAFE_NAME = re.compile(r"^[A-Za-z0-9_.-]+$")
CONTEXT_FILES = {
    "agents": "AGENTS.md",
    "claude": "CLAUDE.md",
    "readme": "README.md",
    "dependencies": "DEPENDENCIES.md",
    "cursor": ".cursor/rules/fac-context.mdc",
    "copilot": ".github/copilot-instructions.md",
}


def fail(message: str) -> dict[str, Any]:
    return {"isError": True, "content": [{"type": "text", "text": message}]}


def ok(text: str) -> dict[str, Any]:
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n\n[TRUNCATED: output limit reached]"
    return {"content": [{"type": "text", "text": text}]}


def resolved_inside(path: Path, base: Path) -> Path | None:
    try:
        target = path.resolve()
        base_resolved = base.resolve()
    except OSError:
        return None
    if target == base_resolved or base_resolved in target.parents:
        return target
    return None


def read_text_file(path: Path) -> dict[str, Any]:
    target = resolved_inside(path, ROOT)
    if target is None:
        return fail("Path escaped the project root.")
    if not target.is_file():
        return fail(f"File not found: {path}")
    try:
        return ok(target.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return fail(f"File is not UTF-8 text: {path}")
    except OSError as exc:
        return fail(f"Unable to read file: {exc}")


def validate_name(name: str) -> bool:
    return bool(name) and bool(SAFE_NAME.fullmatch(name)) and ".." not in name


def list_skills() -> dict[str, Any]:
    root = ROOT / "skills"
    if not root.is_dir():
        return ok("No skills directory found.")
    rows = []
    for skill_md in sorted(root.glob("*/SKILL.md")):
        rows.append(skill_md.parent.name)
    return ok("\n".join(rows) if rows else "No skills found.")


def read_skill(name: str, reference: str | None = None) -> dict[str, Any]:
    if not validate_name(name):
        return fail("Invalid skill name.")
    base = ROOT / "skills" / name
    if resolved_inside(base, ROOT / "skills") is None:
        return fail("Invalid skill path.")
    if reference is None:
        return read_text_file(base / "SKILL.md")
    if not validate_name(reference):
        return fail("Invalid reference name.")
    return read_text_file(base / "references" / f"{reference}.md")


def read_context(key: str) -> dict[str, Any]:
    rel = CONTEXT_FILES.get(key)
    if rel is None:
        allowed = ", ".join(sorted(CONTEXT_FILES))
        return fail(f"Unknown context key. Allowed: {allowed}")
    return read_text_file(ROOT / rel)


def read_readme(relative_path: str) -> dict[str, Any]:
    if not relative_path or Path(relative_path).name != "README.md":
        return fail("Only README.md files can be read.")
    candidate = ROOT / relative_path
    if resolved_inside(candidate, ROOT) is None:
        return fail("Path escaped the project root.")
    return read_text_file(candidate)


def list_scenarios() -> dict[str, Any]:
    base = ROOT / "scenarios"
    if not base.is_dir():
        return ok("No scenarios directory found.")
    rows = []
    for manifest in sorted(base.rglob("scene.json")):
        rows.append(str(manifest.parent.relative_to(ROOT)).replace("\\", "/"))
    return ok("\n".join(rows) if rows else "No scenes found.")


def audit_summary() -> dict[str, Any]:
    skills = len(list((ROOT / "skills").glob("*/SKILL.md"))) if (ROOT / "skills").is_dir() else 0
    readmes = len(list(ROOT.rglob("README.md")))
    scripts = len(list((ROOT / "scripts").rglob("*.py"))) if (ROOT / "scripts").is_dir() else 0
    scenes = len(list((ROOT / "scenarios").rglob("scene.json"))) if (ROOT / "scenarios").is_dir() else 0
    text = (
        f"skills={skills}\n"
        f"readmes={readmes}\n"
        f"scripts={scripts}\n"
        f"scenes={scenes}\n"
    )
    return ok(text)


TOOLS: dict[str, Any] = {
    "list_skills": {
        "description": "List available project-level skills.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "read_skill": {
        "description": "Read a SKILL.md or one reference file by name.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "reference": {"type": "string", "description": "Reference stem, optional."},
            },
            "required": ["name"],
        },
    },
    "read_context": {
        "description": "Read a fixed context/protocol document.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "enum": sorted(CONTEXT_FILES),
                }
            },
            "required": ["key"],
        },
    },
    "read_readme": {
        "description": "Read a README.md by project-relative path.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    "list_scenarios": {
        "description": "List discovered physical scenarios.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "audit_summary": {
        "description": "Return counts of skills, READMEs, scripts and scenes.",
        "inputSchema": {"type": "object", "properties": {}},
    },
}


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    handlers = {
        "list_skills": lambda: list_skills(),
        "read_skill": lambda: read_skill(
            str(arguments.get("name", "")),
            arguments.get("reference"),
        ),
        "read_context": lambda: read_context(str(arguments.get("key", ""))),
        "read_readme": lambda: read_readme(str(arguments.get("path", ""))),
        "list_scenarios": lambda: list_scenarios(),
        "audit_summary": lambda: audit_summary(),
    }
    handler = handlers.get(name)
    if handler is None:
        return fail(f"Unknown tool: {name}")
    return handler()


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    req_id = request.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "fac-context", "version": "1.0.0"},
        }
    elif method == "tools/list":
        result = {
            "tools": [
                {"name": name, **schema} for name, schema in sorted(TOOLS.items())
            ]
        }
    elif method == "tools/call":
        params = request.get("params") or {}
        result = call_tool(str(params.get("name", "")), params.get("arguments") or {})
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def serve_stdio() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
        except json.JSONDecodeError as exc:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
        except Exception as exc:  # keep the protocol alive on unexpected errors
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": f"Internal error: {exc}"},
            }
        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)
    return 0


def selftest() -> int:
    checks = [
        ("list_skills", list_skills()),
        ("read_context", read_context("agents")),
        ("audit_summary", audit_summary()),
        ("traversal", read_readme("../README.md")),
    ]
    for name, result in checks:
        flag = result.get("isError", False)
        print(f"{name}: {'ERROR' if flag else 'OK'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=["stdio", "selftest"],
        default="stdio",
        help="stdio: JSON-RPC loop; selftest: print local check results.",
    )
    args = parser.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    return serve_stdio()


if __name__ == "__main__":
    raise SystemExit(main())
