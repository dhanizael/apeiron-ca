# M3-percepatan — Flow-Law Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Newton memulihkan hukum mikro (tabel flow, k=4) dan makro (J(ρ)) dari juara M1 yang tidak ditanam — 3 gerbang eksak + counterfactual law shift.

**Architecture:** Pemulihan mikro via aljabar teleskop konservasi: dᵢ = vᵢ − newᵢ = fᵢ − fᵢ₋₁ → prefix-sum → medan aliran eksak setelah konstanta dikunci edge aliran-nol; entri tabel diisi dari neighborhood teramati; konflik = kegagalan keras. Makro: sweep --init-cap → J(ρ) diukur dari medan aliran tiap pasangan (instrumen = algoritma pemulihan atas data mentah, bukan GT) → fit piecewise-linear MDL (LM0) → held-out.

**Tech Stack:** Python 3.14 stdlib + pytest (Newton), Rust engine (satu knob baru: --init-cap).

**Spec:** `docs/superpowers/specs/2026-09-21-0and1-design.md` §9 "M3-percepatan (amendemen)".

## Global Constraints

- Kriteria 3a/3b/3c sesuai spec; makro dilaporkan terpisah (negatif = hasil sah).
- FM-E: konstanta tak terkunci → ambigu dilaporkan, tidak mengarang. FM-F: window transien untuk coverage. FM-G: J(ρ) tak mulus → makro negatif jujur.
- Semua fraksi/pelaporan float hanya di Python-analisis; engine tetap integer.
- Deterministik penuh (tanpa random module; ca.Rng seeded).

---

### Task 1: Pemulihan medan aliran (`analysis/newton/flowrecover.py`)

**Files:** Create `analysis/newton/flowrecover.py`, `analysis/tests/test_flowrecover.py`; Modify `analysis/semesta/ca.py` (tambah `unpack_cells`).

**Interfaces:**
- `ca.unpack_cells(state: int, n: int, k: int) -> list[int]` (cell i di bit [i·k,(i+1)·k)).
- `flowrecover.derive_field(cells_prev, cells_next, k) -> list[int] | None` — medan f per edge, atau None bila tak ada edge aliran-nol (FM-E). Raise `ValueError` bila f melanggar kapasitas (data korup).
- `flowrecover.recover_table(pairs: list[(list[int], list[int])], k) -> dict` — {"table": list[int|None], "observed": int, "unconstrained": int, "pairs_used": int, "pairs_ambiguous": int}; entri None = tak teramati (jujur). Konflik antar-pasangan → raise ValueError.
- Tabel pulihan dalam bentuk TER-CLIP (semantik FlowRule).

- [ ] **Step 1: failing tests** `test_flowrecover.py`:

```python
import pytest

from newton import flowrecover
from semesta import ca


def _pairs_from_table(k, table, n, seed, steps):
    cells = ca.from_seed_uniform(n, k, seed)
    out = []
    for _ in range(steps):
        nxt = ca.step_flow(cells, k, table)
        out.append((list(cells), list(nxt)))
        cells = nxt
    return out


def test_field_conservative_telescoping():
    table = ca.clip_table(ca.random_table(2, 3), 2)
    cells = ca.from_seed_uniform(64, 2, 3)
    nxt = ca.step_flow(cells, 2, table)
    f = flowrecover.derive_field(list(cells), list(nxt), 2)
    assert f is not None
    # rekonstruksi: new_i = v_i − f_i + f_{i−1} harus persis
    n = len(cells)
    recon = [cells[i] - f[i] + f[(i - 1) % n] for i in range(n)]
    assert recon == list(nxt)


def test_recover_table_exact_k2_full_coverage():
    k, n = 2, 256
    table = ca.clip_table(ca.random_table(k, 9), k)
    pairs = _pairs_from_table(k, table, n, 9, 40)
    rec = flowrecover.recover_table(pairs, k)
    assert rec["unconstrained"] == 0  # init acak menutup semua 64 entri
    assert rec["table"] == table


def test_recover_table_k4_partial_coverage_honest():
    k, n = 4, 256
    table = ca.clip_table(ca.random_table(k, 11), k)
    pairs = _pairs_from_table(k, table, n, 11, 8)
    rec = flowrecover.recover_table(pairs, k)
    obs = [x for x in rec["table"] if x is not None]
    assert rec["observed"] == len(obs) and rec["observed"] > 0
    # semua entri teramati HARUS eksak
    for idx, v in enumerate(rec["table"]):
        if v is not None:
            assert v == table[idx]
    # sisanya dilaporkan jujur sebagai tak teramati
    assert rec["unconstrained"] == 4096 - rec["observed"]


def test_ambiguous_when_no_zero_flow_edge():
    # k=4, sel semua bernilai 1..max−1? konstruksi: semua = 7, tetangga ≠ batas
    # → tak ada c=0 / r=15 → derive_field None (FM-E)
    cells = [7] * 32
    nxt = [7] * 32
    assert flowrecover.derive_field(cells, nxt, 4) is None


def test_conflict_detected():
    table = ca.clip_table(ca.random_table(2, 5), 2)
    pairs = _pairs_from_table(2, table, 64, 5, 20)
    # pasangan korup: tukar satu sel di next
    s, t = pairs[3]
    bad = list(t)
    bad[7] = (bad[7] + 1) % 4
    pairs2 = pairs[:3] + [(s, bad)] + pairs[4:]
    with pytest.raises(ValueError):
        flowrecover.recover_table(pairs2, 2)
```

