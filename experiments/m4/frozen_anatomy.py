"""Anatomi fixed point — jawab pertanyaan (8) log 007 pada level state.

Apa yang terjadi pada semesta yang dibekukan satu mutasi +1? Anatomi keadaan
beku: histogram nilai sel, entri tabel terrealisasi (+ verifikasi invarian
"semua entri terrealisasi bernilai F=0 pada hukum beku"), perbandingan dengan
hukum asli (apakah kristal menghindari entri yang dipanaskan mutasi?), dan
waktu beku via binary search atas final-state fnv.

Mode full merekonstruksi semesta beku log 007 secara deterministik
(FNV 4f2f83084da03371 — guard silsilah keras).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m3"))

from semesta import ca, io  # noqa: E402

FROZEN_FNV = "4f2f83084da03371"   # log 007: tabel hasil it0 loop v2 (beku)
FROZEN_SEED = 4401                # seed verifikasi log 007 (disklosikan)
MUTATED = [24, 12, 28, 41, 44, 8, 46, 57]  # it0 loop v2 (log 007)


def frozen_table():
    """Rekonstruksi tabel beku dari induk RICH + mutasi it0; guard FNV."""
    F0 = list(Path(ROOT, "experiments/m1v2/result/_work/rule_H_RICH_5700010.bin").read_bytes())
    T = list(F0)
    for e in MUTATED:
        T[e] += 1
    T = ca.clip_table(T, 2)
    fnv = f"{ca.table_fnv(T):016x}"
    assert fnv == FROZEN_FNV, f"silsilah rusak: {fnv} != {FROZEN_FNV}"
    return F0, T


def crystal_state(n):
    """Kristal sintetis {0,2} tanpa tetangga 2-2 — fixed point eksak F0 (tes)."""
    return [2 if i % 2 == 0 else 0 for i in range(n)]


def is_static(states):
    return all(list(a) == list(b) for a, b in zip(states[:-1], states[1:]))


def anatomy(states, table, k, f0_table=None):
    """Anatomi keadaan (window) — states harus statis (beku) agar sah."""
    assert is_static(states), "anatomi menuntut keadaan statis"
    s = list(states[0])
    n = len(s)
    max_cell = (1 << k) - 1
    hist = {}
    for v in s:
        hist[str(v)] = hist.get(str(v), 0) + 1
    realized = {}
    for i in range(n):
        idx = ((s[(i - 1) % n] & max_cell) << (2 * k)) | ((s[i] & max_cell) << k) | (s[(i + 1) % n] & max_cell)
        realized[idx] = realized.get(idx, 0) + 1
    entries = [{"entry": e, "count": c, "f_frozen": table[e],
                "f0": (f0_table[e] if f0_table is not None else None)}
               for e, c in sorted(realized.items())]
    return {
        "n": n,
        "rho": round(sum(s) / (n * max_cell), 6),
        "cell_histogram": dict(sorted(hist.items(), key=lambda kv: -kv[1])),
        "realized_entries": entries,
        "n_realized_entries": len(entries),
        "all_realized_zero_in_law": all(table[e] == 0 for e in realized),
        "all_realized_zero_in_f0": None if f0_table is None else all(f0_table[e] == 0 for e in realized),
        "realized_mutated_hot": sum(1 for e in realized if e in MUTATED and table[e] > 0),
    }


def _final_fnv(engine, table, n, k, seed, steps, cap, workdir):
    """Run engine, kembalikan (fnv_final, window_states)."""
    import subprocess
    d = Path(workdir) / f"fa_{seed}_{steps}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(table))
    cmd = [engine, "run", "--n", str(n), "--k", str(k), "--uniform",
           "--seed", str(seed), "--steps", str(steps), "--window", "2",
           "--rule-table", str(d / "rule.bin"), "--threads", "1",
           "--outdir", str(d / "w"), "--init-cap", str(cap)]
    subprocess.run(cmd, check=True, capture_output=True)
    m = io.read_manifest(d / "w" / "manifest.json")
    return m["fnv_final"]


def freeze_time_search(run_steps, t_final=20000, grid=(1250, 2500, 5000, 10000, 15000)):
    """Bracket waktu-beku: run_steps(steps) -> fnv_final. Beku pada (t_below, t_at]."""
    target = run_steps(t_final)
    below, at = None, None
    for t in sorted(grid):
        if run_steps(t) == target:
            at = t
            break
        below = t
    assert at is not None, "grid tak menemukan kebekuan — perbesar grid"
    return {"t_final": t_final, "t_below": below, "t_at": at,
            "frozen_window": f"({below}, {at}]" if below else f"(0, {at}]"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    a = ap.parse_args()

    F0, T = frozen_table()
    k, n, cap = 2, 16384, 1
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    def run_steps(steps):
        return _final_fnv(a.engine, T, n, k, FROZEN_SEED, steps, cap, outdir / "_work")

    target_fnv = run_steps(20000)
    assert target_fnv == "403a15dbacf71197", f"final state berubah: {target_fnv}"
    search = freeze_time_search(run_steps, t_final=20000)

    # anatomi pada window penuh 20000 (statik terverifikasi ulang)
    d = outdir / "_work" / "fa_anatomy"
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(T))
    import subprocess
    subprocess.run([a.engine, "run", "--n", str(n), "--k", str(k), "--uniform",
                    "--seed", str(FROZEN_SEED), "--steps", "20000", "--window", "512",
                    "--rule-table", str(d / "rule.bin"), "--threads", "1",
                    "--outdir", str(d / "w"), "--init-cap", str(cap)],
                   check=True, capture_output=True)
    m = io.read_manifest(d / "w" / "manifest.json")
    states = [ca.unpack_cells(s, n, k) for s in
              io.read_window(d / "w" / "window.bin", n, m["window_states"], k)]
    assert is_static(states), "window 512 tidak statis — bukan fixed point"

    an = anatomy(states, T, k, f0_table=F0)
    result = {
        "experiment": "frozen-anatomy",
        "frozen_table_fnv": FROZEN_FNV,
        "final_fnv": target_fnv,
        "static_window": True,
        "freeze_time": search,
        "mutated_entries": MUTATED,
        "anatomy": an,
        "reproduce": "python experiments/m4/frozen_anatomy.py",
    }
    (outdir / "frozen_anatomy.json").write_text(json.dumps(result, indent=2))
    print("FROZEN-ANATOMY", json.dumps({
        "freeze_time": search["frozen_window"],
        "rho": an["rho"], "hist": an["cell_histogram"],
        "n_realized": an["n_realized_entries"],
        "all_zero_law": an["all_realized_zero_in_law"],
        "all_zero_f0": an["all_realized_zero_in_f0"],
        "realized_mutated_hot": an["realized_mutated_hot"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
