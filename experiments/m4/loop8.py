"""M4 loop v8 — MIGRASI-K: angkat semesta k=2 → k=4 (log 014).

Per instans (7 segar, 14001–07): atraktor induk 20k (hukum v6-final, cap1)
→ migrasi state (massa eksak) → lanjut 20k DI BAWAH HUKUM LIFT, dua lengan
seed-sama: phase-wrap (receipt) vs embedding-murni (kontrol).
Pengukuran: massa eksak, J, rasio J/(massa/n), statis, max-cell, histogram,
entri terrealisasi (growth meter @2000/@20000), jumlah sel-15.

Kriteria (dibekukan log 014):
  W3v8a: phase-wrap 7/7 — massa eksak, tak statis @20k, J/(massa/n) ≥ 0,90.
  W3v8b: ≥ 6/7 instans max-cell > 3 DAN entri terrealisasi > 6 @20k
         (kontrol embedding dilaporkan berdampingan).
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
from calibrate_freeze import j_from_states  # noqa: E402
from lift_k import lift_law, lift_state  # noqa: E402
from loop2 import binding_stats  # noqa: E402
from density_map import load_v6_final  # noqa: E402
from state_surgery import write_snapshot  # noqa: E402


def run_k(engine, law, state_cells, k, n, seed, steps, window, workdir, tag):
    """Run k-generic dari snapshot state → J, statis, max-cell, realized."""
    d = Path(workdir) / tag
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law))
    write_snapshot(d / "state.bin", state_cells, k)
    subprocess.run([engine, "run", "--n", str(n), "--k", str(k), "--seed", str(seed),
                    "--steps", str(steps), "--window", str(window),
                    "--rule-table", str(d / "rule.bin"),
                    "--init-state", str(d / "state.bin"), "--threads", "1",
                    "--outdir", str(d / "w")], check=True, capture_output=True)
    m = io.read_manifest(d / "w" / "manifest.json")
    states = [ca.unpack_cells(s, n, k) for s in
              io.read_window(d / "w" / "window.bin", n, m["window_states"], k)]
    j, amb, static = j_from_states(states, k)
    pairs = [(list(a), list(b)) for a, b in zip(states[:-1], states[1:])]
    st = binding_stats(pairs, k)
    realized = [i for i in range(1 << (3 * k)) if st["count"][i] > 0]
    last = states[-1]
    hist = {}
    for v in last:
        hist[str(v)] = hist.get(str(v), 0) + 1
    for f in ("window.bin", "final.bin", "state.bin"):
        p = d / "w" / f
        if p.exists():
            p.unlink()
    return {"J": j, "amb": amb, "static": static, "mass": sum(last),
            "max_cell": max(last), "n15": last.count((1 << k) - 1),
            "hist": dict(sorted(hist.items(), key=lambda kv: -kv[1])),
            "n_realized": len(realized), "realized_head": sorted(realized)[:12]}


def migrate_instance(engine, law2, k2, k4, n, seed, steps_full, steps_ckpt,
                     window, workdir):
    d = Path(workdir) / f"base_{seed}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law2))
    subprocess.run([engine, "run", "--n", str(n), "--k", str(k2), "--uniform",
                    "--seed", str(seed), "--steps", "20000", "--window", "2",
                    "--rule-table", str(d / "rule.bin"), "--threads", "1",
                    "--init-cap", "1", "--outdir", str(d / "w")],
                   check=True, capture_output=True)
    import sys as _s
    _s.path.insert(0, str(ROOT / "experiments" / "m4"))
    from state_surgery import read_state
    cells2 = read_state(d / "w" / "final.bin", n, k2)
    cells4 = lift_state(cells2, k2, k4)
    out = {}
    for arm, law4 in (("receipt", lift_law(law2, receipt=True)),
                      ("embedding", lift_law(law2, receipt=False))):
        ck = run_k(engine, law4, cells4, k4, n, seed, steps_ckpt, 32, workdir,
                   f"{arm}_{seed}_ck")
        full = run_k(engine, law4, cells4, k4, n, seed, steps_full, 512, workdir,
                     f"{arm}_{seed}_full")
        out[arm] = {"checkpoint_2000": {"n_realized": ck["n_realized"]},
                    "full": full}
    out["mass_source"] = sum(cells2)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mini", action="store_true")
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    a = ap.parse_args()

    if a.mini:
        k2, k4, n = 2, 4, 128
        steps_full, steps_ckpt = 800, 200
        seeds = [141, 142]
    else:
        k2, k4, n = 2, 4, 16384
        steps_full, steps_ckpt = 20000, 2000
        seeds = list(range(14001, 14008))

    law2 = load_v6_final()
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"

    rows = []
    for s in seeds:
        r = migrate_instance(a.engine, law2, k2, k4, n, s, steps_full,
                             steps_ckpt, 512, workdir)
        mass_ok = (r["receipt"]["full"]["mass"] == r["mass_source"]
                   and r["embedding"]["full"]["mass"] == r["mass_source"])
        fr = r["receipt"]["full"]
        mn = r["mass_source"] / n
        ratio = fr["J"] / mn if fr["J"] is not None else None
        fr["mass_ok"] = mass_ok
        fr["ratio_free_flow"] = round(ratio, 4) if ratio else None
        rows.append(r)
        print(f"seed {s}: receipt J={fr['J']!r} rasio={r['receipt']['ratio_free_flow']} "
              f"max={fr['max_cell']} realized={fr['n_realized']} n15={fr['n15']} "
              f"| embedding: max={r['embedding']['full']['max_cell']} "
              f"realized={r['embedding']['full']['n_realized']}")

    rec = [x["receipt"]["full"] for x in rows]
    w3a = bool(all(x["mass_ok"] and not x["static"]
                   and (x["ratio_free_flow"] or 0) >= 0.90 for x in rec))
    new_strata = sum(1 for x in rec if x["max_cell"] > 3 and x["n_realized"] > 6)
    w3b = bool(new_strata >= min(6, len(rows)))
    emb = [x["embedding"]["full"] for x in rows]
    result = {
        "experiment": "M4-loop-v8",
        "mode": "mini" if a.mini else "full",
        "criteria": {"W3v8a_migration_intact": w3a,
                     "W3v8b_new_strata": w3b, "new_strata_count": new_strata},
        "control_embedding_summary": {
            "max_cell": max(x["max_cell"] for x in emb),
            "n_realized": sorted({x["n_realized"] for x in emb})},
        "iterations": len(rows),
        "rows": rows,
        "reproduce": f"python experiments/m4/loop8.py{' --mini' if a.mini else ''}",
    }
    (outdir / "result_loop8.json").write_text(json.dumps(result, indent=2))
    print("M4-LOOP-V8", f"W3v8a={'PASS' if w3a else 'FAIL'}",
          f"W3v8b={'PASS' if w3b else 'FAIL'}", f"strata={new_strata}/{len(rows)}",
          f"| kontrol embedding max={max(x['max_cell'] for x in emb)} "
          f"realized={sorted({x['n_realized'] for x in emb})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
