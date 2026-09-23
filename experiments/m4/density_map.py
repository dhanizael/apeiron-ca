"""Peta densitas hidup (loop v7, log 013): kurva J(ρ) digambar intervensi.

Untuk tiap kebijakan {uniform-cap2, lane-targeted} × level {10,25,50,100}% ×
massa: suntik ke keadaan atraktor v6-final → lanjutkan 20k (--init-state,
hukum utuh) → J, mobilitas, massa/n, rasio J/(massa/n) [identitas aliran-
bebas], himpunan entri terrealisasi, kemunculan sel-3. Ambang jenuh: level
pertama dengan rasio < 0,98 (per kebijakan).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m3"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca, io  # noqa: E402
from loop2 import binding_stats  # noqa: E402
from calibrate_freeze import j_from_states  # noqa: E402
from mutation_map import load_v5_final  # noqa: E402
from recover import run_window  # noqa: E402
from state_surgery import inject_lane, inject_uniform, read_state, write_snapshot  # noqa: E402

V6_FNV_PREFIX = "078681c4"
LEVELS = [0.10, 0.25, 0.50, 1.00]


def load_v6_final():
    v5 = load_v5_final()
    v6 = json.loads((ROOT / "experiments" / "m4" / "result" / "result_loop6.json").read_text())
    T = list(v5)
    for t in v6["trajectory"]:
        for e, d in t["committed"]:
            T[e] += d
    T = ca.clip_table(T, 2)
    fnv = f"{ca.table_fnv(T):016x}"
    assert fnv.startswith(V6_FNV_PREFIX), f"silsilah v6-final rusak: {fnv}"
    return T


def measure_point(engine, law, base_cells, k, n, policy, level, seed, steps, workdir, tag):
    mass0 = sum(base_cells)
    target = int(round(mass0 * level))
    if policy == "uniform":
        injected, added = inject_uniform(base_cells, target, cap=2, seed=seed)
    else:
        injected, added = inject_lane(base_cells, target, cap=2)
    d = Path(workdir) / f"dm_{tag}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law))
    write_snapshot(d / "state.bin", injected, k)
    subprocess_run(engine, n, k, seed, steps, d)
    m = io.read_manifest(d / "w" / "manifest.json")
    states = [ca.unpack_cells(s, n, k) for s in
              io.read_window(d / "w" / "window.bin", n, m["window_states"], k)]
    j, amb, static = j_from_states(states, k)
    pairs = [(list(a), list(b)) for a, b in zip(states[:-1], states[1:])]
    st = binding_stats(pairs, k)
    realized = [i for i in range(64) if st["count"][i] > 0]
    last = states[-1]
    n3 = sum(1 for v in last if v == 3)
    mn = sum(injected) / n
    ratio = (j / mn) if (j is not None and mn > 0) else None
    for f in ("window.bin", "final.bin", "state.bin"):
        p = d / f
        if p.exists():
            p.unlink()
    return {"policy": policy, "level": level, "seed": seed,
            "mass_added": added, "mass_per_n": round(mn, 6),
            "J": j, "static": static, "ratio_free_flow": (round(ratio, 4) if ratio else None),
            "n_realized": len(realized), "new_realized": sorted(set(realized) - {4, 5, 6, 8, 20, 24}),
            "n3_final": n3, "max_cell": max(last)}


def subprocess_run(engine, n, k, seed, steps, d):
    import subprocess
    subprocess.run([engine, "run", "--n", str(n), "--k", str(k), "--seed", str(seed),
                    "--steps", str(steps), "--window", "512",
                    "--rule-table", str(d / "rule.bin"),
                    "--init-state", str(d / "state.bin"), "--threads", "1",
                    "--outdir", str(d / "w")], check=True, capture_output=True)


def saturation(rows, policy):
    """Level pertama (menaik) dengan rasio < 0,98; None bila tak tercapai."""
    for r in sorted((x for x in rows if x["policy"] == policy), key=lambda x: x["level"]):
        if r["ratio_free_flow"] is None or r["ratio_free_flow"] < 0.98:
            return r["level"]
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    ap.add_argument("--n", type=int, default=16384)
    a = ap.parse_args()

    k, n = 2, a.n
    law = load_v6_final()
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"

    # keadaan atraktor induk (seed 13001)
    d = workdir / "base_13001"
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law))
    import subprocess
    subprocess.run([a.engine, "run", "--n", str(n), "--k", str(k), "--uniform",
                    "--seed", "13001", "--steps", "20000", "--window", "2",
                    "--rule-table", str(d / "rule.bin"), "--threads", "1",
                    "--init-cap", "1", "--outdir", str(d / "w")],
                   check=True, capture_output=True)
    base = read_state(d / "w" / "final.bin", n, k)
    mass0 = sum(base)
    print(f"base: massa={mass0} massa/n={mass0 / n:.4f}")

    rows = []
    for policy in ("uniform", "lane"):
        for level in LEVELS:
            r = measure_point(a.engine, law, base, k, n, policy, level, 13001,
                              20000, workdir, f"{policy}_{level}")
            rows.append(r)
            print(f"{policy:8s} +{level:.0%}: J={r['J']!r:20s} massa/n={r['mass_per_n']:.4f} "
                  f"rasio={r['ratio_free_flow']} stat={r['static']} "
                  f"realized={r['n_realized']} baru={len(r['new_realized'])} n3={r['n3_final']}")

    thresholds = {p: saturation(rows, p) for p in ("uniform", "lane")}
    result = {
        "experiment": "density-map",
        "law": "v6-final", "base_mass": mass0, "seeds": [13001], "k": k, "n": n,
        "thresholds": thresholds, "rows": rows,
        "reproduce": "python experiments/m4/density_map.py",
    }
    (outdir / "density_map.json").write_text(json.dumps(result, indent=2))
    print("DENSITY-MAP thresholds:", thresholds)
    return 0


if __name__ == "__main__":
    sys.exit(main())
