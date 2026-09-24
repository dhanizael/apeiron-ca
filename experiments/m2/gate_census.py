"""Census empiris gerbang (log 023 lanjutan): 300 hukum × 4-run tabel
kebenaran — TANPA filter aljabar (terbukti over-prediksi 3×). Flag kolom
[0,0,0,1] (AND) dan non-trivial."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "m2"))

from gate_search import empirical_gate  # noqa: E402
from semesta import ca  # noqa: E402


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    ap.add_argument("--n-laws", type=int, default=300)
    ap.add_argument("--seed0", type=int, default=22001)
    a = ap.parse_args()
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ands, nontrivial, cols = [], [], []
    for i in range(a.n_laws):
        sl = a.seed0 + i
        law = ca.random_table_rich(4, sl)
        cfg = [(6, 2)]
        r = empirical_gate(a.engine, law, 6, 2, outdir / "_work", f"c_{sl}")
        col = r["column"]
        cols.append(col)
        if col == [0, 0, 0, 1]:
            ands.append(sl)
            print(f"AND law={sl}")
        elif col[3] > max(col[1], col[2]) and col != [1, 1, 1, 1]:
            nontrivial.append({"law": sl, "col": col})
        if (i + 1) % 50 == 0:
            print(f"  …{i+1}/{a.n_laws}: AND={len(ands)} nontrivial={len(nontrivial)}")
    result = {"n_laws": a.n_laws, "and_laws": ands,
              "nontrivial": nontrivial,
              "col_histogram": {str(c): cols.count(c) for c in set(map(tuple, cols))}}
    (outdir / "gate_census.json").write_text(json.dumps(result, indent=2))
    print("GATE-CENSUS", f"AND={len(ands)}", f"nontrivial={len(nontrivial)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
