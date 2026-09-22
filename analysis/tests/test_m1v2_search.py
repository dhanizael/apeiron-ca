"""M1v2 dua lengan — mini end-to-end + determinisme (verdict hipotesis apa adanya)."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_m1v2_mini_deterministic(engine_bin, tmp_path):
    out1 = tmp_path / "run1"
    r1 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m1v2" / "search.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out1)],
        capture_output=True, text=True, timeout=1200,
    )
    assert r1.returncode == 0, f"mini gagal:\n{r1.stdout}\n{r1.stderr}"
    res1 = (out1 / "result.json").read_bytes()
    res = json.loads(res1)
    assert set(res["criteria"]) == {"V1_champions_both_arms_at_horizon", "V2_slack_hypothesis"}
    assert res["pass_rates"]["POOR"] is not None and res["pass_rates"]["RICH"] is not None
    lines = (out1 / "results.jsonl").read_text().strip().split("\n")
    assert len(lines) == 80  # 40 per arm

    out2 = tmp_path / "run2"
    r2 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m1v2" / "search.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out2)],
        capture_output=True, text=True, timeout=1200,
    )
    assert r2.returncode == 0
    assert (out2 / "result.json").read_bytes() == res1, "tidak deterministik"
