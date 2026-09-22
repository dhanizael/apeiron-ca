# M1 — Physics Design Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pencarian otomatis aturan flow (k=2,3) yang lolos K3 — partikel persisten + tanpa competitive exclusion dalam horizon H=10⁶ — atau hasil negatif terdokumentasi penuh.

**Architecture:** Detektor partikel = fungsi murni atas sekuens state (Rust, `detect.rs`); metrik pola integer (top-3 massa, interface) di `metrics.rs`; subkommand `engine probe` menjalankan semesta + observasi berkala, output JSON ringkas; harness Python 3 tahap (A: saringan acak, B: mutasi hill-climbing, C: horizon) memanggil probe per kandidat dan mengeluarkan verdict K3 + manifest.

**Tech Stack:** Rust zero-dep, Python 3.14 stdlib + pytest.

**Spec:** `docs/superpowers/specs/2026-09-21-0and1-design.md` §9 "M1 — Physics Design Search (amendemen)".

## Global Constraints

- Definisi operasional K3 sesuai spec amendemen M1 (dibekukan sebelum pencarian).
- Tanpa float di substrat & metrik Rust (fraksi = pasangan integer [pembilang, penyebut]; entropi hanya di Python untuk juara).
- Ruang pencarian M1: k∈{2,4}.
- Setiap kandidat/hasil wajib manifest + perintah reproduksi; hasil nihil = temuan negatif terdokumentasi.
- Seed hand-designed (sandpile, lapisan-184) dijalankan selalu sebagai baseline kalibrasi.

---

### Task 1: Detektor partikel (`engine/src/detect.rs`)

**Files:** Create `engine/src/detect.rs`; Modify `engine/src/lib.rs`.

**Interfaces:**
- `detect::background(cells: &[u8]) -> u8` (mode; tie → nilai terkecil).
- `detect::Particle { start: usize, width: usize, mass: u64 }`; `detect::particles_at(cells: &[u8], w_max: usize) -> Vec<Particle>` (run kontigu ≠ background, lebar ≤ w_max; wrap-aware).
- `detect::ParticleTracker::new(w_max: usize, max_shift: usize)`; `.update(cells: &[u8])` (dipanggil per observasi); `.count_alive() -> usize`; `.max_lifetime() -> u64` (unit = pemanggilan update); pencocokan greedy: interval overlap setelah geser ≤ max_shift.

- [ ] **Step 1: failing tests** (dalam `detect.rs` mod tests):

```rust
    fn cells_of(v: &[u8]) -> Vec<u8> { v.to_vec() }

    #[test]
    fn background_is_mode_lowest_tie() {
        assert_eq!(background(&[0, 0, 1, 1, 1, 2]), 1);
        assert_eq!(background(&[2, 2, 1, 1]), 1); // tie → terkecil
        assert_eq!(background(&[3, 3, 3]), 3);
    }

    #[test]
    fn particle_single_blob() {
        // background 0, blob di 10..13 massa 5
        let mut c = vec![0u8; 32];
        c[10] = 2; c[11] = 2; c[12] = 1;
        let ps = particles_at(&c, 8);
        assert_eq!(ps.len(), 1);
        assert_eq!((ps[0].start, ps[0].width, ps[0].mass), (10, 3, 5));
    }

    #[test]
    fn wide_blob_is_not_particle() {
        let mut c = vec![0u8; 32];
        for x in c.iter_mut().take(20) { *x = 1; } // lebar 20 > w_max
        assert_eq!(particles_at(&c, 8).len(), 0);
    }

    #[test]
    fn wrap_around_ring_detected_once() {
        let mut c = vec![0u8; 8];
        c[7] = 1; c[0] = 1; // blob membungkus ring
        let ps = particles_at(&c, 4);
        assert_eq!(ps.len(), 1);
        assert_eq!(ps[0].width, 2);
    }

    #[test]
    fn tracker_follows_moving_particle() {
        let mut tr = ParticleTracker::new(8, 4);
        for step in 0..10u64 {
            let mut c = vec![0u8; 32];
            let pos = 5 + step as usize; // bergerak +1 per observasi
            c[pos] = 3; c[pos + 1] = 1;
            tr.update(&c);
        }
        assert_eq!(tr.count_alive(), 1);
        assert_eq!(tr.max_lifetime(), 9);
    }

    #[test]
    fn tracker_merge_kills_old_object() {
        let mut tr = ParticleTracker::new(8, 4);
        let mut a = vec![0u8; 32];
        a[5] = 1; a[20] = 1;
        tr.update(&a);
        let mut b = vec![0u8; 32];
        b[6] = 1; b[7] = 1; // partikel 20 hilang, 5 bergeser
        tr.update(&b);
        assert_eq!(tr.count_alive(), 1);
    }

    #[test]
    fn tracker_counts_two_distinct() {
        let mut tr = ParticleTracker::new(8, 4);
        let mut c = vec![0u8; 32];
        c[5] = 1; c[20] = 1;
        tr.update(&c);
        tr.update(&c);
        assert_eq!(tr.count_alive(), 2);
        assert_eq!(tr.max_lifetime(), 1);
    }
```

- [ ] **Step 2: implementasi** — keputusan kunci:
  - `particles_at`: rotasi scan agar mulai dari sel background (bila ada background); kalau tidak ada background sama sekali → satu blob seluruh ring → lebar > w_max → kosong.
  - Matcher: dua pointer di partikel lama/baru (keduanya terurut start); match bila `prev.start ≤ cur.end + max_shift && cur.start ≤ prev.end + max_shift` (interval bisa bergeser); greedy jalan maju.
  - Lifetime: matched → age+1; unmatched → age=0; max_lifetime = max semua age yang pernah tercatat.
