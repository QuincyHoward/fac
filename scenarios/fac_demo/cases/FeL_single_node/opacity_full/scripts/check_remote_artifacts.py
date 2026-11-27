"""Check remote paths needed by the full-physics opacity stages."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scenarios.run.remote.session import RemoteSession

BASE = "/publicfs01/fs1-e/home/scfa2696/QC/fac_jobs/FeL_single_node_c24m16/work/run"
PATHS = [
    BASE + "/data/Fe08a.rr",
    BASE + "/data/Fe08b.rr",
    BASE + "/data/Fe08b.en",
    BASE + "/data/Fe08a.tr",
    BASE + "/data/Fe08a.ai",
    BASE + "/Fe08/Fe08a_t00d0i3.sp",
    BASE + "/plots_inputs/temperatures.csv",
    BASE + "/plots_inputs/abund.csv",
]

with RemoteSession("specx", "flash_ssh") as session:
    for path in PATHS:
        rc, out, err = session.exec("test -f %s && echo yes || echo no" % path, timeout=60)
        print("%s\t%s" % (out.strip() or "no", path))
