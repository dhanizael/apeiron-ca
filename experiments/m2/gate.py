"""GERBANG PERTAMA (log 020): gerbang AND di semusta flow — tabel kebenaran.

Dunia: k=4 phase-wrap receipt (lift v6-final). Perangkat: parkiran-3 (P) +
penjaga-1 (P+1). Input: pulsa-1 disuntik di hulu (P−10 = A, P−14 = B),
berjalan 1/langkah, MENYETOR ke parkiran saat menghitung P−1, terkonsumsi.
Dua setoran → parkiran 5 → memancar → penjaga melepas pulsa output yang
berjalan ke hilir. Semantik aljabar: output = AND(A,B).

Empat run tabel kebenaran (A,B) ∈ {00,10,01,11}; kolom output dibaca dari
census pulsa di hilir (posisi > P+1) + trajektori parkiran.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m2"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from density_map import load_v6_final  # noqa: E402
from lift_k import lift_law  # noqa: E402
from semesta import ca, io  # noqa: E402
from state_surgery import write_snapshot  # noqa: E402

N = 16384
P = 8000          # posisi parkiran
STEPS = 60        # A tiba ~t=9-10, B ~t=13-14, emit ~t=15, output jalan sampai t=60
PARK, KEEPER = 3, 1


def build_state(a, b):
    """Laut nol + parkiran P + penjaga P+1 + pulsa A (P−10) dan B (P−14)."""
    cells = [0] * N
    cells[P] = PARK
    cells[P + 1] = KEEPER
    if a:
        cells[P - 10] = 1
    if b:
        cells[P - 14] = 1
    return cells


def run_case(engine, law4, a, b, workdir, tag):
    cells = build_state(a, b)
    d = Path(workdir) / tag
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law4))
    write_snapshot(d / "init.bin", cells, 4)
    subprocess = __import__("subprocess")
    subprocess.run([engine, "run", "--n", str(N), "--k", "4", "--seed", "20001",
                    "--steps", str(STEPS), "--window", str(STEPS),
                    "--rule-table", str(d / "rule.bin"),
                    "--init-state", str(d / "init.bin"), "--threads", "1",
                    "--outdir", str(d / "w")], check=True, capture_output=True)
    m = io.read_manifest(d / "w" / "manifest.json")
    raw = io.read_window(d / "w" / "window.bin", N, m["window_states"], 4)
    states = [ca.unpack_cells(x, N, 4) for x in raw]
    park_traj = [s[P] for s in states]
    keeper_traj = [s[P + 1] for s in states]
    # pulsa output: ada sel=1 di posisi > P+1 pada ujung window
    out_tail = [s[P + 2: P + 40] for s in states]
    output_seen = any(1 in seg for seg in out_tail[STEPS // 2:])
    output_max_pos = max((seg.index(1) + P + 2
                          for seg in out_tail if 1 in seg), default=None)
    consumed = states[-1][P - 10] == 0 and states[-1][P - 14] == 0
    return {"park_traj": park_traj, "keeper_tail": keeper_traj[-6:],
            "output_seen": output_seen, "output_max_pos": output_max_pos,
            "inputs_consumed": consumed, "final_park": states[-1][P]}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    cfg = ap.parse_args()
    outdir = Path(cfg.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    law4 = lift_law(load_v6_final(), receipt=True)
    truth = {}
    rows = {}
    for a, b in ((0, 0), (1, 0), (0, 1), (1, 1)):
        r = run_case(cfg.engine, law4, a, b, outdir / "_work", f"gate_{a}{b}")
        rows[f"{a}{b}"] = r
        # output Boolean: parkiran mencapai 5 (ambang terpancing) → emit
        truth[f"{a}{b}"] = 1 if 5 in r["park_traj"] else 0
        print(f"({a},{b}): park {r['park_traj'][:20]}… final={r['final_park']} "
              f"output_seen={r['output_seen']} konsumsi={r['inputs_consumed']} "
              f"→ out={truth[f'{a}{b}']}")

    col = [truth["00"], truth["10"], truth["01"], truth["11"]]
    is_and = col == [0, 0, 0, 1]
    # determinisme: parkir trajektori run (1,1) harus eksak sama saat diulang
    r2 = run_case(cfg.engine, law4, 1, 1, outdir / "_work", "gate_11_rep")
    det = r2["park_traj"] == rows["11"]["park_traj"]

    result = {
        "experiment": "first-gate",
        "law": "receipt-lift v6-final (k=4)",
        "truth_table": truth, "output_column": col, "is_and": bool(is_and),
        "deterministic_rerun": bool(det),
        "rows": {k: {"park_traj": v["park_traj"],
                     "output_seen": v["output_seen"],
                     "inputs_consumed": v["inputs_consumed"]}
                 for k, v in rows.items()},
        "reproduce": "python experiments/m2/gate.py",
    }
    (outdir / "gate.json").write_text(json.dumps(result, indent=2))
    print("GERBANG-PERTAMA", f"kolom={col}", f"AND={is_and}",
          f"deterministik={det}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
