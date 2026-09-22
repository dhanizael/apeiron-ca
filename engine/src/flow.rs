use crate::lattice::World;

/// Fungsi aliran F(l, c, r) = unit yang mengalir melintasi edge (i → i+1),
/// dengan l = v_{i−1}, c = v_i (pengirim), r = v_{i+1} (penerima).
///
/// Kapasitas ditegakkan saat load (clip): 0 ≤ F ≤ min(c, 2^k − 1 − r).
/// Total lattice invariant by telescoping — konservasi adalah STRUKTUR keluarga,
/// bukan properti yang dijaga per aturan: v'_i = v_i − f_i + f_{i−1}.
pub struct FlowRule {
    pub k: u8,
    pub table: Vec<u8>, // 2^(3k) entri, index (l<<2k)|(c<<k)|r, sudah ter-clip
}

impl FlowRule {
    pub fn from_table(k: u8, raw: &[u8]) -> FlowRule {
        assert!(matches!(k, 1 | 2 | 4 | 8), "k harus 1/2/4/8");
        let len = 1usize << (3 * k as usize);
        assert_eq!(raw.len(), len, "tabel harus 2^(3k) entri");
        let mask = ((1u16 << k) - 1) as usize;
        let max_cell = mask;
        let mut table = vec![0u8; len];
        for (idx, slot) in table.iter_mut().enumerate() {
            let r = idx & mask;
            let c = (idx >> k as usize) & mask;
            let cap = c.min(max_cell - r);
            *slot = (raw[idx] as usize).min(cap) as u8;
        }
        FlowRule { k, table }
    }

    /// Rule 184 (traffic) sebagai anggota k=1: F = c AND NOT r.
    pub fn builtin184() -> FlowRule {
        let mut t = [0u8; 8];
        for l in 0..2usize {
            for c in 0..2usize {
                for r in 0..2usize {
                    t[(l << 2) | (c << 1) | r] = (c & (1 - r)) as u8;
                }
            }
        }
        FlowRule::from_table(1, &t)
    }

    pub fn random(k: u8, seed: u64) -> FlowRule {
        let mut rng = crate::rng::Rng::new(seed);
        let len = 1usize << (3 * k as usize);
        let raw: Vec<u8> = (0..len).map(|_| (rng.next_u64() & 0xFF) as u8).collect();
        FlowRule::from_table(k, &raw)
    }

    pub fn table_fnv(&self) -> u64 {
        crate::hash::fnv1a_bytes(&self.table)
    }
}

#[inline]
fn edge_index(k: u8, l: u8, c: u8, r: u8) -> usize {
    ((l as usize) << (2 * k as usize)) | ((c as usize) << (k as usize)) | r as usize
}

/// Referensi kanonik: materialisasi sel → f per edge → nilai baru. Jelas benar, memori O(n).
pub fn step_scalar(w: &World, rule: &FlowRule) -> World {
    assert_eq!(w.k, rule.k, "k world ≠ k rule");
    let n = w.n as usize;
    let cells: Vec<u8> = (0..n).map(|i| w.get_cell(i as u32)).collect();
    let f: Vec<u8> = (0..n)
        .map(|i| {
            let l = cells[(i + n - 1) % n];
            let c = cells[i];
            let r = cells[(i + 1) % n];
            rule.table[edge_index(rule.k, l, c, r)]
        })
        .collect();
    let mut out = World::zeros(w.n, w.k);
    for i in 0..n {
        let newv = cells[i] - f[i] + f[(i + n - 1) % n];
        out.set_cell(i as u32, newv);
    }
    out
}

/// Baca cell via bit-math langsung (tanpa materialisasi). cell ≥ n → panic; pemanggil
/// wajib normalisasi mod n untuk edge; padding lattice ditangani saat penulisan word.
#[inline]
fn cell_bits(w: &World, cell: usize) -> u8 {
    let bit = cell * w.k as usize;
    let word = bit / 64;
    let off = bit % 64;
    let v = if off + w.k as usize <= 64 {
        w.words[word] >> off
    } else {
        (w.words[word] >> off) | (w.words[word + 1] << (64 - off))
    };
    (v as u8) & w.mask()
}

/// Badan satu worker: hitung word [w0, w1) dari state lama. Edge yang dibutuhkan:
/// [start−1, end); tiap edge e membaca sel e−1, e, e+1 → sel [start−2, end] → halo 3.
/// Lane dimaterialisasi sekali (modulo hanya di inisialisasi, lalu jalan maju dengan
/// conditional wrap) → nol pembagian integer di hot loop.
fn run_chunk(w: &World, rule: &FlowRule, w0: usize, w1: usize, head: &mut [u64], n: usize, lpw: usize) {
    let start = w0 * lpw;
    let end = w1 * lpw;
    let len = (end - start) + 3;
    let mut local = vec![0u8; len];
    let mut cell_idx = (start + n - 2) % n; // start − 2 (mod n, sekali saja)
    for slot in local.iter_mut() {
        *slot = cell_bits(w, cell_idx);
        cell_idx += 1;
        if cell_idx == n {
            cell_idx = 0;
        }
    }
    // local[x] = cell(start−2+x) → edge i (aliran i→i+1) memakai local[i−start+1 .. i−start+3]
    let lut = &rule.table;
    let ks = w.k as usize;
    let mut fprev = lut[edge_index(rule.k, local[0], local[1], local[2])]; // edge start−1
    for wi in 0..(w1 - w0) {
        let mut acc: u64 = 0;
        for lane in 0..lpw {
            let i = start + wi * lpw + lane;
            let li = i - start + 1;
            let fi = lut[edge_index(rule.k, local[li], local[li + 1], local[li + 2])];
            let val = if i < n {
                local[li + 1] - fi + fprev
            } else {
                0 // padding lattice
            };
            fprev = fi;
            acc |= (val as u64) << (lane * ks);
        }
        head[wi] = acc;
    }
}

