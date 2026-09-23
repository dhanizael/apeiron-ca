"""Sweep melt (Part B v4) — logika dinding & policy (fisika diuji di skrip)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca  # noqa: E402
from sweep_melt import melt_table, walls_from_state  # noqa: E402

F0 = list(Path(ROOT, "experiments/m1v2/result/_work/rule_H_RICH_5700010.bin").read_bytes())


def test_walls_from_state_crystal():
    """Kristal sintetis {0,2} tanpa 2-2: dinding = entri (0,2,0)=8 SAJA —
    (2,0,2)=34 terrealisasi tapi c=0 ⟹ cap=0 (sel kosong tak bisa memancar:
    hukum struktural r=max/c=0 ⟹ F≡0)."""
    k = 2
    s = [2 if i % 2 == 0 else 0 for i in range(64)]
    w = walls_from_state(s, k)
    assert set(w) == {8}
    assert w[8] == 32


def test_melt_table_clip():
    T = melt_table(F0, [24, 12])
    assert T[24] == F0[24] + 1
    assert T[12] == F0[12] + 1
    # entri di cap tidak berubah (clip)
    at_cap = [e for e in range(64) if F0[e] > 0 and F0[e] == ca.cap_of(e, 2)]
    for e in at_cap:
        T2 = melt_table(F0, [e])
        assert T2[e] == F0[e], f"clip dilanggar di {e}"
