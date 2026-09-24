"""PERPETUUM ECOLOGIS (log 018): fitness populasi hidup + sapu hukum.

Definisi terbekukan: sensus p_v(t); PERPETUUM = (a) koeksistensi (≥2 spesies
mean ≥ 10), (b) amplitudo ((max−min)/mean) ≥ 0,3 pada ≥1 spesies di
sepertiga terakhir, (c) tak statis di sepertiga akhir. Predasi (stretch):
korelasi dua spesies ≤ −0,5 di sepertiga akhir.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m2"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca  # noqa: E402


def pop_trajectories(states, k):
    """p_v(t) untuk semua nilai v yang ada (str.count per char — C-speed)."""
    rings = ["".join(chr(v & ((1 << k) - 1)) for v in s) for s in states]
    values = sorted({v for s in states for v in s})
    return {v: [r.count(chr(v)) for r in rings] for v in values}, rings


def amplitude_last_third(traj):
    """(max−min)/mean pada sepertiga terakhir; None bila mean < 5."""
    t = traj[len(traj) // 3 * 2:]
    mean = sum(t) / len(t)
    if mean < 5:
        return None
    return (max(t) - min(t)) / mean


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
    sy = (sum((y - my) ** 2 for y in ys)) ** 0.5
    return cov / (sx * sy) if sx > 0 and sy > 0 else 0.0


def perpetuum_verdict(trajs, rings, k):
    """Terapkan definisi terbekukan pada horizon penuh (sudah tercensus).
    Return dict verdict + detail (untuk verifikasi 20k juga dipakai)."""
    last3_start = len(next(iter(trajs.values()))) // 3 * 2
    static = all(r == q for r, q in zip(rings[last3_start:-1], rings[last3_start + 1:]))
    coex, amp_max, amp_v = 0, 0.0, None
    details = {}
    for v, traj in trajs.items():
        mean = sum(traj) / len(traj)
        if mean >= 10:
            coex += 1
        a = amplitude_last_third(traj)
        details[v] = None if a is None else round(a, 4)
        if a is not None and a > amp_max:
            amp_max, amp_v = a, v
    alive = coex >= 2
    amp_ok = amp_max >= 0.3
    not_static = not static
    # predasi: korelasi terkuat antar dua spesies berarti (mean ≥ 10)
    strong = [v for v, traj in trajs.items() if sum(traj) / len(traj) >= 10]
    pred = None
    for i, a in enumerate(strong):
        for b in strong[i + 1:]:
            r = pearson(trajs[a][last3_start:], trajs[b][last3_start:])
            if pred is None or r < pred["rho"]:
                pred = {"pair": [a, b], "rho": round(r, 4)}
    return {"perpetuum": bool(alive and amp_ok and not_static),
            "coex": coex, "amp_max": round(amp_max, 4), "amp_species": amp_v,
            "static_last3": static, "predation": pred, "amplitudes": details,
            "checks": {"alive": alive, "amp_ok": amp_ok, "not_static": not_static}}
