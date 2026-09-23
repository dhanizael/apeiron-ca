"""Peta respons mutasi LENGKAP (loop v6, log 012).

Kartografi ekshaustif: SEMUA langkah legal ±1 pada hukum incumben v5-final,
cap1 (J, 20k, window 512, seed 12001 — paired-by-seed) + cap3 (health 3-seed
12001–03, mobilitas, horizon penuh). Peta = (1) jawaban ekshaustif "lolos-
langit-langit atau langit-langit terbukti" untuk kelas ±1, (2) peta kausal
kondensasi lengkap hukum incumben (semua pemicu beku teridentifikasi),
(3) data pengujian H-A/H-B/H-C (hipotesis pre-registered log 012).

Analisis: H-A korelasi ΔJ_cap1 vs frekuensi realized (Pearson); H-B
Δmob_cap3 per kelas c; H-C antisimetri ±. Semua bivalen sesuai ambang yang
dibekukan di log.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m3"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca  # noqa: E402
from loop2 import binding_stats  # noqa: E402
from loop3 import legal_moves, observe_and_j  # noqa: E402
from health_landscape import load_baseline_laws  # noqa: E402
from loop5 import eval_cap1, eval_cap3  # noqa: E402

V5_FNV = "ee65c75045c607ad"
MAP_SEEDS = [12001, 12002, 12003]


def load_v5_final():
    """v5-final = v4-final + komitmen v5; guard FNV."""
    v4 = load_baseline_laws()["v4_final"]
    v5 = json.loads((ROOT / "experiments" / "m4" / "result" / "result_loop5.json").read_text())
    T = list(v4)
    for t in v5["trajectory"]:
        for e, d in t["intervention"]["targeted"]:
            T[e] += d
    T = ca.clip_table(T, 2)
    assert f"{ca.table_fnv(T):016x}" == V5_FNV, "silsilah v5-final rusak"
    return T


def dedup_best_direction(scored_moves):
    """Satu arah terbaik per entri (celah kebijakan v5-it0)."""
    best = {}
    for e, d, s in scored_moves:
        if e not in best or s > best[e][2]:
            best[e] = (e, d, s)
    return sorted(best.values())


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
    sy = (sum((y - my) ** 2 for y in ys)) ** 0.5
    return cov / (sx * sy) if sx > 0 and sy > 0 else 0.0


def map_law(engine, F, k, n, seeds, workdir, tag="map"):
    """Peta respons satu hukum: semua langkah legal ±1 → (dJ_cap1, dmob_cap3,
    cap3_rate) relatif terhadap induk (paired-by-seed). Dipakai main() dan
    loop6 (re-map per iterasi)."""
    p1 = eval_cap1(engine, F, k, n, seeds[0], 20000, 512, workdir, f"{tag}_parent")
    p3 = eval_cap3(engine, F, k, n, seeds, 20000, workdir, f"{tag}_parent")
    rows = []
    for e, dlt in legal_moves(F, k):
        T = list(F)
        T[e] += dlt
        m1 = eval_cap1(engine, T, k, n, seeds[0], 20000, 512, workdir, f"{tag}_m{e}_{dlt}")
        m3 = eval_cap3(engine, T, k, n, seeds, 20000, workdir, f"{tag}_m{e}_{dlt}")
        rows.append({"entry": e, "delta": dlt, "c": (e >> k) & ((1 << k) - 1),
                     "cap1_J": m1["J"], "cap1_static": m1["static"],
                     "cap3_rate": m3["rate"], "cap3_mean_mob": m3["mean_mobility"],
                     "dJ_cap1": (m1["J"] or 0.0) - (p1["J"] or 0.0),
                     "dmob_cap3": m3["mean_mobility"] - p3["mean_mobility"]})
    parent = {"cap1_J": p1["J"], "cap3_rate": p3["rate"],
              "cap3_mean_mob": p3["mean_mobility"]}
    return parent, rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    ap.add_argument("--n", type=int, default=16384)
    a = ap.parse_args()

    k, n = 2, a.n
    F = load_v5_final()
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"

    # baris induk (protokol sama)
    p1 = eval_cap1(a.engine, F, k, n, MAP_SEEDS[0], 20000, 512, workdir, "parent")
    p3 = eval_cap3(a.engine, F, k, n, MAP_SEEDS, 20000, workdir, "parent")
    parent = {"cap1_J": p1["J"], "cap3_rate": p3["rate"],
              "cap3_mean_mob": p3["mean_mobility"]}
    print(f"parent: cap1 J={p1['J']:.4f} | cap3 rate={p3['rate']:.2f} mob={p3['mean_mobility']:.4f}")

    moves = []
    for e, dlt in legal_moves(F, k):
        T = list(F)
        T[e] += dlt
        m1 = eval_cap1(a.engine, T, k, n, MAP_SEEDS[0], 20000, 512, workdir, f"m{e}_{dlt}")
        m3 = eval_cap3(a.engine, T, k, n, MAP_SEEDS, 20000, workdir, f"m{e}_{dlt}")
        row = {"entry": e, "delta": dlt, "c": (e >> k) & ((1 << k) - 1),
               "cap1_J": m1["J"], "cap1_static": m1["static"],
               "cap3_rate": m3["rate"], "cap3_mean_mob": m3["mean_mobility"],
               "dJ_cap1": (m1["J"] or 0.0) - (p1["J"] or 0.0),
               "dmob_cap3": m3["mean_mobility"] - p3["mean_mobility"]}
        moves.append(row)
        if m1["J"] is not None and p1["J"]:
            pass
        print(f"  e={e:2d} {dlt:+d}: dJ1={row['dJ_cap1']:+.4f} "
              f"cap3rate={m3['rate']:.2f} dmob={row['dmob_cap3']:+.4f}")

    # frekuensi realized di atraktor cap1 induk (untuk H-A)
    _s, _j = observe_and_j(a.engine, F, k, MAP_SEEDS[0], n, [1], 20000, 512,
                           workdir, 1, role="freq")
    freq = _s["count"]

    # ---- H-A: ΔJ_cap1 vs frekuensi realized (entri realized ∩ cap>0) ----
    ha_pairs = [(freq[r["entry"]], r["dJ_cap1"]) for r in moves
                if r["delta"] == 1 and freq[r["entry"]] > 0 and r["cap1_J"] is not None]
    rho = pearson([p[0] for p in ha_pairs], [p[1] for p in ha_pairs])
    ha = {"rho": round(rho, 4), "n": len(ha_pairs),
          "verdict": "SUPPORTED" if (len(ha_pairs) >= 5 and rho <= -0.3) else "NOT-SUPPORTED"}

    # ---- H-B: Δmob_cap3 kelas c=3 vs c≤2 (arah +1) ----
    dc3 = [r["dmob_cap3"] for r in moves if r["delta"] == 1 and r["c"] == 3]
    do = [r["dmob_cap3"] for r in moves if r["delta"] == 1 and r["c"] <= 2]
    mb, mo = (sum(dc3) / len(dc3) if dc3 else 0.0), (sum(do) / len(do) if do else 0.0)
    hb = {"mean_c3": round(mb, 4), "mean_c_le2": round(mo, 4),
          "n_c3": len(dc3), "n_other": len(do),
          "verdict": "SUPPORTED" if (dc3 and do and mb - mo >= 0.05) else "NOT-SUPPORTED"}

    # ---- H-C: antisimetri ± pada cap1 ----
    dj = {(r["entry"], r["delta"]): r["dJ_cap1"] for r in moves if r["cap1_J"] is not None}
    diffs = [abs(dj[(e, 1)] + dj[(e, -1)]) for e in set(x[0] for x in dj) if (e, 1) in dj and (e, -1) in dj]
    mean_asym = sum(diffs) / len(diffs) if diffs else 0.0
    hc = {"mean_abs_asym": round(mean_asym, 5), "n_pairs": len(diffs),
          "verdict": "SYMMETRIC" if mean_asym < 0.02 else "NONLINEAR"}

    result = {
        "experiment": "mutation-map",
        "incumbent_fnv": V5_FNV, "map_seeds": MAP_SEEDS, "k": k, "n": n,
        "parent": parent,
        "moves": moves,
        "hypotheses": {"H_A_busy_dangerous": ha, "H_B_c3_heals_cap3": hb,
                       "H_C_antisymmetry": hc},
        "reproduce": "python experiments/m4/mutation_map.py",
    }
    (outdir / "mutation_map.json").write_text(json.dumps(result, indent=2))
    print("MUTATION-MAP", f"n_moves={len(moves)}",
          f"H-A={ha['verdict']} (ρ={ha['rho']})",
          f"H-B={hb['verdict']} ({hb['mean_c3']} vs {hb['mean_c_le2']})",
          f"H-C={hc['verdict']} ({hc['mean_abs_asym']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
