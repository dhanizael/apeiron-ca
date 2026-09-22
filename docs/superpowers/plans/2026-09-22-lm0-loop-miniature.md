# LM0 — Loop Miniature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Loop pertama Semesta↔Newton hidup end-to-end di skala mainan: engine Rule 184 (Rust) → Newton v0 (mikro ekshaustif + makro MDL, Python) → oracle eksak → meter T1 → eksperimen LM-1 dengan kriteria biner.

**Architecture:** 1D ring N sel k=1 NCCA Rule 184 di Rust (deterministik, bit-packed, single-thread — kernel perf mainan, format final). Newton v0 Python membaca window.bin via file seam. Oracle menilai vs ground truth (manifest + run panjang). LM-1 = hukum tanaman: mikro = rule table; makro = fundamental diagram J(ρ)=min(ρ,1−ρ) dipulihkan dari sweep densitas, MAE<0.02 pada held-out terukur.

**Tech Stack:** Rust 1.98 (zero dependency), Python 3.14 stdlib-only + pytest (dev), format snapshot biner versi + manifest JSON.

**Spec:** `docs/superpowers/specs/2026-09-21-0and1-design.md` (§9 LM0 — disetujui 2026-09-22)

## Global Constraints

- Tanpa float di substrat (evolusi integer/bit murni). Float hanya untuk pelaporan bench dan fitting makro Newton (analisis, bukan substrat).
- K1 determinisme dari hari satu: re-run bit-identical lintas proses DAN lintas implementasi (Rust ≡ Python referensi).
- Snapshot biner berversi + manifest JSON deterministik (tanpa wall-clock); setiap klaim eksperimen wajib manifest + perintah reproduksi.
- Layout: `engine/` Rust, `analysis/` Python, `experiments/` manifest+hasil.
- Engine Rust: ZERO external crate. Analysis Python: stdlib only (pytest dev-only).
- Jalur bitwise (`step`) mensyaratkan n kelipatan 64; jalur skalar (`step_scalar`) bebas — ekuivalensi diuji.
- Semua nama/identitas Indonesian-friendly; komentar seperlunya, gaya menyatu dengan codebase.

---

### Task 1: Engine core — lattice, RNG, Rule 184

**Files:**
- Create: `engine/Cargo.toml`, `engine/src/lattice.rs`, `engine/src/rng.rs`, `engine/src/rule184.rs`, `engine/src/lib.rs`
- Test: unit tests di dalam masing-masing modul

**Interfaces:**
- Produces: `lattice::World { n: u32, words: Vec<u64> }` dengan `World::zeros(n)`, `World::from_seed_exact(n, cars, seed)`, `.get(i)`, `.set(i,v)`, `.popcount()`, `.fnv1a()`, `.words` publik; `rng::Rng::new(seed)`, `.next_u64()`, `.below(bound)`; `rule184::step_scalar(&World) -> World`, `rule184::step(&World) -> World` (bitwise, n%64==0).

- [x] **Step 1: Scaffold crate**

```bash
cd "/home/dabroli/Projects/#explorations/0and1" && cargo new engine --lib -q
```

`engine/src/lib.rs`:
```rust
pub mod lattice;
pub mod rng;
pub mod rule184;
```

- [x] **Step 2: Tulis failing tests** (dulu semua test, struktur modul kosong)

`engine/src/rng.rs` (test + impl):
```rust
/// xorshift64* — deterministik, u64 murni, mirror 1:1 dengan Python (analysis/semesta/ca.py).
pub struct Rng(u64);

impl Rng {
    pub fn new(seed: u64) -> Rng {
        Rng(if seed == 0 { 0x9E37_79B9_7F4A_7C15 } else { seed })
    }
    pub fn next_u64(&mut self) -> u64 {
        let mut x = self.0;
        x ^= x >> 12;
        x ^= x << 25;
        x ^= x >> 27;
        self.0 = x;
        x.wrapping_mul(0x2545_F491_4F6C_DD1D)
    }
    /// Uniform integer [0, bound), bound > 0.
    pub fn below(&mut self, bound: u64) -> u64 {
        self.next_u64() % bound
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn deterministic_and_spread() {
        let mut a = super::Rng::new(42);
        let mut b = super::Rng::new(42);
        for _ in 0..100 {
            assert_eq!(a.next_u64(), b.next_u64());
        }
        let mut c = super::Rng::new(43);
        assert_ne!(a.next_u64(), c.next_u64());
        assert_eq!(super::Rng::new(0).0, 0x9E37_79B9_7F4A_7C15);
    }
}
```

`engine/src/lattice.rs`:
```rust
/// Lattice 1D bit-packed k=1, ring (boundary periodik). Cell i = bit (i%64) dari words[i/64].
#[derive(Clone, Debug)]
pub struct World {
    pub n: u32,
    pub words: Vec<u64>,
}

impl World {
    pub fn n_words(n: u32) -> usize {
        (n as usize + 63) / 64
    }
    pub fn zeros(n: u32) -> World {
        World { n, words: vec![0u64; Self::n_words(n)] }
    }
    pub fn get(&self, i: u32) -> u8 {
        let i = i % self.n;
        ((self.words[(i / 64) as usize] >> (i % 64)) & 1) as u8
    }
    pub fn set(&mut self, i: u32, v: u8) {
        let i = i % self.n;
        let (w, b) = ((i / 64) as usize, i % 64);
        if v & 1 == 1 {
            self.words[w] |= 1u64 << b;
        } else {
            self.words[w] &= !(1u64 << b);
        }
    }
    pub fn popcount(&self) -> u64 {
        self.words.iter().map(|w| w.count_ones() as u64).sum()
    }
    /// Tepat `cars` sel = 1 pada posisi acak tanpa pengembalian (Fisher–Yates parsial, seeded).
    pub fn from_seed_exact(n: u32, cars: u32, seed: u64) -> World {
        let mut rng = crate::rng::Rng::new(seed);
        let mut idx: Vec<u32> = (0..n).collect();
        let k = (cars.min(n)) as usize;
        for i in 0..k {
            let j = i + rng.below((n as usize - i) as u64) as usize;
            idx.swap(i, j);
        }
        let mut w = World::zeros(n);
        for &i in &idx[..k] {
            w.set(i, 1);
        }
        w
    }
    /// FNV-1a 64 atas byte word (LE) — identitas snapshot.
    pub fn fnv1a(&self) -> u64 {
        let mut h: u64 = 0xcbf2_9ce4_8422_2325;
        for w in &self.words {
            for b in w.to_le_bytes() {
                h ^= b as u64;
                h = h.wrapping_mul(0x100_0000_01b3);
            }
        }
        h
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn get_set_roundtrip() {
        let mut w = World::zeros(200);
        w.set(0, 1);
        w.set(199, 1);
        w.set(64, 1);
        assert_eq!((w.get(0), w.get(199), w.get(64)), (1, 1, 1));
        assert_eq!(w.get(1), 0);
        w.set(64, 0);
        assert_eq!(w.get(64), 0);
    }

    #[test]
    fn same_seed_same_world() {
        let a = World::from_seed_exact(128, 50, 42);
        let b = World::from_seed_exact(128, 50, 42);
        assert_eq!(a.words, b.words);
        assert_eq!(a.popcount(), 50);
        let c = World::from_seed_exact(128, 50, 43);
        assert_ne!(a.fnv1a(), c.fnv1a());
    }

    #[test]
    fn fnv_distinct_and_stable() {
        let a = World::from_seed_exact(64, 30, 1);
        let b = World::from_seed_exact(64, 30, 1);
        let c = World::from_seed_exact(64, 29, 1);
        assert_eq!(a.fnv1a(), b.fnv1a());
        assert_ne!(a.fnv1a(), c.fnv1a());
    }
}
```

