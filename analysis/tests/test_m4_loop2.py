"""M4 loop v2 (W3 round-2 di semesta RICH) — mini e2e + determinisme + tuas.

Kontrak (plan 2026-09-22-w3-round2-loop-v2.md):
- K1: mini e2e hijau, deterministik byte-identik dua run.
- K2: tuas turun dari temuan — target terarah = entri longgar tersibuk dari
  stats Newton; kontrol disjoint dari terarah.
- K3: atribusi per iterasi: j_by_cap tercatat (efek di rezim linier harus
  > efek rezim jenuh bila mekanisme capacity-bound berlaku).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run(outdir, engine_bin):
    return subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "m4" / "loop2.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(outdir)],
        capture_output=True, text=True, timeout=1200,
    )


def test_m4_loop2_mini_deterministic(engine_bin, tmp_path):
    out1 = tmp_path / "run1"
    r1 = _run(out1, engine_bin)
    assert r1.returncode == 0, f"mini gagal:\n{r1.stdout}\n{r1.stderr}"
    res1 = (out1 / "result.json").read_bytes()
    res = json.loads(res1)
    assert "W3v2_feedback_directed_effect_rich" in res["criteria"]
    assert res["iterations"] == 2
    assert len(res["trajectory"]) == 2
    for it in res["trajectory"]:
        assert set(map(int, it["feedback"]["j_by_cap"])) >= {it["effect_cap"]}
        assert it["feedback"]["delta_paired"] is not None
        assert it["control"]["delta_paired"] is not None

    out2 = tmp_path / "run2"
    r2 = _run(out2, engine_bin)
    assert r2.returncode == 0
    assert (out2 / "result.json").read_bytes() == res1, "hasil mini tidak deterministik"


def test_m4_loop2_lever_is_finding_derived_and_control_disjoint(engine_bin, tmp_path):
    """Tuas harus turun dari temuan: target terarah dari stats longgar
    tersibuk; kontrol acak DISJOINT dari terarah."""
    out = tmp_path / "lever"
    r = _run(out, engine_bin)
    assert r.returncode == 0, r.stderr
    res = json.loads((out / "result.json").read_text())
    for it in res["trajectory"]:
        tgt = it["intervention"]["targeted"]
        ctl = it["intervention"]["control"]
        assert len(tgt) == len(ctl) > 0
        assert not (set(tgt) & set(ctl)), "kontrol tidak disjoint dari terarah"
        # longgar: stats slack entri target > 0 pada observasi induk
        slack = it["observation"]["parent_stats_slack"]
        assert all(slack[e] > 0 for e in tgt), "target bukan entri longgar"
