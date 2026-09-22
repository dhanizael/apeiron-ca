# M0 — Flow-NCCA Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Engine NCCA tergeneralisasi (keluarga flow, k∈{1,2,4,8}, multithread deterministik) + benchmark formal K2 yang membekukan angka throughput ≥10⁹ cell-update/detik.

**Architecture:** Keluarga flow NCCA — v′ᵢ = vᵢ − F(vᵢ₋₁,vᵢ,vᵢ₊₁) + F(vᵢ₋₂,vᵢ₋₁,vᵢ), F = tabel LUT 2^(3k) entri di-clip saat load (konservasi by construction). Jalur lane word-wise dengan halo 2 word, partisi statis antar thread (nol sinkronisasi; state lama read-only). Snapshot v2 (field k) + manifest v2 (rule.bin + rule_fnv + window budget) + backward compat v1/LM0.

**Tech Stack:** Rust 1.98 zero-dep (std::thread::scope), Python 3.14 stdlib + pytest.

**Spec:** `docs/superpowers/specs/2026-09-21-0and1-design.md` §5 "Keluarga flow NCCA (amendemen M0)" — disetujui 2026-09-22.

## Global Constraints

- Tanpa float di substrat; integer/bit murni. Float hanya pelaporan bench.
- K1′: bit-identical lintas thread DAN lintas implementasi (Rust ≡ Python) untuk k=1..4.
- k hanya {1,2,4,8}; 1D ring; sinkron; radius 1 (2D/async/radius>1 ditunda terdokumentasi).
- Zero-dep Rust; pytest dev-only.
- Backward compat: v1 snapshot (k=1) tetap terbaca; run LM-1 (n=4096, cars=2048, seed=7, steps=20000) harus menghasilkan fnv_final identik dengan manifest ter-commit.
- Flow konvensi edge: f(i→i+1) = F(vᵢ₋₁, vᵢ, vᵢ₊₁); new_i = v_i − f_i + f_{i−1}.

---

### Task 1: World k-bit (lane ops)

**Files:** Modify `engine/src/lattice.rs`, `engine/src/rng.rs` (tambah uniform), semua pemanggil `World::zeros`.

**Interfaces:**
- Produces: `World { n: u32, k: u8, words: Vec<u64> }`; `World::zeros(n, k)`; `.get_cell(i)->u8`, `.set_cell(i,v)`, `.cells_per_word()`, `.n_words_total()`, `.cell_sum()->u64`, `World::from_seed_exact(n, cars, seed)` (k=1), `World::from_seed_uniform(n, k, seed)`, `.fnv1a()`, `World::n_words(n, k)`.
- `get_cell`/`set_cell` menerima index mod n; cell i = bit [i·k, (i+1)·k).

- [ ] **Step 1: failing tests** (tambah di `mod tests` lattice; sesuaikan pemanggil lama `zeros(n)` → `zeros(n, 1)`; rule184 `w.get` → `w.get_cell`)

```rust
    #[test]
    fn cell_ops_general_k() {
        let mut w = World::zeros(40, 4); // 40 sel × 4 bit
        w.set_cell(0, 15);
        w.set_cell(39, 9);
        w.set_cell(20, 7);
        assert_eq!((w.get_cell(0), w.get_cell(39), w.get_cell(20)), (15, 9, 7));
        assert_eq!(w.get_cell(1), 0);
        assert_eq!(w.cell_sum(), 31);
        w.set_cell(20, 0);
        assert_eq!(w.cell_sum(), 24);
        // wrap ring
        assert_eq!(w.get_cell(40), 15);
    }

    #[test]
    fn uniform_init_deterministic_and_in_range() {
        let a = World::from_seed_uniform(64, 4, 9);
        let b = World::from_seed_uniform(64, 4, 9);
        assert_eq!(a.words, b.words);
        for i in 0..64 {
            assert!(a.get_cell(i) < 16);
        }
        let c = World::from_seed_uniform(64, 4, 10);
        assert_ne!(a.fnv1a(), c.fnv1a());
    }

    #[test]
    fn one_bit_world_is_back compatible_layout() {
        // k=1: layout bit lama — cell i = bit i
        let mut w = World::zeros(70, 1);
        w.set_cell(64, 1);
        assert_eq!(w.get_cell(64), 1);
        assert_eq!(w.get_cell(63), 0);
        assert_eq!(w.cell_sum(), 1);
    }
```

