"""M3-percepatan — Newton memulihkan hukum juara M1 yang tidak ditanam (spec §9).

Gerbang mikro: (3a) tabel pulihan ≡ GT eksak pada semua entri ter-amati;
(3b) reproduksi window held-out bit-identik; (3c) counterfactual law shift
(juara #2 → tabel berbeda yang cocok GT-nya sendiri). Makro dilaporkan
terpisah: J(ρ) via --init-cap sweep, fit piecewise-linear MDL, held-out MAE
vs ε dari lantai derau terukur. FM-E/F/F-G ditangani jujur.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))

from newton import flowrecover, macro  # noqa: E402
from semesta import ca, io  # noqa: E402


def run_window(engine, n, k, seed, steps, window, rule_bin, outdir, init_cap=0):
    cmd = [engine, "run", "--n", str(n), "--k", str(k), "--uniform",
           "--seed", str(seed), "--steps", str(steps), "--window", str(window),
           "--rule-table", str(rule_bin), "--threads", "1", "--outdir", str(outdir)]
    if init_cap:
        cmd += ["--init-cap", str(init_cap)]
    subprocess.run(cmd, check=True, capture_output=True)
    m = io.read_manifest(outdir / "manifest.json")
    states = io.read_window(outdir / "window.bin", n, m["window_states"], k)
    return [ca.unpack_cells(s, n, k) for s in states]


def pairs_from_states(states):
    return [(list(states[i]), list(states[i + 1])) for i in range(len(states) - 1)]


def recover_micro(engine, champ_dir, n, k, seed, steps_late, window_late, workdir):
    """Pulihkan dari window TRANSIEN (dari t=0, pelajaran F1); verifikasi di
    window RELAKSASI terpisah (t jauh) — tabel dari transien harus
    mereproduksi dinamika termal bit-identik."""
    gt = list(Path(champ_dir, "rule.bin").read_bytes())
    name = Path(champ_dir).name
    # recovery: transien penuh dari TIGA seed (hukum sama, transien berbeda →
    # union observasi menutup entri langka; konflik antar-seed tetap = kegagalan keras)
    steps_rec, win_rec = 4096, 4096
    if k == 2:
        steps_rec, win_rec = 32, 32
    pairs = []
    for s0 in (seed + 1, seed + 2, seed + 3):
        states_rec = run_window(engine, n, k, s0, steps_rec, win_rec,
                                Path(champ_dir, "rule.bin"), workdir / f"wr_{name}_{s0}")
        pairs += pairs_from_states(states_rec)
    rec = flowrecover.recover_table(pairs, k)
    # 3a: eksak pada semua entri ter-amati (dan wajib penuh untuk gerbang lanjut)
    exact_observed = all(rec["table"][i] == gt[i]
                         for i in range(len(gt)) if rec["table"][i] is not None)
    complete = rec["unconstrained"] == 0
    # 3b: reproduksi dinamika RELAKSASI bit-identik (butuh tabel penuh)
    reproduced = None
    if complete:
        states_late = run_window(engine, n, k, seed + 5000, steps_late, window_late,
                                 Path(champ_dir, "rule.bin"), workdir / f"wv_{name}")
        reproduced = all(
            ca.step_flow(s, k, rec["table"]) == t for s, t in pairs_from_states(states_late)
        )
    fnv = ca.table_fnv(rec["table"]) if complete else None
    return {
        "gate_3a_exact_observed": bool(exact_observed),
        "unconstrained": rec["unconstrained"],
        "observed": rec["observed"],
        "pairs_ambiguous": rec["pairs_ambiguous"],
        "table_complete": bool(complete),
        "gate_3b_reproduces_heldout": bool(reproduced) if reproduced is not None else None,
        "recovered_table_fnv": f"{fnv:016x}" if fnv else None,
        "matches_gt_full": bool(complete and rec["table"] == gt),
    }


def measure_j(engine, champ_dir, n, k, seed, steps, window, init_cap, workdir):
    states = run_window(engine, n, k, seed, steps, window, Path(champ_dir, "rule.bin"),
                        workdir / f"wj_{init_cap}_{seed}", init_cap=init_cap)
    pairs = pairs_from_states(states)
    flows, amb = 0, 0
    for s, t in pairs:
        f = flowrecover.derive_field(s, t, k)
        if f is None:
            amb += 1
            continue
        flows += sum(f) / len(f)
    used = len(pairs) - amb
    J = flows / used if used else None
    rho = sum(sum(s) for s in states) / (len(states) * n * ((1 << k) - 1))
    return {"rho": rho, "J": J, "ambiguous_pairs": amb, "pairs": len(pairs)}


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
        # champion mini: hand tables k=2 (sudah ter-commit sebagai bagian harness? tulis sendiri)
        from semesta import ca as _ca
        sand = [0] * 64
        layer = [0] * 64
        for l in range(4):
            for c in range(4):
                for r in range(4):
                    idx = (l << 4) | (c << 2) | r
                    sand[idx] = 1 if c > r + 1 else 0
                    layer[idx] = 1 if ((c & 1) and not (r & 1)) else 0
        d = outdir / "_champs"
        d.mkdir(parents=True, exist_ok=True)
        (d / "A").mkdir(exist_ok=True)
        (d / "B").mkdir(exist_ok=True)
        (d / "A" / "rule.bin").write_bytes(bytes(_ca.clip_table(sand, 2)))
        (d / "B" / "rule.bin").write_bytes(bytes(_ca.clip_table(layer, 2)))
        champs = [(str(d / "A"), 2, 5), (str(d / "B"), 2, 6)]
        n, steps, window = 256, 1000, 16
        caps_train, caps_hold = [], []
    else:
        # pilih dua juara M1 dengan rule_fnv BERBEDA (counterfactual butuh dua hukum)
        m1 = ROOT / "experiments" / "m1" / "result"
        r1 = json.loads((m1 / "result.json").read_text())
        champs = []
        seen_fnv = set()
        for c in r1["champions"]:
            d = m1 / f"champ_k{c['k']}_s{c['seed']}"
            fnv = json.loads((d / "manifest.json").read_text())["rule_fnv"]
            if fnv not in seen_fnv:
                seen_fnv.add(fnv)
                champs.append((str(d), c["k"], c["seed"]))
            if len(champs) == 2:
                break
        assert len(champs) == 2, "butuh dua juara dengan hukum berbeda"
        n, steps, window = 16384, 20000, 64
        caps_train, caps_hold = [1, 2, 3, 4, 5, 8, 11, 12, 13, 14], [6, 10]

    # ---------- Mikro: 3 gerbang + counterfactual ----------
    micro = {}
    for champ_dir, k, seed in champs:
        name = Path(champ_dir).name
        micro[name] = recover_micro(a.engine, champ_dir, n, k, seed, steps, window, workdir)

    complete = all(m["table_complete"] for m in micro.values())
    gate_3a = complete and all(m["gate_3a_exact_observed"] for m in micro.values())
    gate_3b = complete and all(m["gate_3b_reproduces_heldout"] for m in micro.values())
    fnvs = [m["recovered_table_fnv"] for m in micro.values()]
    gate_3c = (len(set(fnvs)) == len(fnvs)) and gate_3a and gate_3b

    # ---------- Makro (dilaporkan terpisah; hanya full mode) ----------
    macro_res = {"attempted": bool(caps_train)}
    if caps_train:
        champ_dir, k, base_seed = champs[0]
        pts, reps = {}, {}
        for cap in caps_train + caps_hold:
            r1 = measure_j(a.engine, champ_dir, n, k, base_seed, steps, window, cap, workdir)
            pts[cap] = r1
            if cap == caps_train[1]:  # lantai derau: cap sama, seed beda
                r2 = measure_j(a.engine, champ_dir, n, k, base_seed + 1, steps, window, cap, workdir)
                reps[cap] = abs(r1["J"] - r2["J"])
        eps = 2.0 * max(reps.values()) if reps else 1e-3
        train = [(pts[c]["rho"], pts[c]["J"]) for c in caps_train]
        xs = [x for x, _ in train]
        # GRID dibatasi rentang data train (segmen kosong merusak prediksi)
        grid_local = [g for g in macro.GRID if min(xs) <= g <= max(xs)]
        model = macro.fit_pw_linear(xs, [y for _, y in train], grid=grid_local)
        ho = [(pts[c]["rho"], pts[c]["J"]) for c in caps_hold]
        errs = [abs(macro.predict(model, x) - y) for x, y in ho]
        mae = sum(errs) / len(errs)
        macro_res.update({
            "points": {str(c): pts[c] for c in pts},
            "noise_floor": reps,
            "eps": eps,
            "n_segments": model["n_segments"],
            "holdout_mae": mae,
            "pass": bool(mae < eps),
        })

    gate_macro = macro_res.get("pass", None)
    result = {
        "experiment": "M3-percepatan",
        "mode": "mini" if a.mini else "full",
        "criteria": {
            "3a_micro_exact_observed": bool(gate_3a),
            "3b_micro_reproduces_heldout": bool(gate_3b),
            "3c_counterfactual_shift": bool(gate_3c),
            "macro_heldout_mae_lt_eps": gate_macro,
        },
        "verdict_micro": bool(gate_3a and gate_3b and gate_3c),
        "micro": micro,
        "macro": macro_res,
        "config": {"n": n, "steps": steps, "window": window,
                   "champions": [
                       str(Path(c[0]).relative_to(outdir))
                       if Path(c[0]).is_relative_to(outdir) else Path(c[0]).name
                       for c in champs
                   ]},
        "reproduce": (
            f"python experiments/m3/recover.py{' --mini' if a.mini else ''} "
            "(butuh hasil M1 untuk champion rule.bin)"
        ),
    }
    (outdir / "result.json").write_text(json.dumps(result, indent=2))
    print("M3", "MICRO-PASS" if result["verdict_micro"] else "MICRO-FAIL",
          json.dumps(result["criteria"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
