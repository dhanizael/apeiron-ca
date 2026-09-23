"""M4 loop v4 (multi-rezim) — mini e2e deterministik + struktur keputusan."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run(outdir, engine_bin):
    return subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m4" / "loop4.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(outdir)],
        capture_output=True, text=True, timeout=3600,
    )


def test_m4_loop4_mini_deterministic(engine_bin, tmp_path):
    out1 = tmp_path / "run1"
    r1 = _run(out1, engine_bin)
    assert r1.returncode == 0, f"mini gagal:\n{r1.stdout}\n{r1.stderr}"
    res1 = (out1 / "result.json").read_bytes()
    res = json.loads(res1)
    assert set(res["criteria"]) == {"W3v4a_multi_regime_repair",
                                    "W3v4b_multi_regime_performance"}
    assert res["iterations"] == 2 and len(res["trajectory"]) == 2
    for it in res["trajectory"]:
        d, iv = it["decision"], it["intervention"]
        assert d["hold"] == (len(d["committed"]) == 0)
        if not d["hold"]:
            assert d["cocktail_trail"], "jejak validasi koktail wajib ada"
            assert all(c["score"] > 0 for c in d["committed"])
        assert iv["m"] == len(d["committed"])
        tgt_e = {e for e, _ in iv["targeted"]}
        ctl_e = {e for e, _ in iv["control"]}
        assert not (tgt_e & ctl_e), "kontrol tidak disjoint dari terarah"
        # j_by_cap kedua rezim tercatat untuk fb dan ctrl
        assert set(it["feedback"]["j_by_cap"]) == {"1", "3"}
        assert set(it["control"]["j_by_cap"]) == {"1", "3"}
        # short dua rezim pada keputusan
        assert set(d["j_parent_short"]) == {"1", "3"}
    # sum per rezim tercatat (atribusi komponen — pelajaran 009)
    assert set(res["sum_j_by_regime"]["feedback"]) == {"1", "3"}

    out2 = tmp_path / "run2"
    r2 = _run(out2, engine_bin)
    assert r2.returncode == 0
    assert (out2 / "result.json").read_bytes() == res1, "hasil mini tidak deterministik"