- [ ] **Step 2: implementasi** — keputusan kunci:
  - `derive_field`: d_i = v_i − new_i; kandidat referensi = edge dengan c=0 atau r=2^k−1 (f=0 pasti); untuk tiap kandidat: prefix-sum ring → f; validasi 0 ≤ f ≤ cap_i (cap = min(c, max−r)) dan rekonstruksi ≡ next; kandidat pertama yang lolos → kembalikan; tidak ada kandidat → None (FM-E); d_i konservasi ring dicek dulu (Σd=0).
  - `recover_table`: per pasangan derive_field (skip ambiguous, hitung); isi `table[idx] = f`; entri sudah terisi dan beda → ValueError; akhirnya clip per-entri sesuai semantik (f teramati sudah ≤ cap, clip idempoten).
- [ ] **Step 3:** `pytest analysis/tests/test_flowrecover.py -q` → PASS.
- [ ] **Step 4:** commit `newton: pemulihan medan aliran — teleskop konservasi, ambigu jujur, konflik keras`.

### Task 2: Engine `--init-cap` + mirror + cross test

**Files:** Modify `engine/src/lattice.rs` (`from_seed_uniform_capped`), `engine/src/main.rs` (flag `--init-cap`, manifest `init_cap`), `analysis/semesta/ca.py` (mirror), `analysis/tests/test_cross_k.py` (satu test cap).

**Interfaces:**
- `World::from_seed_uniform_capped(n, k, seed, cap)` — sel uniform [0, cap] via `rng.next_u64() % (cap+1)`; cap=0 → semua 0; CLI: `--init-cap m` (default 0 = rentang penuh [0, 2^k)); manifest `init_cap`.
- Python: `ca.from_seed_uniform_capped(n, k, seed, cap)` mirror persis.

- [ ] **Step 1: failing tests** — Rust: capped init deterministik + nilai ≤ cap + cap=0 → nol; CLI: manifest berisi `"init_cap": 5`. Python cross: k=4 cap=5 → Rust ≡ Python (pola test_cross_k).
- [ ] **Step 2: implementasi** + mirror.
- [ ] **Step 3:** `cargo test` + `pytest analysis` → PASS.
- [ ] **Step 4:** commit `engine: --init-cap (kerapatan terkendali) + mirror + K1′ cap`.

### Task 3: Eksperimen pemulihan (`experiments/m3/recover.py`)

**Files:** Create `experiments/m3/recover.py`, `analysis/tests/test_m3_recover.py`.

**Interfaces:**
- `recover.py [--mini] [--engine PATH] [--outdir DIR]`:
  - Champion A = `experiments/m1/result/champ_k4_s1161092/rule.bin`, B = `champ_k4_s1161095/rule.bin` (mini: hand table sandpile/layer184 k=2, n=256).
  - Mikro per juara: `engine run --k 4 --uniform --steps 20000 --window 512` (window transien) → pairs (60% pertama recovery, 40% akhir verifikasi) → `recover_table` → gerbang 3a (exact vs GT pada ter-amati) + 3b (reproduksi held-out bit-identik via `ca.step_flow`).
  - Counterfactual 3c: table_fnv(A) ≠ table_fnv(B) dan masing-masing lolos 3a+3b.
  - Makro (dilaporkan terpisah): caps train [2,4,8,12,14], holdout [6,10] (k=4; mini k=2: train [1], holdout [1]? mini: caps [1] saja — makro mini dilewati, hanya struktur). J per cap = rerata medan aliran per pasangan (derive_field per pasangan; ambiguous di-skip & dihitung). fit_pw_linear (LM0) → held-out MAE; ε = 2× derau (sebaran J antar dua seed di cap yang sama) — lantai derau diukur, bukan ditetapkan.
  - `result.json`: criteria {3a, 3b, 3c, macro_mae} + verdict `M3_micro = 3a∧3b∧3c` + reproduce.

- [ ] **Step 1: failing test** `test_m3_recover.py::test_m3_mini_pipeline`: mini end-to-end (champion = hand tables, n=256, steps=1000, window 64) → exit 0, result.json: 3a/3b/3c True (pemulihan k=2 pasti eksak), makro key ada; deterministik dua run.
- [ ] **Step 2: implementasi.**
- [ ] **Step 3:** `pytest analysis -q` → PASS.
- [ ] **Step 4:** commit `m3: eksperimen pemulihan — 3 gerbang + counterfactual (mini teruji)`.

### Task 4: FULL RUN juara #1 & #2 + log 004 + merge

- [ ] **Step 1:** `cargo build --release`; `python experiments/m3/recover.py` (juara asli k=4).
- [ ] **Step 2:** verdict → entri 004 `docs/RESEARCH-LOG.md` + now.md.
- [ ] **Step 3:** `cargo test` + `pytest analysis` hijau.
- [ ] **Step 4:** commit `m3: FULL RUN <verdict> — <ringkasan>` → merge main (ff), hapus branch.

---

## Self-Review

1. **Spec coverage:** 3a/3b/3c ↔ Task 1+3; makro terpisah + ε dari derau ↔ Task 3; FM-E ambigu ↔ derive_field None; FM-F window transien ↔ Task 3; FM-G makro negatif sah ↔ verdict terpisah; counterfactual spec §6 ↔ 3c. ✓
2. **Placeholder scan:** semua test berkode penuh; keputusan implementasi tertulis (kandidat referensi, prefix-sum, clip idempoten). ✓
3. **Type consistency:** `derive_field` → list|None; `recover_table` → dict{kunci tetap}; `ca.unpack_cells` dipakai Task 3; `from_seed_uniform_capped` Rust ≡ Python (modulo cap+1, urutan draw sama). ✓
