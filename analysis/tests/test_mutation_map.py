"""Peta mutasi (v6) — silsilah incumben + dedup satu-arah-terbaik."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca  # noqa: E402
from mutation_map import load_v5_final, dedup_best_direction, pearson  # noqa: E402


def test_v5_final_lineage():
    F = load_v5_final()
    assert f"{ca.table_fnv(F):016x}" == "ee65c75045c607ad"


def test_dedup_best_direction():
    moves = [(25, 1, 0.9), (25, -1, 0.7), (12, -1, 0.5), (12, 1, 0.2), (8, 1, 0.1)]
    out = dedup_best_direction(moves)
    assert sorted(out) == [(8, 1, 0.1), (12, -1, 0.5), (25, 1, 0.9)]


def test_pearson():
    xs = [1, 2, 3, 4, 5]
    assert pearson(xs, [2, 4, 6, 8, 10]) > 0.99
    assert abs(pearson(xs, [5, 4, 3, 2, 1]) + 1.0) < 1e-9
    assert abs(pearson(xs, [3, 3, 3, 3, 3])) < 1e-9  # konstanta → 0
