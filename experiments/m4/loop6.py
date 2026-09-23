"""M4 loop v6 — map-guided commit dengan dedup-entri (log 012; plan 2026-09-23).

Upgrade kognitif: loop tak lagi menilai kandidat satu per satu — ia membaca
PETA RESPONS LENGKAP hukum incumben (mutation_map.map_law: semua langkah
legal ±1, cap1 J + cap3 health 3-seed, horizon penuh), memilih dengan DEDUP
(satu arah terbaik per entri — koreksi celah v5-it0), memvalidasi koktail
(cap1-safe + cap3 3/3 + joint > 0), lalu re-map setelah komit (K=2).

Kriteria (dibekukan log 012):
  W3v6a (self-calibrating): hukum final 7/7+7/7 pada blok 12011–12017 DAN
    (mean J_cap1 > incumben + 0,01 ATAU mean mob_cap3 > incumben + 0,02).
    GAGAL = langit-langit kelas ±1 terbukti (hasil utama, bukan kegagalan
    senyap).
  W3v6b: aditivitas koktail dilaporkan (|gabungan − Σ single| + non-linier).
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
from loop3 import legal_moves, observe_and_j  # noqa: E402
from loop5 import eval_cap1, eval_cap3  # noqa: E402
from mutation_map import dedup_best_direction, load_v5_final, map_law  # noqa: E402
from recover import measure_j  # noqa: E402

R_MIN = 0.3
CAP1, CAP3 = 1, 3


def select_from_map(rows, m):
    """Skor gabungan per langkah → dedup satu-arah-terbaik → top-m."""
    scored = [(r["entry"], r["delta"], r["dJ_cap1"] + r["dmob_cap3"]) for r in rows]
    dedup = dedup_best_direction(scored)
    dedup.sort(key=lambda t: -t[2])
    return [(e, d, round(s, 6)) for e, d, s in dedup[:m] if s > 0]


def validate_cocktail(engine, F, pick, k, n, seeds, cfg, workdir, tag):
    T = list(F)
    for e, d, _s in pick:
        T[e] += d
    T = ca.clip_table(T, k)
    v1 = eval_cap1(engine, T, k, n, seeds[0], cfg["s1"], cfg["w1"], workdir, f"{tag}c1")
    v3 = eval_cap3(engine, T, k, n, seeds, cfg["s3"], workdir, f"{tag}c3")
    p1 = eval_cap1(engine, F, k, n, seeds[0], cfg["s1"], cfg["w1"], workdir, f"{tag}p1")
    p3 = eval_cap3(engine, F, k, n, seeds, cfg["s3"], workdir, f"{tag}p3")
    joint = ((v1["J"] or 0.0) - (p1["J"] or 0.0)) + (v3["mean_mobility"] - p3["mean_mobility"])
    safe = (p1["J"] > 0 and (v1["J"] or 0.0) / p1["J"] >= R_MIN) and v3["rate"] >= 1.0
    return {"table": T, "cap1_J": v1["J"], "cap3_rate": v3["rate"],
            "cap3_mob": v3["mean_mobility"], "parent_cap1_J": p1["J"],
            "parent_cap3_mob": p3["mean_mobility"],
            "joint": round(joint, 6), "safe": safe, "commit": bool(safe and joint > 0)}


def health_block(engine, table, k, n, seeds, cfg, workdir, tag):
    """Kesehatan 7-seed satu blok: cap1 (J/static) + cap3 (mobilitas)."""
    cap1 = [eval_cap1(engine, table, k, n, s, 20000, 512, workdir, f"{tag}b1_{s}") for s in seeds]
    cap3 = [eval_cap3(engine, table, k, n, [s], 20000, workdir, f"{tag}b3_{s}") for s in seeds]
    c1r = sum(1 for c in cap1 if (c["J"] or 0) > 0 or not c["static"]) / len(seeds)
    c3r = sum(h["rate"] for h in cap3) / len(seeds)
    return {"cap1_rate": c1r, "cap3_rate": c3r,
            "cap1_mean_J": round(sum((c["J"] or 0.0) for c in cap1) / len(seeds), 6),
            "cap3_mean_mob": round(sum(h["per_seed"][0]["mobility"] for h in cap3) / len(seeds), 6)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mini", action="store_true")
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    a = ap.parse_args()

    if a.mini:
        F0 = ca.random_table_rich(2, 5700010)
        k, n = 2, 128
        cfg = {"s1": 800, "w1": 32, "s3": 1200}
        map_seeds = [41, 42, 43]
        verdict_seeds = list(range(51, 58))
        cross_seeds = list(range(61, 68))
        M, K = 4, 2
    else:
        F0 = load_v5_final()
        k, n = 2, 16384
        cfg = {"s1": 5000, "w1": 512, "s3": 20000}
        map_seeds = [12001, 12002, 12003]
        verdict_seeds = list(range(12011, 12018))
        cross_seeds = list(range(55001, 55008))
        M, K = 8, 2

    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"
    workdir.mkdir(exist_ok=True)

    F = list(F0)
    trajectory = []
    for it in range(K):
        seeds = [s + it for s in map_seeds]
        parent, rows = map_law(a.engine, F, k, n, seeds, workdir, tag=f"it{it}_")
        pick = select_from_map(rows, M)
        entry = {"iteration": it, "n_moves": len(rows),
                 "parent": parent, "selected": pick, "cocktails": []}
        if not pick:
            entry["committed"] = []
            trajectory.append(entry)
            continue
        for size in (len(pick), max(1, len(pick) // 2), 2, 1):
            sub = pick[:size]
            v = validate_cocktail(a.engine, F, sub, k, n, seeds, cfg, workdir, f"it{it}_k{size}_")
            v["size"] = size
            entry["cocktails"].append({kk: v[kk] for kk in
                                       ("size", "cap1_J", "cap3_rate", "cap3_mob",
                                        "joint", "safe", "commit")})
            if v["commit"]:
                F = v["table"]
                break
        entry["committed"] = [[e, d] for e, d, _s in pick[:entry["cocktails"][-1]["size"]]] \
            if any(c["commit"] for c in entry["cocktails"]) else []
        entry["committed_fnv"] = f"{ca.table_fnv(F):016x}"
        trajectory.append(entry)

    # verdict self-calibrating: incumben vs final pada blok yang sama
    inc = health_block(a.engine, F0, k, n, verdict_seeds, cfg, workdir, "inc_")
    fin = health_block(a.engine, F, k, n, verdict_seeds, cfg, workdir, "fin_")
    cross = health_block(a.engine, F, k, n, cross_seeds, cfg, workdir, "x_")
    beat = ((fin["cap1_mean_J"] - inc["cap1_mean_J"] > 0.01)
            or (fin["cap3_mean_mob"] - inc["cap3_mean_mob"] > 0.02))
    w3a = bool(fin["cap1_rate"] >= 1.0 and fin["cap3_rate"] >= 1.0 and beat)

    # batas aliran-bebas: J vs massa/n (3ρ) — verifikasi identitas konservasi
    ff = {}
    for name, T in (("incumbent", F0), ("final", F)):
        d = workdir / f"ff_{name}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "rule.bin").write_bytes(bytes(T))
        r = measure_j(a.engine, d, n, k, verdict_seeds[0],
                      20000, 512, CAP1, d / "w")
        ff[name] = {"J": r["J"], "rho": r["rho"], "mass_over_n": round(3 * r["rho"], 6)}

    result = {
        "experiment": "M4-loop-v6",
        "mode": "mini" if a.mini else "full",
        "lineage": "v5-final" if not a.mini else "rich-mini",
        "criteria": {"W3v6a_escape_or_ceiling": w3a},
        "verdict": {"incumbent": inc, "final": fin, "cross_block_55001": cross,
                    "beat_incumbent": bool(beat),
                    "free_flow_bound": ff},
        "trajectory": trajectory,
        "reproduce": f"python experiments/m4/loop6.py{' --mini' if a.mini else ''}",
    }
    (outdir / "result_loop6.json").write_text(json.dumps(result, indent=2))
    print("M4-LOOP-V6",
          f"W3v6a={'PASS(lolos)' if w3a else 'LANGIT-LANGIT TERBUKTI'}",
          f"| final cap1={fin['cap1_rate']:.2f} cap3={fin['cap3_rate']:.2f}",
          f"| ΔJ1={fin['cap1_mean_J']-inc['cap1_mean_J']:+.4f}",
          f"Δmob3={fin['cap3_mean_mob']-inc['cap3_mean_mob']:+.4f}",
          f"| free-flow: J={ff['final']['J']:.4f} vs mass/n={ff['final']['mass_over_n']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
