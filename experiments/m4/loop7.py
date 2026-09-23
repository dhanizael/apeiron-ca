"""M4 loop v7 — verdict regulasi densitas (log 013).

W3v7a: kebijakan terbaik peta (level dengan identitas sempurna & J tertinggi
= +50%) pada 7 instans segar (13011–17): tiap instans → atraktor induk 20k →
suntik +50% (lane-targeted) → lanjut 20k → wajib J ≥ 0,60, rasio ∈ [0,98;
1,02], tak statis. Baseline tanpa-suntik diukur berdampingan (paired).
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
from density_map import load_v6_final, measure_point  # noqa: E402
from state_surgery import read_state  # noqa: E402
import subprocess  # noqa: E402


def base_state(engine, law, k, n, seed, workdir):
    d = Path(workdir) / f"base_{seed}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law))
    subprocess.run([engine, "run", "--n", str(n), "--k", str(k), "--uniform",
                    "--seed", str(seed), "--steps", "20000", "--window", "2",
                    "--rule-table", str(d / "rule.bin"), "--threads", "1",
                    "--init-cap", "1", "--outdir", str(d / "w")],
                   check=True, capture_output=True)
    return read_state(d / "w" / "final.bin", n, k)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mini", action="store_true")
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    a = ap.parse_args()

    if a.mini:
        k, n = 2, 128
        steps = 800
        seeds = list(range(71, 78))
        level, policy = 0.50, "lane"
    else:
        k, n = 2, 16384
        steps = 20000
        seeds = list(range(13011, 13018))
        level, policy = 0.50, "lane"  # terbaik dari peta 013 (identitas sempurna)

    law = load_v6_final()
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"

    rows = []
    for s in seeds:
        base = base_state(a.engine, law, k, n, s, workdir)
        b = measure_point(a.engine, law, base, k, n, policy, 0.0, s, steps, workdir, f"b_{s}")
        r = measure_point(a.engine, law, base, k, n, policy, level, s, steps, workdir, f"r_{s}")
        ok = (r["J"] is not None and r["J"] >= 0.60
              and r["ratio_free_flow"] is not None
              and 0.98 <= r["ratio_free_flow"] <= 1.02
              and not r["static"])
        rows.append({"seed": s, "baseline": b, "injected": r, "pass": ok})
        print(f"seed {s}: J {b['J']:.4f} → {r['J']:.4f} (massa/n {r['mass_per_n']:.4f}, "
              f"rasio {r['ratio_free_flow']}) {'PASS' if ok else 'FAIL'}")

    rate = sum(x["pass"] for x in rows) / len(rows)
    w3a = bool(rate >= 1.0)
    result = {
        "experiment": "M4-loop-v7",
        "mode": "mini" if a.mini else "full",
        "criteria": {"W3v7a_density_control": w3a, "rate": rate},
        "policy": {"level": level, "name": policy},
        "rows": rows,
        "reproduce": f"python experiments/m4/loop7.py{' --mini' if a.mini else ''}",
    }
    (outdir / "result_loop7.json").write_text(json.dumps(result, indent=2))
    print("M4-LOOP-V7", f"W3v7a={'PASS' if w3a else 'FAIL'}", f"rate={rate:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
