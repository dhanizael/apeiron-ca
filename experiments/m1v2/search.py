"""M1v2 — hipotesis slack (log 006): dua lengan generator, kriteria di horizon.

Arm POOR: generator lama (0..255 → clip — entri lahir menempel cap).
Arm RICH : generator baru (uniform [0, cap] — slack terjaga).
Mutasi tahap B dua arah (±1). Kriteria juara dinilai LANGSUNG di horizon 10⁶
(koreksi 003). Verdict: V1 (≥1 juara per lengan lolos horizon) + V2 (hipotesis
slack: pass-rate RICH > POOR di tahap A?).
"""
import argparse
import json
import multiprocessing as mp
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))

from semesta import ca  # noqa: E402

M1V2 = Path(__file__).parent


def probe_candidate(engine, n, k, seed, steps, probe_every, rule_path, threads=1):
    out = subprocess.run(
        [engine, "probe", "--n", str(n), "--k", str(k), "--seed", str(seed),
         "--steps", str(steps), "--probe-every", str(probe_every),
         "--rule-table", str(rule_path), "--threads", str(threads)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(out.stdout.strip())


def _probe_one(task):
    engine, n, k, seed, steps, every, table_bytes, workdir = task
    wd = Path(workdir)
    wd.mkdir(parents=True, exist_ok=True)
    rp = wd / f"rule_{k}_{seed}.bin"
    rp.write_bytes(table_bytes)
    return probe_candidate(engine, n, k, seed, steps, every, rp, threads=1)


def exclusion_streak(rep):
    longest = cur = 0
    for _t, top, total in rep["top3_series"]:
        if total > 0 and top * 5 >= total * 4:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0
    return longest


def passes_horizon(rep, min_life_steps, streak_cap, probe_every):
    _t, top, total = rep["top3_series"][-1]
    if total > 0 and top * 5 >= total * 4:
        return False
    if exclusion_streak(rep) > streak_cap:
        return False
    if rep["particles_final"] < 1:
        return False
    life_obs_needed = max(1, -(-min_life_steps // probe_every))
    return rep["max_lifetime"] >= life_obs_needed


def mutate_bidir(table, k, rng):
    """Mutasi DUA ARAH (pelajaran capacity-bound): ±1 pada 1-2 entri, re-clip."""
    t = list(table)
    for _ in range(1 + rng.next_u64() % 2):
        pos = rng.next_u64() % len(t)
        t[pos] += 1 if rng.next_u64() % 2 else -1
    return ca.clip_table(t, k)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mini", action="store_true")
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(M1V2 / "result"))
    a = ap.parse_args()

    if a.mini:
        n_a, steps_a, every_a = 256, 2000, 100
        n_per_arm, min_life_a, streak_cap = 40, 500, 3
        n_b, steps_b = 256, 4000
        horizon, rounds, mutants, top_keep = 4000, 1, 4, 2
    else:
        n_a, steps_a, every_a = 4096, 20000, 1000
        n_per_arm, min_life_a, streak_cap = 6000, 5000, 10
        n_b, steps_b = 16384, 100000
        horizon, rounds, mutants, top_keep = 10 ** 6, 2, 8, 2

    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"
    workdir.mkdir(exist_ok=True)

    arms = {
        "POOR": lambda seed, k: ca.clip_table(ca.random_table(k, seed), k),
        "RICH": lambda seed, k: ca.random_table_rich(k, seed),
    }

    # ---------- Tahap A: dua lengan ----------
    tasks, meta = [], []
    for arm, gen in arms.items():
        for i in range(n_per_arm):
            k = 2 if i % 2 == 0 else 4
            seed = (0 if arm == "POOR" else 500000) + i + 1
            table = gen(seed, k)
            tasks.append((a.engine, n_a, k, seed, steps_a, every_a, bytes(table), str(workdir)))
            meta.append((arm, k, seed))
    workers = min(12, mp.cpu_count() or 1)
    with mp.Pool(workers) as pool:
        reps = pool.map(_probe_one, tasks)

    rows, survivors = [], {"POOR": [], "RICH": []}
    with open(outdir / "results.jsonl", "w") as fh:
        for (arm, k, seed), rep in zip(meta, reps):
            ok = passes_horizon(rep, min_life_a, streak_cap, every_a)
            row = {"stage": "A", "arm": arm, "k": k, "seed": seed,
                   "slack_fraction": round(ca.slack_fraction(
                       arms[arm](seed, k), k), 4),
                   "particles_final": rep["particles_final"],
                   "max_lifetime": rep["max_lifetime"],
                   "passes": ok}
            fh.write(json.dumps(row) + "\n")
            if ok:
                survivors[arm].append({"arm": arm, "k": k, "seed": seed,
                                       "table": arms[arm](seed, k),
                                       "score": rep["max_lifetime"]})

    # ---------- Tahap B: mutasi dua arah, per lengan ----------
    pool_list = {arm: sorted(survivors[arm], key=lambda x: -x["score"])[:top_keep]
                 for arm in arms}
    rng = ca.Rng(424242)
    for rnd in range(rounds):
        for arm in arms:
            cands = []
            for s in pool_list[arm][:top_keep]:
                for m in range(mutants):
                    t = mutate_bidir(s["table"], s["k"], rng)
                    seed_m = 700000 + rnd * 100000 + s["seed"] * 10 + m
                    rp = workdir / f"rule_{arm}_{rnd}_{s['seed']}_{m}.bin"
                    rp.write_bytes(bytes(t))
                    rep = probe_candidate(a.engine, n_b, s["k"], seed_m % 100000,
                                          steps_b, every_a, rp)
                    cands.append({"arm": arm, "k": s["k"], "seed": seed_m,
                                  "table": t, "score": rep["max_lifetime"]})
            pool_list[arm] = sorted(pool_list[arm] + cands,
                                    key=lambda x: -x["score"])[:top_keep]

    # ---------- Tahap C: kriteria LANGSUNG di horizon ----------
    champions = []
    for arm in arms:
        for s in pool_list[arm][:top_keep]:
            rp = workdir / f"rule_H_{arm}_{s['seed']}.bin"
            rp.write_bytes(bytes(s["table"]))
            rep = probe_candidate(a.engine, n_b, s["k"], s["seed"] % 100000,
                                  horizon, every_a, rp)
            ok = passes_horizon(rep, min_life_a * 10 if not a.mini else 500,
                                streak_cap, every_a)
            champions.append({
                "arm": arm, "k": s["k"], "seed": s["seed"],
                "table_fnv": f"{ca.table_fnv(s['table']):016x}",
                "slack_fraction": round(ca.slack_fraction(s["table"], s["k"]), 4),
                "horizon": horizon,
                "particles_final": rep["particles_final"],
                "max_lifetime": rep["max_lifetime"],
                "exclusion_streak_max": exclusion_streak(rep),
                "passes_horizon": bool(ok),
            })

    v1 = (any(c["arm"] == "POOR" and c["passes_horizon"] for c in champions)
          and any(c["arm"] == "RICH" and c["passes_horizon"] for c in champions))
    rate = {arm: (len(survivors[arm]) / n_per_arm) for arm in arms}
    v2 = ("supported" if rate["RICH"] > rate["POOR"]
          else "not-supported" if rate["POOR"] > rate["RICH"] else "inconclusive")

    result = {
        "experiment": "M1v2-slack-hypothesis",
        "mode": "mini" if a.mini else "full",
        "criteria": {
            "V1_champions_both_arms_at_horizon": bool(v1),
            "V2_slack_hypothesis": v2,
        },
        "pass_rates": rate,
        "n_survivors": {arm: len(survivors[arm]) for arm in arms},
        "champions": champions,
        "reproduce": f"python experiments/m1v2/search.py{' --mini' if a.mini else ''}",
    }
    (outdir / "result.json").write_text(json.dumps(result, indent=2))
    print("M1V2", json.dumps(result["criteria"]),
          f"pass_rates={json.dumps(rate)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
