"""Assemble full-physics stage outputs into one remote build output directory."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scenarios.run.remote.session import RemoteSession  # noqa: E402

JOBS = "/publicfs01/fs1-e/home/scfa2696/QC/fac_jobs"
CRM = JOBS + "/ofull_crm_v3/archive/opacity_full_outputs"
PIDENSE = JOBS + "/ofull_pidense_v5/archive/opacity_full_outputs"
AIDR = JOBS + "/ofull_aidr_v4/archive/opacity_full_outputs"
BUILD = JOBS + "/ofull_build/archive/opacity_full_outputs"

COMMANDS = [
    "mkdir -p %s/dense_pi %s/resonances %s/crm_pop/Fe08 %s/crm_pop/Fe09 %s/crm_pop/Fe10" % (BUILD, BUILD, BUILD, BUILD, BUILD),
    "cp -f %s/dense_pi/*.csv %s/dense_pi/ 2>/dev/null || true" % (PIDENSE, BUILD),
    "cp -f %s/resonances/*.csv %s/resonances/ 2>/dev/null || true" % (AIDR, BUILD),
    "cp -f %s/resonances/manifest.json %s/resonances/ 2>/dev/null || true" % (AIDR, BUILD),
    "cp -f %s/dense_pi/manifest.json %s/dense_pi/ 2>/dev/null || true" % (PIDENSE, BUILD),
    "cp -a %s/crm_pop/Fe08/. %s/crm_pop/Fe08/ 2>/dev/null || true" % (CRM, BUILD),
    "cp -a %s/crm_pop/Fe09/. %s/crm_pop/Fe09/ 2>/dev/null || true" % (CRM, BUILD),
    "cp -a %s/crm_pop/Fe10/. %s/crm_pop/Fe10/ 2>/dev/null || true" % (CRM, BUILD),
    "find %s -maxdepth 3 -type f | wc -l" % BUILD,
]

with RemoteSession("specx", "flash_ssh") as session:
    for command in COMMANDS:
        rc, out, err = session.exec(command, timeout=600)
        print(command)
        if out.strip():
            print(out.strip())
        if rc != 0:
            print("ERR", err.strip())
