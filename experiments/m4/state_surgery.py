"""Operasi ruang-keadaan (loop v7, log 013): penulis snapshot + suntik massa.

Intervensi RUANG-KEADAAN: hukum utuh, keadaan diedit (suntik massa) lalu
dilanjutkan via engine --init-state. Penulis snapshot = mirror format v2
(header 36 byte + fnv1a over LE-words — mirror lattice.rs). Validasi kekuatan:
engine wajib menerbaca tulisan kita (checksum cocok).
"""
import struct
from pathlib import Path

MAGIC = 0x30444E31304C4D30
MASK64 = (1 << 64) - 1


def fnv1a_words(words):
    """Mirror lattice::World::fnv1a — FNV-1a over LE bytes tiap word."""
    h = 0xCBF29CE484222325
    for w in words:
        for b in w.to_bytes(8, "little"):
            h ^= b
            h = (h * 0x100000001B3) & MASK64
    return h


def pack_words(cells, k):
    """Cell i di bit [i·k, (i+1)·k) → daftar word u64 (LE)."""
    big = 0
    for i, v in enumerate(cells):
        big |= (v & ((1 << k) - 1)) << (i * k)
    nw = (len(cells) * k + 63) // 64
    return [(big >> (64 * j)) & MASK64 for j in range(nw)]


def unpack_words(words, n, k):
    mask = (1 << k) - 1
    big = 0
    for w in reversed(words):
        big = (big << 64) | w
    return [(big >> (i * k)) & mask for i in range(n)]


def write_snapshot(path, cells, k, rule_id=0, step=0):
    words = pack_words(cells, k)
    fnv = fnv1a_words(words)
    b = struct.pack("<QHBBIIQQ", MAGIC, 2, k, 0, rule_id, len(cells), step, fnv)
    b += b"".join(w.to_bytes(8, "little") for w in words)
    Path(path).write_bytes(b)
    return fnv


def read_state(path, n, k):
    """Baca snapshot (validasi header) → cells."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "analysis"))
    from semesta import io as sio
    snap = sio.read_snapshot(path)
    assert snap["n"] == n and snap["k"] == k, "snapshot mismatch"
    return unpack_words(list(snap_words(snap)), n, k)


def snap_words(snap):
    """words dari hasil io.read_snapshot (state big-int → words)."""
    big = snap["state"]
    nw = (snap["n"] * snap["k"] + 63) // 64
    return [(big >> (64 * j)) & MASK64 for j in range(nw)]


def mass(cells):
    return sum(cells)


def inject_uniform(cells, mass_add, cap=2, seed=0):
    """Suntik buta: +1 pada sel acak bernilai < cap (kebijakan cap-2
    anti-parkir). Deterministik via ca.Rng."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "analysis"))
    from semesta import ca
    rng = ca.Rng(seed)
    c = list(cells)
    added = 0
    guard = 0
    while added < mass_add and guard < 50 * len(c) * cap:
        guard += 1
        i = rng.next_u64() % len(c)
        if c[i] < cap:
            c[i] += 1
            added += 1
    return c, added


def inject_lane(cells, mass_add, cap=2):
    """Suntik turunan-temuan (012): prioritas sel-1 yang kiri-nya 1
    (→ konfigurasi (1,2,·) emisi-penuh), lalu sel-0 dengan kiri-1 (→(1,1,·)),
    lalu uniform-cap2. Deterministik (urutan index)."""
    c = list(cells)
    n = len(c)

    def left(i):
        return c[(i - 1) % n]

    added = 0
    for phase in (
        [i for i in range(n) if c[i] == 1 and left(i) == 1],
        [i for i in range(n) if c[i] == 0 and left(i) == 1],
    ):
        for i in phase:
            if added >= mass_add:
                return c, added
            if c[i] < cap:
                c[i] += 1
                added += 1
    if added < mass_add:
        c2, added2 = inject_uniform(c, mass_add - added, cap)
        return c2, added + added2
    return c, added
