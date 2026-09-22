"""M1 — Physics design search (spec §9 amendemen M1).

Tiga tahap: (A) saringan acak seeded, (B) mutasi re-clip hill-climbing,
(C) horizon H + verdict K3. Semua kandidat dilaporkan (results.jsonl —
distribusi penuh), bukan hanya yang lolos. Seed hand-designed dijalankan
selalu sebagai baseline kalibrasi. Deterministik penuh (tanpa random module).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))

from semesta import ca  # noqa: E402


def probe_candidate(engine, n, k, seed, steps, probe_every, rule_path, threads=None):
    """rule_path: file tabel yang SUDAH ditulis unik per kandidat (bebas balapan)."""
    if threads is None:
        threads = 4 if n > 65536 else 1  # n kecil: overhead spawn thread/langkah > manfaat
    out = subprocess.run(
        [engine, "probe", "--n", str(n), "--k", str(k), "--seed", str(seed),
         "--steps", str(steps), "--probe-every", str(probe_every),
         "--rule-table", str(rule_path), "--threads", str(threads)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(out.stdout.strip())


def exclusion_streak(rep, streak_needed):
    """Jumlah titik berurutan terpanjang dengan top3 ≥ 0.8 (proxy exclusion)."""
    longest = cur = 0
    for _t, top, total in rep["top3_series"]:
        if total > 0 and top * 5 >= total * 4:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0
    return longest


def passes_a(rep, min_lifetime_steps, streak_cap, probe_every):
    _t, top, total = rep["top3_series"][-1]
    if total > 0 and top * 5 >= total * 4:
        return False  # sudah runtuh di akhir
    if exclusion_streak(rep, 0) > streak_cap:
        return False
    if rep["particles_final"] < 1:
        return False
    # satuan langkah fisika: observasi berturut-turut × probe_every
    life_obs_needed = max(1, -(-min_lifetime_steps // probe_every))
    if rep["max_lifetime"] < life_obs_needed:
        return False
    return True


def hand_seeds():
    """Dua fisika hand-designed sebagai baseline kalibrasi (tidak ikut juara)."""
    sand = [0] * 64
    layer = [0] * 64
    for l in range(4):
        for c in range(4):
            for r in range(4):
                idx = (l << 4) | (c << 2) | r
                sand[idx] = 1 if c > r + 1 else 0
                layer[idx] = 1 if ((c & 1) and not (r & 1)) else 0
    return {"sandpile_k2": ca.clip_table(sand, 2), "layer184_k2": ca.clip_table(layer, 2)}


def _probe_one(task):
    """Worker pool: (engine, n, k, seed, steps, every, table_bytes, workdir) → report JSON."""
    engine, n, k, seed, steps, every, table_bytes, workdir = task
    wd = Path(workdir)
    wd.mkdir(parents=True, exist_ok=True)
    rule_path = wd / f"rule_{k}_{seed}.bin"
    rule_path.write_bytes(table_bytes)
    return probe_candidate(engine, n, k, seed, steps, every, rule_path, threads=1)


def score_of(rep):
    _t, top, total = rep["top3_series"][-1]
    frac = (top / total) if total else 1.0
    return rep["max_lifetime"] * (1.0 - frac) * (1 if rep["particles_final"] >= 1 else 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mini", action="store_true")
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    a = ap.parse_args()

    if a.mini:
        n_a, steps_a, every_a = 256, 2000, 100
        nA, min_life, streak_cap = 200, 500, 3  # min_life = langkah fisika
        n_b, steps_b, rounds, mutants = 256, 4000, 1, 4
        steps_c = 4000
        top_keep = 3
    else:
        n_a, steps_a, every_a = 4096, 20000, 1000
        nA, min_life, streak_cap = 20000, 50000, 10  # T_persist = 5×10⁴ langkah
        n_b, steps_b, rounds, mutants = 16384, 100000, 3, 8
        steps_c = 10 ** 6
        top_keep = 5

    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"
    workdir.mkdir(exist_ok=True)

    # ---------- Baseline kalibrasi ----------
    baselines = {}
    for name, table in hand_seeds().items():
        rp = workdir / f"rule_base_{name}.bin"
        rp.write_bytes(bytes(table))
        rep = probe_candidate(a.engine, n_a, 2, 1, steps_a, every_a, rp)
        baselines[name] = {
            "table_fnv": rep["rule_fnv"],
            "top3_final": rep["top3_series"][-1],
            "particles_final": rep["particles_final"],
            "max_lifetime": rep["max_lifetime"],
        }

    # ---------- Tahap A: saringan acak (paralel ANTAR kandidat) ----------
    import multiprocessing as mp

    n_k2 = nA // 2
    args_list = []
    for i in range(nA):
        k = 2 if i < n_k2 else 4
        seed = i + 1
        table = ca.clip_table(ca.random_table(k, seed), k)
        args_list.append((a.engine, n_a, k, seed, steps_a, every_a, bytes(table), str(workdir)))

    workers = min(12, mp.cpu_count() or 1)
    if workers > 1:
        with mp.Pool(workers) as pool:
            reps = pool.map(_probe_one, args_list)
    else:
        reps = [_probe_one(t) for t in args_list]

    jsonl = outdir / "results.jsonl"
    survivors = []
    with open(jsonl, "w") as fh:
        for (k, seed), rep in zip([(x[2], x[3]) for x in args_list], reps):
            row = {
                "stage": "A", "k": k, "seed": seed,
                "table_fnv": rep["rule_fnv"],
                "particles_final": rep["particles_final"],
                "max_lifetime": rep["max_lifetime"],
                "top3_final": rep["top3_series"][-1],
                "mass_final": rep["mass_final"],
                "max_lifetime_steps": rep["max_lifetime"] * every_a,
            "passes": passes_a(rep, min_life, streak_cap, every_a),
            }
            fh.write(json.dumps(row) + "\n")
            if row["passes"]:
                survivors.append({"k": k, "seed": seed, "score": score_of(rep)})

    # ---------- Tahap B: mutasi re-clip hill-climbing ----------
    pool = list(survivors)
    rng = ca.Rng(777000)
    for rnd in range(rounds):
        candidates = []
        for s in pool[:top_keep]:
            base = ca.clip_table(ca.random_table(s["k"], s["seed"]), s["k"])
            for m in range(mutants):
                table = list(base)
                for _ in range(1 + rng.next_u64() % 2):  # 1-2 entri berubah
                    pos = rng.next_u64() % len(table)
                    table[pos] = rng.next_u64() & 0xFF
                table = ca.clip_table(table, s["k"])
                seed_m = 900000 + rnd * 100000 + s["seed"] * 10 + m
                rp = workdir / f"rule_B_{rnd}_{s['seed']}_{m}.bin"
                rp.write_bytes(bytes(table))
                rep = probe_candidate(a.engine, n_b, s["k"], seed_m % 100000, steps_b, every_a, rp)
                candidates.append({"k": s["k"], "seed": seed_m, "table": table,
                                   "rep": rep, "score": score_of(rep)})
        pool = sorted(pool + candidates, key=lambda x: -x["score"])[:top_keep]

    # ---------- Tahap C: horizon + verdict ----------
    champions = []
    for s in pool[:top_keep]:
        table = s.get("table") or ca.clip_table(ca.random_table(s["k"], s["seed"]), s["k"])
        if "rep" not in s:
            rp = workdir / f"rule_C_{s['seed']}.bin"
            rp.write_bytes(bytes(table))
            rep = probe_candidate(a.engine, n_b, s["k"], s["seed"], steps_b, every_a, rp)
        else:
            rep = s["rep"]
        # horizon penuh
        rule_bin = workdir / f"rule_champ_{s['k']}_{s['seed']}.bin"
        rule_bin.write_bytes(bytes(table))
        run_dir = outdir / f"champ_k{s['k']}_s{s['seed']}"
        subprocess.run(
            [a.engine, "run", "--n", str(n_b), "--k", str(s["k"]), "--uniform",
             "--seed", str(s["seed"] % 100000), "--steps", str(steps_c),
             "--window", "256", "--rule-table", str(rule_bin),
             "--threads", "4", "--outdir", str(run_dir)],
            check=True, capture_output=True,
        )
        _t, top, total = rep["top3_series"][-1]
        no_exclusion = not (total > 0 and top * 5 >= total * 4) and exclusion_streak(rep, 0) <= streak_cap
        life_obs_needed = max(1, -(-min_life // every_a))
        particles = rep["particles_final"] >= 1 and rep["max_lifetime"] >= life_obs_needed
        champions.append({
            "k": s["k"], "seed": s["seed"], "table_fnv": rep["rule_fnv"],
            "score": s["score"], "horizon_H": steps_c,
            "particles_final": rep["particles_final"],
            "max_lifetime": rep["max_lifetime"],
            "top3_final": rep["top3_series"][-1],
            "exclusion_streak_max": exclusion_streak(rep, 0),
            "criterion_particles": bool(particles),
            "criterion_no_exclusion": bool(no_exclusion),
            "manifest": str((run_dir / "manifest.json").relative_to(outdir)),
        })

    k3_pass = any(c["criterion_particles"] and c["criterion_no_exclusion"] for c in champions)
    result = {
        "experiment": "M1",
        "mode": "mini" if a.mini else "full",
        "criteria": {"K3_particle_persistent_and_no_exclusion": bool(k3_pass)},
        "stages": {"a": {"n_candidates": nA, "n_survivors": len(survivors)},
                   "b": {"rounds": rounds, "mutants_per_survivor": mutants},
                   "c": {"horizon_H": steps_c, "n_champions": len(champions)}},
        "baselines": baselines,
        "n_survivors": len(survivors),
        "champions": champions,
        "reproduce": (
            "cargo build --release (di engine/) && "
            f"python experiments/m1/search.py{' --mini' if a.mini else ''}"
        ),
    }
    (outdir / "result.json").write_text(json.dumps(result, indent=2))
    print("M1", "K3-PASS" if k3_pass else "K3-NO-CANDIDATE",
          f"survivors={len(survivors)} champions={len(champions)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
