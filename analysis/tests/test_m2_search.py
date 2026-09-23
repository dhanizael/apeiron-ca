"""M2 search — event definition + kalibrasi aljabar (fisika di skrip)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "m2"))

from m2_search import event_of


def test_event_of():
    assert event_of([1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2])["sustained"] is True
    assert event_of([1, 2, 1, 1, 1])["sustained"] is False  # transien
    assert event_of([1, 1, 1, 1]) is None                    # tak pernah naik
    assert event_of([2, 2, 2]) is None                       # awal bukan 1 copy
    ev = event_of([1, 0, 2, 2, 2])                          # naik transien (list pendek)
    assert ev is not None and ev["sustained"] is False
    # catatan: c2[0]=1 dibutuhkan; pola lenyap lalu muncul = bukan event beku
