"""CA referensi 1D (Python) — implementasi independen dari engine Rust.

Peran: (1) pengujian silang K1 lintas implementasi; (2) generator sintetis tes Newton;
(3) langkah ECA umum untuk verifier mikro Newton. Cell i = bit i.
"""
MASK64 = (1 << 64) - 1


class Rng:
    """xorshift64* — mirror persis engine/src/rng.rs."""

    def __init__(self, seed: int):
        self.s = 0x9E3779B97F4A7C15 if seed == 0 else seed

    def next_u64(self) -> int:
        x = self.s
        x ^= x >> 12
        x ^= (x << 25) & MASK64
        x ^= x >> 27
        self.s = x
        return (x * 0x2545F4914F6CDD1D) & MASK64

    def below(self, bound: int) -> int:
        return self.next_u64() % bound


def from_seed_exact(n: int, cars: int, seed: int) -> int:
    """Mirror lattice::World::from_seed_exact — state awal identik dengan Rust."""
    rng, idx = Rng(seed), list(range(n))
    k = min(cars, n)
    for i in range(k):
        j = i + rng.below(n - i)
        idx[i], idx[j] = idx[j], idx[i]
    state = 0
    for i in idx[:k]:
        state |= 1 << i
    return state


def _rot_left(state: int, n: int, mask: int) -> int:
    # L[i] = state[i-1]
    return ((state << 1) | (state >> (n - 1))) & mask


def _rot_right(state: int, n: int, mask: int) -> int:
    # R[i] = state[i+1]
    return ((state >> 1) | (state << (n - 1))) & mask


def step_rule184(state: int, n: int) -> int:
    mask = (1 << n) - 1
    L, C, R = _rot_left(state, n, mask), state, _rot_right(state, n, mask)
    return (L & R) | (L & ~C & ~R & mask) | (~L & C & R & mask)


def step_rule(state: int, n: int, rule_id: int) -> int:
    """ECA umum (LUT per sel) — lambat; untuk tes & verifier, bukan performa."""
    out = 0
    for i in range(n):
        nb = (
            ((state >> ((i - 1) % n)) & 1) << 2
            | ((state >> i) & 1) << 1
            | ((state >> ((i + 1) % n)) & 1)
        )
        if (rule_id >> nb) & 1:
            out |= 1 << i
    return out


# ---------- k-bit generalisasi (keluarga flow, M0) ----------

def from_seed_uniform(n: int, k: int, seed: int) -> list[int]:
    """Mirror lattice::World::from_seed_uniform — tiap sel uniform [0, 2^k)."""
    rng, mask = Rng(seed), (1 << k) - 1
    return [rng.next_u64() & mask for _ in range(n)]


def random_table(k: int, seed: int) -> list[int]:
    """Mirror flow::FlowRule::random — 2^(3k) entri mentah, satu draw per entri."""
    rng = Rng(seed)
    return [rng.next_u64() & 0xFF for _ in range(1 << (3 * k))]


def clip_table(raw: list[int], k: int) -> list[int]:
    """Mirror flow::FlowRule::from_table — clip per entri: min(raw, c, 2^k−1−r)."""
    mask = (1 << k) - 1
    out = []
    for idx, v in enumerate(raw):
        r = idx & mask
        c = (idx >> k) & mask
        out.append(max(0, min(v, c, mask - r)))
    return out


def table_fnv(table: list[int]) -> int:
    """FNV-1a 64 atas byte tabel (urutan index) — mirror hash::fnv1a_bytes."""
    h = 0xCBF29CE484222325
    for b in table:
        h ^= b
        h = (h * 0x100000001B3) & MASK64
    return h


def pack_cells(cells: list[int], k: int) -> int:
    """Kemas cell list → int bit-packed (cell i di bit [i·k, (i+1)·k))."""
    state = 0
    for i in reversed(range(len(cells))):
        state = (state << k) | (cells[i] & ((1 << k) - 1))
    return state


def step_flow(cells: list[int], k: int, table: list[int]) -> list[int]:
    """Mirror flow::step_scalar — konvensi edge sama: f(i→i+1)=F(v[i−1],v[i],v[i+1])."""
    n = len(cells)
    mask = (1 << k) - 1

    def f(e: int) -> int:
        e %= n
        idx = ((cells[(e - 1) % n] & mask) << (2 * k)) | ((cells[e] & mask) << k) | (cells[(e + 1) % n] & mask)
        return table[idx]

    return [cells[i] - f(i) + f(i - 1) for i in range(n)]


def unpack_cells(state: int, n: int, k: int) -> list[int]:
    """Bongkar state bit-packed → daftar sel (cell i di bit [i·k, (i+1)·k))."""
    mask = (1 << k) - 1
    return [(state >> (i * k)) & mask for i in range(n)]


def from_seed_uniform_capped(n: int, k: int, seed: int, cap: int) -> list[int]:
    """Mirror World::from_seed_uniform_capped — sel uniform [0, cap]."""
    rng = Rng(seed)
    return [rng.next_u64() % (cap + 1) for _ in range(n)]


def cap_of(idx: int, k: int) -> int:
    """Kapasitas flow entri idx: min(c, 2^k−1−r)."""
    mask = (1 << k) - 1
    c = (idx >> k) & mask
    r = idx & mask
    return min(c, mask - r)


def random_table_rich(k: int, seed: int) -> list[int]:
    """Generator slack-rich: tiap entri uniform [0, cap] — nilai terdistribusi
    di bawah kapasitas, bukan 0..255 yang ter-clip menempel cap (akar
    capacity-bound, log 006)."""
    rng = Rng(seed)
    return [rng.next_u64() % (cap_of(i, k) + 1) for i in range(1 << (3 * k))]


def slack_fraction(table: list[int], k: int) -> float:
    """Fraksi entri cap>0 yang bernilai < cap — ruang longgar struktural."""
    size = 1 << (3 * k)
    total = loose = 0
    for i in range(size):
        c = cap_of(i, k)
        if c > 0:
            total += 1
            if table[i] < c:
                loose += 1
    return loose / total if total else 0.0
