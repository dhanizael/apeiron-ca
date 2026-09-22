"""LM-1 end-to-end versi mini — loop penuh hidup: engine→Newton→oracle→meter."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_lm1_mini_pass(engine_bin, tmp_path):
    out = tmp_path / "lm1"
    r = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "lm1" / "run_lm1.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out)],
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"LM-1 mini gagal:\n{r.stdout}\n{r.stderr}"
    res = json.loads((out / "result.json").read_text())
    assert res["criteria"]["1_micro_exact"] is True
    assert res["criteria"]["2_macro_mae_lt_eps"] is True
    assert res["criteria"]["3_meter_emits"] is True
    assert res["micro"]["ground_truth"] == 184
