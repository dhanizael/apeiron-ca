"""Sensus pola (M2, log 015): census kejadian pola + probe soliton.

Definisi operasional terbekukan (log 015): pola = blok kontigu terjangkar;
copy = kemunculan non-overlap (str.count); replikasi event = 1 → ≥2 copy;
sustained = masih ≥2 pada T+1000; terverifikasi = ≥3 seed.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))

from semesta import ca, io  # noqa: E402


def count_copies(states, pattern):
    """Jumlah copy non-overlap per state (ring → string, wrap via doubling
    dengan jaga panjang)."""
    w = len(pattern)
    p = "".join(chr(v) for v in pattern)
    counts = []
    for s in states:
        ring = "".join(chr(v) for v in s)
        wrapped = ring + ring[: w - 1]
        c = wrapped.count(p)
        # pola yang lebih panjang dari setengah ring bisa menghitung ganda;
        # w <= n/2 dijaga oleh pemanggil
        counts.append(min(c, len(s) // w if w else 0))
    return counts


def replication_event(counts, sustain=10):
    """1 copy awal → ≥2 copy → sustained: tetap ≥2 selama `sustain` sensus
    berturut (sensus tiap 100 langkah → 10 sensus = 1000 langkah)."""
    if not counts or counts[0] != 1:
        return None
    for i in range(1, len(counts)):
        if counts[i] >= 2:
            tail = counts[i: i + sustain]
            if len(tail) >= sustain and all(c >= 2 for c in tail):
                return {"t_index": i, "peak": max(counts)}
            return {"t_index": i, "peak": max(counts), "sustained": False}
    return None


def plant_state(base_cells, pattern, bg_ones=0, seed=0):
    """Kanvas kosong + pola tertanam + latar difus (1s acak deterministik)."""
    import sys
    sys.path.insert(0, str(ROOT / "experiments" / "m4"))
    from semesta import ca
    n = len(base_cells)
    cells = [0] * n
    for i, v in enumerate(pattern):
        cells[i] = v
    if bg_ones:
        rng = ca.Rng(seed)
        placed = 0
        guard = 0
        while placed < bg_ones and guard < 100 * n:
            guard += 1
            i = rng.next_u64() % n
            if cells[i] == 0:
                cells[i] = 1
                placed += 1
    return cells


def run_window(engine, n, k, seed, steps, window, rule_bin, outdir, init_state=None):
    cmd = [engine, "run", "--n", str(n), "--k", str(k), "--seed", str(seed),
           "--steps", str(steps), "--window", str(window),
           "--rule-table", str(rule_bin), "--threads", "1",
           "--outdir", str(outdir)]
    if init_state is not None:
        from state_surgery import write_snapshot
        write_snapshot(outdir.parent / "init_state.bin", init_state, k)
        cmd += ["--init-state", str(outdir.parent / "init_state.bin")]
    subprocess.run(cmd, check=True, capture_output=True)
    m = io.read_manifest(outdir / "manifest.json")
    return [ca.unpack_cells(s, n, k) for s in
            io.read_window(outdir / "window.bin", n, m["window_states"], k)]
