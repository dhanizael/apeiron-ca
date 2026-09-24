"""PERPETUUM sweep (log 018): cari hukum yang populasinya tak pernah selesai.

Sapu: k=2 (300 hukum slack-rich, IC {all-1, all-2, difus-0.5}) + k=4 (150
hukum, IC {all-1, all-2, all-3, difus-0.5}), 2000 langkah, window 1000,
sensus populasi per spesies. Fitness = definisi beku log 018 (amplitudo-ekor
≥ 0,3, koeksistensi, tak-statis). Kandidat → --verify: 3 seed × 20k langkah
(kriteria dievaluasi di sepertiga akhir 20k).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m2"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from perpetuum import perpetuum_verdict, pop_trajectories  # noqa: E402
from semesta import ca, io  # noqa: E402
from state_surgery import write_snapshot  # noqa: E402

N = 16384


def uniform_sea(v, n):
    return [v] * n


def diffuse_sea(n, seed, p=0.5, values=(0, 1)):
    rng = ca.Rng(seed)
    vs = list(values)
    return [vs[rng.next_u64() % len(vs)] for _ in range(n)]


def run_pop(engine, law, k, cells, seed, steps, workdir, tag, window=1000):
    d = Path(workdir) / tag
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law))
    write_snapshot(d / "init.bin", cells, k)
    subprocess.run([engine, "run", "--n", str(N), "--k", str(k), "--seed", str(seed),
                    "--steps", str(steps), "--window", str(window),
                    "--rule-table", str(d / "rule.bin"),
                    "--init-state", str(d / "init.bin"), "--threads", "1",
                    "--outdir", str(d / "w")], check=True, capture_output=True)
    m = io.read_manifest(d / "w" / "manifest.json")
    raw = io.read_window(d / "w" / "window.bin", N, m["window_states"], k)
    states = [ca.unpack_cells(raw[j], N, k) for j in range(0, len(raw), 5)]
    trajs, rings = pop_trajectories(states, k)
    for f in ("window.bin", "final.bin", "init.bin"):
        p = d / "w" / f
        if p.exists():
            p.unlink()
    return perpetuum_verdict(trajs, rings, k)


def ics_for(k):
    ics = [("all1", uniform_sea(1, N)), ("all2", uniform_sea(2, N))]
    if k == 4:
        ics.append(("all3", uniform_sea(3, N)))
    ics.append(("difus", diffuse_sea(N, 20001)))
    return ics


def sweep(engine, outdir, n_k2=300, n_k4=150, steps=2000):
    workdir = outdir / "_work"
    cands, fate = [], {"absorbed": 0, "pulsed": 0, "alive": 0}
    for k, laws in ((2, n_k2), (4, n_k4)):
        for i in range(laws):
            sl = (19001 + i) if k == 2 else (19501 + i)
            law = ca.random_table_rich(k, sl)
            for name, cells in ics_for(k):
                v = run_pop(engine, law, k, cells, 15002, steps, workdir,
                            f"p{k}_{sl}_{name}")
                if v["perpetuum"]:
                    cands.append({"law_seed": sl, "k": k, "ic": name, **{
                        kk: v[kk] for kk in ("coex", "amp_max", "amp_species",
                                             "predation")}})
                    print(f"KANDIDAT k={k} law={sl} IC={name}: amp={v['amp_max']} "
                          f"(sp {v['amp_species']}) coex={v['coex']}")
                elif v["amp_max"] >= 0.3 and v["coex"] < 2:
                    fate["pulsed"] += 1
                elif v["amp_max"] is not None and v["amp_max"] < 0.1 and v["static_last3"]:
                    fate["absorbed"] += 1
                else:
                    fate["alive"] += 1
            if (i + 1) % 50 == 0:
                print(f"  …k{k}: {i+1}/{laws} hukum, {len(cands)} kandidat, nasib {fate}")
    return cands, fate


def verify(engine, outdir, cand, steps=20000):
    """3 seed × 20k — kriteria dievaluasi di sepertiga akhir 20k."""
    workdir = outdir / "_verify"
    law = ca.random_table_rich(cand["k"], cand["law_seed"])
    results = []
    for s in (15101, 15102, 15103):
        ics = dict(ics_for(cand["k"]))
        cells = ics[cand["ic"]]
        v = run_pop(engine, law, cand["k"], cells, s, steps, workdir,
                    f"v_{cand['law_seed']}_{s}", window=6000)
        results.append({"seed": s, "perpetuum": v["perpetuum"],
                        "amp_max": v["amp_max"], "coex": v["coex"],
                        "static": v["static_last3"], "predation": v["predation"]})
    ok = all(r["perpetuum"] for r in results)
    return {"verified": ok, "results": results}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    ap.add_argument("--verify-law", type=int, default=0, help="seed hukum kandidat untuk verifikasi")
    ap.add_argument("--verify-k", type=int, default=0)
    ap.add_argument("--verify-ic", default="")
    a = ap.parse_args()
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if a.verify_law:
        cand = {"law_seed": a.verify_law, "k": a.verify_k, "ic": a.verify_ic}
        v = verify(a.engine, outdir, cand)
        (outdir / f"perpetuum_verify_{a.verify_law}.json").write_text(json.dumps(
            {"candidate": cand, **v}, indent=2))
        print("M2-PERPETUUM-VERIFY", f"law={a.verify_law}",
              f"verified={v['verified']}", json.dumps(v["results"]))
        return 0

    cands, fate = sweep(a.engine, outdir)
    result = {
        "experiment": "perpetuum-sweep",
        "criteria": {"W_P1_perpetuum": bool(cands)},
        "candidates": cands, "fate_counts": fate,
        "reproduce": "python experiments/m2/perpetuum_search.py",
    }
    (outdir / "perpetuum_sweep.json").write_text(json.dumps(result, indent=2))
    print("PERPETUUM-SWEEP", f"kandidat={len(cands)}", f"nasib={fate}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
