"""M4 loop v7 (regulasi densitas) — mini e2e deterministik."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_m4_loop7_mini_deterministic(engine_bin, tmp_path):
    out1 = tmp_path / "run1"
    r1 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m4" / "loop7.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out1)],
        capture_output=True, text=True, timeout=3600)
    assert r1.returncode == 0, f"mini gagal:\n{r1.stdout}\n{r1.stderr}"
    res1 = (out1 / "result_loop7.json").read_bytes()
    res = json.loads(res1)
    assert "W3v7a_density_control" in res["criteria"]
    assert len(res["rows"]) == 7
    for row in res["rows"]:
        assert row["injected"]["mass_added"] == row["injected"]["mass_added"]
        assert row["injected"]["J"] is not None
    out2 = tmp_path / "run2"
    r2 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m4" / "loop7.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out2)],
        capture_output=True, text=True, timeout=3600)
    assert r2.returncode == 0
    assert (out2 / "result_loop7.json").read_bytes() == res1, "tidak deterministik"