`engine/src/rule184.rs`:
```rust
use crate::lattice::World;

/// Rule 184 (traffic; number-conserving). Output 1 utk (L,C,R) ∈ {111,101,100,011}.
/// Kanonik scalar; jalur bitwise wajib setara bit-dengan ini (diuji).
pub fn step_scalar(w: &World) -> World {
    let n = w.n;
    let mut out = World::zeros(n);
    for i in 0..n {
        let l = w.get((i + n - 1) % n) as u64;
        let c = w.get(i) as u64;
        let r = w.get((i + 1) % n) as u64;
        let f = (l & r) | (l & !c & !r) | (!l & c & r);
        out.set(i, (f & 1) as u8);
    }
    out
}

/// Rotasi ring 1 bit lintas kata. left=true → L[i]=cell[i-1]; left=false → R[i]=cell[i+1].
fn rot(words: &[u64], left: bool) -> Vec<u64> {
    let m = words.len();
    let mut out = vec![0u64; m];
    for j in 0..m {
        let cur = words[j];
        if left {
            let prev = words[(j + m - 1) % m];
            out[j] = (cur << 1) | (prev >> 63);
        } else {
            let next = words[(j + 1) % m];
            out[j] = (cur >> 1) | (next << 63);
        }
    }
    out
}

/// Jalur bitwise (butuh n % 64 == 0 — tanpa bit padding). F = (L&R)|(L&!C&!R)|(!L&C&R).
pub fn step(w: &World) -> World {
    assert!(
        w.n % 64 == 0 && w.words.len() == (w.n / 64) as usize,
        "jalur bitwise butuh n kelipatan 64; pakai step_scalar"
    );
    let l = rot(&w.words, true);
    let r = rot(&w.words, false);
    let c = &w.words;
    let mut out = Vec::with_capacity(c.len());
    for j in 0..c.len() {
        out.push((l[j] & r[j]) | (l[j] & !c[j] & !r[j]) | (!l[j] & c[j] & r[j]));
    }
    World { n: w.n, words: out }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn single_car_moves_right_one_per_step() {
        let mut w = World::zeros(64);
        w.set(4, 1);
        let mut cur = w;
        for k in 1..=3u32 {
            cur = step_scalar(&cur);
            assert_eq!(cur.popcount(), 1, "partikel hilang/duplikat");
            assert_eq!(cur.get(4 + k), 1, "mobil harus di {}", 4 + k);
        }
    }

    #[test]
    fn jam_leader_moves_hole_propagates() {
        // 0110 → 0101: pemimpin gerombolan maju, celah bergeser (jam wave backward)
        let mut w = World::zeros(64);
        w.set(10, 1);
        w.set(11, 1);
        let n1 = step_scalar(&w);
        assert_eq!((n1.get(10), n1.get(11), n1.get(12)), (1, 0, 1));
    }

    #[test]
    fn popcount_conserved_random_worlds() {
        for seed in 1..=30u64 {
            let mut cur = World::from_seed_exact(256, 100, seed);
            assert_eq!(cur.popcount(), 100);
            for _ in 0..200 {
                cur = step_scalar(&cur);
                assert_eq!(cur.popcount(), 100, "konservasi rusak seed={}", seed);
            }
        }
    }

    #[test]
    fn fast_equals_scalar() {
        for seed in 1..=50u64 {
            let mut cur = World::from_seed_exact(4096, 2048, seed);
            for _ in 0..10 {
                let a = step_scalar(&cur);
                let b = step(&cur);
                assert_eq!(a.words, b.words, "fast != scalar seed={}", seed);
                cur = b;
            }
        }
    }

    #[test]
    fn k1_rerun_bit_identical() {
        let mut a = World::from_seed_exact(4096, 1500, 777);
        let mut b = World::from_seed_exact(4096, 1500, 777);
        for _ in 0..500 {
            a = step(&a);
            b = step(&b);
        }
        assert_eq!(a.words, b.words);
    }
}
```

- [x] **Step 3: Run semua test** — `cd engine && cargo test` → semua PASS.
- [x] **Step 4: Commit**

```bash
git add engine && git commit -m "engine: lattice+RNG+rule184 — determinisme & konservasi teruji"
```

---

### Task 2: Snapshot format + manifest

**Files:**
- Create: `engine/src/snapshot.rs`; Modify: `engine/src/lib.rs` (tambah `pub mod snapshot;`)

**Interfaces:**
- Produces: `snapshot::MAGIC: u64`, `write_snapshot(path, &World, rule_id, step) -> io::Result<u64>` (kembalikan fnv), `read_snapshot(path) -> Result<Snapshot,String>`, `Snapshot { rule_id, n_cells, step, fnv, words }`, `write_window(path, &[World]) -> io::Result<()>`, `manifest_json(&[(k, v)]) -> String` (JSON deterministik tanpa wall-clock).

- [x] **Step 1: Tulis failing tests + impl `snapshot.rs`**

