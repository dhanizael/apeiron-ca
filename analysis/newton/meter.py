"""Meter T1 (spec §7 Tiang 1): kurva (waktu semesta, bit model terbaik Newton).

Ini adalah angka pertama proyek — open-endedness didefinisikan operasional
sebagai pertumbuhan persisten kurva ini. LM0 hanya emit; M4 yang membaca.
"""


def log(entries: list[dict]) -> list[dict]:
    curve = []
    for e in entries:
        if not {"t", "bits", "what"} <= set(e):
            raise ValueError(f"entri meter malformed: {e}")
        curve.append({"t": e["t"], "bits": e["bits"], "what": e["what"]})
    curve.sort(key=lambda e: e["t"])
    return curve
