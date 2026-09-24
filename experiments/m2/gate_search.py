"""Pencarian hukum-gerbang (log 021): filter aljabar + verifikasi empiris.

Kondisi aljabar untuk (memori m, penjaga kr) pada tabel k=4:
(1) idle F[0,m,kr]=0; (2) deposit F[l,1,m]≠0 l∈{0,1}; (3) pasca-1
F[0,m+1,kr]=0; (4) emit F[0,m+2,kr]≠0; (5) penjaga F[m,kr,0]=0;
(6) travel F[0,1,0]≠0.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m2"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca  # noqa: E402

K = 4
SZ = 1 << (3 * K)


def idx(l, c, r):
    return ((l & 15) << 8) | ((c & 15) << 4) | (r & 15)


def gate_configs(law):
    """Semua (m, kr) yang lolos keenam kondisi aljabar."""
    out = []
    for kr in range(1, 15):
        for m in range(1, 14):
            if law[idx(0, m, kr)] != 0:
                continue                                    # (1) idle
            if not all(law[idx(l, 1, m)] != 0 for l in (0, 1)):
                continue                                    # (2) deposit
            if law[idx(0, m + 1, kr)] != 0:
                continue                                    # (3) pasca-1
            if law[idx(0, m + 2, kr)] == 0:
                continue                                    # (4) emit
            if law[idx(m, kr, 0)] != 0:
                continue                                    # (5) penjaga
            if law[idx(0, 1, 0)] == 0:
                continue                                    # (6) travel
            out.append((m, kr))
    return out


def empirical_gate(engine, law, m, kr, workdir, tag, n=16384, steps=60):
    """4 run tabel kebenaran; kolom output + detail."""
    import subprocess
    P = 8000
    col, rows = [], {}
    for a, b in ((0, 0), (1, 0), (0, 1), (1, 1)):
        cells = [0] * n
        cells[P] = m
        cells[P + 1] = kr
        if a:
            cells[P - 10] = 1
        if b:
            cells[P - 14] = 1
        d = Path(workdir) / f"{tag}_{a}{b}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "rule.bin").write_bytes(bytes(law))
        write_snapshot(d / "init.bin", cells, K)
        subprocess.run([engine, "run", "--n", str(n), "--k", str(K), "--seed", "20001",
                        "--steps", str(steps), "--window", str(steps),
                        "--rule-table", str(d / "rule.bin"),
                        "--init-state", str(d / "init.bin"), "--threads", "1",
                        "--outdir", str(d / "w")], check=True, capture_output=True)
        mi = io.read_manifest(d / "w" / "manifest.json")
        raw = io.read_window(d / "w" / "window.bin", n, mi["window_states"], K)
        states = [ca.unpack_cells(x, n, K) for x in raw]
        mem_traj = [s[P] for s in states]
        # output: sel ≠ 0 di hilir (pos > P+1) pada paruh kedua
        tail = [s[P + 2: P + 40] for s in states[steps // 2:]]
        out_seen = any(any(v != 0 for v in seg) for seg in tail)
        col.append(1 if out_seen else 0)
        for f in ("window.bin", "final.bin", "init.bin"):
            p = d / "w" / f
            if p.exists():
                p.unlink()
        rows[f"{a}{b}"] = {"mem_traj": mem_traj[:16], "out_seen": out_seen}
    return {"column": col, "rows": rows}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    ap.add_argument("--n-laws", type=int, default=300)
    ap.add_argument("--verify-max", type=int, default=10)
    a = ap.parse_args()
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    passed, verified = [], []
    for i in range(a.n_laws):
        sl = 22001 + i
        law = ca.random_table_rich(K, sl)
        cfgs = gate_configs(law)
        if cfgs:
            passed.append({"law_seed": sl, "configs": cfgs[:6],
                           "n_configs": len(cfgs)})
    print(f"filter aljabar: {len(passed)}/{a.n_laws} hukum lolos")

    for rec in passed[: a.verify_max]:
        sl = rec["law_seed"]
        law = ca.random_table_rich(K, sl)
        m, kr = rec["configs"][0]
        r = empirical_gate(a.engine, law, m, kr, outdir / "_work", f"g{sl}")
        col = r["column"]
        nontrivial = col[3] > max(col[1], col[2]) or (col[3] == 1 and col[1] == 0 and col[2] == 0 and max(col) == 1)
        rec.update({"empirical_column": col, "empirical_rows": r["rows"],
                    "nontrivial": bool(nontrivial)})
        verified.append(rec)
        print(f"law {sl} (m={m},kr={kr}): kolom={col} "
              f"{'NON-TRIVIAL' if nontrivial else 'trivial/global'}")

    ands = [r for r in verified if r["empirical_column"] == [0, 0, 0, 1]]
    result = {
        "experiment": "gate-law-search",
        "algebra_passed": len(passed), "n_laws": a.n_laws,
        "verified": verified,
        "nontrivial_count": sum(1 for r in verified if r["nontrivial"]),
        "and_laws": [r["law_seed"] for r in ands],
        "reproduce": f"python experiments/m2/gate_search.py --n-laws {a.n_laws}",
    }
    (outdir / "gate_search.json").write_text(json.dumps(result, indent=2))
    print("GATE-SEARCH", f"algebra={len(passed)}/{a.n_laws}",
          f"nontrivial={result['nontrivial_count']}/{len(verified)}",
          f"AND={len(ands)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