```rust
use crate::lattice::World;
use std::io::{Read, Write};
use std::path::Path;

pub const MAGIC: u64 = 0x3044_4E31_304C_4D30;

pub struct Snapshot {
    pub rule_id: u32,
    pub n_cells: u32,
    pub step: u64,
    pub fnv: u64,
    pub words: Vec<u64>,
}

/// Header (LE): magic u64, versi u16, rule_id u32, n_cells u32, step u64, fnv u64; lalu words.
pub fn write_snapshot(path: &Path, w: &World, rule_id: u32, step: u64) -> std::io::Result<u64> {
    let fnv = w.fnv1a();
    let mut f = std::fs::File::create(path)?;
    f.write_all(&MAGIC.to_le_bytes())?;
    f.write_all(&1u16.to_le_bytes())?;
    f.write_all(&rule_id.to_le_bytes())?;
    f.write_all(&w.n.to_le_bytes())?;
    f.write_all(&step.to_le_bytes())?;
    f.write_all(&fnv.to_le_bytes())?;
    for word in &w.words {
        f.write_all(&word.to_le_bytes())?;
    }
    Ok(fnv)
}

pub fn read_snapshot(path: &Path) -> Result<Snapshot, String> {
    let mut buf = Vec::new();
    std::fs::File::open(path)
        .and_then(|mut f| f.read_to_end(&mut buf))
        .map_err(|e| e.to_string())?;
    let need = |off: usize, len: usize| -> Result<Vec<u8>, String> {
        buf.get(off..off + len)
            .ok_or_else(|| "snapshot terlalu pendek".to_string())
            .map(|s| s.to_vec())
    };
    let q = |v: Vec<u8>| u64::from_le_bytes(v.try_into().unwrap());
    let d = |v: Vec<u8>| u32::from_le_bytes(v.try_into().unwrap());
    if q(need(0, 8)?) != MAGIC {
        return Err("magic salah".into());
    }
    let version = u16::from_le_bytes(need(8, 2)?.try_into().unwrap());
    if version != 1 {
        return Err(format!("versi {} tidak didukung", version));
    }
    let rule_id = d(need(10, 4)?);
    let n_cells = d(need(14, 4)?);
    let step = q(need(18, 8)?);
    let fnv = q(need(26, 8)?);
    let nw = (n_cells as usize + 63) / 64;
    let mut words = Vec::with_capacity(nw);
    for j in 0..nw {
        words.push(q(need(34 + j * 8, 8)?));
    }
    let w = World { n: n_cells, words };
    if w.fnv1a() != fnv {
        return Err("checksum fnv tidak cocok".into());
    }
    Ok(Snapshot { rule_id, n_cells, step, fnv, words })
}

/// Window: states berturutan tanpa header (count ada di manifest).
pub fn write_window(path: &Path, states: &[World]) -> std::io::Result<()> {
    let mut f = std::fs::File::create(path)?;
    for w in states {
        for word in &w.words {
            f.write_all(&word.to_le_bytes())?;
        }
    }
    Ok(())
}

/// Manifest JSON deterministik (urutan kunci = urutan argumen, tanpa wall-clock).
pub fn manifest_json(kv: &[(&str, String)]) -> String {
    let body: Vec<String> = kv.iter().map(|(k, v)| format!("  \"{}\": {}", k, v)).collect();
    format!("{{\n{}\n}}\n", body.join(",\n"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn snapshot_roundtrip_and_checksum() {
        let w = crate::lattice::World::from_seed_exact(128, 60, 5);
        let dir = std::env::temp_dir().join(format!("lm0_snap_{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let p = dir.join("s.bin");
        let fnv = write_snapshot(&p, &w, 184, 123).unwrap();
        let s = read_snapshot(&p).unwrap();
        assert_eq!((s.rule_id, s.n_cells, s.step, s.fnv), (184, 128, 123, fnv));
        assert_eq!(s.words, w.words);
    }

    #[test]
    fn corrupt_byte_rejected() {
        let w = crate::lattice::World::zeros(64);
        let dir = std::env::temp_dir().join(format!("lm0_snapc_{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let p = dir.join("s.bin");
        write_snapshot(&p, &w, 184, 0).unwrap();
        let mut b = std::fs::read(&p).unwrap();
        let last = b.len() - 1;
        b[last] ^= 0xff;
        std::fs::write(&p, b).unwrap();
        assert!(read_snapshot(&p).is_err(), "korupsi harus tertolak checksum");
    }

    #[test]
    fn window_roundtrip_size() {
        let states: Vec<_> = (0..5)
            .map(|i| crate::lattice::World::from_seed_exact(128, 64, i))
            .collect();
        let dir = std::env::temp_dir().join(format!("lm0_win_{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let p = dir.join("w.bin");
        write_window(&p, &states).unwrap();
        assert_eq!(std::fs::metadata(&p).unwrap().len() as usize, 5 * 2 * 8);
    }

    #[test]
    fn manifest_format() {
        let m = manifest_json(&[
            ("rule_id", "184".into()),
            ("seed", "7".into()),
            ("note", "\"apapun\"".into()),
        ]);
        assert!(m.contains("\"rule_id\": 184"));
        assert!(m.contains("\"note\": \"apapun\""));
        assert!(!m.contains('\r'));
    }
}
```

- [x] **Step 2: `cargo test` → PASS.** — run
- [x] **Step 3: Commit** — `git add engine && git commit -m "engine: format snapshot/window/manifest final (v1)"`

---

### Task 3: CLI `run` + `bench`

**Files:**
- Create: `engine/src/main.rs`, `engine/tests/cli.rs`

**Interfaces:**
- Produces: biner `engine`; `engine run --n N --cars K --seed S --steps T --window W --outdir DIR` → `manifest.json` + `final.bin` + `window.bin` ((W+1) state terakhir) + stdout ringkas; `engine bench --n N --steps T` → cell-updates/detik (jujur, apa adanya). Exit code 0 sukses.

- [x] **Step 1: Tulis `main.rs`**

```rust
mod lattice;
mod rng;
mod rule184;
mod snapshot;

use std::collections::VecDeque;
use std::path::Path;

fn flag(args: &[String], name: &str, default: &str) -> String {
    let mut it = args.iter();
    while let Some(a) = it.next() {
        if a == name {
            return it.next().cloned().unwrap_or_default();
        }
    }
    default.to_string()
}

fn cmd_run(args: &[String]) -> i32 {
    let n: u32 = flag(args, "--n", "4096").parse().unwrap();
    let cars: u32 = flag(args, "--cars", "2048").parse().unwrap();
    let seed: u64 = flag(args, "--seed", "1").parse().unwrap();
    let steps: u64 = flag(args, "--steps", "20000").parse().unwrap();
    let window: usize = flag(args, "--window", "512").parse().unwrap();
    let outdir = flag(args, "--outdir", "run");
    if n == 0 || n % 64 != 0 {
        eprintln!("--n harus kelipatan 64 dan > 0");
        return 1;
    }
    if window == 0 || (window as u64) >= steps {
        eprintln!("--window harus > 0 dan < --steps");
        return 1;
    }
    if std::fs::create_dir_all(&outdir).is_err() {
        eprintln!("tidak bisa membuat {}", outdir);
        return 1;
    }
    let mut cur = lattice::World::from_seed_exact(n, cars, seed);
    let cars0 = cur.popcount();
    let mut ring: VecDeque<lattice::World> = VecDeque::with_capacity(window + 1);
    for t in 0..=steps {
        ring.push_back(cur.clone());
        if ring.len() > window + 1 {
            ring.pop_front();
        }
        if t < steps {
            cur = rule184::step(&cur);
        }
    }
    let states: Vec<lattice::World> = ring.into_iter().collect();
    let final_state = states.last().unwrap();
    let fnv = snapshot::write_snapshot(&Path::new(&outdir).join("final.bin"), final_state, 184, steps)
        .unwrap();
    snapshot::write_window(&Path::new(&outdir).join("window.bin"), &states).unwrap();
    let manifest = snapshot::manifest_json(&[
        ("schema", "\"0and1-manifest\"".into()),
        ("version", "1".into()),
        ("rule_id", "184".into()),
        ("n_cells", n.to_string()),
        ("cars", cars0.to_string()),
        ("seed", seed.to_string()),
        ("steps", steps.to_string()),
        ("window_states", (window + 1).to_string()),
        ("fnv_final", format!("\"{:016x}\"", fnv)),
        ("engine_version", "\"lm0.1\"".into()),
    ]);
    std::fs::write(Path::new(&outdir).join("manifest.json"), manifest).unwrap();
    println!(
        "n={} cars={} steps={} window_states={} fnv_final={:016x}",
        n, cars0, steps, window + 1, fnv
    );
    0
}

fn cmd_bench(args: &[String]) -> i32 {
    let n: u32 = flag(args, "--n", "65536").parse().unwrap();
    let steps: u64 = flag(args, "--steps", "200000").parse().unwrap();
    if n == 0 || n % 64 != 0 {
        eprintln!("--n harus kelipatan 64 dan > 0");
        return 1;
    }
    let mut cur = lattice::World::from_seed_exact(n, n / 2, 12345);
    let t0 = std::time::Instant::now();
    for _ in 0..steps {
        cur = rule184::step(&cur);
    }
    let dt = t0.elapsed().as_secs_f64();
    let updates = n as f64 * steps as f64;
    println!(
        "cell_updates={} detik={:.3} cell_updates_per_detik={:.0} fnv={:016x}",
        updates as u64,
        dt,
        updates / dt,
        cur.fnv1a()
    );
    0
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let code = match args.get(1).map(|s| s.as_str()) {
        Some("run") => cmd_run(&args),
        Some("bench") => cmd_bench(&args),
        _ => {
            eprintln!(
                "pemakaian: engine run --n N --cars K --seed S --steps T --window W --outdir D \
                 | engine bench --n N --steps T"
            );
            2
        }
    };
    std::process::exit(code);
}
```

