"""W-FO2/FO3 (log 023): verifikasi gerbang + fan-out pada hukum dua-properti."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m2"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from gate_search import empirical_gate  # noqa: E402
from semesta import ca, io  # noqa: E402
from state_surgery import write_snapshot  # noqa: E402

N = 16384
DUAL = [22127, 22161, 22166, 22205, 22225, 22248, 22256, 22290, 22291]
ENGINE = str(ROOT / "engine" / "target" / "release" / "engine")
OUT = Path(__file__).parent / "result"


def fanout_probe(law, steps=40):
    """Satu [2] di 0s → apakah membelah jadi dua [1] yang berjalan?"""
    cells = [0] * N
    cells[8000] = 2
    d = OUT / "_work" / "fo"
    (d / "w").mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law))
    write_snapshot(d / "init.bin", cells, 4)
    subprocess.run([ENGINE, "run", "--n", str(N), "--k", "4", "--seed", "23001",
                    "--steps", str(steps), "--window", str(steps),
                    "--rule-table", str(d / "rule.bin"),
                    "--init-state", str(d / "init.bin"), "--threads", "1",
                    "--outdir", str(d / "w")], check=True, capture_output=True)
    m = io.read_manifest(d / "w" / "manifest.json")
    states = [ca.unpack_cells(x, N, 4) for x in
              io.read_window(d / "w" / "window.bin", N, m["window_states"], 4)]
    traj = []
    for s in states:
        nz = [(i - 7990, v) for i, v in enumerate(s) if v != 0 and 7980 <= i <= 8030]
        traj.append(nz)
    for f in ("window.bin", "final.bin", "init.bin"):
        p = d / "w" / f
        if p.exists():
            p.unlink()
    return traj


def branch_demo(engine, law, m, kr):
    """Satu [2] di hulu → belah → kedua belahan menyetor ke DUA memori
    gerbang (P1=8100, P2=8200). Latar difus untuk menuntun belahan."""
    cells = [0] * N
    cells[8100], cells[8101] = m, kr   # gerbang-1
    cells[8200], cells[8201] = m, kr   # gerbang-2
    cells[8050] = 2                    # sumber [2] → belah
    # latar difus tipis untuk menuntun? cukup belah sendiri dulu: tanpa difus
    d = OUT / "_work" / "branch"
    (d / "w").mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law))
    write_snapshot(d / "init.bin", cells, 4)
    subprocess.run([ENGINE, "run", "--n", str(N), "--k", "4", "--seed", "23001",
                    "--steps", "200", "--window", "200",
                    "--rule-table", str(d / "rule.bin"),
                    "--init-state", str(d / "init.bin"), "--threads", "1",
                    "--outdir", str(d / "w")], check=True, capture_output=True)
    mi = io.read_manifest(d / "w" / "manifest.json")
    states = [ca.unpack_cells(x, N, 4) for x in
              io.read_window(d / "w" / "window.bin", N, mi["window_states"], 4)]
    g1 = [s[8100] for s in states]
    g2 = [s[8200] for s in states]
    g1_held = any(v == m + 1 for v in g1)
    g2_held = any(v == m + 1 for v in g2)
    return {"g1_held_deposit": g1_held, "g2_held_deposit": g2_held,
            "g1_traj_tail": g1[-6:], "g2_traj_tail": g2[-6:]}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=ENGINE)
    a = ap.parse_args()
    results = []
    best = None
    for sl in DUAL:
        law = ca.random_table_rich(4, sl)
        cfgs = gate_cfgs_of(sl)
        m, kr = cfgs[0]
        r = empirical_gate(a.engine, law, m, kr, OUT / "_work", f"fo_{sl}")
        col = r["column"]
        andy = col == [0, 0, 0, 1]
        nontrivial = col[3] > max(col[1], col[2]) or (col == [0, 0, 0, 1])
        fo = fanout_probe(law)
        # fan-out: ada t dengan ≥2 sel nonzero (belahan) berasal dari 1 sel
        split = any(len(set(i for i, v in seg if v != 0)) >= 2 for seg in fo[2:])
        rec = {"law_seed": sl, "m": m, "kr": kr, "column": col,
               "is_and": bool(andy), "nontrivial": bool(nontrivial),
               "fanout_split": bool(split), "fanout_traj": fo[:8]}
        results.append(rec)
        print(f"law {sl} (m={m},kr={kr}): kolom={col} AND={andy} fanout_split={split}")
        if nontrivial and split and best is None:
            best = rec
    print("TERBAIK:", json.dumps({k: best[k] for k in ("law_seed", "m", "kr", "column")} if best else None))
    (OUT / "fanout_verify.json").write_text(json.dumps(
        {"results": results, "best": best}, indent=2))


def gate_cfgs_of(sl):
    sys.path.insert(0, str(ROOT / "experiments" / "m2"))
    from gate_search import gate_configs
    return gate_configs(ca.random_table_rich(4, sl))


if __name__ == "__main__":
    sys.exit(main())