- [ ] **Step 2: implementasi** — `lattice.rs` inti:

```rust
#[derive(Clone, Debug)]
pub struct World {
    pub n: u32,
    pub k: u8,
    pub words: Vec<u64>,
}

impl World {
    pub fn cells_per_word(k: u8) -> u32 {
        64 / k as u32
    }
    pub fn n_words(n: u32, k: u8) -> usize {
        ((n as usize * k as usize) + 63) / 64
    }
    pub fn zeros(n: u32, k: u8) -> World {
        assert!(matches!(k, 1 | 2 | 4 | 8), "k harus 1/2/4/8");
        World { n, k, words: vec![0u64; Self::n_words(n, k)] }
    }
    pub fn cells_per_word_of(&self) -> u32 {
        Self::cells_per_word(self.k)
    }
    pub fn mask(&self) -> u8 {
        ((1u16 << self.k) - 1) as u8 // k ≤ 8 → muat u16
    }
}
```
`get_cell(i)`: `let i = i % self.n; let bit = i as usize * k as usize; let w = bit / 64; let off = bit % 64; let v = if off + k <= 64 { self.words[w] >> off } else { (self.words[w] >> off) | (self.words[w + 1] << (64 - off)) }; ((v as u8) & mask)`. `set_cell` kebalikannya (clear lalu OR). `cell_sum`: iterasi word → unpack lane → jumlah. `from_seed_uniform`: per cell `rng.next_u64() as u8 & mask`. `from_seed_exact`: mantulkan perilaku lama, k=1.
- [ ] **Step 3:** `cargo test` → PASS (semua test lama + baru).
- [ ] **Step 4:** commit `engine: World k-bit + lane ops`.

### Task 2: FlowRule + step scalar/lane + ekuivalensi

**Files:** Create `engine/src/flow.rs`, `engine/src/hash.rs`; Modify `lib.rs`.

**Interfaces:**
- `hash::fnv1a_bytes(&[u8]) -> u64` (mirror fnv1a word-loop).
- `FlowRule { k: u8, table: Vec<u8> }`; `FlowRule::from_table(k, &[u8]) -> FlowRule` (clip per entri: min(raw, c, 2^k−1−r), decode idx→(l,c,r)); `FlowRule::builtin184()`; `FlowRule::random(k, seed)`; `.table_fnv()`.
- `flow::step_scalar(w, rule) -> World` (referensi: materialisasi sel → f vec → baru).
- `flow::step_words(w, rule, threads) -> World` (jalur lane word-wise + halo 2 word; threads≥1; partisi sel rata ke threads, batas chunk kelipatan cells_per_word kecuali chunk terakhir).
- Konvensi: f(i→i+1) = F(v_{i−1}, v_i, v_{i+1}); new_i = v_i − f_i + f_{i−1} (index ring).

- [ ] **Step 1: failing tests** `engine/src/flow.rs` `mod tests`:

