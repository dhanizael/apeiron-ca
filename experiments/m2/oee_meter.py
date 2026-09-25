"""Meter OEE (log 019): model_bits(t) = k × entri teramati pada window ~t,
protokol K5 (log 005), dijalankan pada dunia perpetuum (19631) + baseline.
Pertanyaan: apakah model Newton TERUS BERTUMBUH (OEE-flavored) atau jenuh
(kuantifikasi gap OEE)? Coverage = entri aktif di window sekitar t.
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
CHECKPOINTS = [10**3, 10**4, 10**5, 10**6]
CAP_W = 2000


def checkpoint(engine, law, k, cells, seed, t, workdir, tag):
    """Run t langkah dari init-state, window=min(t,2000): coverage + populasi."""
    d = Path(workdir) / tag
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law))
    write_snapshot(d / "init.bin", cells, k)
    window = min(t, CAP_W)
    subprocess.run([engine, "run", "--n", str(N), "--k", str(k), "--seed", str(seed),
                    "--steps", str(t), "--window", str(window),
                    "--rule-table", str(d / "rule.bin"),
                    "--init-state", str(d / "init.bin"), "--threads", "1",
                    "--outdir", str(d / "w")], check=True, capture_output=True)
    m = io.read_manifest(d / "w" / "manifest.json")
    raw = io.read_window(d / "w" / "window.bin", N, m["window_states"], k)
    states = [ca.unpack_cells(x, N, k) for x in raw]
    # entri aktif di window: triple (l,c,r) yang muncul di pasangan state
    # (semantik K5: entri teramati dari pasangan, eksak)
    active = set()
    for s, t2 in zip(states[:-1], states[1:]):
        for i in range(N):
            f_out = s[i] - t2[i]
            l, c, r = s[(i - 1) % N], s[i], s[(i + 1) % N]
            active.add((l << (2 * k)) | (c << k) | r)
    pops = {}
    for s in states[-len(states) // 3:]:
        for v in s:
            pops[v] = pops.get(v, 0) + 1
    live_last3 = all(pops.get(v, 0) > 0 for v in (0, 1, 2))
    vals = sorted(pops)
    import collections
    h = collections.Counter(states[-1])
    for f in ("window.bin", "final.bin", "init.bin"):
        p = d / "w" / f
        if p.exists():
            p.unlink()
    return {"t": t, "coverage_active": len(active),
            "model_bits": k * len(active),
            "ceiling_bits": k * (1 << (3 * k)),
            "tail_hist": {str(v): h.get(v, 0) for v in sorted(h)},
            "static_tail": len(set(tuple(s) for s in states)) == 1}


def world_seeds(engine, name):
    """(law, k, cells, tag) per dunia."""
    sys.path.insert(0, str(ROOT / "experiments" / "m4"))
    if name == "perpetuum19631":
        law = ca.random_table_rich(4, 19631)
        rng = ca.Rng(21001)
        cells = [(0 if rng.next_u64() % 2 == 0 else 1) for _ in range(N)]
        return law, 4, cells
    if name == "v6final":
        from density_map import load_v6_final
        rng = ca.Rng(21001)  # instans-tunggal (log 027: per-elemen = laut-1)
        return load_v6_final(), 2, [rng.next_u64() % 2 for _ in range(N)]
    if name == "replicator16295":
        law = ca.random_table_rich(2, 16295)
        rng = ca.Rng(21001)
        return law, 2, [rng.next_u64() % 2 for _ in range(N)]
    raise ValueError(name)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    a = ap.parse_args()
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"
    result = {}
    for name in ("perpetuum19631", "v6final", "replicator16295"):
        law, k, cells = world_seeds(a.engine, name)
        rows = []
        for t in CHECKPOINTS:
            r = checkpoint(a.engine, law, k, cells, 21001, t, workdir,
                           f"{name}_{t}")
            rows.append(r)
            print(f"{name} t={t}: coverage={r['coverage_active']} "
                  f"model_bits={r['model_bits']}/{r['ceiling_bits']} "
                  f"static_tail={r['static_tail']}")
        result[name] = rows
    (outdir / "oee_meter.json").write_text(json.dumps(
        {"experiment": "oee-meter", "checkpoints": CHECKPOINTS,
         "worlds": result,
         "reproduce": "python experiments/m2/oee_meter.py"}, indent=2))
    print("OEE-METER selesai")
    return 0


if __name__ == "__main__":
    sys.exit(main())
