"""M2 hunt (log 015): probe soliton + grid sensus replikasi.

Fase A — probe soliton: pola cepat [1] di belakang blok lambat [2,2,2]
(v6-final k=2; entri pass (1,2,2)=1 ada) → lacak POSISI: pass-through =
posisi [1] melompati posisi blok, keduanya utuh setelahnya.
Fase B — grid sensus: hukum {v6-final k=2, k=4 receipt-lift} × pola ×
latar {kosong, difus} × 20k langkah, sensus tiap 100 → replikasi event
(definisi terbekukan: 1 → ≥2, sustained 1000 langkah).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m2"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from census import count_copies, plant_state, replication_event  # noqa: E402
from semesta import ca, io  # noqa: E402
from density_map import load_v6_final  # noqa: E402
from lift_k import lift_law  # noqa: E402
from state_surgery import read_state  # noqa: E402

N = 16384
STEPS = 20000
WINDOW = 200
CENSUS_EVERY = 100
SUSTAIN = 10


def positions(states, pattern):
    """Posisi kemunculan pertama per state (None bila lenyap)."""
    p = "".join(chr(v) for v in pattern)
    w = len(pattern)
    out = []
    for s in states:
        ring = "".join(chr(v) for v in s)
        idx = (ring + ring[: w - 1]).find(p)
        out.append(idx if idx >= 0 else None)
    return out


def phase_a_soliton(engine, law, k, outdir):
    """Probe: [1] di belakang [2,2,2], jarak 8 sel; lacak posisi."""
    import subprocess
    base = [0] * N
    block = [2, 2, 2]
    for i, v in enumerate(block):
        base[200 + i] = v
    base[190] = 1  # di belakang (dynamics bergerak kanan)
    d = Path(outdir) / "probe_soliton"
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law))
    write = None
    sys.path.insert(0, str(ROOT / "experiments" / "m4"))
    from state_surgery import write_snapshot
    write_snapshot(d / "init_state.bin", base, k)
    subprocess.run([engine, "run", "--n", str(N), "--k", str(k), "--seed", "15001",
                    "--steps", "400", "--window", "400",
                    "--rule-table", str(d / "rule.bin"),
                    "--init-state", str(d / "init_state.bin"), "--threads", "1",
                    "--outdir", str(d / "w")], check=True, capture_output=True)
    m = io.read_manifest(d / "w" / "manifest.json")
    states = [ca.unpack_cells(s, N, k) for s in
              io.read_window(d / "w" / "window.bin", N, m["window_states"], k)]
    pos1 = positions(states, [1])
    posb = positions(states, [2, 2, 2])
    # pass-through: ada t, pos1[t] > posb[t] dan sebelumnya pos1 < posb
    crossed = None
    for t in range(1, len(pos1)):
        if None in (pos1[t], posb[t]) or None in (pos1[t - 1], posb[t - 1]):
            continue
        before = pos1[t - 1] < posb[t - 1]
        after = pos1[t] > posb[t]
        if before and after:
            crossed = t
            break
    both_survive = pos1[-1] is not None and posb[-1] is not None
    for f in ("window.bin", "final.bin", "init_state.bin"):
        p = d / "w" / f
        if p.exists():
            p.unlink()
    (d.parent / "probe_soliton.json") if False else None
    return {"crossed_at": crossed, "both_survive": both_survive,
            "pos1_tail": pos1[-5:], "posb_tail": posb[-5:]}


def phase_b_grid(engine, outdir):
    """Grid: hukum × pola × latar → census + replikasi event."""
    import subprocess
    law2 = load_v6_final()
    law4 = lift_law(law2, receipt=True)
    grids = [(law2, 2, [[1], [2], [1, 1], [2, 2], [2, 2, 2]]),
             (law4, 4, [[1], [2], [1, 1], [2, 2], [2, 2, 2], [3], [5]])]
    events = []
    rows = []
    for law, k, pats in grids:
        for pat in pats:
            for bg in (0, int(0.05 * N)):
                tag = f"k{k}_p{''.join(map(str, pat))}_bg{bg}"
                cells = plant_state([0] * N, pat, bg_ones=bg, seed=15002)
                d = Path(outdir) / "grid" / tag
                d.mkdir(parents=True, exist_ok=True)
                (d / "rule.bin").write_bytes(bytes(law))
                from state_surgery import write_snapshot
                write_snapshot(d / "init_state.bin", cells, k)
                subprocess.run([engine, "run", "--n", str(N), "--k", str(k),
                                "--seed", "15002", "--steps", str(STEPS),
                                "--window", str(WINDOW),
                                "--rule-table", str(d / "rule.bin"),
                                "--init-state", str(d / "init_state.bin"),
                                "--threads", "1", "--outdir", str(d / "w")],
                               check=True, capture_output=True)
                m = io.read_manifest(d / "w" / "manifest.json")
                states = [ca.unpack_cells(s, N, k) for s in
                          io.read_window(d / "w" / "window.bin", N,
                                         m["window_states"], k)]
                counts = count_copies(states, pat)
                ev = replication_event(counts, sustain=SUSTAIN)
                rows.append({"tag": tag, "counts_head": counts[:6],
                             "counts_tail": counts[-3:], "max": max(counts),
                             "event": ev})
                if ev and ev.get("sustained", False):
                    events.append({"tag": tag, **ev})
                for f in ("window.bin", "final.bin", "init_state.bin"):
                    p = d / "w" / f
                    if p.exists():
                        p.unlink()
                print(f"{tag}: counts={counts[:4]}… max={max(counts)} "
                      f"event={'EV' if ev and ev.get('sustained') else ('transien' if ev else '-')}")
    return events, rows


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    a = ap.parse_args()
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    law2 = load_v6_final()
    soliton = phase_a_soliton(a.engine, law2, 2, outdir)
    print("PROBE-SOLITON:", json.dumps(soliton))
    events, rows = phase_b_grid(a.engine, outdir)
    result = {
        "experiment": "M2-hunt",
        "soliton": soliton,
        "events": events,
        "n_events_sustained": len(events),
        "rows": rows,
        "reproduce": "python experiments/m2/m2_hunt.py",
    }
    (outdir / "m2_hunt.json").write_text(json.dumps(result, indent=2))
    print("M2-HUNT", f"soliton={'YA' if soliton['crossed_at'] else 'TIDAK'}",
          f"events_sustained={len(events)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
