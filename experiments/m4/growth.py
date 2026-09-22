"""M4 — growth meter (K5/W4, spec §9 amendemen M4).

model_bits(t) = k × entri tabel teramati pada window sekitar t (+ catatan: bit
makro ≈ konstanta kecil, diukur terpisah di M3). Checkpoint t ∈ {10³,10⁴,10⁶},
tiga rezim: juara A, juara B (counterfactual M3), 184 (rezim runtuh).
Kompresi window (zlib) dilaporkan per checkpoint (W4). Kurva dilaporkan apa
adanya — saturasi adalah pembacaan sah (R1 tetap terbuka).
"""
import argparse
import json
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))

from newton import flowrecover  # noqa: E402
from semesta import ca, io  # noqa: E402


def measure_checkpoint(engine, rule_path, n, k, seed, t, cap_w, workdir, cars=None):
    window = min(t, cap_w)
    cmd = [engine, "run", "--n", str(n), "--k", str(k), "--seed", str(seed),
           "--steps", str(t), "--window", str(window),
           "--rule-table", str(rule_path), "--threads", "1",
           "--outdir", str(workdir)]
    if k == 1:
        cmd += ["--cars", str(cars or n // 2)]
    else:
        cmd += ["--uniform"]
    subprocess.run(cmd, check=True, capture_output=True)
    m = io.read_manifest(workdir / "manifest.json")
    packed = io.read_window(workdir / "window.bin", n, m["window_states"], k)
    states = [ca.unpack_cells(x, n, k) for x in packed]
    pairs = [(states[i], states[i + 1]) for i in range(len(states) - 1)]
    rec = flowrecover.recover_table(pairs, k)
    raw = (workdir / "window.bin").stat().st_size
    comp = len(zlib.compress((workdir / "window.bin").read_bytes(), 9))
    return {
        "t": t,
        "model_bits": k * rec["observed"],
        "coverage": rec["observed"],
        "table_size": 1 << (3 * k),
        "compressed": comp,
        "raw": raw,
        "ratio": (comp / raw) if raw else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mini", action="store_true")
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    a = ap.parse_args()

    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"
    workdir.mkdir(exist_ok=True)

    if a.mini:
        sand = [0] * 64
        layer = [0] * 64
        for l in range(4):
            for c in range(4):
                for r in range(4):
                    idx = (l << 4) | (c << 2) | r
                    sand[idx] = 1 if c > r + 1 else 0
                    layer[idx] = 1 if ((c & 1) and not (r & 1)) else 0
        regimes = [("sandpile_k2", 2, ca.clip_table(sand, 2)),
                   ("layer184_k2", 2, ca.clip_table(layer, 2))]
        n, checkpoints, cap_w, seed = 256, [100, 400], 64, 5
    else:
        m1 = ROOT / "experiments" / "m1" / "result"
        r1 = json.loads((m1 / "result.json").read_text())
        regimes = []
        seen = set()
        for c in r1["champions"]:
            d = m1 / f"champ_k{c['k']}_s{c['seed']}"
            fnv = json.loads((d / "manifest.json").read_text())["rule_fnv"]
            if fnv in seen:
                continue
            seen.add(fnv)
            regimes.append((f"champ_k{c['k']}_s{c['seed']}", 4,
                            list((d / "rule.bin").read_bytes())))
            if len(regimes) == 2:
                break
        b184 = [0] * 8
        for l in range(2):
            for c in range(2):
                for r in range(2):
                    b184[(l << 2) | (c << 1) | r] = c & (1 - r)
        regimes.append(("rule184_k1", 1, b184))
        n, checkpoints, cap_w, seed = 16384, [1000, 10000, 1000000], 2048, 1092

    curves = {}
    for name, k, table in regimes:
        rp = workdir / f"rule_{name}.bin"
        rp.write_bytes(bytes(table))
        pts = []
        for t in checkpoints:
            pts.append(measure_checkpoint(a.engine, rp, n, k, seed, t, cap_w,
                                          workdir / f"gm_{name}_{t}"))
        curves[name] = pts

    measured = [nm for nm, pts in curves.items() if len(pts) == len(checkpoints)]
    k5 = len(measured) >= 2
    # pembacaan jujur per rezim: saturasi bila bits(t_akhir) − bits(t_pertama) kecil
    reading = {}
    for name, pts in curves.items():
        growth = pts[-1]["model_bits"] - pts[0]["model_bits"]
        reading[name] = {
            "delta_model_bits": growth,
            "reading": "saturated" if pts[-1]["model_bits"] > 0 and growth <= pts[0]["model_bits"] else "growing",
        }
    result = {
        "experiment": "M4-growth",
        "mode": "mini" if a.mini else "full",
        "criteria": {"K5_curve_measured": bool(k5)},
        "regimes_measured": measured,
        "curves": curves,
        "reading": reading,
        "note_macro_bits": "bit makro ≈ konstanta kecil (136 bit pada M3) — diukur terpisah",
        "reproduce": f"python experiments/m4/growth.py{' --mini' if a.mini else ''}",
    }
    (outdir / "result.json").write_text(json.dumps(result, indent=2))
    print("M4-GROWTH", "K5-PASS" if k5 else "K5-FAIL",
          json.dumps({k: v["reading"] for k, v in reading.items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