/// Jalur utama: partisi statis per word-range, satu worker per chunk, nol sinkronisasi
/// di hot loop (input read-only; output = rentang word disjoint). threads ≥ 1.
/// Hasil independen jumlah thread (K1′) karena tiap cell baru adalah fungsi murni state lama.
pub fn step_words(w: &World, rule: &FlowRule, threads: usize) -> World {
    assert_eq!(w.k, rule.k, "k world ≠ k rule");
    let n = w.n as usize;
    let nw = w.words.len();
    let lpw = w.cells_per_word_of() as usize;
    let threads = threads.max(1).min(nw.max(1));

    // rentang word [w0, w1) per worker
    let mut ranges: Vec<(usize, usize)> = Vec::with_capacity(threads);
    for t in 0..threads {
        let w0 = nw * t / threads;
        let w1 = nw * (t + 1) / threads;
        if w1 > w0 {
            ranges.push((w0, w1));
        }
    }

    let mut outw = vec![0u64; nw];
    // Satu range → jalan inline (tanpa spawn): n kecil × langkah banyak,
    // biaya spawn per langkah melahap semuanya (pelajaran M1).
    if ranges.len() == 1 {
        let (w0, w1) = ranges[0];
        run_chunk(w, rule, w0, w1, &mut outw[w0..w1], n, lpw);
        return World { n: w.n, k: w.k, words: outw };
    }

    std::thread::scope(|s| {
        let mut rest: &mut [u64] = &mut outw;
        for &(w0, w1) in &ranges {
            let (head, tail) = rest.split_at_mut(w1 - w0);
            rest = tail;
            s.spawn(move || {
                run_chunk(w, rule, w0, w1, head, n, lpw);
            });
        }
    });

    World {
        n: w.n,
        k: w.k,
        words: outw,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn builtin184_matches_rule184_bitwise() {
        for seed in 1..=20u64 {
            let w = World::from_seed_exact(4096, 2048, seed);
            let a = crate::rule184::step_scalar(&w);
            let b = step_scalar(&w, &FlowRule::builtin184());
            assert_eq!(a.words, b.words, "184 ≠ flow(184) seed={}", seed);
        }
    }

    #[test]
    fn lane_equals_scalar_random_rules() {
        for k in [1u8, 2, 4] {
            for seed in 1..=10u64 {
                let rule = FlowRule::random(k, seed * 31);
                let w = World::from_seed_uniform(256, k, seed);
                let a = step_scalar(&w, &rule);
                let b = step_words(&w, &rule, 1);
                assert_eq!(a.words, b.words, "lane≠scalar k={} seed={}", k, seed);
            }
        }
    }

    #[test]
    fn conservation_by_construction() {
        for k in [1u8, 2, 4, 8] {
            let rule = FlowRule::random(k, 7);
            let mut w = World::from_seed_uniform(512, k, 7);
            let s0 = w.cell_sum();
            for _ in 0..100 {
                w = step_words(&w, &rule, 1);
                assert_eq!(w.cell_sum(), s0, "konservasi rusak k={}", k);
            }
        }
    }

    #[test]
    fn clip_bounds_flow() {
        // entri mentah di luar kapasitas harus ter-clip: F ≤ min(c, 2^k−1−r)
        let rule = FlowRule::from_table(2, &[255u8; 64]);
        let idx = |l: usize, c: usize, r: usize| (l << 4) | (c << 2) | r;
        assert_eq!(rule.table[idx(0, 3, 0)], 3); // ≤ c
        assert_eq!(rule.table[idx(0, 3, 1)], 2); // ≤ 3−r
        assert_eq!(rule.table[idx(0, 0, 0)], 0); // ≤ c=0
        assert_eq!(rule.table[idx(3, 3, 3)], 0); // penuh, tak ada ruang
    }

    #[test]
    fn k1_prime_identical_across_thread_counts() {
        for k in [1u8, 2, 4] {
            let rule = FlowRule::random(k, 99);
            let mut one = World::from_seed_uniform(4096, k, 99);
            let mut many = one.clone();
            for _ in 0..100 {
                one = step_words(&one, &rule, 1);
                many = step_words(&many, &rule, 4);
            }
            assert_eq!(one.words, many.words, "K1′ rusak k={}", k);
        }
    }

    #[test]
    fn thread_count_sweep() {
        let rule = FlowRule::random(4, 5);
        let refw = World::from_seed_uniform(8192, 4, 5);
        let refw = step_words(&refw, &rule, 1);
        for t in [2usize, 3, 7, 16] {
            let w = World::from_seed_uniform(8192, 4, 5);
            let w = step_words(&w, &rule, t);
            assert_eq!(w.words, refw.words, "threads={} ≠ 1", t);
        }
    }

    #[test]
    fn odd_size_no_padding_wrap() {
        // n bukan kelipatan cells_per_word: padding + wrap ring di ujung
        for k in [1u8, 2, 4] {
            let rule = FlowRule::random(k, 13);
            let w = World::from_seed_uniform(300, k, 13); // 300 bukan kelipatan 64/k
            let a = step_scalar(&w, &rule);
            let b = step_words(&w, &rule, 3);
            assert_eq!(a.words, b.words, "odd-size k={} scalar≠lane", k);
        }
    }
}
