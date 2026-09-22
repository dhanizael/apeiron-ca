"""M3 recovery — mini end-to-end + determinisme."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_m3_mini_pipeline_deterministic(engine_bin, tmp_path):
    out1 = tmp_path / "run1"
    r1 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m3" / "recover.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out1)],
        capture_output=True, text=True, timeout=1200,
    )
    assert r1.returncode == 0, f"mini gagal:\n{r1.stdout}\n{r1.stderr}"
    res1 = (out1 / "result.json").read_bytes()
    res = json.loads(res1)
    # k=2 hand tables: pemulihan pasti eksak → tiga gerbang hijau
    assert res["criteria"]["3a_micro_exact_observed"] is True
    assert res["criteria"]["3b_micro_reproduces_heldout"] is True
    assert res["criteria"]["3c_counterfactual_shift"] is True
    assert res["verdict_micro"] is True
    assert res["criteria"]["macro_heldout_mae_lt_eps"] is None  # mini: makro dilewati

    out2 = tmp_path / "run2"
    r2 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m3" / "recover.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out2)],
        capture_output=True, text=True, timeout=1200,
    )
    assert r2.returncode == 0
    assert (out2 / "result.json").read_bytes() == res1, "hasil mini tidak deterministik"
