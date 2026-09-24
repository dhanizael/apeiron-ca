"""M2 census — definisi operasional replikasi (terbekukan log 015)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "m2"))

from census import count_copies, plant_state, replication_event


def test_count_copies():
    states = [[0, 1, 2, 0, 1, 2, 0, 0]]  # pola [1,2] muncul 2 kali
    assert count_copies(states, [1, 2]) == [2]
    assert count_copies(states, [1, 2, 0, 0, 1]) == [0]
    # wraparound: [0,1][0,0,1,2] → pola [2,0,1] melintasi ujung? ring: terakhir 0, pertama 0 → [2,0,0]... cek manual
    assert count_copies([[1, 0, 0, 1]], [1, 0, 0, 1]) == [1]


def test_replication_event_definition():
    # 1 copy → naik 2 → bertahan
    c = [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    ev = replication_event(c)
    assert ev is not None and ev.get("sustained", True) and ev["peak"] >= 2
    # transien: naik lalu turun
    c2 = [1, 2, 1, 1, 1]
    ev2 = replication_event(c2)
    assert ev2 is not None and ev2.get("sustained") is False
    # tak pernah naik
    assert replication_event([1, 1, 1, 1]) is None
    # awal bukan 1 copy → bukan event
    assert replication_event([2, 2, 2]) is None


def test_plant_state():
    cells = plant_state([0] * 64, [2, 2, 2], bg_ones=6, seed=3)
    assert cells[:3] == [2, 2, 2]
    assert sum(1 for v in cells if v == 1) == 6
    assert sum(cells) == 6 + 6
