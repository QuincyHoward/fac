"""Cancel an HPC job by ID using configured credentials."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scenarios.run.remote.session import RemoteSession  # noqa: E402

job = sys.argv[1] if len(sys.argv) > 1 else ""
if not job:
    raise SystemExit("usage: cancel_hpc_job.py <job_id>")

with RemoteSession("specx", "flash_ssh") as session:
    rc, out, err = session.exec("scancel %s" % job, timeout=60)
    print("rc=%s out=%s err=%s" % (rc, out.strip(), err.strip()))
