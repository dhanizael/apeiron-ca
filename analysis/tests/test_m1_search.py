"""M1 search harness — mini end-to-end + determinisme byte-per-byte."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_m1_mini_pipeline_deterministic(engine_bin, tmp_path):
    out1 = tmp_path / "run1"
    r1 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m1" / "search.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out1)],
        capture_output=True, text=True, timeout=1200,
    )
    assert r1.returncode == 0, f"mini gagal:\n{r1.stdout}\n{r1.stderr}"
    res1 = (out1 / "result.json").read_bytes()

    res = json.loads(res1)
    assert res["experiment"] == "M1"
    assert res["stages"]["a"]["n_candidates"] == 200
    assert set(res["baselines"]) == {"sandpile_k2", "layer184_k2"}
    assert "K3_particle_persistent_and_no_exclusion" in res["criteria"]
    assert "reproduce" in res
    # distribusi penuh dilaporkan
    lines = (out1 / "results.jsonl").read_text().strip().split("\n")
    assert len(lines) == 200
    assert all(json.loads(l)["stage"] == "A" for l in lines)

    # determinisme: run kedua identik byte-per-byte
    out2 = tmp_path / "run2"
    r2 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m1" / "search.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out2)],
        capture_output=True, text=True, timeout=1200,
    )
    assert r2.returncode == 0
    assert (out2 / "result.json").read_bytes() == res1, "hasil mini tidak deterministik"
