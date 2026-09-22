"""M4 growth meter — mini end-to-end + determinisme (K5 terukur)."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_m4_mini_growth_deterministic(engine_bin, tmp_path):
    out1 = tmp_path / "run1"
    r1 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m4" / "growth.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out1)],
        capture_output=True, text=True, timeout=1200,
    )
    assert r1.returncode == 0, f"mini gagal:\n{r1.stdout}\n{r1.stderr}"
    res1 = (out1 / "result.json").read_bytes()
    res = json.loads(res1)
    assert res["criteria"]["K5_curve_measured"] is True
    assert len(res["regimes_measured"]) == 2
    for name, pts in res["curves"].items():
        assert len(pts) == 2
        assert all(p["model_bits"] >= 0 for p in pts)
        assert all(p["compressed"] > 0 for p in pts)
    assert "reading" in res and res["reading"]

    out2 = tmp_path / "run2"
    r2 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m4" / "growth.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out2)],
        capture_output=True, text=True, timeout=1200,
    )
    assert r2.returncode == 0
    assert (out2 / "result.json").read_bytes() == res1, "hasil mini tidak deterministik"
