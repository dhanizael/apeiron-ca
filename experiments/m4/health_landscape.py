"""Baseline lanskap kesehatan multi-seed (Part gerbang loop v5, log 011).

Pertanyaan: seberapa sehat hukum-hukum known di KEDUA rezim pada BANYAK
instans? (1) Gerbang instrumen: horizon-pendek 5000 harus menyetujui 20000;
(2) lanskap: adakah hukum known yang cap3-nya 7/7? — meng-instantiasi
threshold W3v5a (aturannya pre-frozen di plan; disklosikan).

Hukum: F0 (juara RICH 006), cocktail20 (probe 007: cap1 0,5042 / cap3 1,4870
pada seed 1093 — silsilah dipatok via tanda tangan J), v3-final, v4-final.
Kesehatan: cap1 = J > 0 (bila FM-E → mobilitas); cap3 = mobilitas > 0
(window akhir 64 langkah; J dilaporkan bila terukur). Anti-kuota: window/
final dihapus segera setelah metrik.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m3"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca, io  # noqa: E402
from recover import run_window  # noqa: E402
from calibrate_freeze import j_from_states  # noqa: E402

COCKTAIL20 = [24, 12, 28, 41, 44, 8, 46, 57, 9, 20, 30, 37, 40, 54, 61, 62, 10, 14, 21, 22]


def health_from_states(states, k):
    """Kesehatan dari window: flowing = ada transisi berbeda; mobilitas =
    fraksi sel berubah per langkah; J dihitung selalu (None bila FM-E —
    state diam pun J-nya terukur: semua d=0 → f=0)."""
    pairs = [(list(a), list(b)) for a, b in zip(states[:-1], states[1:])]
    changed = sum(1 for a, b in pairs if a != b)
    mob = (sum(sum(1 for x, y in zip(a, b) if x != y) for a, b in pairs)
           / (len(pairs) * len(states[0]))) if pairs else 0.0
    try:
        j, _amb, _st = j_from_states(states, k)
    except ValueError:
        j = None
    return {"flowing": changed > 0, "mobility": round(mob, 6), "J": j,
            "n_changed": changed, "n_pairs": len(pairs)}


def load_baseline_laws():
    F0 = list(Path(ROOT, "experiments/m1v2/result/_work/rule_H_RICH_5700010.bin").read_bytes())
    c20 = ca.clip_table([v + (1 if i in COCKTAIL20 else 0) for i, v in enumerate(F0)], 2)
    v3 = json.loads((ROOT / "experiments" / "m4" / "result" / "result.json").read_text())
    v3f = list(F0)
    for c in v3["trajectory"][0]["decision"]["committed"]:
        v3f[c["entry"]] += c["delta"]
    v3f = ca.clip_table(v3f, 2)
    assert f"{ca.table_fnv(v3f):016x}" == v3["trajectory"][-1]["feedback"]["table_fnv"]
    v4 = json.loads((ROOT / "experiments" / "m4" / "result" / "result_loop4.json").read_text())
    v4f = list(v3f)
    for t in v4["trajectory"]:
        for e, d in t["intervention"]["targeted"]:
            v4f[e] += d
    v4f = ca.clip_table(v4f, 2)
    assert f"{ca.table_fnv(v4f):016x}" == v4["trajectory"][-1]["feedback"]["table_fnv"]
    return {"F0": F0, "cocktail20": c20, "v3_final": v3f, "v4_final": v4f}


def measure(engine, table, k, n, seed, steps, window, cap, workdir, tag):
    d = Path(workdir) / f"h_{tag}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(table))
    states = run_window(engine, n, k, seed, steps, window, d / "rule.bin",
                        d / "w", init_cap=cap)
    h = health_from_states(states, k)
    for f in ("window.bin", "final.bin"):
        p = d / "w" / f
        if p.exists():
            p.unlink()
    return h


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    ap.add_argument("--n", type=int, default=16384)
    a = ap.parse_args()

    k, n = 2, a.n
    laws = load_baseline_laws()
    seeds = list(range(55001, 55008))
    horizons = [(5000, 512), (20000, 512)]  # (langkah, window)
    cap3_window = 64
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"

    rows = []
    for lname, tab in laws.items():
        for cap, win in ((1, 512), (3, cap3_window)):
            for steps, w in horizons:
                hs = [measure(a.engine, tab, k, n, s, steps, w, cap, workdir,
                              f"{lname}_{cap}_{steps}_{s}") for s in seeds]
                rate = sum(h["flowing"] for h in hs) / len(hs)
                rows.append({"law": lname, "cap": cap, "steps": steps,
                             "rate": rate, "per_seed": [
                                 {"seed": s, "flowing": h["flowing"],
                                  "mobility": h["mobility"], "J": h["J"]}
                                 for s, h in zip(seeds, hs)]})
                print(f"{lname:11s} cap{cap} {steps:5d}: rate={rate:.2f} "
                      f"mob={[round(h['mobility'], 3) for h in hs]}")

    # gerbang: 5000 vs 20000 sepakat?
    mismatch = []
    for lname in laws:
        for cap in (1, 3):
            r5 = next(r["rate"] for r in rows if r["law"] == lname and r["cap"] == cap and r["steps"] == 5000)
            r20 = next(r["rate"] for r in rows if r["law"] == lname and r["cap"] == cap and r["steps"] == 20000)
            if r5 != r20:
                mismatch.append({"law": lname, "cap": cap, "rate5000": r5, "rate20000": r20})

    result = {
        "experiment": "health-landscape",
        "seeds": seeds, "k": k, "n": n,
        "gate_5000_equals_20000": not mismatch,
        "gate_mismatches": mismatch,
        "rows": rows,
        "reproduce": "python experiments/m4/health_landscape.py",
    }
    (outdir / "health_landscape.json").write_text(json.dumps(result, indent=2))
    print("HEALTH-LANDSCAPE", "GATE-PASS" if not mismatch else f"GATE-FAIL {mismatch}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
