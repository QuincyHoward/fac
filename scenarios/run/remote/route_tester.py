"""SSH 多线路延迟探测；不修改账户配置。"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

FAC_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_ROOT = FAC_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import paramiko  # noqa: E402

logging.getLogger("paramiko").setLevel(logging.CRITICAL)

from credentials._core import get as get_secret  # noqa: E402
from credentials.hpc_accounts import load as load_hpc  # noqa: E402


def test_routes(namespace: str = "specx", credential: str = "flash_ssh") -> list[tuple[str, int, float, str]]:
    config = load_hpc(namespace).get("accounts", {}).get(credential, {})
    user_at = str(config.get("ssh_username", ""))
    user = user_at
    password = str(get_secret(namespace, f"hpc.{credential}.password", "") or "")
    results = []
    for route in config.get("routes", []):
        host = str(route.get("host", ""))
        port = int(route.get("port", 22) or 22)
        start = time.time()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        status = "OK"
        try:
            client.connect(host, port=port, username=user, password=password or None, timeout=10)
        except Exception as exc:
            status = type(exc).__name__
        finally:
            client.close()
        results.append((host, port, round(time.time() - start, 3), status))
    return sorted(results, key=lambda row: row[2])
