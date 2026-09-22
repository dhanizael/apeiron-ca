"""Newton Tahap-B mikro (v0): pemulihan aturan mikro ECA radius-1.

Strategi: ekshaustif-konsistensi atas 2^8 aturan. Kendala per sel: aturan harus
memetakan neighborhood (L,C,R) → bit teramati. Substrat bebas noise → aturan
sejati selalu konsisten; coverage tak lengkap → kandidat >1 (dilaporkan jujur,
TIDAK dipaksa pilih). Deskripsi aturan seragam 8 bit → seleksi = nol-error
konsistensi; penalti panjang model (MDL) muncul di tingkat makro (macro.py).
"""
from semesta import ca


class ContradictionError(Exception):
    """Dua bit berbeda diamati untuk neighborhood sama → asumsi substrat rusak."""


def constraints(states: list[int], n: int, max_pairs: int | None = None) -> dict[int, int]:
    seq = states if max_pairs is None else states[: max_pairs + 1]
    mask = (1 << n) - 1
    cons: dict[int, int] = {}
    for s, t in zip(seq, seq[1:]):
        L = ((s << 1) | (s >> (n - 1))) & mask
        R = ((s >> 1) | (s << (n - 1))) & mask
        for i in range(n):
            nb = (((L >> i) & 1) << 2) | (((s >> i) & 1) << 1) | ((R >> i) & 1)
            b = (t >> i) & 1
            prev = cons.get(nb)
            if prev is None:
                cons[nb] = b
            elif prev != b:
                raise ContradictionError(f"neighborhood {nb:03b} → {prev} dan {b}")
    return cons


def consistent_rules(cons: dict[int, int]) -> list[int]:
    return [
        rid for rid in range(256)
        if all(((rid >> nb) & 1) == b for nb, b in cons.items())
    ]


def verify_rule(rule_id: int, states: list[int], n: int) -> bool:
    """Gerbang eksak: aturan harus mereproduksi SELURUH window bit-identical."""
    for s, t in zip(states, states[1:]):
        if ca.step_rule(s, n, rule_id) != t:
            return False
    return True


def recover(states: list[int], n: int, max_pairs: int | None = None) -> dict:
    cons = constraints(states, n, max_pairs)
    cands = consistent_rules(cons)
    verified = [r for r in cands if verify_rule(r, states, n)]
    return {"candidates": cands, "verified": verified, "constraints": cons}
