"""Baseline lanskap kesehatan (v5) — metrik health + rekonstruksi silsilah."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca  # noqa: E402
from health_landscape import health_from_states, load_baseline_laws  # noqa: E402


def test_health_from_states():
    s = [1, 2, 0, 3]
    mov = [[1, 2, 0, 3], [0, 2, 1, 3], [0, 2, 1, 3]]  # berubah lalu diam
    h = health_from_states(mov, 2)
    assert h["flowing"] is True and h["mobility"] > 0
    frozen = [list(s)] * 5
    h2 = health_from_states(frozen, 2)
    assert h2["flowing"] is False and h2["mobility"] == 0.0
    # J terukur pada state diam: semua d=0 → f=0 (bila ada ref)
    assert h2["J"] == 0.0


def test_baseline_lineage():
    """4 hukum baseline ter-rekonstruksi dengan FNV terverifikasi."""
    laws = load_baseline_laws()
    assert set(laws) == {"F0", "cocktail20", "v3_final", "v4_final"}
    assert f"{ca.table_fnv(laws['F0']):016x}" == "85eba35fbd113e83"
    assert f"{ca.table_fnv(laws['v4_final']):016x}" == "5413597c82d83c83"
    # cocktail20 dipatok tanda tangan J log 007 (seed 1093: cap1 0.5042, cap3 1.4870)
    assert laws["cocktail20"] != laws["F0"]
    assert laws["v3_final"] != laws["v4_final"]