Catatan: `Instant`/`as_secs_f64` hanya di jalur pelaporan bench — evolusi substrat tetap integer murni.

- [x] **Step 2: Tulis integration test `engine/tests/cli.rs`**

```rust
use std::process::Command;

fn run_engine(outdir: &str, n: &str, cars: &str, steps: &str, window: &str) {
    let s = Command::new(env!("CARGO_BIN_EXE_engine"))
        .args([
            "run", "--n", n, "--cars", cars, "--seed", "7", "--steps", steps,
            "--window", window, "--outdir", outdir,
        ])
        .status()
        .unwrap();
    assert!(s.success());
}

fn read_field(manifest: &str, key: &str) -> String {
    manifest
        .lines()
        .find(|l| l.contains(&format!("\"{}\":", key)))
        .unwrap()
        .split(':')
        .nth(1)
        .unwrap()
        .trim()
        .trim_end(',')
        .to_string()
}

#[test]
fn run_produces_seam_files_deterministic() {
    let base = std::env::temp_dir().join(format!("lm0_cli_{}", std::process::id()));
    let a = base.join("a");
    let b = base.join("b");
    run_engine(a.to_str().unwrap(), "64", "32", "128", "16");
    run_engine(b.to_str().unwrap(), "64", "32", "128", "16");
    for d in [&a, &b] {
        for f in ["manifest.json", "final.bin", "window.bin"] {
            assert!(d.join(f).exists(), "{} hilang di {:?}", f, d);
        }
    }
    let ma = std::fs::read_to_string(a.join("manifest.json")).unwrap();
    let mb = std::fs::read_to_string(b.join("manifest.json")).unwrap();
    assert_eq!(read_field(&ma, "rule_id"), "184");
    assert_eq!(read_field(&ma, "n_cells"), "64");
    assert_eq!(read_field(&ma, "window_states"), "17");
    assert_eq!(read_field(&ma, "fnv_final"), read_field(&mb, "fnv_final"));
    // window: 17 state × 1 word × 8 byte
    assert_eq!(std::fs::metadata(a.join("window.bin")).unwrap().len(), 17 * 8);
    // konservasi partikel lintas seluruh run: final snapshot popcount = cars
    let snap = engine::snapshot::read_snapshot(&a.join("final.bin")).unwrap();
    let w = engine::lattice::World { n: snap.n_cells, words: snap.words };
    assert_eq!(w.popcount(), 32);
}

#[test]
fn bad_args_rejected() {
    let s = Command::new(env!("CARGO_BIN_EXE_engine"))
        .args(["run", "--n", "100", "--cars", "50", "--outdir", "/tmp/x_lm0"])
        .status()
        .unwrap();
    assert!(!s.success(), "n bukan kelipatan 64 harus ditolak");
}
```

