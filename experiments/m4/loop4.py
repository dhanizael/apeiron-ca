"""M4 loop v4 — kontrafaktual multi-rezim (log 010; plan 2026-09-23).

Upgrade kognitif loop: v3 aman di rezim intervensi tetapi buta terhadap rezim
lain (hukum v3: cap1 0,50 / cap3 0,00 — kerusakan yang didisklosikan sendiri).
v4 mengevaluasi tiap kandidat di KEDUA rezim (init_cap 1 & 3, horizon-pendek
skala penuh — instrumen warisan 009): keselamatan = tanpa kolaps di rezim mana
pun yang induknya hidup; skor = Δ(J_c1 + J_c3); validasi koktail dua-rezim +
fallback. Kontrol = 8 acak uniform dari pool legal yang SAMA (kelas aksi sama,
tanpa kontrafaktual; perubahan dari loose-observed didisklosikan pra-run di
log 010 — loose-observed induk v3 kosong → kontrol v2-style degenerate).

Kriteria (dibekukan pra-run):
  W3v4a (perbaikan multi-rezim): hukum fb final J_cap1 > 0 DAN J_cap3 > 0.
  W3v4b (kinerja multi-rezim): Σ(J_c1+J_c3)_fb > Σ(J_c1+J_c3)_ctrl, K=4.
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
from recover import run_window  # noqa: E402

R_MIN = 0.3
CAPS = [1, 3]


def short_two(engine, table, k, n, seed, steps, window, workdir, tag):
    """Verdict horizon-pendek dua rezim (init_cap 1 & 3) — kosmos segar per
    rezim, seed sama (paired vs parent)."""
    out = {}
    for cap in CAPS:
        d = Path(workdir) / f"s_{tag}_{cap}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "rule.bin").write_bytes(bytes(table))
        states = run_window(engine, n, k, seed, steps, window, d / "rule.bin",
                            d / "w", init_cap=cap)
        j, amb, static = j_from_states(states, k)
        out[cap] = {"J": j, "amb": amb, "static": static}
    return out


def safe_two(vp, vm):
    """Keselamatan dua rezim: kolaps (J/J_p < R_MIN, termasuk beku) dihitung
    hanya bila parent rezim itu hidup (J_p > 0) — rezim induk yang sudah mati
    tak punya apa-apa untuk dilindungi (misinya justru dihidupkan)."""
    for cap in vp:
        jp, jm = vp[cap]["J"], vm[cap]["J"]
        if jp > 0 and jm / jp < R_MIN:
            return False
    return True


def score_two(vp, vm):
    return sum(vm[c]["J"] for c in CAPS) - sum(vp[c]["J"] for c in CAPS)


def decide(engine, table, k, n, seed, short_steps, short_window, workdir, m, it):
    """Kontrafaktual dua rezim: pool legal → filter keselamatan → rank skor →
    validasi koktail → fallback 8/4/2/1 → hold bila semua gagal."""
    pool = legal_moves(table, k)
    jp = short_two(engine, table, k, n, seed, short_steps, short_window, workdir, f"p_{it}")
    jp_sum = sum(jp[c]["J"] for c in CAPS)
    scored, rejected = [], 0
    for e, dlt in pool:
        T = list(table)
        T[e] += dlt
        vm = short_two(engine, T, k, n, seed, short_steps, short_window, workdir, f"c{e}_{dlt}_{it}")
        if not safe_two(jp, vm):
            rejected += 1
            continue
        sc = score_two(jp, vm)
        if sc > 0:
            scored.append({"entry": e, "delta": dlt,
                           "short": {str(c): vm[c]["J"] for c in CAPS},
                           "score": round(sc, 6)})
    scored.sort(key=lambda c: (-c["score"], c["entry"]))
    trail, committed = [], []
    for size in (m, max(1, m // 2), 2, 1):
        pick = scored[:size]
        if len(pick) < size:
            continue
        T = list(table)
        for c in pick:
            T[c["entry"]] += c["delta"]
        vm = short_two(engine, T, k, n, seed, short_steps, short_window, workdir, f"k{size}_{it}")
        ok = safe_two(jp, vm)
        trail.append({"size": size, "short": {str(c): vm[c]["J"] for c in CAPS},
                      "score": round(score_two(jp, vm), 6), "safe": ok})
        if ok:
            committed = pick
            break
    return {"hold": not committed, "committed": committed, "cocktail_trail": trail,
            "n_pool": len(pool), "n_rejected_unsafe": rejected,
            "n_positive": len(scored), "j_parent_short": {str(c): jp[c]["J"] for c in CAPS}}


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
        steps, window = 1500, 32
        short_steps, short_window = 400, 32
        K, m_entries = 2, 4
        base_seed = 11
    else:
        F0 = list(Path(ROOT, "experiments/m1v2/result/_work/rule_H_RICH_5700010.bin").read_bytes())
        v3 = json.loads((ROOT / "experiments" / "m4" / "result" / "result.json").read_text())
        Fb = list(F0)
        for c in v3["trajectory"][0]["decision"]["committed"]:
            Fb[c["entry"]] += c["delta"]
        Fb = ca.clip_table(Fb, 2)
        expect = v3["trajectory"][-1]["feedback"]["table_fnv"]
        assert f"{ca.table_fnv(Fb):016x}" == expect, "silsilah hukum v3 rusak"
        F0 = Fb  # loop v4 melanjutkan semesta loop v3
        k, n = 2, 16384
        steps, window = 20000, 512
        short_steps, short_window = 5000, 512
        K, m_entries = 4, 8
        base_seed = 8801  # verdict segar
    if a.iterations:
        K = a.iterations
    assert all(0 < c < (1 << k) for c in CAPS), "init_cap wajib di (0, 2^k−1)"

    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"
    workdir.mkdir(exist_ok=True)

    trajectory = []
    F_fb, F_ctrl = list(F0), list(F0)
    j_fb = {c: [] for c in CAPS}
    j_ctrl = {c: [] for c in CAPS}
    for it in range(K):
        seed_i = base_seed + 1 + it  # pasangan seed-sama

        stats_fb, jcap_parent = observe_and_j(
            a.engine, F_fb, k, seed_i, n, CAPS, steps, window, workdir, CAPS[0],
            role="fb_parent")
        decision = decide(a.engine, F_fb, k, n, seed_i, short_steps, short_window,
                          workdir, m_entries, it)
        tgt_moves = [(c["entry"], c["delta"]) for c in decision["committed"]]
        if decision["hold"]:
            F_fb_new = list(F_fb)
        else:
            F_fb_new = list(F_fb)
            for e, d in tgt_moves:
                F_fb_new[e] += d
            F_fb_new = ca.clip_table(F_fb_new, k)
        _s, jcap_fb = observe_and_j(
            a.engine, F_fb_new, k, seed_i, n, CAPS, steps, window, workdir, CAPS[0],
            role="fb_child")
        F_fb = F_fb_new

        s_ctrl, jcap_parent_c = observe_and_j(
            a.engine, F_ctrl, k, seed_i, n, CAPS, steps, window, workdir, CAPS[0],
            role="ctrl_parent")
        # kontrol: acak uniform dari pool legal yang sama, disjoint dari terarah
        rng = ca.Rng(base_seed + 300 + it)
        tgt_set = {e for e, _ in tgt_moves}
        cand = [(e, d) for e, d in legal_moves(F_ctrl, k) if e not in tgt_set]
        ctl_moves = []
        for _ in range(m_entries):
            if not cand:
                break
            i = rng.next_u64() % len(cand)
            ctl_moves.append(cand.pop(i))
        if ctl_moves:
            F_ctrl_new = list(F_ctrl)
            for e, d in ctl_moves:
                F_ctrl_new[e] += d
            F_ctrl_new = ca.clip_table(F_ctrl_new, k)
        else:
            F_ctrl_new = list(F_ctrl)
        _s2, jcap_ctrl = observe_and_j(
            a.engine, F_ctrl_new, k, seed_i, n, CAPS, steps, window, workdir, CAPS[0],
            role="ctrl_child")
        F_ctrl = F_ctrl_new

        for c in CAPS:
            j_fb[c].append(jcap_fb[c])
            j_ctrl[c].append(jcap_ctrl[c])
        trajectory.append({
            "iteration": it, "seed": seed_i,
            "decision": decision,
            "intervention": {"targeted": [list(t) for t in tgt_moves],
                             "control": [list(t) for t in ctl_moves],
                             "m": len(tgt_moves), "m_control": len(ctl_moves)},
            "observation": {"loose_diagnostics": observed_slack_coverage(stats_fb)},
            "feedback": {"j_parent": jcap_parent[CAPS[0]], "j": jcap_fb[CAPS[0]],
                         "delta_paired": jcap_fb[CAPS[0]] - jcap_parent[CAPS[0]],
                         "j_by_cap": jcap_fb,
                         "table_fnv": f"{ca.table_fnv(F_fb):016x}"},
            "control": {"j_parent": jcap_parent_c[CAPS[0]], "j": jcap_ctrl[CAPS[0]],
                        "delta_paired": jcap_ctrl[CAPS[0]] - jcap_parent_c[CAPS[0]],
                        "j_by_cap": jcap_ctrl,
                        "table_fnv": f"{ca.table_fnv(F_ctrl):016x}"},
        })

    w3a = bool(j_fb[CAPS[0]][-1] > 0 and j_fb[CAPS[1]][-1] > 0)
    sum_fb = sum(j_fb[c][i] for c in CAPS for i in range(K))
    sum_ctrl = sum(j_ctrl[c][i] for c in CAPS for i in range(K))
    w3b = bool(sum_fb > sum_ctrl)
    result = {
        "experiment": "M4-loop-v4",
        "mode": "mini" if a.mini else "full",
        "universe": "rich-mini" if a.mini else "RICH",
        "lineage": "v3-final (cap1 0.50 / cap3 0.00)" if not a.mini else "rich-mini",
        "criteria": {"W3v4a_multi_regime_repair": w3a,
                     "W3v4b_multi_regime_performance": w3b},
        "sum_j_multi_regime": {"feedback": round(sum_fb, 6), "control": round(sum_ctrl, 6)},
        "sum_j_by_regime": {"feedback": {str(c): round(sum(j_fb[c]), 6) for c in CAPS},
                            "control": {str(c): round(sum(j_ctrl[c]), 6) for c in CAPS}},
        "iterations": K,
        "trajectory": trajectory,
        "reproduce": f"python experiments/m4/loop4.py{' --mini' if a.mini else ''}",
    }
    (outdir / "result.json").write_text(json.dumps(result, indent=2))
    print("M4-LOOP-V4",
          f"W3v4a={'PASS' if w3a else 'FAIL'}",
          f"W3v4b={'PASS' if w3b else 'FAIL'}",
          f"ΣJ fb={sum_fb:.4f} ctrl={sum_ctrl:.4f}",
          f"fb[cap3]={j_fb[3][-1]:.4f} ctrl[cap3]={j_ctrl[3][-1]:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
