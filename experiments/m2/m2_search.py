"""M2 ronde 2 — pencarian hukum-replikator, census-fitness (log 016).

Fitness: tanam 1×[2] + latar difus [1] (bg=819) → 2000 langkah (window=steps,
sensus tiap 10 sampel) → trajektori [2]-count. Event = 1 → ≥2 sustained
(≥10 sampel berturut = 1000 langkah). Kanal fusi: sel-1 STALL (entri (l,1,r)
dingin) menerima emisi tetangga → 2 lahir.

Kalibrasi wajib: v6-final HARUS menunjukkan transmutasi dikenal ([2] 1→0,
[1] +2) — harness divalidasi presence & absence.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m2"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca, io  # noqa: E402
from census import count_copies, plant_state  # noqa: E402
from state_surgery import write_snapshot  # noqa: E402

N = 16384
STEPS = 2000
BG = 819
SUSTAIN = 10
P2 = [2]
P1 = [1]


def run_census(engine, law, seed, workdir, tag, steps=STEPS):
    """Tanam 1×[2] + latar difus → run → sensus [2] & [1]."""
    cells = plant_state([0] * N, P2, bg_ones=BG, seed=seed)
    d = Path(workdir) / tag
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law))
    write_snapshot(d / "init_state.bin", cells, 2)
    subprocess = __import__("subprocess")
    subprocess.run([engine, "run", "--n", str(N), "--k", "2", "--seed", str(seed),
                    "--steps", str(steps), "--window", str(steps),
                    "--rule-table", str(d / "rule.bin"),
                    "--init-state", str(d / "init_state.bin"), "--threads", "1",
                    "--outdir", str(d / "w")], check=True, capture_output=True)
    m = io.read_manifest(d / "w" / "manifest.json")
    raw = io.read_window(d / "w" / "window.bin", N, m["window_states"], 2)
    # census tiap-10: unpack HANYA sampel (bottleneck Python: 16384 shift/state)
    states = [ca.unpack_cells(raw[i], N, 2) for i in range(0, len(raw), 10)]
    c2 = count_copies(states[::10], P2)
    c1 = count_copies(states[::10], P1)
    for f in ("window.bin", "final.bin", "init_state.bin"):
        p = d / "w" / f
        if p.exists():
            p.unlink()
    return {"c2": c2, "c1": c1}


def event_of(c2, sustain=SUSTAIN):
    """1 → ≥2 sustained. Return dict atau None."""
    if not c2 or c2[0] != 1:
        return None
    for i in range(1, len(c2)):
        if c2[i] >= 2:
            tail = c2[i: i + sustain]
            ok = len(tail) >= sustain and all(x >= 2 for x in tail)
            return {"t_index": i, "peak": max(c2), "sustained": ok}
    return None


def calibration(engine, workdir):
    """v6-final HARUS menunjukkan: [2] 1→0 (transmutasi) DAN [1] naik ≥+2 —
    harness valid menangkap kehadiran & ketiadaan."""
    law = list(Path(ROOT, "experiments/m1v2/result/_work/rule_H_RICH_5700010.bin").read_bytes())
    # v6-final = silsilah penuh — ambil dari density_map loader
    sys.path.insert(0, str(ROOT / "experiments" / "m4"))
    from density_map import load_v6_final
    law = load_v6_final()
    r = run_census(engine, law, 15002, workdir, "calib")
    saw_transmutation = (r["c2"][0] == 1 and max(r["c2"]) <= 1 and r["c1"][-1] - r["c1"][0] >= 2)
    assert saw_transmutation, f"kalibrasi gagal: c2={r['c2'][:5]} c1={r['c1'][0]}→{r['c1'][-1]}"
    return {"calibrated": True, "c2_head": r["c2"][:3], "c1_growth": r["c1"][-1] - r["c1"][0]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    ap.add_argument("--n-laws", type=int, default=300)
    a = ap.parse_args()
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"

    calib = calibration(a.engine, workdir)
    print("KALIBRASI:", json.dumps(calib))

    candidates = []
    for i in range(a.n_laws):
        seed_law = 16001 + i
        law = ca.random_table_rich(2, seed_law)
        r = run_census(a.engine, law, 15002, workdir, f"law{seed_law}")
        ev = event_of(r["c2"])
        if ev and ev["sustained"]:
            candidates.append({"seed_law": seed_law, **ev,
                               "c2": r["c2"], "c1_head": r["c1"][:3],
                               "c1_tail": r["c1"][-3:]})
            print(f"KANDIDAT law={seed_law}: c2 max={ev['peak']} @t={ev['t_index']}")
        if i % 50 == 49:
            print(f"  …{i + 1}/{a.n_laws} hukum disapu, {len(candidates)} kandidat")

    result = {
        "experiment": "M2-search",
        "calibration": calib,
        "n_laws": a.n_laws,
        "candidates": candidates,
        "reproduce": f"python experiments/m2/m2_search.py --n-laws {a.n_laws}",
    }
    (outdir / "m2_search.json").write_text(json.dumps(result, indent=2))
    print("M2-SEARCH", f"kandidat={len(candidates)}/{a.n_laws}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
