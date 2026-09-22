"""Anatomi fixed point (log 007 pertanyaan 8) — invarian, struktur, waktu-beku."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca  # noqa: E402
from frozen_anatomy import anatomy, crystal_state, freeze_time_search, is_static  # noqa: E402

F0 = list(Path(ROOT, "experiments/m1v2/result/_work/rule_H_RICH_5700010.bin").read_bytes())


def test_anatomy_of_synthetic_crystal():
    """Kristal {0,2} tanpa tetangga 2-2: fixed point eksak di bawah F0 —
    semua entri terrealisasi (8, 34) bernilai 0 → invarian beku terpenuhi."""
    k, n = 2, 64
    state = crystal_state(n)
    a = anatomy([state], F0, k, f0_table=F0)
    assert a["all_realized_zero_in_law"] is True
    assert a["cell_histogram"]["2"] == n // 2
    assert a["all_realized_zero_in_f0"] is True
    realized = {e["entry"] for e in a["realized_entries"]}
    assert realized == {8, 34}, realized  # (0,2,0) dan (2,0,2)
    assert a["rho"] > 0.30 and a["rho"] < 0.36


def test_is_static():
    s = [1, 2, 0, 3]
    assert is_static([s, list(s), list(s)])
    assert not is_static([s, [0, 0, 0, 0], list(s)])


def test_freeze_time_search_bracket():
    """Logika bracket: fnv(t) == target mulai t>=5000 → beku pada (2500, 5000]."""
    calls = []

    def fake_run(steps):
        calls.append(steps)
        return "AAA" if steps >= 5000 else "BBB"

    out = freeze_time_search(fake_run, t_final=20000, grid=[1250, 2500, 5000, 10000])
    assert out["t_below"] == 2500 and out["t_at"] == 5000
    assert out["frozen_window"] == "(2500, 5000]"
    assert 20000 in calls  # target direkonstruksi sendiri
