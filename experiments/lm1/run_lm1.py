"""LM-1 — eksperimen hukum tanaman (kriteria biner LM0, spec §9).

Protokol: sweep densitas → ukur J(ρ) tiap run (ground truth TERUKUR, bukan
rumus tekstbook). Newton mikro dari window run tengah; makro: train pada
subset ρ, prediksi held-out. Seed tetap per protokol (deterministik penuh).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))

from newton import macro, meter, micro, oracle, verify  # noqa: E402
from semesta import io  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mini", action="store_true", help="versi kecil untuk tes")
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    a = ap.parse_args()

    if a.mini:
        n, steps, W, seed = 1024, 4000, 128, 7
        densities = [0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.65, 0.7, 0.8]
        holdout = [0.25, 0.65]
    else:
        n, steps, W, seed = 4096, 20000, 512, 7
        densities = [round(0.05 + 0.075 * k, 3) for k in range(13)]
        holdout = [0.2, 0.35, 0.65, 0.8]

    outdir = Path(a.outdir)
    runs = {}
    for rho in densities:
        cars = round(rho * n)
        out = outdir / f"rho{rho:.3f}"
        subprocess.run(
            [a.engine, "run", "--n", str(n), "--cars", str(cars), "--seed", str(seed),
             "--steps", str(steps), "--window", str(W), "--outdir", str(out)],
            check=True, capture_output=True,
        )
        m = io.read_manifest(out / "manifest.json")
        states = io.read_window(out / "window.bin", n, m["window_states"])
        runs[rho] = (m, states)

    # --- Newton mikro: window TRANSIEN awal (init acak ρ=0.5 → keragaman
    #     neighborhood maksimal). Fase ter-order pasca-relaksasi miskin pola
    #     (kelas kegagalan F1): semua mobil dalam platoon → coverage tak lengkap.
    micro_out = outdir / "micro_transient"
    subprocess.run(
        [a.engine, "run", "--n", str(n), "--cars", str(n // 2), "--seed", str(seed),
         "--steps", "64", "--window", "63", "--outdir", str(micro_out)],
        check=True, capture_output=True,
    )
    m_micro = io.read_manifest(micro_out / "manifest.json")
    states_micro = io.read_window(micro_out / "window.bin", n, m_micro["window_states"])
    rec = micro.recover(states_micro, n)
    micro_rule = rec["verified"][0] if rec["verified"] else -1
    micro_gate = verify.gate_micro(micro_rule, states_micro, n) if rec["verified"] else False
    g_micro = oracle.grade_micro(micro_rule, m_micro)

    # --- Newton makro: J(ρ) dari window pasca-relaksasi ---
    J = {rho: macro.measure_flow(states, n) for rho, (_, states) in runs.items()}
    train = [(r, J[r]) for r in densities if r not in holdout]
    model = macro.fit_pw_linear([x for x, _ in train], [y for _, y in train])
    macro_gate = verify.gate_macro(model, [x for x, _ in train], [y for _, y in train])
    ho = [(r, J[r]) for r in holdout]
    g_macro = oracle.grade_macro(model, ho, eps=0.02)

    # --- Meter T1: angka pertama proyek ---
    curve = meter.log([
        {"t": steps, "bits": 8, "what": "micro_rule_table"},
        {"t": steps, "bits": model["model_bits"], "what": "macro_pw_linear"},
    ])

    result = {
        "experiment": "LM-1",
        "mode": "mini" if a.mini else "full",
        "criteria": {
            "1_micro_exact": bool(micro_gate and g_micro["exact"]),
            "2_macro_mae_lt_eps": bool(macro_gate and g_macro["pass"]),
            "3_meter_emits": len(curve) > 0,
            "4_k1_cross": None,
        },
        "micro": {**g_micro, "n_candidates": len(rec["candidates"]),
                  "n_verified": len(rec["verified"])},
        "macro": g_macro,
        "J_measured": {f"{r:.3f}": J[r] for r in densities},
        "model": {"segments": model["segments"], "model_bits": model["model_bits"],
                  "n_segments": model["n_segments"]},
        "meter": curve,
        "config": {"n": n, "steps": steps, "window": W + 1, "seed": seed,
                   "densities": densities, "holdout": holdout},
        "reproduce": (
            f"engine run (lihat manifest per-run di {outdir}/rho*/) && "
            f"python experiments/lm1/run_lm1.py{' --mini' if a.mini else ''}"
        ),
    }
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "result.json").write_text(json.dumps(result, indent=2))

    ok = all(v for v in result["criteria"].values() if v is not None)
    print("LM-1", "PASS" if ok else "FAIL", json.dumps(result["criteria"]))
    print(f"micro={g_micro} macro_mae={g_macro['mae']:.4f} "
          f"model_bits={model['model_bits']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
