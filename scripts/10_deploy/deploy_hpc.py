#!/usr/bin/env python3
"""将 FAC 项目部署到 HPC：目标 ~/<凭证用户名>/fac/fac。"""

from __future__ import annotations

import argparse
import tarfile
import tempfile
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS_ROOT = ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))
SCENARIOS_ROOT = ROOT / "scenarios"
if str(SCENARIOS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCENARIOS_ROOT))

from scenarios.run.env.devices import sim_user  # noqa: E402
from scenarios.run.remote.session import RemoteSession  # noqa: E402

EXCLUDE_DIRS = {".git", "__pycache__", "build", "dist", "logs", "runs", "outputs", "temp", "tmp"}
EXCLUDE_SUFFIX = (".pyc", ".pyo", ".tar", ".gz", ".zip", ".rar", ".7z")


def make_archive(source: Path, archive: Path) -> None:
    with tarfile.open(archive, "w:gz") as tar:
        for path in sorted(source.rglob("*")):
            rel = path.relative_to(source)
            if any(part in EXCLUDE_DIRS for part in rel.parts):
                continue
            if path.is_file() and path.name.endswith(EXCLUDE_SUFFIX):
                continue
            tar.add(path, arcname=str(rel))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default="specx")
    parser.add_argument("--credential", default="flash_ssh")
    parser.add_argument("--source", default=str(ROOT))
    parser.add_argument("-n", "--dry-run", action="store_true")
    args = parser.parse_args(argv)

    source = Path(args.source).resolve()
    user = sim_user(args.namespace)
    with RemoteSession(args.namespace, args.credential) as session:
        home = session.home()
        target = f"{home}/{user}/fac/fac"
        print(f"SSH 线路    : {session.selected_route}")
        print(f"HPC HOME    : {home}")
        print(f"凭证用户名  : {user}")
        print(f"部署目标    : {target}")
        if args.dry_run:
            return 0

        session.mkdir_p(target)
        with tempfile.TemporaryDirectory() as tmpdir:
            archive = Path(tmpdir) / "fac_deploy.tar.gz"
            make_archive(source, archive)
            remote_archive = f"{home}/{user}/fac_deploy.tar.gz"
            session.upload(archive, remote_archive)
            rc, out, err = session.exec(
                f'tar -xzf "{remote_archive}" -C "{target}" && rm -f "{remote_archive}"',
                timeout=300,
            )
            if rc != 0:
                print("远端解包失败：", err.strip())
                return 1
        rc, out, err = session.exec(f'test -f "{target}/README.md" && echo OK')
        if rc != 0 or "OK" not in out:
            print("部署校验失败。")
            return 1
    print("部署完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
