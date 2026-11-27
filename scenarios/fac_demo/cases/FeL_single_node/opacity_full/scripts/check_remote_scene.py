"""Check whether the HPC wrapper scene exists on the remote deployment."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scenarios.run.remote.session import RemoteSession

PATH = "/publicfs01/fs1-e/home/scfa2696/QC/fac/fac/scenarios/fac_demo/cases/FeL_opacity_full/run.py"

with RemoteSession("specx", "flash_ssh") as session:
    rc, out, err = session.exec("test -f %s && echo yes || echo no" % PATH, timeout=60)
    print("rc=%s out=%s err=%s" % (rc, out.strip(), err.strip()))
