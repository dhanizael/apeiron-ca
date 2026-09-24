"""SIRKUIT DUA-GERBANG (log 022): (A∧B)∧C dari dua gerbang law 22126.

Tata letak: gerbang-1 (memori 6 @8000, penjaga 2 @8001), input A @7990,
B @7986; kawat 76 sel; gerbang-2 (memori 6 @8080, penjaga 2 @8081), input
C @8070 (tiba dulu, MENAHAN satu setoran). Gerbang-1 memancar t≈15 →
output menempuh kawat → setoran kedua ke gerbang-2 → memancar.
Tabel kebenaran 8 baris (A,B,C) ∈ {0,1}³; vonis: out = (A∧B)∧C eksak.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m2"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca, io  # noqa: E402
from state_surgery import write_snapshot  # noqa: E402

N = 16384
STEPS = 150
P1, P2 = 8000, 8080


def build(a, b, c):
    cells = [0] * N
    cells[P1], cells[P1 + 1] = 6, 2      # gerbang-1
    cells[P2], cells[P2 + 1] = 6, 2      # gerbang-2
    if a:
        cells[P1 - 10] = 1
    if b:
        cells[P1 - 14] = 1
    if c:
        cells[P2 - 10] = 1
    return cells


def run_case(engine, law, a, b, c, workdir, tag):
    cells = build(a, b, c)
    d = Path(workdir) / tag
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law))
    write_snapshot(d / "init.bin", cells, 4)
    subprocess.run([engine, "run", "--n", str(N), "--k", "4", "--seed", "23001",
                    "--steps", str(STEPS), "--window", str(STEPS),
                    "--rule-table", str(d / "rule.bin"),
                    "--init-state", str(d / "init.bin"), "--threads", "1",
                    "--outdir", str(d / "w")], check=True, capture_output=True)
    m = io.read_manifest(d / "w" / "manifest.json")
    raw = io.read_window(d / "w" / "window.bin", N, m["window_states"], 4)
    states = [ca.unpack_cells(x, N, 4) for x in raw]
    g1 = [s[P1] for s in states]           # memori gerbang-1
    g2 = [s[P2] for s in states]           # memori gerbang-2
    g1_fired = 8 in g1
    g2_fired = 8 in g2
    tail = [s[P2 + 2: P2 + 40] for s in states[STEPS // 2:]]
    out_seen = any(any(v != 0 for v in seg) for seg in tail)
    for f in ("window.bin", "final.bin", "init.bin"):
        p = d / "w" / f
        if p.exists():
            p.unlink()
    return {"g1_fired": g1_fired, "g2_fired": g2_fired, "out_seen": out_seen,
            "g1_tail": g1[-4:], "g2_tail": g2[-4:]}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    cfg = ap.parse_args()
    outdir = Path(cfg.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    law = ca.random_table_rich(4, 22126)
    table, rows = {}, {}
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                r = run_case(cfg.engine, law, a, b, c, outdir / "_work",
                             f"c{a}{b}{c}")
                key = f"{a}{b}{c}"
                expected = 1 if (a and b and c) else 0
                got = 1 if r["g2_fired"] else 0
                table[key] = got
                rows[key] = {**r, "expected": expected}
                print(f"({a},{b},{c}): g1_fired={r['g1_fired']} g2_fired={r['g2_fired']} "
                      f"→ out={got} (harap {expected})")

    exact = all(table[k] == (1 if (int(k[0]) and int(k[1]) and int(k[2])) else 0)
                for k in table)
    # determinisme: ulang (1,1,1)
    r2 = run_case(cfg.engine, law, 1, 1, 1, outdir / "_work", "c111_rep")
    det = (r2["g2_fired"] == rows["111"]["g2_fired"])
    result = {
        "experiment": "two-gate-circuit",
        "law": "22126", "truth_table": table,
        "circuit_exact": bool(exact), "deterministic_rerun": bool(det),
        "rows": rows,
        "reproduce": "python experiments/m2/circuit.py",
    }
    (outdir / "circuit.json").write_text(json.dumps(result, indent=2))
    print("SIRKUIT-DUA-GERBANG", f"eksak={exact}", f"deterministik={det}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