```rust
    #[test]
    fn builtin184_matches_rule184_bitwise() {
        for seed in 1..=20u64 {
            let w = World::from_seed_exact(4096, 2048, seed);
            let a = crate::rule184::step_scalar(&w);
            let b = super::step_scalar(&w, &super::FlowRule::builtin184());
            assert_eq!(a.words, b.words, "184 ≠ flow(184) seed={}", seed);
        }
    }

    #[test]
    fn lane_equals_scalar_random_rules() {
        for k in [1u8, 2, 4] {
            for seed in 1..=10u64 {
                let rule = super::FlowRule::random(k, seed * 31);
                let w = World::from_seed_uniform(256, k, seed);
                let a = super::step_scalar(&w, &rule);
                let b = super::step_words(&w, &rule, 1);
                assert_eq!(a.words, b.words, "lane≠scalar k={} seed={}", k, seed);
            }
        }
    }

    #[test]
    fn conservation_by_construction() {
        for k in [1u8, 2, 4, 8] {
            let rule = super::FlowRule::random(k, 7);
            let mut w = World::from_seed_uniform(512, k, 7);
            let s0 = w.cell_sum();
            for _ in 0..100 {
                w = super::step_words(&w, &rule, 1);
                assert_eq!(w.cell_sum(), s0, "konservasi rusak k={}", k);
            }
        }
    }

    #[test]
    fn clip_bounds_flow() {
        // entri mentah di luar kapasitas harus ter-clip: F ≤ min(c, 2^k−1−r)
        let rule = super::FlowRule::from_table(2, &[255u8; 64]);
        let idx = |l: u8, c: u8, r: u8| ((l as usize) << 4) | ((c as usize) << 2) | r as usize;
        assert_eq!(rule.table[idx(0, 3, 0)], 3);  // ≤ c
        assert_eq!(rule.table[idx(0, 3, 1)], 2);  // ≤ 3−r
        assert_eq!(rule.table[idx(0, 0, 0)], 0);  // ≤ c=0
    }
```

- [ ] **Step 2: implementasi** — poin kunci (kode lengkap di saat eksekusi, kerangka keputusan):
  - `step_scalar`: `let cells: Vec<u8> = (0..w.n).map(|i| w.get_cell(i)).collect(); let f: Vec<u8> = (0..w.n).map(|i| rule.table[idx(cells[(i+w.n−1)%w.n], cells[i], cells[(i+1)%w.n)])].collect(); let out = World::zeros(w.n, w.k); for i: out.set_cell(i, cells[i] − f[i] + f[(i+w.n−1)%w.n])`.
  - `step_words`: chunk sel rata ke `threads` (batas kelipatan cells_per_word, chunk terakhir sisa); tiap chunk butuh halo 2 word kiri/kanan (index ring); per word: unpack lane → hitung f lokal → new lane → pack. Buffer per worker dialokasi sekali via `Vec<Vec<u8>>` scratch. `std::thread::scope`; tulisan ke `out.words` per rentang word disjoint.
  - `idx(l,c,r) = (l<<2k)|(c<<k)|r`.
- [ ] **Step 3:** `cargo test` → PASS.
- [ ] **Step 4:** commit `engine: keluarga flow NCCA — konservasi by construction, lane≡scalar`.

### Task 3: Determinisme lintas thread (K1′)

**Files:** Modify `engine/src/flow.rs` (tests), tidak ada kode baru bila `step_words(threads)` sudah benar.

- [ ] **Step 1: failing test**

```rust
    #[test]
    fn k1_prime_identical_across_thread_counts() {
        for k in [1u8, 2, 4] {
            let rule = super::FlowRule::random(k, 99);
            let mut one = World::from_seed_uniform(4096, k, 99);
            let mut many = one.clone();
            for _ in 0..100 {
                one = super::step_words(&one, &rule, 1);
                many = super::step_words(&many, &rule, 4);
            }
            assert_eq!(one.words, many.words, "K1′ rusak k={}", k);
        }
    }

    #[test]
    fn thread_count_sweep() {
        let rule = super::FlowRule::random(4, 5);
        let mut refw = World::from_seed_uniform(8192, 4, 5);
        refw = super::step_words(&refw, &rule, 1);
        for t in [2usize, 3, 7, 16] {
            let mut w = World::from_seed_uniform(8192, 4, 5);
            w = super::step_words(&w, &rule, t);
            assert_eq!(w.words, refw.words, "threads={} ≠ 1", t);
        }
    }
```

