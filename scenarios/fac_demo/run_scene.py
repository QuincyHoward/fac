#!/usr/bin/env python3
"""CLI for FAC demo scenarios: list/describe/run/anchors with run targets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCENARIOS_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SCENARIOS_ROOT.parent
for path in (str(SCENARIOS_ROOT), str(PROJECT_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from core.anchors import load_anchors, resolve_anchor  # noqa: E402
from core.discovery import discover_scenes, find_scene  # noqa: E402
from scenarios.run.execution import ExecOptions, SceneSpec, explain_target, run_scene  # noqa: E402


def to_spec(scene) -> SceneSpec:
    return SceneSpec(scene.name, scene.path, scene.archetype, scene.entry)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List discovered scenes.")

    describe = sub.add_parser("describe", help="Describe one scene.")
    describe.add_argument("--name", required=True)

    run = sub.add_parser("run", help="Run or submit one scene.")
    run.add_argument("--name", required=True)
    run.add_argument("--mode", default="auto", help="auto/local/wsl/hpc-remote/hpc-insitu.")
    run.add_argument("--cores", default="auto")
    run.add_argument("--namespace", default="specx")
    run.add_argument("--credential", default="flash_ssh")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("extra", nargs="*")

    explain = sub.add_parser("explain", help="Explain target resolution.")
    explain.add_argument("--name", required=True)
    explain.add_argument("--mode", default="auto")

    anchors = sub.add_parser("anchors", help="Show logical anchors.")
    anchors.add_argument("--resolve")

    args = parser.parse_args(argv)

    if args.command == "list":
        scenes = discover_scenes()
        for scene in scenes:
            print(scene.summary())
        print(f"\nTotal scenes: {len(scenes)}")
        return 0

    scene = find_scene(args.name) if args.command in {"describe", "run", "explain"} else None
    if args.command in {"describe", "run", "explain"} and scene is None:
        print(f"Scene not found: {args.name}")
        return 2

    if args.command == "describe":
        print(scene.summary())
        print("Entry:", scene.entry)
        return 0

    if args.command == "explain":
        options = ExecOptions(mode=args.mode, namespace="specx")
        print(json.dumps(explain_target(to_spec(scene), options), ensure_ascii=False, indent=2))
        return 0

    if args.command == "run":
        options = ExecOptions(
            mode=args.mode,
            namespace=args.namespace,
            credential=args.credential,
            cores=args.cores,
            dry_run=args.dry_run,
            extra=tuple(args.extra),
        )
        return run_scene(to_spec(scene), options, args.extra)

    if args.command == "anchors":
        if args.resolve:
            print(resolve_anchor(args.resolve))
        else:
            for key, value in load_anchors().items():
                print(f"{key}\t{value}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
