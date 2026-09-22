"""M4 — loop tertutup v1: discover → intervene → verify (W3, spec §9 amendemen M4).

Per iterasi: Newton mengamati medan aliran (eksak, FM-E aman) → mengidentifikasi
entri IKAT (cap>0, f=cap, sering — kemacetan) dan LONGGAR aktif (f<cap, tersibuk)
→ intervensi terarah: +1 pada 64 longgar tersibuk; kontrol: +1 pada 64 longgar
acak (besaran sama, tanpa arah) → prediksi: ΔJ_max terarah > kontrol.
Bukan klaim open-endedness — bukti loop: temuan → intervensi → konsekuensi.
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

M_ENTRIES = 64


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


def select_targeted(stats, m=M_ENTRIES):
    """Longgar tersibuk — intervensi diturunkan dari temuan."""
    cands = [(stats["slack"][i], i) for i in range(len(stats["slack"])) if stats["slack"][i] > 0]
    cands.sort(reverse=True)
    return [i for _, i in cands[:m]]


def select_control(stats, m=M_ENTRIES, seed=0):
    """Longgar acak — besaran sama, tanpa arah."""
    rng = ca.Rng(seed)
    cands = [i for i in range(len(stats["slack"])) if stats["slack"][i] > 0]
    return [cands[rng.next_u64() % len(cands)] for _ in range(min(m, len(cands)))]


def mutate(table, k, entries):
    t = list(table)
    for e in entries:
        t[e] += 1
    return ca.clip_table(t, k)


def observe_and_j(engine, table, k, seed, n, caps, steps, window, workdir, init_cap=0):
    """Observasi medan + J per cap pada init_cap yang SAMA (amati rezim yang
    kau intervensi). Kembalikan (stats, J_max, J_by_cap)."""
    d = Path(workdir) / f"u_{seed}_{init_cap}"
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
    j_max = j_by_cap[max(caps)]
    return stats, j_max, j_by_cap


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mini", action="store_true")
    ap.add_argument("--engine", default=str(ROOT / "engine" / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    ap.add_argument("--iterations", type=int, default=0)
    a = ap.parse_args()

    if a.mini:
        sand = [0] * 64
        for l in range(4):
            for c in range(4):
                for r in range(4):
                    sand[(l << 4) | (c << 2) | r] = 1 if c > r + 1 else 0
        F0 = ca.clip_table(sand, 2)
        k, n, caps = 2, 256, [2]
        steps, window = 1000, 32
        K = 2
        m_entries = 8
        base_seed = 11
    else:
        m1 = ROOT / "experiments" / "m1" / "result"
        r1 = json.loads((m1 / "result.json").read_text())
        c0 = r1["champions"][0]
        F0 = list(Path(m1, f"champ_k{c0['k']}_s{c0['seed']}", "rule.bin").read_bytes())
        k, n, caps = 4, 16384, [6, 10, 14]
        steps, window = 20000, 512
        K = 4
        m_entries = 256
        base_seed = 1092

    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = outdir / "_work"
    workdir.mkdir(exist_ok=True)

    trajectory = []
    F_fb, F_ctrl = list(F0), list(F0)
    deltas_fb, deltas_ctrl = [], []
    # Rezim efek: LINIER (cap rendah) — di rezim jenuh medan aliran diklip
    # kapasitas, J tak peka terhadap mutasi tabel (pelajaran run-2).
    cap_lin = caps[0]
    for it in range(K):
        # PASANGAN SEED-SAMA (pelajaran run-1): J(F', s) − J(F, s) mengisolasi
        # efek mutasi murni — semesta deterministik, nol derau seed.
        seed_i = base_seed + 1 + it
        stats_fb, J_parent_fb, jcap_parent = observe_and_j(a.engine, F_fb, k, seed_i, n, caps, steps, window, workdir, init_cap=cap_lin)
        tgt = set(select_targeted(stats_fb, m_entries)[:m_entries])
        F_fb = mutate(F_fb, k, list(tgt))
        _s, J_fb, jcap_fb = observe_and_j(a.engine, F_fb, k, seed_i, n, caps, steps, window, workdir, init_cap=cap_lin)
        s_ctrl, J_parent_ctrl, _ = observe_and_j(a.engine, F_ctrl, k, seed_i, n, caps, steps, window, workdir, init_cap=cap_lin)
        ctl = [e for e in select_control(s_ctrl, m_entries * 3, seed=base_seed + 300 + it)
               if e not in tgt][:m_entries]  # kontrol ≠ terarah (disjoint)
        F_ctrl = mutate(F_ctrl, k, ctl)
        _s2, J_ctrl1, jcap_ctrl = observe_and_j(a.engine, F_ctrl, k, seed_i, n, caps, steps, window, workdir, init_cap=cap_lin)
        d_fb = J_fb - J_parent_fb
        d_ctrl = J_ctrl1 - J_parent_ctrl
        deltas_fb.append(d_fb)
        deltas_ctrl.append(d_ctrl)
        trajectory.append({
            "iteration": it,
            "effect_cap": cap_lin,
            "feedback": {"j_parent": J_parent_fb, "j": J_fb, "delta_paired": d_fb,
                         "j_by_cap": jcap_fb,
                         "table_fnv": f"{ca.table_fnv(F_fb):016x}"},
            "control": {"j_parent": J_parent_ctrl, "j": J_ctrl1, "delta_paired": d_ctrl,
                        "j_by_cap": jcap_ctrl,
                        "table_fnv": f"{ca.table_fnv(F_ctrl):016x}"},
        })

    mean_fb = sum(deltas_fb) / len(deltas_fb)
    mean_ctrl = sum(deltas_ctrl) / len(deltas_ctrl)
    w3 = bool(mean_fb > mean_ctrl and all(d >= 0 for d in deltas_fb))
    result = {
        "experiment": "M4-loop",
        "mode": "mini" if a.mini else "full",
        "criteria": {"W3_feedback_directed_effect": w3},
        "mean_delta_feedback": mean_fb,
        "mean_delta_control": mean_ctrl,
        "iterations": K,
        "trajectory": trajectory,
        "reproduce": f"python experiments/m4/loop.py{' --mini' if a.mini else ''}",
    }
    (outdir / "result.json").write_text(json.dumps(result, indent=2))
    print("M4-LOOP", "W3-PASS" if w3 else "W3-NULL",
          f"mean_dJ fb={mean_fb:.4f} ctrl={mean_ctrl:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
