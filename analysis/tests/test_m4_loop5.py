"""M4 loop v5 (robust-health) — mini e2e deterministik + kebijakan baru."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run(outdir, engine_bin):
    return subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m4" / "loop5.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(outdir)],
        capture_output=True, text=True, timeout=3600,
    )


def test_m4_loop5_mini_deterministic(engine_bin, tmp_path):
    out1 = tmp_path / "run1"
    r1 = _run(out1, engine_bin)
    assert r1.returncode == 0, f"mini gagal:\n{r1.stdout}\n{r1.stderr}"
    res1 = (out1 / "result_loop5.json").read_bytes()
    res = json.loads(res1)
    assert set(res["criteria"]) == {"W3v5a_robust_multi_regime_health",
                                    "W3v5b_multi_regime_performance"}
    assert res["iterations"] == 2 and len(res["trajectory"]) == 2
    for it in res["trajectory"]:
        d, iv = it["decision"], it["intervention"]
        assert d["hold"] == (len(d["committed"]) == 0)
        if not d["hold"]:
            # KEBIJAKAN BARU: koktail yang dikomit wajib safe DAN skor > 0
            ok_trail = [t for t in d["cocktail_trail"] if t["safe"]]
            assert ok_trail and all(t["joint_score"] > 0 for t in ok_trail)
            assert all(c["score"] > 0 for c in d["committed"])
        # health cap3 multi-seed tercatat di keputusan dan pengukuran penuh
        assert len(d["j_parent_short"]["cap3_health"]) == d["cap3_seeds"]
        assert len(it["feedback"]["cap3_health"]) == d["cap3_seeds"]
        assert len(it["control"]["cap3_health"]) == d["cap3_seeds"]
        tgt_e = {e for e, _ in iv["targeted"]}
        ctl_e = {e for e, _ in iv["control"]}
        assert not (tgt_e & ctl_e)
    # verdict 7-seed pada hukum final tercatat
    assert len(res["final_verdict"]["seeds"]) == 7
    assert "cap1_rate" in res["final_verdict"] and "cap3_rate" in res["final_verdict"]

    out2 = tmp_path / "run2"
    r2 = _run(out2, engine_bin)
    assert r2.returncode == 0
    assert (out2 / "result_loop5.json").read_bytes() == res1, "hasil mini tidak deterministik"
