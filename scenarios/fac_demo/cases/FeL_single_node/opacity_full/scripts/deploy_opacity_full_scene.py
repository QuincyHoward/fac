"""Deploy only the opacity_full scene files to the existing HPC FAC tree."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scenarios.run.env.devices import sim_user  # noqa: E402
from scenarios.run.remote.session import RemoteSession  # noqa: E402

LOCAL_BASE = ROOT / "scenarios" / "fac_demo" / "cases"
RELATIVE_FILES = [
    "FeL_opacity_full/scene.json",
    "FeL_opacity_full/run.py",
    "FeL_single_node/opacity_full/scene.json",
    "FeL_single_node/opacity_full/config.json",
    "FeL_single_node/opacity_full/run.py",
    "FeL_single_node/opacity_full/README.md",
    "FeL_single_node/opacity_full/docs/physics_notes.md",
]
RELATIVE_FILES += ["FeL_single_node/opacity_full/scripts/" + p.name for p in (LOCAL_BASE / "FeL_single_node/opacity_full/scripts").glob("*.py")]
RELATIVE_FILES += ["FeL_single_node/opacity_full/plots/" + p.name for p in (LOCAL_BASE / "FeL_single_node/opacity_full/plots").glob("*.py")]

with RemoteSession("specx", "flash_ssh") as session:
    target = "%s/%s/fac/fac/scenarios/fac_demo/cases" % (session.home(), sim_user("specx"))
    for rel in RELATIVE_FILES:
        local = LOCAL_BASE / rel
        remote = target + "/" + rel
        session.mkdir_p(str(Path(remote).parent))
        session.upload(str(local), remote)
        print(rel)
    check = target + "/FeL_opacity_full/run.py"
    rc, out, err = session.exec("test -f %s && echo yes || echo no" % check, timeout=60)
    print("remote_wrapper_exists=%s rc=%s" % (out.strip(), rc))
