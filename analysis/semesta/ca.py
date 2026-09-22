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
