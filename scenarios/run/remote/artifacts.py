"""产物回传执行点。"""

from __future__ import annotations

import posixpath
from pathlib import Path

from .fetch_policy import select_fetch_files
from .session import RemoteSession


def fetch_artifacts(session: RemoteSession, remote_dir: str, local_dir: Path) -> list[Path]:
    names = session.listdir(remote_dir)
    selected = select_fetch_files(names)
    local_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for name in selected:
        remote = posixpath.join(remote_dir, name)
        local = local_dir / name
        local.parent.mkdir(parents=True, exist_ok=True)
        saved.append(session.download(remote, local))
    return saved
