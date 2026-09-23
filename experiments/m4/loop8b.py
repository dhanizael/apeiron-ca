"""Loop v8b — EKSPERIMEN KOMPOSISI (post-hoc, non-gated; log 014).

Latar: W3v8b FAIL 0/7 — headroom kapasitas INERT di atraktor aliran-bebas
(dinamika translasi murni, nilai tak pernah bercampur). Tempat yang benar:
rezim densitas +100% (log 013: 875 sel-3 dinamis parkir di sel-3 abadi).

Hipotesis pre-registered (sebelum run): pada instans +100% yang dimigrasi ke
k=4 — (a) lengan RECEIPT (fase-bungkus): sel-3 menerima → strata >3 tercapai
(mass memanjat), aliran bertahan; (b) lengan EMBEDDING: sel-3 tetap abadi
(max ≤ 3), parkiran bertahan. Kontras = bukti receipt membubarkan keabadian
sel-penuh — motivasi asli migrasi-k.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m3"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from density_map import load_v6_final, measure_point  # noqa: E402
from lift_k import lift_law, lift_state  # noqa: E402
from loop7 import base_state  # noqa: E402
from loop8 import run_k  # noqa: E402


def main() -> int:
    engine = str(ROOT / "engine" / "target" / "release" / "engine")
    k2, k4, n = 2, 4, 16384
    law2 = load_v6_final()
    outdir = Path(__file__).parent / "result"
    workdir = outdir / "_work"
    seeds = list(range(14001, 14008))

    rows = []
    for s in seeds:
        base = base_state(engine, law2, k2, n, s, workdir)
        mass0 = sum(base)
        sys.path.insert(0, str(ROOT / "experiments" / "m4"))
        from state_surgery import inject_lane, write_snapshot
        dense_cells, added = inject_lane(base, mass0, cap=2)  # +100% (v7 ambang)
        d = Path(workdir) / f"v8b_dense_state_{s}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "rule.bin").write_bytes(bytes(law2))
        write_snapshot(d / "state.bin", dense_cells, k2)
        import subprocess
        subprocess.run([engine, "run", "--n", str(n), "--k", str(k2), "--seed", str(s),
                        "--steps", "20000", "--window", "2",
                        "--rule-table", str(d / "rule.bin"),
                        "--init-state", str(d / "state.bin"), "--threads", "1",
                        "--outdir", str(d / "w")], check=True, capture_output=True)
        from state_surgery import read_state
        cells_dense = read_state(d / "w" / "final.bin", n, k2)
        cells4 = lift_state(cells_dense, k2, k4)
        out = {"seed": s, "mass_added": added, "dense_k2_max": max(cells_dense),
               "dense_k2_n3": cells_dense.count(3)}
        for arm, law4 in (("receipt", lift_law(law2, receipt=True)),
                          ("embedding", lift_law(law2, receipt=False))):
            full = run_k(engine, law4, cells4, k4, n, s, 20000, 512, workdir,
                         f"v8b_{arm}_{s}_full")
            out[arm] = {"max_cell": full["max_cell"], "n15": full["n15"],
                        "n_realized": full["n_realized"], "J": full["J"],
                        "static": full["static"],
                        "hist": full["hist"]}
        rows.append(out)
        print(f"seed {s}: dense_k2 max={out['dense_k2_max']} n3={out['dense_k2_n3']} | "
              f"receipt max={out['receipt']['max_cell']} n15={out['receipt']['n15']} "
              f"realized={out['receipt']['n_realized']} | "
              f"embedding max={out['embedding']['max_cell']} "
              f"realized={out['embedding']['n_realized']}")

    climb = sum(1 for x in rows if x["receipt"]["max_cell"] > 3)
    emb_stay = sum(1 for x in rows if x["embedding"]["max_cell"] <= 3)
    result = {
        "experiment": "M4-loop-v8b-compose",
        "hypothesis": "receipt memanjat ke strata >3; embedding tetap ≤3",
        "climb_rate_receipt": climb, "embedding_stays_le3": emb_stay,
        "rows": rows,
        "reproduce": "python experiments/m4/loop8b.py",
    }
    (outdir / "result_loop8b.json").write_text(json.dumps(result, indent=2))
    print("M4-LOOP-V8B", f"climb={climb}/7 embedding_stay_le3={emb_stay}/7")
    return 0


if __name__ == "__main__":
    sys.exit(main())
