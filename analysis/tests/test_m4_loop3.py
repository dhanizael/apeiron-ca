"""M4 loop v3 (penghindar-fixed-point) — mini e2e deterministik + struktur keputusan."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca  # noqa: E402
from loop3 import legal_moves  # noqa: E402


def _run(outdir, engine_bin):
    return subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m4" / "loop3.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(outdir)],
        capture_output=True, text=True, timeout=3600,
    )


def test_legal_moves():
    F0 = list(Path(ROOT, "experiments/m1v2/result/_work/rule_H_RICH_5700010.bin").read_bytes())
    up = [(e, 1) for e in range(64) if F0[e] < ca.cap_of(e, 2)]
    dn = [(e, -1) for e in range(64) if F0[e] > 0]
    assert legal_moves(F0, 2) == sorted(up + dn)
    assert (24, 1) in up and (12, 1) in up          # longgar: 0<cap, 2<cap=3
    assert (12, -1) in dn                            # entri aktif bisa diturunkan
    assert all(F0[e] + d >= 0 for e, d in legal_moves(F0, 2))


def test_m4_loop3_mini_deterministic(engine_bin, tmp_path):
    out1 = tmp_path / "run1"
    r1 = _run(out1, engine_bin)
    assert r1.returncode == 0, f"mini gagal:\n{r1.stdout}\n{r1.stderr}"
    res1 = (out1 / "result.json").read_bytes()
    res = json.loads(res1)
    assert set(res["criteria"]) == {"W3v3a_feedback_never_freezes",
                                    "W3v3b_cumulative_performance"}
    assert res["iterations"] == 2 and len(res["trajectory"]) == 2
    for it in res["trajectory"]:
        c = it["decision"]
        assert c["hold"] == (len(c["committed"]) == 0)
        if not c["hold"]:
            assert all(cand["short_class"] in ("raise", "flat", "drop")
                       for cand in c["committed"]) or c["committed"]
            assert c["cocktail_trail"], "jejak validasi koktail wajib ada"
        assert it["intervention"]["m"] == len(c["committed"])
        assert not (set(c2["entry"] for c2 in c["committed"]) & set(it["intervention"]["control"]))
        assert it["feedback"]["delta_paired"] is not None
        assert it["control"]["delta_paired"] is not None

    out2 = tmp_path / "run2"
    r2 = _run(out2, engine_bin)
    assert r2.returncode == 0
    assert (out2 / "result.json").read_bytes() == res1, "hasil mini tidak deterministik"
