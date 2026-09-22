"""Kalibrasi freeze — logika klasifikasi & gate (fisika diuji di skrip full)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from calibrate_freeze import classify  # noqa: E402


def test_classify():
    assert classify(0.0, 0.25, static=True) == "freeze"
    assert classify(0.0, 0.25, static=False) == "drop"  # J=0 tanpa statis: drop besar
    assert classify(0.10, 0.25, static=False) == "drop"
    assert classify(0.26, 0.25, static=False) == "raise"
    assert classify(0.25, 0.25, static=False) == "flat"
