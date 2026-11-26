"""唯一 SSH/SFTP 实现：从加密凭证读取密码，不打印敏感信息。"""

from __future__ import annotations

import logging
import os
import posixpath
import sys
from pathlib import Path

FAC_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_ROOT = FAC_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import paramiko  # noqa: E402

logging.getLogger("paramiko").setLevel(logging.CRITICAL)

from credentials._core import get as get_secret  # noqa: E402
from credentials.hpc_accounts import load as load_hpc  # noqa: E402


class RemoteSession:
    def __init__(self, namespace: str = "specx", credential: str = "flash_ssh", timeout: int = 20) -> None:
        self.namespace = namespace
        self.credential = credential
        self.timeout = timeout
        config = load_hpc(namespace).get("accounts", {}).get(credential)
        if not config:
            raise RuntimeError(f"未找到 HPC 账户配置：{credential}")
        user_at = str(config.get("ssh_username", ""))
        self.username = user_at
        self.account_config = config
        self.routes = config.get("routes") or []
        self.password = str(get_secret(namespace, f"hpc.{credential}.password", "") or "")
        self.client = self._connect()

    def _connect(self) -> paramiko.SSHClient:
        errors = []
        for route in self.routes:
            host = str(route.get("host", ""))
            port = int(route.get("port", 22) or 22)
            if not host:
                continue
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(
                    hostname=host,
                    port=port,
                    username=self.username,
                    password=self.password or None,
                    timeout=self.timeout,
                    allow_agent=True,
                    look_for_keys=True,
                )
                self.selected_route = f"{host}:{port}"
                return client
            except Exception as exc:
                errors.append(f"{host}:{port}: {type(exc).__name__}")
                client.close()
        raise RuntimeError("SSH 连接失败：" + "; ".join(errors))

    def exec(self, command: str, timeout: int = 300) -> tuple[int, str, str]:
        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        stdin.close()
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        rc = stdout.channel.recv_exit_status()
        return rc, out, err

    def home(self) -> str:
        rc, out, _ = self.exec('printf "%s" "$HOME"')
        if rc != 0 or not out.strip():
            raise RuntimeError("无法解析远端 HOME")
        return out.strip()

    def abs_path(self, path: str) -> str:
        path = str(path).replace("\\", "/")
        if path.startswith("~/"):
            return posixpath.join(self.home(), path[2:])
        if path == "~":
            return self.home()
        if not path.startswith("/"):
            return posixpath.join(self.home(), path)
        return path

    def exists(self, path: str) -> bool:
        rc, _, _ = self.exec(f'test -e "{self.abs_path(path)}"')
        return rc == 0

    def mkdir_p(self, path: str) -> str:
        target = self.abs_path(path)
        rc, out, err = self.exec(f'mkdir -p "{target}"')
        if rc != 0:
            raise RuntimeError(f"mkdir 失败：{err.strip()}")
        return target

    def _sftp(self) -> paramiko.SFTPClient:
        return self.client.open_sftp()

    def _sftp_mkdirs(self, sftp: paramiko.SFTPClient, remote_dir: str) -> None:
        parts = []
        current = remote_dir
        while current and current != "/":
            parts.append(current)
            current = posixpath.dirname(current)
        for item in reversed(parts):
            try:
                sftp.stat(item)
            except IOError:
                sftp.mkdir(item)

    def upload(self, local: Path, remote: str) -> str:
        target = self.abs_path(remote)
        sftp = self._sftp()
        try:
            self._sftp_mkdirs(sftp, posixpath.dirname(target))
            sftp.put(str(local), target)
        finally:
            sftp.close()
        return target

    def download(self, remote: str, local: Path) -> Path:
        target = self.abs_path(remote)
        local.parent.mkdir(parents=True, exist_ok=True)
        sftp = self._sftp()
        try:
            sftp.get(target, str(local))
        finally:
            sftp.close()
        return local

    def listdir(self, remote: str) -> list[str]:
        target = self.abs_path(remote)
        sftp = self._sftp()
        try:
            return sftp.listdir(target)
        finally:
            sftp.close()

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "RemoteSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
