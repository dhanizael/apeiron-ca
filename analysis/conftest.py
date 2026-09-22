import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))


@pytest.fixture(scope="session")
def engine_bin() -> str:
    env = os.environ.get("ENGINE_BIN")
    if env:
        return env
    binp = ROOT / "engine" / "target" / "release" / "engine"
    if not binp.exists():
        subprocess.run(["cargo", "build", "--release", "-q"], cwd=ROOT / "engine", check=True)
    assert binp.exists(), "engine belum dibangun: jalankan cargo build --release"
    return str(binp)
