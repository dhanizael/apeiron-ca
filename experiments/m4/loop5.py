"""M4 loop v5 — robustness multi-seed sebagai kriteria (log 011; plan 2026-09-23).

Misi: atasi bistability cap3 — hukum sehat di KEDUA rezim pada SEMUA instans.
Upgrade kognitif: kriteria dari level-instans (v2–v4) ke LAJU.

Instrumen (warisan 009/010 + gerbang baseline 011):
  cap1: J pada horizon-pendek 5000, window 512 (terkalibrasi; gerbang lolos).
  cap3: HEALTH via mobilitas pada horizon PENUH 20000, 3 seed — gerbang
        baseline menemukan kristalisasi LAMBAT (v4-final 7/7@5000 → 6/7@20000),
        jadi horizon-pendek DITOLAK untuk cap3; mobilitas murah (tanpa
        derive_field) sehingga horizon penuh terjangkau.

Kebijakan komit (baru, koreksi v4-it2): koktail wajib cap1-safe DAN cap3
3/3 mengalir DAN skor gabungan > 0 — fallback 8/4/2/1, hold bila semua gagal.
Filter kandidat: cap1-safe (warisan r_min) DAN cap3 3/3; rank ΔJ_cap1 +
Δmean-mobility_cap3. Kontrol: 8 acak uniform dari pool legal yang sama.

Kriteria (dibekukan; instantiasi dari baseline — disklosikan):
  W3v5a: hukum fb final di 7 seed verdict (11011–11017): cap1 7/7 mengalir
         DAN cap3 7/7 mengalir (threshold = max(6/7, terbaik-baseline 7/7);
         > laju v4-final 6/7).
  W3v5b: Σ_i (J_cap1 + rate_cap3)_fb > Σ_i (...)_ctrl, K=4.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m3"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca  # noqa: E402
from loop2 import observed_slack_coverage  # noqa: E402
from loop3 import legal_moves, observe_and_j  # noqa: E402
from calibrate_freeze import j_from_states  # noqa: E402
from health_landscape import health_from_states  # noqa: E402
from recover import run_window  # noqa: E402

R_MIN = 0.3
CAP1 = 1
CAP3 = 3


def eval_cap1(engine, table, k, n, seed, steps, window, workdir, tag):
    """J cap1 horizon-pendek (instrumen warisan 009)."""
    d = Path(workdir) / f"v5c1_{tag}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(table))
    states = run_window(engine, n, k, seed, steps, window, d / "rule.bin",
                        d / "w", init_cap=CAP1)
    j, amb, static = j_from_states(states, k)
    for f in ("window.bin", "final.bin"):
        p = d / "w" / f
        if p.exists():
            p.unlink()
    return {"J": j, "amb": amb, "static": static}


def eval_cap3(engine, table, k, n, seeds, steps, workdir, tag):
    """Health cap3 multi-seed pada horizon PENUH (mobilitas window 64)."""
    out = []
    for i, seed in enumerate(seeds):
        d = Path(workdir) / f"v5c3_{tag}_{i}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "rule.bin").write_bytes(bytes(table))
        states = run_window(engine, n, k, seed, steps, 64, d / "rule.bin",
                            d / "w", init_cap=CAP3)
        h = health_from_states(states, k)
        out.append({"seed": seed, "flowing": h["flowing"],
                    "mobility": h["mobility"], "J": h["J"]})
        for f in ("window.bin", "final.bin"):
            p = d / "w" / f
            if p.exists():
                p.unlink()
    rate = sum(h["flowing"] for h in out) / len(out)
    mean_mob = sum(h["mobility"] for h in out) / len(out)
    return {"per_seed": out, "rate": rate, "mean_mobility": mean_mob}


def cap1_safe(jp, vm):
    return not (jp["J"] > 0 and vm["J"] / jp["J"] < R_MIN)


def decide(engine, table, k, n, seed, cfg, workdir, m, it):
    """Kontrafaktual: cap1 J + cap3 health 3-seed → filter → rank → koktail
    (safe dua rezim + skor gabungan > 0) → fallback → hold."""
    pool = legal_moves(table, k)
    c3_seeds = cfg["c3_seeds"](seed)
    jp1 = eval_cap1(engine, table, k, n, seed, cfg["s1"], cfg["w1"], workdir, f"p{it}")
    jp3 = eval_cap3(engine, table, k, n, c3_seeds, cfg["s3"], workdir, f"p{it}")
    scored, rejected = [], 0
    for e, dlt in pool:
        T = list(table)
        T[e] += dlt
        vm1 = eval_cap1(engine, T, k, n, seed, cfg["s1"], cfg["w1"], workdir, f"c{e}_{dlt}_{it}")
        if not cap1_safe(jp1, vm1):
            rejected += 1
            continue
        vm3 = eval_cap3(engine, T, k, n, c3_seeds, cfg["s3"], workdir, f"c{e}_{dlt}_{it}")
        if vm3["rate"] < 1.0:
            rejected += 1
            continue
        sc = (vm1["J"] - jp1["J"]) + (vm3["mean_mobility"] - jp3["mean_mobility"])
        if sc > 0:
            scored.append({"entry": e, "delta": dlt,
                           "short_cap1": vm1["J"], "cap3_rate": vm3["rate"],
                           "cap3_mob": vm3["mean_mobility"], "score": round(sc, 6)})
    scored.sort(key=lambda c: (-c["score"], c["entry"]))
    trail, committed = [], []
    for size in (m, max(1, m // 2), 2, 1):
        pick = scored[:size]
        if len(pick) < size:
            continue
        T = list(table)
        for c in pick:
            T[c["entry"]] += c["delta"]
        vk1 = eval_cap1(engine, T, k, n, seed, cfg["s1"], cfg["w1"], workdir, f"k{size}_{it}")
        vk3 = eval_cap3(engine, T, k, n, c3_seeds, cfg["s3"], workdir, f"k{size}_{it}")
        joint = (vk1["J"] - jp1["J"]) + (vk3["mean_mobility"] - jp3["mean_mobility"])
        safe = cap1_safe(jp1, vk1) and vk3["rate"] >= 1.0
        # KEBIJAKAN BARU: skor gabungan koktail wajib > 0 (koreksi v4-it2)
        ok = safe and joint > 0
        trail.append({"size": size, "cap1": vk1["J"], "cap3_rate": vk3["rate"],
                      "joint_score": round(joint, 6), "safe": safe, "commit": ok})
        if ok:
            committed = pick
            break
    return {"hold": not committed, "committed": committed, "cocktail_trail": trail,
            "n_pool": len(pool), "n_rejected_unsafe": rejected,
            "n_positive": len(scored), "cap3_seeds": len(c3_seeds),
            "j_parent_short": {"cap1": jp1["J"], "cap3_health": jp3["per_seed"]}}


def final_verdict(engine, table, k, n, seeds, cfg, workdir):
    """Verdict 7-seed hukum final: cap1 J / mobilitas; cap3 mobilitas."""
    cap1 = [eval_cap1(engine, table, k, n, s, 20000, 512, workdir, f"fv1_{s}") for s in seeds]
    cap1_health = [h["J"] if h["J"] is not None else (1.0 if not h["static"] else 0.0)
                   for h in ({"J": c["J"], "static": c["static"]} for c in cap1)]
    cap3 = [eval_cap3(engine, table, k, n, [s], 20000, workdir, f"fv3_{s}") for s in seeds]
    c1r = sum(1 for c in cap1 if (c["J"] or 0) > 0 or not c["static"]) / len(seeds)
    c3r = sum(h["rate"] for h in cap3) / len(seeds)
    return {"seeds": seeds, "cap1_rate": c1r, "cap3_rate": c3r,
            "cap1_detail": [{"seed": s, "J": c["J"], "static": c["static"]}
                            for s, c in zip(seeds, cap1)],
            "cap3_detail": [{"seed": s, "flowing": h["per_seed"][0]["flowing"],
                             "mobility": h["per_seed"][0]["mobility"]}
                            for s, h in zip(seeds, cap3)]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mini", action="store_true")
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    ap.add_argument("--iterations", type=int, default=0)
    a = ap.parse_args()

    if a.mini:
        F0 = ca.random_table_rich(2, 5700010)
        k, n = 2, 128
        cfg = {"s1": 800, "w1": 32, "s3": 1200, "c3_seeds": lambda s: [s, s + 100]}
        steps, window = 1500, 32
        K, m_entries = 2, 4
        base_seed = 11
        verdict_seeds = [41, 42, 43, 44, 45, 46, 47]
    else:
        from health_landscape import load_baseline_laws
        F0 = load_baseline_laws()["v4_final"]  # kontinuitas: lanjutkan semesta v4
        k, n = 2, 16384
        cfg = {"s1": 5000, "w1": 512, "s3": 20000,
               "c3_seeds": lambda s: [s, s + 100, s + 200]}
        steps, window = 20000, 512
        K, m_entries = 4, 8
        base_seed = 11001  # trajectory: 11002–11005; verdict: 11011–11017
        verdict_seeds = list(range(11011, 11018))
    if a.iterations:
        K = a.iterations
    assert all(0 < c < (1 << k) for c in (CAP1, CAP3)), "init_cap wajib di (0, 2^k−1)"

    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"
    workdir.mkdir(exist_ok=True)

    trajectory = []
    F_fb, F_ctrl = list(F0), list(F0)
    H_fb, H_ctrl = [], []
    for it in range(K):
        seed_i = base_seed + 1 + it
        stats_fb, jcap_parent = observe_and_j(
            a.engine, F_fb, k, seed_i, n, [CAP1], steps, window, workdir, CAP1,
            role="fb_parent")
        decision = decide(a.engine, F_fb, k, n, seed_i, cfg, workdir, m_entries, it)
        tgt_moves = [(c["entry"], c["delta"]) for c in decision["committed"]]
        F_fb_new = list(F_fb)
        for e, d in tgt_moves:
            F_fb_new[e] += d
        F_fb_new = ca.clip_table(F_fb_new, k)
        _s, jcap_fb = observe_and_j(
            a.engine, F_fb_new, k, seed_i, n, [CAP1], steps, window, workdir, CAP1,
            role="fb_child")
        h3_fb = eval_cap3(a.engine, F_fb_new, k, n, cfg["c3_seeds"](seed_i),
                          cfg["s3"], workdir, f"fbfull_{it}")
        F_fb = F_fb_new

        s_ctrl, jcap_parent_c = observe_and_j(
            a.engine, F_ctrl, k, seed_i, n, [CAP1], steps, window, workdir, CAP1,
            role="ctrl_parent")
        rng = ca.Rng(base_seed + 300 + it)
        tgt_set = {e for e, _ in tgt_moves}
        cand = [(e, d) for e, d in legal_moves(F_ctrl, k) if e not in tgt_set]
        ctl_moves = []
        for _ in range(m_entries):
            if not cand:
                break
            i = rng.next_u64() % len(cand)
            ctl_moves.append(cand.pop(i))
        F_ctrl_new = list(F_ctrl)
        for e, d in ctl_moves:
            F_ctrl_new[e] += d
        F_ctrl_new = ca.clip_table(F_ctrl_new, k)
        _s2, jcap_ctrl = observe_and_j(
            a.engine, F_ctrl_new, k, seed_i, n, [CAP1], steps, window, workdir, CAP1,
            role="ctrl_child")
        h3_ctrl = eval_cap3(a.engine, F_ctrl_new, k, n, cfg["c3_seeds"](seed_i),
                            cfg["s3"], workdir, f"ctrlfull_{it}")
        F_ctrl = F_ctrl_new

        H_fb.append(jcap_fb[CAP1] + h3_fb["rate"])
        H_ctrl.append(jcap_ctrl[CAP1] + h3_ctrl["rate"])
        trajectory.append({
            "iteration": it, "seed": seed_i,
            "decision": decision,
            "intervention": {"targeted": [list(t) for t in tgt_moves],
                             "control": [list(t) for t in ctl_moves],
                             "m": len(tgt_moves), "m_control": len(ctl_moves)},
            "observation": {"loose_diagnostics": observed_slack_coverage(stats_fb)},
            "feedback": {"j_parent": jcap_parent[CAP1], "j": jcap_fb[CAP1],
                         "delta_paired": jcap_fb[CAP1] - jcap_parent[CAP1],
                         "cap3_health": h3_fb["per_seed"],
                         "table_fnv": f"{ca.table_fnv(F_fb):016x}"},
            "control": {"j_parent": jcap_parent_c[CAP1], "j": jcap_ctrl[CAP1],
                        "delta_paired": jcap_ctrl[CAP1] - jcap_parent_c[CAP1],
                        "cap3_health": h3_ctrl["per_seed"],
                        "table_fnv": f"{ca.table_fnv(F_ctrl):016x}"},
        })

    fv = final_verdict(a.engine, F_fb, k, n, verdict_seeds, cfg, workdir)
    w3a = bool(fv["cap1_rate"] >= 1.0 and fv["cap3_rate"] >= 1.0)
    sum_fb, sum_ctrl = sum(H_fb), sum(H_ctrl)
    w3b = bool(sum_fb > sum_ctrl)
    result = {
        "experiment": "M4-loop-v5",
        "mode": "mini" if a.mini else "full",
        "lineage": "v4-final" if not a.mini else "rich-mini",
        "criteria": {"W3v5a_robust_multi_regime_health": w3a,
                     "W3v5b_multi_regime_performance": w3b},
        "sum_H": {"feedback": round(sum_fb, 6), "control": round(sum_ctrl, 6)},
        "final_verdict": fv,
        "iterations": K,
        "trajectory": trajectory,
        "reproduce": f"python experiments/m4/loop5.py{' --mini' if a.mini else ''}",
    }
    (outdir / "result_loop5.json").write_text(json.dumps(result, indent=2))
    print("M4-LOOP-V5",
          f"W3v5a={'PASS' if w3a else 'FAIL'}",
          f"W3v5b={'PASS' if w3b else 'FAIL'}",
          f"ΣH fb={sum_fb:.4f} ctrl={sum_ctrl:.4f}",
          f"final: cap1={fv['cap1_rate']:.2f} cap3={fv['cap3_rate']:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
