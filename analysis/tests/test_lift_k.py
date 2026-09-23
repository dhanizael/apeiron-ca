"""lift_k (v8) — desain phase-wrap, kapasitas, embedding, migrasi state."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from lift_k import (capacity_ok, embedding_matches, lift_law,  # noqa: E402
                    lift_state)
from semesta import ca  # noqa: E402

F2 = list(Path(ROOT, "experiments/m1v2/result/_work/rule_H_RICH_5700010.bin").read_bytes())


def test_lift_law_capacity_and_embedding():
    f4r = lift_law(F2, receipt=True)
    f4e = lift_law(F2, receipt=False)
    assert len(f4r) == 4096 and len(f4e) == 4096
    assert capacity_ok(f4r) and capacity_ok(f4e)
    assert embedding_matches(F2, f4r) and embedding_matches(F2, f4e)
    # fase-bungkus: entri r=3 menerima seperti fase-0 (hanya lengan receipt)
    assert f4r[(0 << 8) | (1 << 4) | 3] == F2[(0 << 4) | (1 << 2) | 0]  # (0,1,3)→(0,1,0)=1
    assert f4e[(0 << 8) | (1 << 4) | 3] == 0
    # sel penuh k=4 tetap 0
    assert all(f4r[idx] == 0 for idx in range(4096) if (idx & 15) == 15)


def test_lift_state_mass_exact():
    cells = [ca.unpack_cells(ca.pack_cells([0, 1, 2, 3] * 4, 2), 16, 2)]
    c = cells[0]
    out = lift_state(c)
    assert out == c and sum(out) == sum(c)  # nilai & massa eksak
