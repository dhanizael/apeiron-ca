"""M4 loop v8 (migrasi-k) — mini e2e deterministik."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_m4_loop8_mini_deterministic(engine_bin, tmp_path):
    out1 = tmp_path / "run1"
    r1 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m4" / "loop8.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out1)],
        capture_output=True, text=True, timeout=3600)
    assert r1.returncode == 0, f"mini gagal:\n{r1.stdout}\n{r1.stderr}"
    res1 = (out1 / "result_loop8.json").read_bytes()
    res = json.loads(res1)
    assert set(res["criteria"]) >= {"W3v8a_migration_intact", "W3v8b_new_strata"}
    assert len(res["rows"]) == 2
    for row in res["rows"]:
        assert row["receipt"]["full"]["mass"] == row["mass_source"]
        assert row["embedding"]["full"]["mass"] == row["mass_source"]
    assert "control_embedding_summary" in res
    out2 = tmp_path / "run2"
    r2 = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m4" / "loop8.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out2)],
        capture_output=True, text=True, timeout=3600)
    assert r2.returncode == 0
    assert (out2 / "result_loop8.json").read_bytes() == res1, "tidak deterministik"
