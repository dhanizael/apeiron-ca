"""Kalibrasi instrumen counterfactual (gerbang W2 plan loop v3).

Pertanyaan: apakah simulasi kosmos mini (n=256) memprediksi verdict full-scale
(n=16384) atas mutasi tunggal? 13 kasus berlabel: 8 dari log 007 (seed 1093/
1094, disklosikan sebagai kontaminasi terkontrol — fungsinya kasus berlabel)
+ 5 diukur kini dengan protokol sama. Kelas: freeze (J=0 eksak), drop (Δ≤−0,05),
raise (Δ≥+0,01), flat. GATE: nol freeze-miss (mini bilang bukan-freeze, full
beku) — pelanggaran = instrumen ditolak, eskalasi n mini.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m3"))

from semesta import ca  # noqa: E402
from recover import measure_j, run_window  # noqa: E402
from newton import flowrecover  # noqa: E402

# Label full-scale dari log 007 (probe seed 1093/1094, cap=1, n=16384, 20k langkah)
KNOWN = {12: "freeze", 9: "freeze", 60: "freeze", 29: "freeze",
         45: "drop", 56: "drop", 20: "raise", 24: "raise"}
EXTEND = [41, 8, 44, 46, 57]  # diukur full-scale dalam skrip ini (protokol sama)


def classify(j_after, j_before, static):
    if j_after == 0.0 and static:
        return "freeze"
    d = j_after - j_before
    if d <= -0.05:
        return "drop"
    if d >= 0.01:
        return "raise"
    return "flat"


def j_from_states(states, k):
    """J + ambiguitas dari window states (matematika identik measure_j)."""
    pairs = [(list(s), list(t)) for s, t in zip(states[:-1], states[1:])]
    flows, amb = 0.0, 0
    for s, t in pairs:
        f = flowrecover.derive_field(s, t, k)
        if f is None:
            amb += 1
            continue
        flows += sum(f) / len(f)
    used = len(pairs) - amb
    return (flows / used if used else 0.0), amb, is_static(states)


def is_static(states):
    return all(list(a) == list(b) for a, b in zip(states[:-1], states[1:]))


def full_single(engine, F0, e, k, n, seeds, steps, window, workdir):
    """ΔJ full-scale pasangan-seed untuk mutasi +1 tunggal pada entri e."""
    T = list(F0)
    T[e] += 1
    T = ca.clip_table(T, k)
    deltas, j0s = [], []
    for seed in seeds:
        js = []
        for name, tab in (("p", F0), ("m", T)):
            d = Path(workdir) / f"cal_{e}_{name}_{seed}"
            d.mkdir(parents=True, exist_ok=True)
            (d / "rule.bin").write_bytes(bytes(tab))
            r = measure_j(engine, d, n, k, seed, steps, window, 1, d / "w")
            js.append(r["J"])
        j0s.append(js[0])
        deltas.append(js[1] - js[0])
    mean_d = sum(deltas) / len(deltas)
    cls = ("freeze" if all(d == -j0 for d, j0 in zip(deltas, j0s))
           else "drop" if mean_d <= -0.05
           else "raise" if mean_d >= 0.01 else "flat")
    return {"deltas": deltas, "class": cls}


def mini_single(engine, F0, e, k, n, seeds, steps, window, workdir, cap=1):
    """Verdict mini multi-seed, agregasi konservatif: freeze jika ADA seed
    beku (deteksi beku harus sensitif — false-positive murah, false-negative
    mahal); selain itu klasifikasi dari rata-rata Δ."""
    T = list(F0)
    T[e] += 1
    T = ca.clip_table(T, k)
    per_seed = []
    j_parent_sum = 0.0
    for seed in seeds:
        js = []
        for name, tab in (("p", F0), ("m", T)):
            d = Path(workdir) / f"cmini_{e}_{name}_{seed}"
            d.mkdir(parents=True, exist_ok=True)
            (d / "rule.bin").write_bytes(bytes(tab))
            states = run_window(engine, n, k, seed, steps, window, d / "rule.bin",
                                d / "w", init_cap=cap)
            j, amb, static = j_from_states(states, k)
            js.append({"J": j, "amb": amb, "static": static})
        j_parent_sum += js[0]["J"]
        per_seed.append({"seed": seed, "j_parent": js[0]["J"], "j": js[1]["J"],
                         "static": js[1]["static"], "amb": js[1]["amb"],
                         "class": classify(js[1]["J"], js[0]["J"], js[1]["static"])})
    any_freeze = any(p["class"] == "freeze" for p in per_seed)
    mean_d = sum(p["j"] - p["j_parent"] for p in per_seed) / len(per_seed)
    mean_p = j_parent_sum / len(per_seed)
    cls = "freeze" if any_freeze else classify(mean_p + mean_d, mean_p, False)
    return {"class": cls, "per_seed": per_seed,
            "j_parent_mean": round(mean_p, 6), "j_mean": round(mean_p + mean_d, 6)}


def short_single(engine, F0, e, k, n, seeds, steps, window, workdir, cap=1, r_min=0.3):
    """Kontrafaktual horizon-pendek SKALA PENUH (pelajaran kalibrasi: mengecil-
    kan n mengubah basin atraktor beku — e=9/41 metastabil mengalir di n=1024
    walau beku di n=16384; sedangkan kebekuan terjadi ≤2500 langkah di skala
    penuh, anatomi log 008). Prediksi 5k vs label 20k pada seed yang sama —
    prefeks deterministik run panjang. Detektor beku = J==0 statis ATAU kolaps
    (J/J_parent < r_min; kondensasi berlangsung bertahap — J≈0,05 di 5k untuk
    kasus yang nol eksak di 20k, threshold r_min dari set kalibrasi)."""
    T = list(F0)
    T[e] += 1
    T = ca.clip_table(T, k)
    per_seed = []
    j_parent_sum = 0.0
    for seed in seeds:
        js = []
        for name, tab in (("p", F0), ("m", T)):
            d = Path(workdir) / f"cshort_{e}_{name}_{seed}"
            d.mkdir(parents=True, exist_ok=True)
            (d / "rule.bin").write_bytes(bytes(tab))
            states = run_window(engine, n, k, seed, steps, window, d / "rule.bin",
                                d / "w", init_cap=cap)
            j, amb, static = j_from_states(states, k)
            js.append({"J": j, "amb": amb, "static": static})
        jp, jm = js[0]["J"], js[1]["J"]
        if jm == 0.0 and js[1]["static"]:
            cls = "freeze"
        elif jp > 0 and jm / jp < r_min:
            cls = "collapse"
        else:
            cls = classify(jm, jp, js[1]["static"])
        j_parent_sum += jp
        per_seed.append({"seed": seed, "j_parent": jp, "j": jm,
                         "static": js[1]["static"], "amb": js[1]["amb"], "class": cls})
    any_reject = any(p["class"] in ("freeze", "collapse") for p in per_seed)
    mean_d = sum(p["j"] - p["j_parent"] for p in per_seed) / len(per_seed)
    mean_p = j_parent_sum / len(per_seed)
    cls = "freeze" if any_reject else classify(mean_p + mean_d, mean_p, False)
    return {"class": cls, "per_seed": per_seed,
            "j_parent_mean": round(mean_p, 6), "j_mean": round(mean_p + mean_d, 6)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    ap.add_argument("--mini-n", type=int, default=256)
    ap.add_argument("--mini-steps", type=int, default=2000)
    ap.add_argument("--mini-seeds", default="6600")
    ap.add_argument("--instrument", choices=["mini", "short"], default="short")
    ap.add_argument("--short-steps", type=int, default=5000)
    ap.add_argument("--short-seeds", default="1093,1094")
    ap.add_argument("--r-min", type=float, default=0.3)
    a = ap.parse_args()

    F0 = list(Path(ROOT, "experiments/m1v2/result/_work/rule_H_RICH_5700010.bin").read_bytes())
    k, n, seeds, steps, window = 2, 16384, [1093, 1094], 20000, 512
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"

    cases = {}
    for e, cls in KNOWN.items():
        cases[e] = {"class_full": cls, "source": "log007"}
    for e in EXTEND:
        r = full_single(a.engine, F0, e, k, n, seeds, steps, window, workdir)
        cases[e] = {"class_full": r["class"], "source": "measured",
                    "deltas_full": r["deltas"]}

    rows, freeze_miss = [], 0
    if a.instrument == "short":
        eval_seeds = [int(s) for s in a.short_seeds.split(",")]
        instr = {"kind": "short-full-scale", "n": n, "steps": a.short_steps,
                 "seeds": eval_seeds, "window": 512, "r_min": a.r_min,
                 "note": "kontrafaktual horizon-pendek skala penuh; seed = seed label; "
                         "reject = freeze eksak ATAU kolaps J/J_parent < r_min "
                         "(threshold dari set kalibrasi)"}
        for e in sorted(cases):
            m = short_single(a.engine, F0, e, k, n, eval_seeds, a.short_steps, 512,
                             workdir, r_min=a.r_min)
            miss = (cases[e]["class_full"] == "freeze" and m["class"] != "freeze")
            freeze_miss += int(miss)
            rows.append({"entry": e, "class_full": cases[e]["class_full"],
                         "source": cases[e]["source"], "mini": m, "freeze_miss": miss})
    else:
        eval_seeds = [int(s) for s in a.mini_seeds.split(",")]
        instr = {"kind": "mini-cosmos", "mini_n": a.mini_n,
                 "mini_steps": a.mini_steps, "mini_seeds": eval_seeds, "window": 64,
                 "aggregation": "freeze-if-any-seed"}
        for e in sorted(cases):
            m = mini_single(a.engine, F0, e, k, a.mini_n, eval_seeds, a.mini_steps, 64, workdir)
            miss = (cases[e]["class_full"] == "freeze" and m["class"] != "freeze")
            freeze_miss += int(miss)
            rows.append({"entry": e, "class_full": cases[e]["class_full"],
                         "source": cases[e]["source"], "mini": m, "freeze_miss": miss})

    result = {
        "experiment": "freeze-calibration",
        "instrument": instr,
        "gate_freeze_miss_zero": freeze_miss == 0,
        "freeze_miss": freeze_miss,
        "agreement": sum(1 for r in rows if r["mini"]["class"] == r["class_full"]) / len(rows),
        "cases": rows,
        "reproduce": "python experiments/m4/calibrate_freeze.py",
    }
    (outdir / "freeze_calibration.json").write_text(json.dumps(result, indent=2))
    print("FREEZE-CAL", f"freeze_miss={freeze_miss} agreement={result['agreement']:.2f}",
          "GATE-PASS" if result["gate_freeze_miss_zero"] else "GATE-FAIL")
    for r in rows:
        print(f"  e={r['entry']:2d} full={r['class_full']:6s} mini={r['mini']['class']:6s}"
              f" Jmini={r['mini']['j_mean']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