- [ ] **Step 3:** `cargo test` → PASS.
- [ ] **Step 4:** commit `engine: detektor partikel — pure fn + tracker (sintetis teruji)`.

### Task 2: Metrik pola + `engine probe`

**Files:** Create `engine/src/metrics.rs`, `engine/src/probe.rs` (logika probe); Modify `lib.rs`, `main.rs`.

**Interfaces:**
- `metrics::PatternMass::new(k)`; `.observe(w: &World)` (hitung neighborhood 3-sel; k≤4); `.top3() -> (u64, u64)` (top3_count, total); `.interface() -> (u64, u64)` (edge dengan v_i ≠ v_{i+1}, n).
- `probe::run(w, rule, steps, probe_every, w_max, max_shift, seed_info) -> ProbeReport` — ProbeReport ser-JSON manual: k, n, seed, steps, rule_fnv, fnv_final, top3_series: [[t, top, total]...], interfaces_series: [[t, i, n]...], particles_final, max_lifetime, mass_final.
- CLI: `engine probe --n N --k K --seed S --steps T --probe-every E [--w-max W] [--rule builtin:184|--rule-table P|--rule random] --threads T` → satu baris JSON ke stdout.

- [ ] **Step 1: failing tests** (`metrics.rs`):
  - 184 k=1 pada init acak ρ=0.5, 2000 langkah → top3/total ≥ 4/5 (collapse — kalibrasi baseline).
  - Uniform semua 5 (k=4) → interface = (0, n); partikel 0.
  - probe CLI: jalankan via Command dengan steps kecil → stdout berisi semua key JSON; dua pemanggilan identik (determinisme).
- [ ] **Step 2: implementasi** — probe = loop `step_words` + observasi tiap `probe_every` (pattern + tracker) + observasi akhir; JSON hand-rolled (urutan kunci tetap). `observe` pakai `cell_bits` (ring) — n kecil, single-thread cukup.
- [ ] **Step 3:** `cargo test` → PASS.
- [ ] **Step 4:** commit `engine: probe — metrik top-3/interface/partikel + JSON deterministik`.

### Task 3: Harness pencarian + verdict K3 (`experiments/m1/search.py`)

**Files:** Create `experiments/m1/search.py`, `analysis/tests/test_m1_search.py`.

**Interfaces:**
- `search.py [--mini] [--engine PATH] [--outdir DIR]`:
  - Tahap A: k=2 seed 1..10000, k=3 seed 10001..20000 (mini: 200 kandidat, n=256, steps=2000, probe-every 100); setiap kandidat: tabel = clip(random_table(k, seed)); `engine probe`; parse JSON; simpan satu baris `results.jsonl` (distribusi PENUH dilaporkan).
  - Filter A: `top3_final/total < 0.8` AND `particles_final ≥ 1` AND `max_lifetime ≥ 500` (mini: lifetime ≥ 20).
  - Baseline: rule sandpile k=2 (F=1 iff c > r+1) dan lapisan-184 k=2 (F = (c&1) & !(r&1)) di-probe dulu — dilaporkan sebagai kalibrasi, tidak ikut juara.
  - Tahap B: survivor → mutasi (ubah 1-2 entri acak, re-clip; 8 mutant/survivor/round, 3 round) probe n=16384×10⁵ (mini: n=256×4000); skor = `max_lifetime × (1 − top3_frac) × (particles_final ≥ 1)`; top-5 lanjut.
  - Tahap C: juara → `engine run` n=16384, steps=10⁶ (mini: 4000), H dicatat; verdict K3 per juara + `result.json` (criteria biner, manifests, reproduce command).

- [ ] **Step 1: failing test** (`test_m1_search.py::test_m1_mini_pipeline`): jalankan `search.py --mini` via subprocess; assert exit 0; `result.json` berisi `criteria`, `stages.a.n_candidates == 200`, `baselines` berisi 2 seed, `reproduce` ada; determinisme: jalankan dua kali → result.json identik byte-per-byte.
- [ ] **Step 2: implementasi** harness sesuai interfaces (JSONL append per kandidat; final result.json ditulis atomic).
- [ ] **Step 3:** `pytest analysis -q` → PASS.
- [ ] **Step 4:** commit `m1: harness 3 tahap + verdict K3 (mini teruji, deterministik)`.

### Task 4: FULL M1 RUN + log 003 + merge

- [ ] **Step 1:** `cargo build --release`; jalankan `search.py` penuh (tahap A ±10-15 menit).
- [ ] **Step 2:** verdict K3 → entri 003 `docs/RESEARCH-LOG.md` (angka, distribusi, juara atau hasil negatif + eskalasi) + now.md.
- [ ] **Step 3:** `cargo test` + `pytest analysis` penuh hijau.
- [ ] **Step 4:** commit `m1: FULL RUN <verdict> — <ringkasan>` → merge main (ff), hapus branch.

---

## Self-Review

1. **Spec coverage:** definisi operasional K3 ↔ Task 1 (partikel) + Task 2 (top-3/interface) + Task 3 (criterion streak 0.8×10⁴); strategi 3 tahap ↔ Task 3; baseline hand-seeded ↔ Task 3; hasil nihil = temuan ↔ Task 4 step 2; H dilaporkan ↔ Task 3 verdict. ✓
2. **Placeholder scan:** semua test punya kode; implementasi = keputusan kunci tertulis (matcher greedy, rotasi scan, JSON hand-rolled). ✓
3. **Type consistency:** `Particle{start,width,mass}`; `ParticleTracker{count_alive, max_lifetime}`; probe JSON keys sama di Task 2 & 3; `random_table/clip_table` Python sudah ada (M0). ✓
