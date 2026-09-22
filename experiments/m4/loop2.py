"""M4 loop v2 — W3 round-2 di semesta RICH (log 007; plan 2026-09-22).

Latar: W3-NULL run-1..3 (log 005) teratribusi — semesta POOR ~100%
capacity-bound, J tak peka terhadap mutasi tabel. Log 006 menemukan juara
RICH (slack 61%, tak pernah runtuh di horizon 10⁶): semestra yang TIDAK
capacity-bound → prediksi eksplisit: tuas level-tabel hidup kembali.

Per iterasi (K=4): Newton mengamati medan aliran semesta RICH pada init_cap
LINIER (rezim yang diintervensi) → identifikasi entri longgar tersibuk →
intervensi terarah +1 pada M entri; kontrol: +1 pada M longgar acak disjoint
→ pasangan seed-sama: ΔJ = J(F', s) − J(F, s) (efek mutasi murni, nol derau
seed) → prediksi W3v2: mean ΔJ_fb > mean ΔJ_ctrl, semua ΔJ_fb ≥ 0.

Atribusi per iterasi (W3 plan): J diukur juga di cap jenuh — jika efek
linier > efek jenuh, mekanisme capacity-bound (run-2) direplikasi di RICH;
jika keduanya hidup, RICH benar-benar bukan kapasitas-bound.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m3"))

from newton import flowrecover  # noqa: E402
from recover import measure_j, run_window  # noqa: E402
from semesta import ca  # noqa: E402


def binding_stats(pairs, k):
    """Per entri teramati: count, at_cap (f=cap>0), slack (f<cap, cap>0)."""
    size = 1 << (3 * k)
    max_cell = (1 << k) - 1
    count = [0] * size
    at_cap = [0] * size
    slack = [0] * size
    for s, t in pairs:
        f = flowrecover.derive_field(s, t, k)
        if f is None:
            continue
        n = len(s)
        for i in range(n):
            l, c, r = s[(i - 1) % n], s[i], s[(i + 1) % n]
            idx = (l << (2 * k)) | (c << k) | r
            cap = min(c, max_cell - r)
            if cap <= 0:
                continue
            count[idx] += 1
            if f[i] == cap:
                at_cap[idx] += 1
            else:
                slack[idx] += 1
    return {"count": count, "at_cap": at_cap, "slack": slack}


def select_targeted(stats, m):
    """Longgar tersibuk — intervensi diturunkan dari temuan Newton."""
    cands = [(stats["slack"][i], i) for i in range(len(stats["slack"])) if stats["slack"][i] > 0]
    cands.sort(reverse=True)
    return [i for _, i in cands[:m]]


def select_control(stats, m, seed, exclude=()):
    """Longgar acak disjoint dari terarah — besaran sama, tanpa arah."""
    rng = ca.Rng(seed)
    cands = [i for i in range(len(stats["slack"]))
             if stats["slack"][i] > 0 and i not in exclude]
    return [cands[rng.next_u64() % len(cands)] for _ in range(min(m, len(cands)))]


def observed_slack_coverage(stats):
    """Diagnostik atribusi: berapa banyak entri longgar TERAMATI + teratas."""
    s = stats["slack"]
    loose = [i for i in range(len(s)) if s[i] > 0]
    top = sorted(loose, key=lambda i: -s[i])[:8]
    return {"n_loose_observed": len(loose),
            "top_slack_observed": [[i, s[i]] for i in top]}


def observe_and_j(engine, table, k, seed, n, caps, steps, window, workdir, init_cap, role):
    """Observasi medan pada init_cap yang diintervensi + J per cap (atribusi).
    role = fb_parent|fb_child|ctrl_parent|ctrl_child — dir unik per peran
    (kolisi arsip lama: satu rule.bin ditimpa 4 kali per iterasi)."""
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


def mutate(table, k, entries):
    t = list(table)
    for e in entries:
        t[e] += 1
    return ca.clip_table(t, k)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mini", action="store_true")
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    ap.add_argument("--iterations", type=int, default=0)
    a = ap.parse_args()

    if a.mini:
        # semesta RICH mini: generator rich k=2 (slack by construction)
        F0 = ca.random_table_rich(2, 5700010)
        k, n, caps = 2, 256, [2, 3]
        steps, window = 1000, 32
        K, m_entries = 2, 8
        base_seed = 11
    else:
        champ = ROOT / "experiments" / "m1v2" / "result" / "_work" / "rule_H_RICH_5700010.bin"
        F0 = list(champ.read_bytes())
        # k=2 → cell maks 3: init_cap WAJIB < 2^k (guard di bawah; pelajaran
        # kegagalan run-1 full: caps v1 k=4 [6,14] tidak valid untuk k=2).
        k, n, caps = 2, 16384, [1, 3]  # 1: rezim linier (intervensi); 3: jenuh (atribusi)
        steps, window = 20000, 512
        # Tabel k=2 hanya 64 entri — m=256 warisan v1 (k=4) degenerate;
        # m=8 terkalibrasi probe (busiest-8 vs random-8 terpisah 100×).
        K, m_entries = 4, 8
        # Seed verdict segar (2201+): seed 1093/1094 terpakai probe kalibrasi.
        base_seed = 2201
    if a.iterations:
        K = a.iterations
    assert all(0 < c < (1 << k) for c in caps), f"init_cap wajib di (0, 2^k−1): caps={caps} k={k}"

    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"
    workdir.mkdir(exist_ok=True)

    cap_lin = caps[0]  # rezim efek: LINIER — observasi & intervensi di sini
    trajectory = []
    F_fb, F_ctrl = list(F0), list(F0)
    deltas_fb, deltas_ctrl = [], []
    for it in range(K):
        seed_i = base_seed + 1 + it  # pasangan seed-sama (efek mutasi murni)
        stats_fb, jcap_parent = observe_and_j(
            a.engine, F_fb, k, seed_i, n, caps, steps, window, workdir, cap_lin,
            role="fb_parent")
        tgt = select_targeted(stats_fb, m_entries)
        F_fb_new = mutate(F_fb, k, tgt)
        _s, jcap_fb = observe_and_j(
            a.engine, F_fb_new, k, seed_i, n, caps, steps, window, workdir, cap_lin,
            role="fb_child")
        F_fb = F_fb_new

        s_ctrl, jcap_parent_c = observe_and_j(
            a.engine, F_ctrl, k, seed_i, n, caps, steps, window, workdir, cap_lin,
            role="ctrl_parent")
        ctl_set = set(tgt)
        ctl = [e for e in select_control(s_ctrl, m_entries * 3, seed=base_seed + 300 + it)
               if e not in ctl_set][:m_entries]
        F_ctrl_new = mutate(F_ctrl, k, ctl)
        _s2, jcap_ctrl = observe_and_j(
            a.engine, F_ctrl_new, k, seed_i, n, caps, steps, window, workdir, cap_lin,
            role="ctrl_child")
        F_ctrl = F_ctrl_new

        d_fb = jcap_fb[cap_lin] - jcap_parent[cap_lin]
        d_ctrl = jcap_ctrl[cap_lin] - jcap_parent_c[cap_lin]
        deltas_fb.append(d_fb)
        deltas_ctrl.append(d_ctrl)
        trajectory.append({
            "iteration": it,
            "effect_cap": cap_lin,
            "seed": seed_i,
            "intervention": {
                "targeted": tgt,
                "control": ctl,
                "m": len(tgt),
            },
            "observation": {
                "parent_stats_slack": stats_fb["slack"],
                "loose_diagnostics": observed_slack_coverage(stats_fb),
            },
            "feedback": {"j_parent": jcap_parent[cap_lin], "j": jcap_fb[cap_lin],
                         "delta_paired": d_fb, "j_by_cap": jcap_fb,
                         "table_fnv": f"{ca.table_fnv(F_fb):016x}"},
            "control": {"j_parent": jcap_parent_c[cap_lin], "j": jcap_ctrl[cap_lin],
                        "delta_paired": d_ctrl, "j_by_cap": jcap_ctrl,
                        "table_fnv": f"{ca.table_fnv(F_ctrl):016x}"},
        })

    mean_fb = sum(deltas_fb) / len(deltas_fb)
    mean_ctrl = sum(deltas_ctrl) / len(deltas_ctrl)
    w3v2 = bool(mean_fb > mean_ctrl and all(d >= 0 for d in deltas_fb))
    # W3v2b — konsekuensi: intervensi turunan-temuan berdampak lebih besar
    # daripada acak (|Δ| fb > |Δ| ctrl per iterasi, mean). Probe kalibrasi
    # (seed 1093/1094) menunjukkan +1 busiest-slack cenderung MEMBEKUKAN
    # semesta (Δ = −J0); kriteria ini menangkap "tuas kuat" apa pun arahnya,
    # dan arah dilaporkan terpisah oleh W3v2a di atas.
    w3v2b = bool(sum(abs(d) for d in deltas_fb) / len(deltas_fb)
                 > sum(abs(d) for d in deltas_ctrl) / len(deltas_ctrl))

    result = {
        "experiment": "M4-loop-v2",
        "mode": "mini" if a.mini else "full",
        "universe": "RICH" if not a.mini else "rich-mini",
        "criteria": {"W3v2_feedback_directed_effect_rich": w3v2,
                     "W3v2b_finding_lever_magnitude": w3v2b},
        "mean_delta_feedback": mean_fb,
        "mean_delta_control": mean_ctrl,
        "iterations": K,
        "trajectory": trajectory,
        "reproduce": f"python experiments/m4/loop2.py{' --mini' if a.mini else ''}",
    }
    (outdir / "result.json").write_text(json.dumps(result, indent=2))
    print("M4-LOOP-V2", "W3v2-PASS" if w3v2 else "W3v2-NULL",
          f"mean_dJ fb={mean_fb:.4f} ctrl={mean_ctrl:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
