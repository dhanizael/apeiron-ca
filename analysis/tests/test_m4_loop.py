"""M4 loop — mini end-to-end + determinisme (W3 verdict apa adanya di mini)."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_m4_mini_loop_deterministic(engine_bin, tmp_path):
    out1 = tmp_path / "run1"
    r1 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m4" / "loop.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out1)],
        capture_output=True, text=True, timeout=1200,
    )
    assert r1.returncode == 0, f"mini gagal:\n{r1.stdout}\n{r1.stderr}"
    res1 = (out1 / "result.json").read_bytes()
    res = json.loads(res1)
    assert "W3_feedback_directed_effect" in res["criteria"]
    assert res["iterations"] == 2
    assert len(res["trajectory"]) == 2
    assert res["mean_delta_feedback"] is not None and res["mean_delta_control"] is not None

    out2 = tmp_path / "run2"
    r2 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m4" / "loop.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out2)],
        capture_output=True, text=True, timeout=1200,
    )
    assert r2.returncode == 0
    assert (out2 / "result.json").read_bytes() == res1, "hasil mini tidak deterministik"
