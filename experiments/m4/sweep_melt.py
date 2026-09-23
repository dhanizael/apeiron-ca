"""Sweep jendela kritis kristalisasi (Part B loop v4, log 010).

Mengadili prediksi falsifiabel log 008: "pelelehan tepat-waktu menjaga J>0
sepanjang horizon; terlambat → kristal permanen" — dengan data, termasuk
kontradiksi tersisa (anekdot v2-it1 melelehkan kristal PENUH dengan sukses).

Protokol: hukum pembeku v2-it0 (FNV 4f2f83084da03371, seed 4401 — silsilah
anatomi 009) → beku T langkah → S_T (final.bin) → leleh: +1 pada M dinding
teramati tersebar (entri realized ∩ cap>0, terbanyak — policy findings-
derived: dinding kristal = tepi domain yang masih membawa massa) vs kontrol
+1 pada M dinding acak disjoint (paired via S_T sama) → lanjut 20.000 langkah
dari S_T (--init-state, hukum lelehan) → recovery = J_akhir > 0 dan tak
statis. Kronologi massa nilai antara (1&2) di S_T tiap T tercatat (indikator
008). Baseline tanpa-leleh wajib J=0 (sanity harness).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m3"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca, io  # noqa: E402
from recover import measure_j  # noqa: E402
from calibrate_freeze import j_from_states  # noqa: E402

FREEZE_FNV = "4f2f83084da03371"
FREEZE_SEED = 4401


def frozen_table():
    F0 = list(Path(ROOT, "experiments/m1v2/result/_work/rule_H_RICH_5700010.bin").read_bytes())
    T = list(F0)
    for e in [24, 12, 28, 41, 44, 8, 46, 57]:  # komitmen it0 loop v2 (log 007)
        T[e] += 1
    T = ca.clip_table(T, 2)
    assert f"{ca.table_fnv(T):016x}" == FREEZE_FNV, "silsilah rusak"
    return T


def state_cells(snapshot_path, n, k):
    snap = io.read_snapshot(snapshot_path)
    assert snap["n"] == n and snap["k"] == k, "snapshot mismatch"
    return ca.unpack_cells(snap["state"], n, k)


def walls_from_state(s, k):
    """Dinding kristal: entri realized dengan cap>0 (tepi domain pembawa
    massa) — frekuensi kemunculannya di state."""
    max_cell = (1 << k) - 1
    freq = {}
    n = len(s)
    for i in range(n):
        idx = ((s[(i - 1) % n] & max_cell) << (2 * k)) | ((s[i] & max_cell) << k) | (s[(i + 1) % n] & max_cell)
        if ca.cap_of(idx, k) > 0:
            freq[idx] = freq.get(idx, 0) + 1
    return freq


def melt_table(table, entries):
    T = list(table)
    for e in entries:
        T[e] += 1
    return ca.clip_table(T, 2)


def run_from_state(engine, state_path, table, n, k, steps, workdir, tag):
    """Run 20k dari S_T dengan hukum table (--init-state) → J + statis."""
    d = Path(workdir) / f"melt_{tag}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(table))
    subprocess.run([engine, "run", "--n", str(n), "--k", str(k),
                    "--seed", str(FREEZE_SEED), "--steps", str(steps),
                    "--window", "512", "--rule-table", str(d / "rule.bin"),
                    "--init-state", str(state_path), "--threads", "1",
                    "--outdir", str(d / "w")], check=True, capture_output=True)
    m = io.read_manifest(d / "w" / "manifest.json")
    assert m["init_source"] == "snapshot"
    states = [ca.unpack_cells(s, n, k) for s in
              io.read_window(d / "w" / "window.bin", n, m["window_states"], k)]
    j, amb, static = j_from_states(states, k)
    return {"J": j, "amb": amb, "static": static}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    ap.add_argument("--n", type=int, default=16384)
    a = ap.parse_args()

    k, n = 2, a.n
    freeze_tab = frozen_table()
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"
    workdir.mkdir(exist_ok=True)
    grid = [250, 500, 1000, 2000, 3000, 5000, 10000, 20000]

    # run beku penuh sekali (sumber S_T via --steps per titik? final(T) butuh
    # run per T — murah); gunakan hukum beku, seed 4401, init_cap=1
    rows = []
    for T in grid:
        d = workdir / f"fz_{T}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "rule.bin").write_bytes(bytes(freeze_tab))
        subprocess.run([a.engine, "run", "--n", str(n), "--k", str(k),
                        "--uniform", "--seed", str(FREEZE_SEED),
                        "--steps", str(T), "--window", "2",
                        "--rule-table", str(d / "rule.bin"), "--threads", "1",
                        "--init-cap", "1", "--outdir", str(d / "w")],
                       check=True, capture_output=True)
        s = state_cells(d / "w" / "final.bin", n, k)
        mid = sum(1 for v in s if v in (1, 2))
        walls = walls_from_state(s, k)
        ranked = sorted(walls, key=lambda e: (-walls[e], e))
        m = min(8, max(1, len(ranked) // 2)) if len(ranked) >= 2 else 0
        tgt = ranked[:m]
        rng = ca.Rng(9900 + T)
        pool = [e for e in ranked if e not in set(tgt)]
        rnd = [pool[rng.next_u64() % len(pool)] for _ in range(min(m, len(pool)))] if pool else []
        row = {"T": T, "mid_values": mid, "n_wall_entries": len(ranked),
               "m": m, "targeted": tgt, "control": rnd}

        # sanity: tanpa leleh (satu titik saja)
        if T == 3000:
            r0 = run_from_state(a.engine, d / "w" / "final.bin", freeze_tab, n, k,
                                20000, workdir, f"none_{T}")
            row["no_melt"] = r0
        if m > 0:
            mt = melt_table(freeze_tab, tgt)
            row["melt_targeted"] = run_from_state(
                a.engine, d / "w" / "final.bin", mt, n, k, 20000, workdir, f"t_{T}")
            if rnd:
                mr = melt_table(freeze_tab, rnd)
                row["melt_random"] = run_from_state(
                    a.engine, d / "w" / "final.bin", mr, n, k, 20000, workdir, f"r_{T}")
        rows.append(row)
        rec_t = row.get("melt_targeted", {})
        print(f"T={T:5d} mid={mid:5d} walls={len(ranked):2d} m={m} "
              f"J_targeted={rec_t.get('J', float('nan')):.4f} "
              f"static={rec_t.get('static')}")

    result = {
        "experiment": "crystallization-critical-window",
        "freeze_table_fnv": FREEZE_FNV, "seed": FREEZE_SEED, "k": k, "n": n,
        "grid": grid, "policy": {"m": "min(8, walls//2)",
                                 "targeted": "top realized-cap>0 by freq",
                                 "control": "random disjoint walls"},
        "rows": rows,
        "reproduce": "python experiments/m4/sweep_melt.py",
    }
    (outdir / "sweep_melt.json").write_text(json.dumps(result, indent=2))
    print("SWEEP-MELT selesai →", outdir / "sweep_melt.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