Perlu `engine/src/lib.rs` tetap modul publik (main.rs punya modul sendiri — file main menggunakan `engine::` via path? TIDAK — integration test otomatis link ke lib crate `engine`; main.rs mendeklarasikan `mod lattice;` sendiri (duplikasi modul bin vs lib itu normal untuk crate bin+lib). Test CLI memakai `engine::snapshot::read_snapshot` dari lib ✓.

- [x] **Step 3: `cargo test` → PASS.**
- [x] **Step 4: `cargo build --release` + `./target/release/engine bench --n 65536 --steps 200000`** — catat angka (informasional, bukan klaim K2).
- [x] **Step 5: Commit** — `git add engine && git commit -m "engine: CLI run/bench — file seam final + determinisme lintas proses"`

---

### Task 4: Python — CA referensi, IO, K1 lintas implementasi

**Files:**
- Create: `analysis/pyproject.toml` (atau venv sederhana), `analysis/conftest.py`, `analysis/semesta/__init__.py`, `analysis/semesta/ca.py`, `analysis/semesta/io.py`, `analysis/tests/__init__.py`, `analysis/tests/test_ca.py`, `analysis/tests/test_cross.py`

**Interfaces:**
- Produces (Python): `semesta.ca.step_rule184(state:int, n:int)->int`, `semesta.ca.step_rule(state,n,rule_id)->int`, `semesta.ca.from_seed_exact(n,cars,seed)->int`, `semesta.ca.Rng`; `semesta.io.read_manifest(path)->dict`, `read_snapshot(path)->dict{rule_id,n,step,fnv,state}`, `read_window(path,n,count)->list[int]`. Cell i = bit i (konsisten dengan Rust LE bit order).

- [x] **Step 1: Env** — di root repo: `python3 -m venv .venv && .venv/bin/pip -q install pytest` (atau `uv venv && uv pip install pytest` bila uv ada). `.venv` di .gitignore.
- [x] **Step 2: Tulis `ca.py` + `test_ca.py` (TDD: test dulu untuk rule184 pattern)**

`analysis/semesta/ca.py`:
```python
"""CA referensi 1D (Python) — implementasi independen dari engine Rust.

Peran: (1) pengujian silang K1 lintas implementasi; (2) generator sintetis tes Newton;
(3) langkah ECA umum untuk verifier mikro Newton. Cell i = bit i.
"""
MASK64 = (1 << 64) - 1


class Rng:
    """xorshift64* — mirror persis engine/src/rng.rs."""

    def __init__(self, seed: int):
        self.s = 0x9E3779B97F4A7C15 if seed == 0 else seed

    def next_u64(self) -> int:
        x = self.s
        x ^= x >> 12
        x ^= (x << 25) & MASK64
        x ^= x >> 27
        self.s = x
        return (x * 0x2545F4914F6CDD1D) & MASK64

    def below(self, bound: int) -> int:
        return self.next_u64() % bound


def from_seed_exact(n: int, cars: int, seed: int) -> int:
    """Mirror lattice::World::from_seed_exact — state awal identik dengan Rust."""
    rng, idx = Rng(seed), list(range(n))
    k = min(cars, n)
    for i in range(k):
        j = i + rng.below(n - i)
        idx[i], idx[j] = idx[j], idx[i]
    state = 0
    for i in idx[:k]:
        state |= 1 << i
    return state


def _rot_left(state: int, n: int, mask: int) -> int:
    # L[i] = state[i-1]
    return ((state << 1) | (state >> (n - 1))) & mask


def _rot_right(state: int, n: int, mask: int) -> int:
    # R[i] = state[i+1]
    return ((state >> 1) | (state << (n - 1))) & mask


def step_rule184(state: int, n: int) -> int:
    mask = (1 << n) - 1
    L, C, R = _rot_left(state, n, mask), state, _rot_right(state, n, mask)
    return (L & R) | (L & ~C & ~R & mask) | (~L & C & R & mask)


def step_rule(state: int, n: int, rule_id: int) -> int:
    """ECA umum (LUT per sel) — lambat; untuk tes & verifier, bukan performa."""
    out = 0
    for i in range(n):
        nb = (
            ((state >> ((i - 1) % n)) & 1) << 2
            | ((state >> i) & 1) << 1
            | ((state >> ((i + 1) % n)) & 1)
        )
        if (rule_id >> nb) & 1:
            out |= 1 << i
    return out
```

`analysis/tests/test_ca.py`:
```python
from semesta import ca


def test_single_car_moves_right():
    n = 64
    s = 1 << 4
    for k in (1, 2, 3):
        for _ in range(1):
            pass
    s1 = ca.step_rule184(s, n)
    assert s1 == 1 << 5
    s2 = ca.step_rule184(s1, n)
    assert s2 == 1 << 6


def test_jam_0110_to_0101():
    n = 64
    s = (1 << 10) | (1 << 11)
    t = ca.step_rule184(s, n)
    assert t == (1 << 10) | (1 << 12)


def test_popcount_conserved():
    n = 256
    s = ca.from_seed_exact(n, 100, 9)
    assert s.bit_count() == 100
    for _ in range(300):
        s = ca.step_rule184(s, n)
        assert s.bit_count() == 100


def test_step_rule_agrees_184():
    n = 128
    s = ca.from_seed_exact(n, 60, 3)
    assert ca.step_rule(s, n, 184) == ca.step_rule184(s, n)


def test_rng_mirror_selfconsistent():
    r = ca.Rng(42)
    vals = [r.next_u64() for _ in range(3)]
    r2 = ca.Rng(42)
    assert [r2.next_u64() for _ in range(3)] == vals
```

- [x] **Step 3: Tulis `io.py` + `conftest.py` + `test_cross.py`**

`analysis/semesta/io.py`:
```python
"""Pembaca file seam (snapshot/window/manifest) — mirror format engine v1."""
import json
import struct
from pathlib import Path

MAGIC = 0x30444E31304C4D30


def read_manifest(path) -> dict:
    return json.loads(Path(path).read_text())


def read_snapshot(path) -> dict:
    b = Path(path).read_bytes()
    if len(b) < 34:
        raise ValueError("snapshot terlalu pendek")
    magic, version, rule_id, n_cells, step, fnv = struct.unpack_from("<QHIIQQ", b, 0)
    if magic != MAGIC:
        raise ValueError(f"magic salah: {magic:#x}")
    if version != 1:
        raise ValueError(f"versi {version} tidak didukung")
    nw = (n_cells + 63) // 64
    words = struct.unpack_from(f"<{nw}Q", b, 34)
    state = 0
    for w in reversed(words):
        state = (state << 64) | w
    return {"rule_id": rule_id, "n": n_cells, "step": step, "fnv": fnv, "state": state}


def read_window(path, n: int, count: int) -> list[int]:
    b = Path(path).read_bytes()
    nw = (n + 63) // 64
    expect = nw * 8 * count
    if len(b) != expect:
        raise ValueError(f"window.bin {len(b)} byte, harap {expect}")
    states = []
    for s in range(count):
        words = struct.unpack_from(f"<{nw}Q", b, s * nw * 8)
        st = 0
        for w in reversed(words):
            st = (st << 64) | w
        states.append(st)
    return states
```

`analysis/conftest.py`:
```python
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))


@pytest.fixture(scope="session")
def engine_bin() -> str:
    env = os.environ.get("ENGINE_BIN")
    if env:
        return env
    binp = ROOT / "target" / "release" / "engine"
    if not binp.exists():
        subprocess.run(["cargo", "build", "--release", "-q"], cwd=ROOT, check=True)
    assert binp.exists(), "engine belum dibangun: jalankan cargo build --release"
    return str(binp)
```

`analysis/tests/test_cross.py`:
```python
"""K1 dua arah: evolusi Python referensi ≡ engine Rust, bit-identical."""
import subprocess

from semesta import ca, io


def test_rust_python_bit_identical(engine_bin, tmp_path):
    n, cars, seed, steps, W = 4096, 2048, 99, 2000, 32
    out = tmp_path / "run"
    subprocess.run(
        [engine_bin, "run", "--n", str(n), "--cars", str(cars), "--seed", str(seed),
         "--steps", str(steps), "--window", str(W), "--outdir", str(out)],
        check=True, capture_output=True,
    )
    m = io.read_manifest(out / "manifest.json")
    assert m["rule_id"] == 184 and m["n_cells"] == n
    states = io.read_window(out / "window.bin", n, W + 1)
    st = ca.from_seed_exact(n, cars, seed)
    chain = [st]
    for _ in range(steps):
        st = ca.step_rule184(st, n)
        chain.append(st)
    assert chain[-(W + 1):] == states, "window Rust ≠ evolusi Python"
    snap = io.read_snapshot(out / "final.bin")
    assert snap["state"] == chain[-1], "final.bin ≠ akhir rantai Python"
    assert snap["fnv"] == int(m["fnv_final"], 16)
```

- [x] **Step 4: Run** — `.venv/bin/pytest analysis -q` → semua PASS.
- [x] **Step 5: Commit** — `git add analysis .gitignore && git commit -m "analysis: CA referensi + pembaca seam + K1 lintas implementasi (Rust≡Python)"`

---

### Task 5: Newton v0 — pemulihan mikro

**Files:**
- Create: `analysis/newton/__init__.py`, `analysis/newton/micro.py`, `analysis/tests/test_micro.py`

**Interfaces:**
- Produces: `newton.micro.constraints(states, n, max_pairs=None) -> dict[int,int]` (raise `ContradictionError` bila substrat bising), `consistent_rules(cons) -> list[int]`, `recover(states, n, max_pairs=None) -> {"candidates": [...], "verified": [...], "constraints": {...}}`, `verify_rule(rule_id, states, n) -> bool`. Semua rule_id ∈ [0,256) urutan Wolfram.

- [x] **Step 1: Test dulu `test_micro.py`**

```python
import pytest

from semesta import ca
from newton import micro


def _stream(rule_id, n=128, cars=64, seed=5, length=20):
    s = ca.from_seed_exact(n, cars, seed)
    out = [s]
    for _ in range(length - 1):
        s = ca.step_rule(s, n, rule_id)
        out.append(s)
    return out


@pytest.mark.parametrize("rule_id", [184, 110, 90, 30, 51])
def test_recovers_known_rule(rule_id):
    states = _stream(rule_id)
    rec = micro.recover(states, 128)
    assert rule_id in rec["verified"]
    assert len(rec["verified"]) >= 1


def test_unique_when_coverage_complete():
    # init acak ρ=0.5 hampir pasti menutup 8 neighborhood dalam 20 pasangan
    states = _stream(184)
    rec = micro.recover(states, 128)
    assert len(rec["candidates"]) == 1
    assert rec["candidates"][0] == 184


def test_ambiguity_reported_honestly():
    # init kosong → hanya neighborhood 000 teramati → banyak aturan konsisten
    n = 64
    states = [0, 0, 0]
    rec = micro.recover(states, n)
    assert len(rec["candidates"]) > 1  # jujur: tidak mengklaim unik


def test_contradiction_detected():
    states = _stream(184, n=64, cars=32)
    bad = states[-1] ^ 1  # corrupt 1 bit
    states_bad = states[:-1] + [bad]
    with pytest.raises(micro.ContradictionError):
        micro.constraints(states_bad, 64)


def test_verified_reproduces_whole_window():
    states = _stream(184, n=256, cars=128, seed=11, length=12)
    rec = micro.recover(states, 256)
    r = rec["verified"][0]
    assert micro.verify_rule(r, states, 256)
```

- [x] **Step 2: Impl `micro.py`**

```python
"""Newton Tahap-B mikro (v0): pemulihan aturan mikro ECA radius-1.

Strategi: ekshaustif-konsistensi atas 2^8 aturan. Kendala per sel: aturan harus
memetakan neighborhood (L,C,R) → bit teramati. Substrat bebas noise → aturan
sejati selalu konsisten; coverage tak lengkap → kandidat >1 (dilaporkan jujur,
TIDAK dipaksa pilih). Deskripsi aturan seragam 8 bit → seleksi = nol-error
konsistensi; penalti panjang model (MDL) muncul di tingkat makro (macro.py).
"""
from semesta import ca


class ContradictionError(Exception):
    """Dua bit berbednya diamati untuk neighborhood sama → asumsi substrat rusak."""


def constraints(states: list[int], n: int, max_pairs: int | None = None) -> dict[int, int]:
    seq = states if max_pairs is None else states[: max_pairs + 1]
    mask = (1 << n) - 1
    cons: dict[int, int] = {}
    for s, t in zip(seq, seq[1:]):
        L = ((s << 1) | (s >> (n - 1))) & mask
        R = ((s >> 1) | (s << (n - 1))) & mask
        for i in range(n):
            nb = (((L >> i) & 1) << 2) | (((s >> i) & 1) << 1) | ((R >> i) & 1)
            b = (t >> i) & 1
            prev = cons.get(nb)
            if prev is None:
                cons[nb] = b
            elif prev != b:
                raise ContradictionError(f"neighborhood {nb:03b} → {prev} dan {b}")
    return cons


def consistent_rules(cons: dict[int, int]) -> list[int]:
    return [
        rid for rid in range(256)
        if all(((rid >> nb) & 1) == b for nb, b in cons.items())
    ]


def verify_rule(rule_id: int, states: list[int], n: int) -> bool:
    """Gerbang eksak: aturan harus mereproduksi SELURUH window bit-identical."""
    for s, t in zip(states, states[1:]):
        if ca.step_rule(s, n, rule_id) != t:
            return False
    return True


def recover(states: list[int], n: int, max_pairs: int | None = None) -> dict:
    cons = constraints(states, n, max_pairs)
    cands = consistent_rules(cons)
    verified = [r for r in cands if verify_rule(r, states, n)]
    return {"candidates": cands, "verified": verified, "constraints": cons}
```

- [x] **Step 3: Run → PASS.** (Catatan performa: verify_rule O(len·n) Python murni — cukup untuk LM0.)
- [x] **Step 4: Commit** — `git add analysis && git commit -m "newton: mikro v0 — ekshaustif 256 aturan + gerbang verifikasi eksak"`

---

### Task 6: Newton v0 — pemulihan makro (J(ρ), MDL)

**Files:**
- Create: `analysis/newton/macro.py`, `analysis/tests/test_macro.py`

**Interfaces:**
- Produces: `macro.measure_flow(states, n) -> float` (J = penyeberangan edge per site per step), `macro.fit_pw_linear(xs, ys, max_segments=3) -> {"segments": [(x0,x1,a,b)...], "mdl", "model_bits", "sse", "n_segments"}`, `macro.predict(model, x) -> float`. GRID breakpoint 0.05..0.95 step 0.05.

- [x] **Step 1: Test dulu `test_macro.py`**

```python
from semesta import ca
from newton import macro


def _window(n, cars, seed, warmup, length):
    s = ca.from_seed_exact(n, cars, seed)
    for _ in range(warmup):
        s = ca.step_rule184(s, n)
    out = [s]
    for _ in range(length - 1):
        s = ca.step_rule184(s, n)
        out.append(s)
    return out


def test_flow_free_traffic():
    # ρ = 0.3 < 1/2 → semua mobil jalan → J ≈ ρ
    n = 512
    states = _window(n, cars=153, seed=4, warmup=600, length=300)
    J = macro.measure_flow(states, n)
    assert abs(J - 153 / n) < 0.02


def test_flow_jammed():
    # ρ = 0.8 > 1/2 → J ≈ 1-ρ
    n = 512
    states = _window(n, cars=410, seed=4, warmup=600, length=300)
    J = macro.measure_flow(states, n)
    assert abs(J - (1 - 410 / n)) < 0.02


def test_recovers_fundamental_diagram_exact():
    xs = [0.1 * k for k in range(1, 10)]  # 0.1..0.9
    ys = [min(x, 1 - x) for x in xs]
    m = macro.fit_pw_linear(xs, ys)
    for x in (0.25, 0.55):
        assert abs(macro.predict(m, x) - min(x, 1 - x)) < 1e-6
    assert m["n_segments"] == 2  # MDL: 2 segmen cukup, 3 boros


def test_mdl_prefers_simplest():
    xs = [0.1 * k for k in range(1, 10)]
    ys = [0.5 * x for x in xs]
    m = macro.fit_pw_linear(xs, ys)
    assert m["n_segments"] == 1


def test_holds_out_prediction_within_eps():
    # data terukur (dengan transit finite) → prediksi held-out akurat
    n = 512
    pts = []
    for k in range(1, 10):
        rho = 0.1 * k
        states = _window(n, cars=round(rho * n), seed=17, warmup=600, length=300)
        pts.append((rho, macro.measure_flow(states, n)))
    train = [(x, y) for x, y in pts if x not in (0.2, 0.7)]
    hold = [(x, y) for x, y in pts if x in (0.2, 0.7)]
    m = macro.fit_pw_linear([x for x, _ in train], [y for _, y in train])
    for x, y in hold:
        assert abs(macro.predict(m, x) - y) < 0.02
```

- [x] **Step 2: Impl `macro.py`**

```python
"""Newton Tahap-B makro (v0): pemulihan J(ρ) — fundamental diagram Rule 184.

Ruang hipotesis: piecewise-linear ≤ max_segments segmen, breakpoint pada GRID.
Seleksi MDL: error_bits + model_bits (spec §6.1 parsimoni eksplisit — bukan
akurasi semata). measure_flow = pengamatan Newton atas window (bukan pemberian
engine): mobil menyeberang edge (i→i+1) iff s_i=1, s_{i+1}=0, t_{i+1}=1.
"""
import itertools
import math

GRID = [round(0.05 * k, 2) for k in range(1, 20)]  # 0.05..0.95
PARAM_BITS = 32  # a,b tiap segmen (float32)
BP_BITS = 8      # indeks grid breakpoint


def _r(state: int, n: int, mask: int) -> int:
    """Vektor bit i ← state[i+1]."""
    return ((state >> 1) | (state << (n - 1))) & mask


def measure_flow(states: list[int], n: int) -> float:
    mask = (1 << n) - 1
    crossings = 0
    for s, t in zip(states, states[1:]):
        crossed = s & ~_r(s, n, mask) & _r(t, n, mask) & ~t & mask
        crossings += crossed.bit_count()
    return crossings / ((len(states) - 1) * n)


def _fit_segment(pts: list[tuple[float, float]]):
    m = len(pts)
    if m == 0:
        return (0.0, 0.0, 0.0)
    if m == 1:
        return (pts[0][1], 0.0, 0.0)
    mx = sum(x for x, _ in pts) / m
    my = sum(y for _, y in pts) / m
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    if sxx == 0:
        return (my, 0.0, sum((y - my) ** 2 for _, y in pts))
    b = sum((x - mx) * (y - my) for x, y in pts) / sxx
    a = my - b * mx
    sse = sum((y - (a + b * x)) ** 2 for x, y in pts)
    return (a, b, sse)


def fit_pw_linear(xs: list[float], ys: list[float], max_segments: int = 3) -> dict:
    pts = sorted(zip(xs, ys))
    n = len(pts)
    best = None
    for k in range(1, max_segments + 1):
        for bps in itertools.combinations(GRID, k - 1):
            cuts = [0.0, *bps, 1.0]
            segs, sse = [], 0.0
            for lo, hi in zip(cuts, cuts[1:]):
                seg_pts = [(x, y) for x, y in pts if lo <= x < hi or (hi >= 1.0 and x <= 1.0)]
                a, b, e = _fit_segment(seg_pts)
                sse += e
                segs.append((lo, hi, a, b))
            model_bits = k * 2 * PARAM_BITS + (k - 1) * BP_BITS
            err_bits = n * math.log2(max(sse, 1e-12) / n + 1e-9)
            mdl = err_bits + model_bits
            if best is None or mdl < best["mdl"]:
                best = {
                    "segments": segs, "mdl": mdl, "model_bits": model_bits,
                    "sse": sse, "n_segments": k,
                }
    return best


def predict(model: dict, x: float) -> float:
    for lo, hi, a, b in model["segments"]:
        if lo <= x < hi or (hi >= 1.0 and x <= 1.0):
            return a + b * x
    _, _, a, b = model["segments"][-1]
    return a + b * x
```

- [x] **Step 3: Run → PASS.**
- [x] **Step 4: Commit** — `git add analysis && git commit -m "newton: makro v0 — measure_flow + piecewise-linear MDL (fundamental diagram)"`

---

### Task 7: Oracle, verifier, meter T1

**Files:**
- Create: `analysis/newton/verify.py`, `analysis/newton/oracle.py`, `analysis/newton/meter.py`, `analysis/tests/test_oracle_meter.py`

**Interfaces:**
- Produces: `verify.gate_micro(rule_id, states, n) -> bool`; `verify.gate_macro(model, xs, ys, max_mae_train=0.01) -> bool`; `oracle.grade_micro(recovered, manifest) -> dict` (kunci `exact`); `oracle.grade_macro(model, holdout, eps=0.02) -> dict` (kunci `mae`, `pass`); `meter.log(entries: list[dict]) -> list[dict]` (validasi + kembalikan kurva (t, bits, what)).

- [x] **Step 1: Test `test_oracle_meter.py`**

```python
from newton import macro, meter, oracle, verify
from semesta import ca


def test_gate_micro_true_and_false():
    n = 128
    s = ca.from_seed_exact(n, 64, 5)
    states = [s, ca.step_rule184(s, n)]
    assert verify.gate_micro(184, states, n)
    assert not verify.gate_micro(110, states, n)


def test_gate_macro():
    xs = [0.1 * k for k in range(1, 10)]
    ys = [min(x, 1 - x) for x in xs]
    m = macro.fit_pw_linear(xs, ys)
    assert verify.gate_macro(m, xs, ys)
    assert not verify.gate_macro(m, xs, [y + 0.5 for y in ys])


def test_grade_micro_exact():
    manifest = {"rule_id": 184}
    g = oracle.grade_micro(184, manifest)
    assert g["exact"] is True
    g2 = oracle.grade_micro(110, manifest)
    assert g2["exact"] is False and g2["ground_truth"] == 184


def test_grade_macro_eps():
    xs = [0.1 * k for k in range(1, 10)]
    ys = [min(x, 1 - x) for x in xs]
    m = macro.fit_pw_linear(xs, ys)
    ho = [(0.25, min(0.25, 0.75)), (0.75, min(0.75, 0.25))]
    g = oracle.grade_macro(m, ho, eps=0.02)
    assert g["pass"] is True and g["mae"] < 0.02
    g2 = oracle.grade_macro(m, [(0.25, 0.9)], eps=0.02)
    assert g2["pass"] is False


def test_meter_emits_curve():
    curve = meter.log([
        {"t": 1000, "bits": 8, "what": "micro_rule_table"},
        {"t": 1000, "bits": 200, "what": "macro_pw_linear"},
    ])
    assert len(curve) == 2 and curve[0]["t"] == 1000
    assert all(set(e) >= {"t", "bits", "what"} for e in curve)


def test_meter_rejects_malformed():
    import pytest
    with pytest.raises(ValueError):
        meter.log([{"bits": 3}])
```

- [x] **Step 2: Implementasi tiga modul**

`analysis/newton/verify.py`:
```python
"""Gerbang verifier eksak (spec §6.3) — mencegah konfabulasi."""
from newton import macro, micro


def gate_micro(rule_id: int, states: list[int], n: int) -> bool:
    return micro.verify_rule(rule_id, states, n)


def gate_macro(model: dict, xs: list[float], ys: list[float],
               max_mae_train: float = 0.01) -> bool:
    if not xs:
        return False
    mae = sum(abs(macro.predict(model, x) - y) for x, y in zip(xs, ys)) / len(xs)
    return mae <= max_mae_train
```

`analysis/newton/oracle.py`:
```python
"""Oracle (spec §7 Tiang 3): grading eksak vs ground truth."""
from newton import macro


def grade_micro(recovered: int, manifest: dict) -> dict:
    truth = manifest["rule_id"]
    return {"recovered": recovered, "ground_truth": truth, "exact": recovered == truth}


def grade_macro(model: dict, holdout: list[tuple[float, float]], eps: float = 0.02) -> dict:
    errs = [abs(macro.predict(model, x) - y) for x, y in holdout]
    mae = sum(errs) / len(errs)
    return {
        "mae": mae,
        "eps": eps,
        "pass": mae < eps,
        "holdout": [
            {"rho": x, "j_measured": y, "j_predicted": macro.predict(model, x)}
            for x, y in holdout
        ],
    }
```

`analysis/newton/meter.py`:
```python
"""Meter T1 (spec §7 Tiang 1): kurva (waktu semesta, bit model terbaik Newton).

Ini adalah angka pertama proyek — open-endedness didefinisikan operasional
sebagai pertumbuhan persisten kurva ini. LM0 hanya emit; M4 yang membaca.
"""


def log(entries: list[dict]) -> list[dict]:
    curve = []
    for e in entries:
        if not {"t", "bits", "what"} <= set(e):
            raise ValueError(f"entri meter malformed: {e}")
        curve.append({"t": e["t"], "bits": e["bits"], "what": e["what"]})
    curve.sort(key=lambda e: e["t"])
    return curve
```

- [x] **Step 3: Run → PASS.**
- [x] **Step 4: Commit** — `git add analysis && git commit -m "instrumen: oracle eksak + gerbang verifier + meter T1"`

---

### Task 8: Harness LM-1 (end-to-end, mini)

**Files:**
- Create: `experiments/lm1/run_lm1.py`, `analysis/tests/test_lm1_e2e.py`

**Interfaces:**
- Consumes: semua task sebelumnya.
- Produces: `run_lm1.py [--mini] [--engine PATH] [--outdir DIR]` → `result.json` + stdout `LM-1 PASS|FAIL {kriteria}`. Kriteria: `1_micro_exact`, `2_macro_mae_lt_eps`, `3_meter_emits` (biner; `4_k1_cross` diisi oleh test suite, dilaporkan terpisah).

- [x] **Step 1: Tulis `run_lm1.py`**

```python
"""LM-1 — eksperimen hukum tanaman (kriteria biner LM0, spec §9).

Protokol: sweep densitas → ukur J(ρ) tiap run (ground truth TERUKUR, bukan
rumus tekstbook). Newton mikro dari window run tengah; makro: train pada
subset ρ, prediksi held-out. Seed tetap per protokol (deterministik penuh).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))

from newton import macro, meter, micro, oracle, verify  # noqa: E402
from semesta import io  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mini", action="store_true", help="versi kecil untuk tes")
    ap.add_argument("--engine", default=str(ROOT / "target" / "release" / "engine"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "result"))
    a = ap.parse_args()

    if a.mini:
        n, steps, W, seed = 1024, 4000, 128, 7
        densities = [0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.65, 0.7, 0.8]
        holdout = [0.25, 0.65]
    else:
        n, steps, W, seed = 4096, 20000, 512, 7
        densities = [round(0.05 + 0.075 * k, 3) for k in range(13)]
        holdout = [0.2, 0.35, 0.65, 0.8]

    outdir = Path(a.outdir)
    runs = {}
    for rho in densities:
        cars = round(rho * n)
        out = outdir / f"rho{rho:.3f}"
        subprocess.run(
            [a.engine, "run", "--n", str(n), "--cars", str(cars), "--seed", str(seed),
             "--steps", str(steps), "--window", str(W), "--outdir", str(out)],
            check=True, capture_output=True,
        )
        m = io.read_manifest(out / "manifest.json")
        states = io.read_window(out / "window.bin", n, m["window_states"])
        runs[rho] = (m, states)

    # --- Newton mikro: run densitas tengah ---
    mid = densities[len(densities) // 2]
    m_mid, states_mid = runs[mid]
    rec = micro.recover(states_mid, n, max_pairs=64)
    micro_rule = rec["verified"][0] if rec["verified"] else -1
    micro_gate = verify.gate_micro(micro_rule, states_mid, n) if rec["verified"] else False
    g_micro = oracle.grade_micro(micro_rule, m_mid)

    # --- Newton makro: J(ρ) train/held-out ---
    J = {rho: macro.measure_flow(states, n) for rho, (_, states) in runs.items()}
    train = [(r, J[r]) for r in densities if r not in holdout]
    model = macro.fit_pw_linear([x for x, _ in train], [y for _, y in train])
    macro_gate = verify.gate_macro(model, [x for x, _ in train], [y for _, y in train])
    ho = [(r, J[r]) for r in holdout]
    g_macro = oracle.grade_macro(model, ho, eps=0.02)

    # --- Meter T1: angka pertama proyek ---
    curve = meter.log([
        {"t": steps, "bits": 8, "what": "micro_rule_table"},
        {"t": steps, "bits": model["model_bits"], "what": "macro_pw_linear"},
    ])

    result = {
        "experiment": "LM-1",
        "mode": "mini" if a.mini else "full",
        "criteria": {
            "1_micro_exact": bool(micro_gate and g_micro["exact"]),
            "2_macro_mae_lt_eps": bool(macro_gate and g_macro["pass"]),
            "3_meter_emits": len(curve) > 0,
            "4_k1_cross": None,
        },
        "micro": {**g_micro, "n_candidates": len(rec["candidates"]),
                  "n_verified": len(rec["verified"])},
        "macro": g_macro,
        "J_measured": {f"{r:.3f}": J[r] for r in densities},
        "model": {"segments": model["segments"], "model_bits": model["model_bits"],
                  "n_segments": model["n_segments"]},
        "meter": curve,
        "config": {"n": n, "steps": steps, "window": W + 1, "seed": seed,
                   "densities": densities, "holdout": holdout},
        "reproduce": (
            f"engine run (lihat manifest per-run di {outdir}/rho*/) && "
            f"python experiments/lm1/run_lm1.py{' --mini' if a.mini else ''}"
        ),
    }
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "result.json").write_text(json.dumps(result, indent=2))

    ok = all(v for v in result["criteria"].values() if v is not None)
    print("LM-1", "PASS" if ok else "FAIL", json.dumps(result["criteria"]))
    print(f"micro={g_micro} macro_mae={g_macro['mae']:.4f} "
          f"model_bits={model['model_bits']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 2: Test e2e mini `analysis/tests/test_lm1_e2e.py`**

```python
"""LM-1 end-to-end versi mini — loop penuh hidup: engine→Newton→oracle→meter."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_lm1_mini_pass(engine_bin, tmp_path):
    out = tmp_path / "lm1"
    r = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "lm1" / "run_lm1.py"),
         "--mini", "--engine", engine_bin, "--outdir", str(out)],
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"LM-1 mini gagal:\n{r.stdout}\n{r.stderr}"
    res = json.loads((out / "result.json").read_text())
    assert res["criteria"]["1_micro_exact"] is True
    assert res["criteria"]["2_macro_mae_lt_eps"] is True
    assert res["criteria"]["3_meter_emits"] is True
    assert res["micro"]["ground_truth"] == 184
```

- [x] **Step 3: Run → PASS.** Kalau `2_macro` gagal di mini: naikkan `--steps` mini (bukan eps) — flakiness pengukuran, bukan hukum.
- [x] **Step 4: Commit** — `git add experiments analysis && git commit -m "lm1: harness eksperimen hukum tanaman — loop penuh end-to-end (mini teruji)"`

---

### Task 9: LM-1 full run — angka pertama proyek

**Files:**
- Create: `experiments/lm1/result/result.json` (output full run), catat di commit message.
- Modify: `.agent-state/now.md`

- [x] **Step 1:** `cargo build --release`
- [x] **Step 2:** `python experiments/lm1/run_lm1.py` (full) — catat verdict + MAE + model_bits.
- [x] **Step 3:** Pastikan `4_k1_cross` = PASS dari `pytest analysis -q` (test_cross).
- [x] **Step 4:** Update `.agent-state/now.md` (status LM0, angka LM-1, next = M0 atau iterasi LM0).
- [x] **Step 5:** Commit — `git add experiments && git commit -m "lm1: FULL RUN <verdict> — mikro <exact/->, makro MAE=<x>, meter=<bits> bit (angka pertama 0and1)"`

---

## Self-Review (dijalankan saat menulis plan)

1. **Spec coverage:** LM0 §9 butir 1–4 ↔ Task 5+6 (mikro eksak, makro MAE<0.02 held-out terukur), Task 7+8 (meter emit, K1 dua arah via Task 4 test_cross). Format final snapshot/manifest/file-seam ↔ Task 2–3. Tanpa float di substrat ↔ Task 1 (integer murni; float hanya bench/analisis). ✓
2. **Placeholder scan:** tidak ada TBD/TODO; semua step punya kode. ✓
3. **Type consistency:** `World{n,words}` dipakai konsisten; `micro.recover -> {"candidates","verified","constraints"}` dipakai di Task 8; `fit_pw_linear -> model{"segments","mdl","model_bits","sse","n_segments"}` dipakai verify/oracle/Task 8; MAGIC sama di Rust (`0x3044_4E31_304C_4D30`) dan Python (`0x30444E31304C4D30`). ✓