- [ ] **Step 2:** jalankan → PASS (kalau gagal: bug partisi/halo — perbaiki di step_words, BUKAN di test).
- [ ] **Step 3:** commit `engine: K1′ — bit-identical lintas thread (1≡2≡3≡7≡16)`.

### Task 4: Snapshot v2 + manifest v2 + window budget

**Files:** Modify `engine/src/snapshot.rs`, `engine/src/main.rs` (run v2), `engine/tests/cli.rs`.

**Interfaces:**
- Header v2 (36 B): magic u64, version u16=2, k u8, reserved u8=0, rule_id u32, n_cells u32, step u64, fnv u64. `read_snapshot` menerima v1 (34 B, k=1) dan v2. `Snapshot{k, ...}`.
- Manifest v2 keys: schema, version=2, rule ("builtin:184" | "flow-table"), rule_fnv, k, n_cells, cars|init="uniform", seed, steps, window_states, window_budget, threads, fnv_final, engine_version="m0.1". `rule.bin` = tabel ter-clip (ditulis selalu).
- Window budget: `W_actual = max(2, min(W, budget / state_bytes − 1))`; state_bytes = n_words×8.

- [ ] **Step 1: failing tests** (snapshot): roundtrip v2 dengan k=4 (assert k terbaca); file v1 sintetis (header 34 B, k implisit 1) terbaca; Python-side menyusul di Task 5. (CLI): run k=1 builtin:184 → manifest berisi `"k": 1`, `"rule": "builtin:184"`, `rule.bin` ada; run k=4 uniform + --rule-table → rule_fnv = fnv tabel; window budget kecil (mis. 128 byte, n=256 k=4 → state 128 B → W_actual=2) tercermin di manifest & ukuran window.bin = 3 state.
- [ ] **Step 2: implementasi** sesuai interfaces (main.rs: parse k/rule-table/budget/threads; thread default = `std::thread::available_parallelism()`).
- [ ] **Step 3:** `cargo test` → PASS + **regresi LM0**: test baru baca `experiments/lm1/result/rho0.500/manifest.json` (via `env!("CARGO_MANIFEST_DIR")/../..`), jalankan engine konfigurasi identik (n=4096, cars=2048, seed=7, steps=20000, window=512, builtin:184, threads=1), assert fnv_final sama persis.
- [ ] **Step 4:** commit `engine: snapshot v2 + manifest v2 + window budget + regresi LM-1`.

### Task 5: Python mirror k-bit + cross test

**Files:** Modify `analysis/semesta/ca.py`, `analysis/semesta/io.py`; Create `analysis/tests/test_cross_k.py`.

**Interfaces:**
- `ca.from_seed_uniform(n, k, seed) -> list[int]`; `ca.random_table(k, seed) -> list[int]` (2^(3k) entri, `(rng.next_u64() & 0xFF)`); `ca.clip_table(raw, k) -> list[int]`; `ca.step_flow(cells, k, table) -> list[int]` (konvensi edge sama); `ca.table_fnv(table) -> int` (FNV-1a byte).
- `io.read_snapshot` menerima v1+v2 (header `<QHBBIIQQ` 36 B); kembalikan `k`.

- [ ] **Step 1: failing test** `test_cross_k.py`:

