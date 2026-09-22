# M4 — Closed Loop + Growth Meter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Loop tertutup v1 (temuan Newton → intervensi terarah → efek terukur vs kontrol, W3) + kurva growth-rate lintas 3 rezim (K5) + kompresi (W4).

**Architecture:** Loop: per iterasi, observasi medan aliran → entri IKAT (F=cap>0, sering) & LONGGAR aktif (F<cap, tersibuk) → mutasi +1 pada 64 longgar tersibuk (terarah) vs 64 acak (kontrol) → ΔJ_max dibandingkan. Growth meter: model_bits(t) = k × entri teramati + bit makro, t ∈ {10³,10⁴,10⁶}, rezim = juara A/B (M1) + 184.

**Tech Stack:** Python stdlib + pytest; engine eksisting (tanpa perubahan).

**Spec:** `docs/superpowers/specs/2026-09-21-0and1-design.md` §9 "M4 (amendemen)".

## Global Constraints

- Semua definisi dibekukan di spec amendemen M4; R1 tetap terbuka (saturasi = pembacaan sah).
- Deterministik (ca.Rng seeded); float hanya analisis Python.
- FM-H/F-I/F-J sesuai spec; hasil nihil = temuan terdokumentasi.

---

### Task 1: Loop runner (`experiments/m4/loop.py`) — W3

**Files:** Create `experiments/m4/loop.py`, `analysis/tests/test_m4_loop.py`.

**Interfaces:**
- `loop.binding_stats(pairs, k, table) -> dict` — per entri teramati: count, at_cap (f == cap(e)>0), slack count (f < cap).
- `loop.mutate(table, k, entries, delta=+1) -> list` (re-clip).
- `loop.select_targeted(stats, m=64) / select_control(stats, m=64, rng)` — terarah = longgar tersibuk; kontrol = longgar acak.
- `main [--mini]`: K=4 iterasi × (feedback, kontrol): per iterasi — observasi (run window 512 pasangan, n=16384 k=4; mini n=256 k=2 hand-table) → ΔJ_max masing-masing jalur (J_max = J pada cap tertinggi via measure_j M3, 3 cap: [14, 10, 6] full / [2] mini? mini: J pada cap=2) → verdict W3: mean ΔJ terarah > kontrol.
- `result.json`: criteria {W3_feedback_directed_effect}, trajectory (per iterasi, kedua jalur: fnv, J_max, top3), reproduce.

- [ ] **Step 1: failing test** `test_m4_loop.py::test_m4_mini_loop`: mini end-to-end (k=2 hand table, n=256, K=2 iterasi) → exit 0, W3 criteria ada (nilainya bool apa pun — arah tidak dipaksakan di mini), deterministik dua run.
- [ ] **Step 2: implementasi** (reuse M3 run_window/measure_j + flowrecover.derive_field untuk stats).
- [ ] **Step 3:** pytest → PASS. commit `m4: loop runner — intervensi terarah vs kontrol (mini teruji)`.

### Task 2: Growth meter (`experiments/m4/growth.py`) — K5 + W4

**Files:** Create `experiments/m4/growth.py`, `analysis/tests/test_m4_growth.py`.

**Interfaces:**
- `growth.model_bits(states, k, macro_bits=0) -> dict` — {bits: k × entri teramati (via flowrecover.recover_table) + macro_bits, coverage, compressed: len(zlib(window bytes)), raw: len}.
- `main [--mini]`: rezim = 2 juara M1 (fnv berbeda, pilih dinamis seperti M3) + 184 (k=1, builtin); checkpoint t ∈ {10³, 10⁴, 10⁶} (mini: {100, 400}), window = min(t, 2048) (mini: min(t,64)); per checkpoint: run + recovery + model_bits + kompresi. K5 verdict: ≥2 rezim terukur penuh; **reading**: kurva saturasi/tumbuh dilaporkan apa adanya.
- `result.json`: criteria {K5_curve_measured}, curves per rezim (t, bits, coverage, compressed), reading, reproduce.

- [ ] **Step 1: failing test** `test_m4_growth.py::test_m4_mini_growth`: mini (2 rezim hand-table k=2 + 184? 184 k=1 butuh jalur khusus — mini pakai 2 hand table saja) → exit 0, K5 True, curves ada, deterministik.
- [ ] **Step 2: implementasi.** Catatan 184 full: k=1, run `--cars 2048`, recovery flowrecover k=1 (maks 8 entri).
- [ ] **Step 3:** pytest → PASS. commit `m4: growth meter — 3 rezim, checkpoint, kompresi (mini teruji)`.

### Task 3: FULL RUN keduanya + log 005 + merge

- [ ] **Step 1:** `python experiments/m4/loop.py` + `python experiments/m4/growth.py` (full).
- [ ] **Step 2:** verdict W3 + kurva K5 → entri 005 (termasuk pembacaan jujur saturasi/tumbuh) + now.md.
- [ ] **Step 3:** `cargo test` + `pytest analysis` hijau.
- [ ] **Step 4:** commit `m4: FULL RUN <verdict> — kontrak K1-K5 selesai (log 005)` → merge main (ff), hapus branch.

---

## Self-Review

1. Spec: W3 ↔ Task 1 (ikatan eksak, terarah vs kontrol, K=4); K5 ↔ Task 2 (3 rezim, 3 checkpoint); W4 ↔ kompresi + pelaporan; FM-H/I/J ↔ guard di kedua eksperimen. ✓
2. Placeholder: semua test berkode; keputusan (binding/slack definisi, model_bits rumus, checkpoint) tertulis. ✓
3. Konsistensi: measure_j/run_window dari M3 dipakai ulang; model_bits rumus sama di test & implementasi; rezim dinamis fnv-berbeda seperti M3. ✓
