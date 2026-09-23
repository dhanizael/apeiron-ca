"""M4 loop v6 (map-guided + dedup) — mini e2e deterministik."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run(outdir, engine_bin):
    return subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m4" / "loop6.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(outdir)],
        capture_output=True, text=True, timeout=3600,
    )


def test_m4_loop6_mini_deterministic(engine_bin, tmp_path):
    out1 = tmp_path / "run1"
    r1 = _run(out1, engine_bin)
    assert r1.returncode == 0, f"mini gagal:\n{r1.stdout}\n{r1.stderr}"
    res1 = (out1 / "result_loop6.json").read_bytes()
    res = json.loads(res1)
    assert set(res["criteria"]) == {"W3v6a_escape_or_ceiling"}
    assert len(res["trajectory"]) == 2
    for it in res["trajectory"]:
        # dedup: tak ada entri ganda dalam seleksi
        entries = [e for e, _d, _s in it["selected"]]
        assert len(entries) == len(set(entries))
        # setiap koktail yang dikomit wajib safe + joint > 0
        for c in it["cocktails"]:
            if c["commit"]:
                assert c["safe"] and c["joint"] > 0
    # verdict self-calibrating: incumben & final di blok sama + free-flow bound
    v = res["verdict"]
    assert set(v["incumbent"]) >= {"cap1_rate", "cap3_rate", "cap1_mean_J", "cap3_mean_mob"}
    assert "free_flow_bound" in v and "mass_over_n" in v["free_flow_bound"]["final"]

    out2 = tmp_path / "run2"
    r2 = _run(out2, engine_bin)
    assert r2.returncode == 0
    assert (out2 / "result_loop6.json").read_bytes() == res1, "hasil mini tidak deterministik"