```python
def test_rust_python_flow_k4(engine_bin, tmp_path):
    n, k, steps, W, seed = 256, 4, 300, 32, 21
    raw = ca.random_table(k, seed + 1)
    table = ca.clip_table(raw, k)
    rule_bin = tmp_path / "rule.bin"
    rule_bin.write_bytes(bytes(table))
    out = tmp_path / "run"
    subprocess.run([engine_bin, "run", "--n", str(n), "--k", str(k), "--uniform",
                    "--seed", str(seed), "--steps", str(steps), "--window", str(W),
                    "--rule-table", str(rule_bin), "--outdir", str(out)],
                   check=True, capture_output=True)
    m = io.read_manifest(out / "manifest.json")
    assert m["k"] == k and m["rule"] == "flow-table"
    assert int(m["rule_fnv"], 16) == ca.table_fnv(table)
    states = io.read_window(out / "window.bin", n, m["window_states"])
    cells = ca.from_seed_uniform(n, k, seed)
    for _ in range(steps):
        cells = ca.step_flow(cells, k, table)
    # bandingkan state akhir + window: kemas cell list → int bit-packed
    tail = ca.pack_cells(cells[-(W + 1):], k, n)
    assert tail == states


def test_rust_python_flow_k2(...):  # pola sama, k=2
```
(`ca.pack_cells(cells, k, n) -> int`: bit i·k..; helper baru.)
- [ ] **Step 2: implementasi** ca.py/io.py sesuai interfaces.
- [ ] **Step 3:** `pytest analysis -q` → PASS (termasuk lama).
- [ ] **Step 4:** commit `analysis: mirror flow k-bit + K1′ lintas implementasi k=2,4`.

### Task 6: Benchmark formal (protokol K2)

**Files:** Modify `engine/src/main.rs` (`bench --protocol k2`).

**Interfaces:**
- `engine bench --protocol k2`: k=4, n=2²⁷, steps=100, rule=FlowRule::random(4, 20260922), world=from_seed_uniform(2²⁷, 4, 20260922), threads=available_parallelism; 1 warmup + 5 run terukur (tiap run: world di-init ulang dari seed yang sama); output: config lengkap + median/min/max cell_updates_per_detik + table_fnv + ARCH. Zero float kecuali pelaporan.
- `bench` legacy (LM0) tetap jalan.

- [ ] **Step 1: smoke test** (`engine/tests/bench.rs`): `bench --protocol k2 --steps 2 --runs 2 --n 65536` (override utk test) exit 0 + output berisi `median_cell_updates_per_detik`. (Protokol penuh dijalankan manual di Task 7 — parameter override hanya untuk smoke.)
- [ ] **Step 2: implementasi**; median via sort integer (hindari float untuk statistik: simpan updates_per_detik sebagai integer cell/detik? waktu f64 untuk hitung lalu simpan `ups = (n*steps/dt) as u64`; median = sort ups).
- [ ] **Step 3:** `cargo test` → PASS.
- [ ] **Step 4:** commit `engine: benchmark protokol K2 beku (median-5, jalur LUT generik)`.

### Task 7: FULL K2 RUN + research log 002 + merge

- [ ] **Step 1:** `cargo build --release && ./target/release/engine bench --protocol k2` → catat output.
- [ ] **Step 2:** assert median ≥ 10⁹ (kalau gagal: profil — jangan langsung optimasi buta; periksa alokasi per step & ukuran chunk dulu).
- [ ] **Step 3:** `pytest analysis -q` + `cargo test` penuh → hijau.
- [ ] **Step 4:** research log 002 (angka K2, config, klaim dibatasi) + now.md.
- [ ] **Step 5:** commit `m0: K2 <angka> cell-updates/detik (median-5, k=4 LUT) — entri 002` → merge ke main (ff), hapus branch.

---

## Self-Review

1. **Spec coverage:** K1′ (Task 3, 5), K2 protokol beku (Task 6-7), snapshot v2 + rule.bin/rule_fnv (Task 4-5), window budget (Task 4), backward compat v1 + regresi LM-1 (Task 4), konservasi by construction (Task 2), deferred 2D/async/radius dicatat di spec. ✓
2. **Placeholder scan:** kerangka step_words di Task 2 Step 2 adalah keputusan desain (bukan "TBD") — kode final ditulis penuh saat eksekusi mengikuti kontrak test Task 2-3. Semua test punya kode penuh. ✓
3. **Type consistency:** `World{n,k,words}` konsisten; `FlowRule.table` u8; manifest v2 keys disebut sama di Task 4 & 5; `table_fnv` Rust (`fnv1a_bytes`) ≡ Python `ca.table_fnv`. ✓
