"""M4 loop v3 — intervensi penghindar-fixed-point (log 008; plan 2026-09-23).

Kekuatan baru loop: KONTRAFAKTUAL. Newton (yang tahu hukum semusta — warisan
M3) menguji setiap langkah kandidat pada horizon-pendek skala penuh (n sama,
5000 langkah, seed iterasi — prefeks deterministik run 20k; instrumen
terkalibrasi GATE-PASS freeze_miss=0/13, addendum plan) SEBELUM berkomitmen.

Per iterasi (K=4, seed 5502..5505, pasangan seed-sama):
 1. Observasi penuh semusta induk (binding stats + J di cap 1 & 3).
 2. Pool kandidat = langkah legal tabel: +1 (table[e]<cap(e)) dan −1
    (table[e]>0) — mutasi dua arah (pelajaran M1v2).
 3. Evaluasi singkat tiap kandidat → REJECT freeze/kolaps (J/J_p < 0,3).
 4. Peringkat ΔJ_short > 0 → top-8 → VALIDASI KOKTAIL (uji gabungan; jika
    kolaps → fallback prefix 4/2/1; jika semua gagal → hold).
 5. Komit → ukur ΔJ 20k pasangan-seed. Kontrol: 8 longgar-acak disjoint
    TANPA filter (null: tanpa kekuatan kontrafaktual) — protokol v2 persis.

Kriteria (dibekukan pra-run):
  W3v3a: min_i J_fb_after_i > 0 (feedback tak pernah membekukan semusta).
  W3v3b: Σ J_fb_after > Σ J_ctrl_after (kumulatif K=4).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m3"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from newton import flowrecover  # noqa: E402
from recover import measure_j, run_window  # noqa: E402
from semesta import ca  # noqa: E402
from loop2 import binding_stats, mutate, observed_slack_coverage, select_control  # noqa: E402
from calibrate_freeze import j_from_states  # noqa: E402

R_MIN = 0.3  # detektor kolaps (threshold kalibrasi — addendum plan)


def legal_moves(table, k):
    """Semua langkah legal: +1 pada longgar, −1 pada aktif. Deterministik."""
    up = [(e, 1) for e in range(len(table)) if table[e] < ca.cap_of(e, k)]
    dn = [(e, -1) for e in range(len(table)) if table[e] > 0]
    return sorted(up + dn)


def short_eval(engine, table, k, n, seed, steps, window, cap, workdir, tag):
    """J horizon-pendek skala penuh + predikat keamanan (freeze/kolaps)."""
    d = Path(workdir) / f"s_{tag}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(table))
    states = run_window(engine, n, k, seed, steps, window, d / "rule.bin",
                        d / "w", init_cap=cap)
    j, amb, static = j_from_states(states, k)
    return {"J": j, "amb": amb, "static": static}


def safe(verdict, j_parent):
    if verdict["J"] == 0.0 and verdict["static"]:
        return False
    if j_parent > 0 and verdict["J"] / j_parent < R_MIN:
        return False
    return True


def observe_and_j(engine, table, k, seed, n, caps, steps, window, workdir, init_cap, role):
    """Sama dengan loop2 (protokol v2, termasuk fix review: dir unik per
    peran — fb_parent|fb_child|ctrl_parent|ctrl_child — satu rule.bin tak
    boleh ditimpa antar-peran): stats + J per cap pada init_cap sama."""
    d = Path(workdir) / f"u_{role}_{seed}_{init_cap}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(table))
    states = run_window(engine, n, k, seed, steps, window, d / "rule.bin", d / "w",
                        init_cap=init_cap)
    pairs = [(list(states[i]), list(states[i + 1])) for i in range(len(states) - 1)]
    stats = binding_stats(pairs, k)
    j_by_cap = {}
    for cap in caps:
        r = measure_j(engine, d, n, k, seed, steps, window, cap, d / f"j{cap}")
        j_by_cap[cap] = r["J"]
    return stats, j_by_cap


def decide(engine, table, k, n, seed, short_steps, short_window, cap, workdir, m, it):
    """Kontrafaktual: evaluasi pool → filter → rank → validasi koktail → komit."""
    pool = legal_moves(table, k)
    jp_s = short_eval(engine, table, k, n, seed, short_steps, short_window, cap,
                      workdir, f"p_{it}")["J"]
    scored, rejected = [], 0
    for e, dlt in pool:
        cand = mutate(table, k, [e] if dlt > 0 else [])
        if dlt < 0:
            cand = list(table)
            cand[e] -= 1
        v = short_eval(engine, cand, k, n, seed, short_steps, short_window, cap,
                       workdir, f"c{e}_{dlt}_{it}")
        if not safe(v, jp_s):
            rejected += 1
            continue
        scored.append({"entry": e, "delta": dlt, "short_j": v["J"],
                       "short_delta": v["J"] - jp_s, "short_class": (
                           "raise" if v["J"] - jp_s >= 0.01 else
                           "drop" if v["J"] - jp_s <= -0.05 else "flat")})
    scored.sort(key=lambda c: (-c["short_delta"], c["entry"]))
    positive = [c for c in scored if c["short_delta"] > 0]

    trail, committed = [], []
    for size in (m, max(1, m // 2), 2, 1):
        if not positive:
            break
        pick = positive[:size]
        if len(pick) < size:
            continue
        T = list(table)
        for c in pick:
            T[c["entry"]] += c["delta"]
        v = short_eval(engine, T, k, n, seed, short_steps, short_window, cap,
                       workdir, f"k{size}_{it}")
        ok = safe(v, jp_s)
        trail.append({"size": size, "short_j": v["J"], "safe": ok})
        if ok:
            committed = pick
            break
    return {"hold": not committed, "committed": committed, "cocktail_trail": trail,
            "n_pool": len(pool), "n_rejected_unsafe": rejected,
            "n_positive": len(positive), "j_parent_short": jp_s}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mini", action="store_true")
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    ap.add_argument("--iterations", type=int, default=0)
    a = ap.parse_args()

    if a.mini:
        F0 = ca.random_table_rich(2, 5700010)
        k, n, caps = 2, 128, [1, 3]
        steps, window = 1500, 32
        short_steps, short_window = 400, 32
        K, m_entries = 2, 4
        base_seed = 11
    else:
        champ = ROOT / "experiments" / "m1v2" / "result" / "_work" / "rule_H_RICH_5700010.bin"
        F0 = list(champ.read_bytes())
        k, n, caps = 2, 16384, [1, 3]
        steps, window = 20000, 512
        short_steps, short_window = 5000, 512
        K, m_entries = 4, 8
        base_seed = 5501  # verdict segar (kalibrasi hanya menyentuh 1093/1094)
    if a.iterations:
        K = a.iterations
    assert all(0 < c < (1 << k) for c in caps), f"init_cap wajib di (0, 2^k−1): {caps}"

    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"
    workdir.mkdir(exist_ok=True)

    cap_lin = caps[0]
    trajectory = []
    F_fb, F_ctrl = list(F0), list(F0)
    j_fb_after, j_ctrl_after = [], []
    for it in range(K):
        seed_i = base_seed + 1 + it  # pasangan seed-sama (efek mutasi murni)

        stats_fb, jcap_parent = observe_and_j(
            a.engine, F_fb, k, seed_i, n, caps, steps, window, workdir, cap_lin,
            role="fb_parent")
        decision = decide(a.engine, F_fb, k, n, seed_i, short_steps, short_window,
                          cap_lin, workdir, m_entries, it)
        tgt = [c["entry"] for c in decision["committed"]]
        if decision["hold"]:
            F_fb_new = list(F_fb)
        else:
            F_fb_new = list(F_fb)
            for c in decision["committed"]:
                F_fb_new[c["entry"]] += c["delta"]
            F_fb_new = ca.clip_table(F_fb_new, k)
        _s, jcap_fb = observe_and_j(
            a.engine, F_fb_new, k, seed_i, n, caps, steps, window, workdir, cap_lin,
            role="fb_child")
        F_fb = F_fb_new

        s_ctrl, jcap_parent_c = observe_and_j(
            a.engine, F_ctrl, k, seed_i, n, caps, steps, window, workdir, cap_lin,
            role="ctrl_parent")
        ctl = [e for e in select_control(s_ctrl, m_entries * 3, seed=base_seed + 300 + it)
               if e not in set(tgt)][:m_entries]
        F_ctrl_new = mutate(F_ctrl, k, ctl) if ctl else list(F_ctrl)
        _s2, jcap_ctrl = observe_and_j(
            a.engine, F_ctrl_new, k, seed_i, n, caps, steps, window, workdir, cap_lin,
            role="ctrl_child")
        F_ctrl = F_ctrl_new

        d_fb = jcap_fb[cap_lin] - jcap_parent[cap_lin]
        d_ctrl = jcap_ctrl[cap_lin] - jcap_parent_c[cap_lin]
        j_fb_after.append(jcap_fb[cap_lin])
        j_ctrl_after.append(jcap_ctrl[cap_lin])
        trajectory.append({
            "iteration": it, "seed": seed_i, "effect_cap": cap_lin,
            "decision": decision,
            "intervention": {"targeted": tgt, "control": ctl,
                             "m": len(tgt),
                             "m_control": len(ctl)},
            "observation": {"loose_diagnostics": observed_slack_coverage(stats_fb)},
            "feedback": {"j_parent": jcap_parent[cap_lin], "j": jcap_fb[cap_lin],
                         "delta_paired": d_fb, "j_by_cap": jcap_fb,
                         "table_fnv": f"{ca.table_fnv(F_fb):016x}"},
            "control": {"j_parent": jcap_parent_c[cap_lin], "j": jcap_ctrl[cap_lin],
                        "delta_paired": d_ctrl, "j_by_cap": jcap_ctrl,
                        "table_fnv": f"{ca.table_fnv(F_ctrl):016x}"},
        })

    w3a = bool(all(j > 0 for j in j_fb_after))
    w3b = bool(sum(j_fb_after) > sum(j_ctrl_after))
    result = {
        "experiment": "M4-loop-v3",
        "mode": "mini" if a.mini else "full",
        "universe": "rich-mini" if a.mini else "RICH",
        "criteria": {"W3v3a_feedback_never_freezes": w3a,
                     "W3v3b_cumulative_performance": w3b},
        "sum_j_feedback": sum(j_fb_after), "sum_j_control": sum(j_ctrl_after),
        "v2_baseline": {"sum_fb": 1.3258, "sum_ctrl": 1.9927,
                        "source": "log 007 (seed 2201-2205)"},
        "instrument": {"kind": "short-horizon-full-scale", "short_steps": short_steps,
                       "r_min": R_MIN, "calibration": "freeze_miss=0/13 (GATE-PASS)"},
        "iterations": K,
        "trajectory": trajectory,
        "reproduce": f"python experiments/m4/loop3.py{' --mini' if a.mini else ''}",
    }
    (outdir / "result.json").write_text(json.dumps(result, indent=2))
    print("M4-LOOP-V3",
          f"W3v3a={'PASS' if w3a else 'FAIL'}",
          f"W3v3b={'PASS' if w3b else 'FAIL'}",
          f"ΣJ fb={sum(j_fb_after):.4f} ctrl={sum(j_ctrl_after):.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
