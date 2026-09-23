"""MIGRASI-K (loop v8, log 014): angkat hukum & state k=2 → k=4.

Phase-wrap lift: F_k4[l,c,r] = F_k2[l&3,c&3,r&3] (r&3 ≠ 3);
F_k4[l,c,r] = F_k2[l&3,c&3,0] (r&3 = 3, r < 15 — penerimaan fase-bungkus);
F_k4[l,c,15] = 0 (penuh — struktural). Embedding murni (tanpa receipt) =
lengan kontrol. Kapasitas-aman diverifikasi: semua F ≤ min(c, 15−r).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from state_surgery import pack_words, unpack_words, write_snapshot  # noqa: E402

K2, K4 = 2, 4


def lift_law(f2, receipt=True):
    """64 entri k=2 → 4096 entri k=4 (phase-wrap bila receipt, else embedding)."""
    assert len(f2) == 1 << (3 * K2)
    f4 = [0] * (1 << (3 * K4))
    for idx in range(1 << (3 * K4)):
        l, c, r = idx >> 8, (idx >> 4) & 15, idx & 15
        if r == 15:
            f4[idx] = 0
        elif (r & 3) == 3 and receipt:
            f4[idx] = f2[((l & 3) << 4) | ((c & 3) << 2) | 0]
        else:
            f4[idx] = f2[((l & 3) << 4) | ((c & 3) << 2) | (r & 3)]
    return f4


def capacity_ok(f4):
    """Semua entri ≤ min(c, 15−r) — syarat konservasi keluarga flow."""
    for idx, v in enumerate(f4):
        c, r = (idx >> 4) & 15, idx & 15
        if v > min(c, 15 - r):
            return False
    return True


def embedding_matches(f2, f4):
    """Verifikasi: pada r&3 ≠ 3, lift = embedding eksak."""
    for idx in range(1 << (3 * K4)):
        l, c, r = idx >> 8, (idx >> 4) & 15, idx & 15
        if (r & 3) != 3:
            if f4[idx] != f2[((l & 3) << 4) | ((c & 3) << 2) | (r & 3)]:
                return False
    return True


def lift_state(cells, k_from=K2, k_to=K4):
    """Migrasi state: nilai sel sama, sel lebih lebar (massa eksak sama)."""
    assert k_to > k_from
    for v in cells:
        assert 0 <= v < (1 << k_from), "nilai di luar rentang sumber"
    return list(cells)  # nilai sama; lebar sel berubah saat pack


def write_state(path, cells, k):
    return write_snapshot(path, cells, k)


def read_state_cells(path, n, k):
    """Baca snapshot engine → cells (via state_surgery.unpack_words)."""
    sys.path.insert(0, str(ROOT / "analysis"))
    from semesta import io as sio
    snap = sio.read_snapshot(path)
    assert snap["n"] == n and snap["k"] == k, "snapshot mismatch"
    nw = (n * k + 63) // 64
    big = snap["state"]
    words = [(big >> (64 * j)) & ((1 << 64) - 1) for j in range(nw)]
    return unpack_words(words, n, k)
