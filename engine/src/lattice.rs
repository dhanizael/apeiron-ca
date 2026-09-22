/// Lattice 1D bit-packed, k-bit per sel (k ∈ {1,2,4,8}), ring (boundary periodik).
/// Cell i menempati bit [i·k, (i+1)·k).
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
        (n as usize * k as usize + 63) / 64
    }

    pub fn zeros(n: u32, k: u8) -> World {
        assert!(matches!(k, 1 | 2 | 4 | 8), "k harus 1/2/4/8");
        World {
            n,
            k,
            words: vec![0u64; Self::n_words(n, k)],
        }
    }

    pub fn cells_per_word_of(&self) -> u32 {
        Self::cells_per_word(self.k)
    }

    pub fn mask(&self) -> u8 {
        ((1u16 << self.k) - 1) as u8
    }

    pub fn get_cell(&self, i: u32) -> u8 {
        let i = i % self.n;
        let bit = i as usize * self.k as usize;
        let w = bit / 64;
        let off = bit % 64;
        let v = if off + self.k as usize <= 64 {
            self.words[w] >> off
        } else {
            (self.words[w] >> off) | (self.words[w + 1] << (64 - off))
        };
        (v as u8) & self.mask()
    }

    pub fn set_cell(&mut self, i: u32, v: u8) {
        let i = i % self.n;
        let bit = i as usize * self.k as usize;
        let w = bit / 64;
        let off = bit % 64;
        let m = (self.mask() as u64) << off;
        let vv = (v & self.mask()) as u64;
        self.words[w] &= !m;
        self.words[w] |= vv << off;
        let spill = off as i32 + self.k as i32 - 64;
        if spill > 0 {
            // tinggi cell meluber ke word berikutnya (bit [0, spill))
            let spill = spill as usize;
            let m2 = (1u64 << spill) - 1;
            self.words[w + 1] &= !m2;
            self.words[w + 1] |= vv >> (self.k as usize - spill);
        }
    }

    pub fn popcount(&self) -> u64 {
        self.words.iter().map(|w| w.count_ones() as u64).sum()
    }

    /// Jumlah nilai sel — invariant keluarga flow (konservasi by construction).
    pub fn cell_sum(&self) -> u64 {
        let lpw = self.cells_per_word_of() as usize;
        let ks = self.k as usize;
        let mut s = 0u64;
        for (wi, &word) in self.words.iter().enumerate() {
            for lane in 0..lpw {
                if (wi * lpw + lane) as u32 >= self.n {
                    break;
                }
                s += (word >> (lane * ks)) & self.mask() as u64;
            }
        }
        s
    }

    /// Tepat `cars` sel = 1 pada posisi acak tanpa pengembalian (Fisher–Yates parsial, seeded).
    /// k=1 — kompatibilitas LM0 (mirror persis di analysis/semesta/ca.py).
    pub fn from_seed_exact(n: u32, cars: u32, seed: u64) -> World {
        let mut rng = crate::rng::Rng::new(seed);
        let mut idx: Vec<u32> = (0..n).collect();
        let k = (cars.min(n)) as usize;
        for i in 0..k {
            let j = i + rng.below((n as usize - i) as u64) as usize;
            idx.swap(i, j);
        }
        let mut w = World::zeros(n, 1);
        for &i in &idx[..k] {
            w.set_cell(i, 1);
        }
        w
    }

    /// Tiap sel uniform [0, 2^k) — mirror persis analysis/semesta/ca.py::from_seed_uniform.
    pub fn from_seed_uniform(n: u32, k: u8, seed: u64) -> World {
        let mut rng = crate::rng::Rng::new(seed);
        let mut w = World::zeros(n, k);
        for i in 0..n {
            let v = (rng.next_u64() & w.mask() as u64) as u8;
            w.set_cell(i, v);
        }
        w
    }

    /// Tiap sel uniform [0, cap] — kerapatan terkendali untuk sweep makro.
    /// cap = 0 → semua nol; mirror persis ca.py::from_seed_uniform_capped.
    pub fn from_seed_uniform_capped(n: u32, k: u8, seed: u64, cap: u8) -> World {
        assert!(cap < (1u16 << k) as u8, "cap harus < 2^k");
        let mut rng = crate::rng::Rng::new(seed);
        let mut w = World::zeros(n, k);
        for i in 0..n {
            let v = (rng.next_u64() % (cap as u64 + 1)) as u8;
            w.set_cell(i, v);
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
        let mut w = World::zeros(200, 1);
        w.set_cell(0, 1);
        w.set_cell(199, 1);
        w.set_cell(64, 1);
        assert_eq!((w.get_cell(0), w.get_cell(199), w.get_cell(64)), (1, 1, 1));
        assert_eq!(w.get_cell(1), 0);
        w.set_cell(64, 0);
        assert_eq!(w.get_cell(64), 0);
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
    fn cell_ops_cross_word_boundary() {
        // k=8: cell 7 = bit [56,64) pas di word 0; cell 8 = bit [64,72) luruh ke word 1
        let mut w = World::zeros(16, 8);
        w.set_cell(7, 255);
        w.set_cell(8, 170);
        assert_eq!(w.get_cell(7), 255);
        assert_eq!(w.get_cell(8), 170);
        // k=4: cell 15 = bit [60,64), cell 16 = [64,68) — beda word
        let mut w4 = World::zeros(32, 4);
        w4.set_cell(15, 15);
        w4.set_cell(16, 5);
        assert_eq!((w4.get_cell(15), w4.get_cell(16)), (15, 5));
        // k=2 luruh di tengah: cell 31 = bit [62,64), cell 32 = [64,66)
        let mut w2 = World::zeros(64, 2);
        w2.set_cell(31, 3);
        w2.set_cell(32, 2);
        assert_eq!((w2.get_cell(31), w2.get_cell(32)), (3, 2));
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
    fn capped_init_deterministic_in_range() {
        let a = World::from_seed_uniform_capped(64, 4, 9, 5);
        let b = World::from_seed_uniform_capped(64, 4, 9, 5);
        assert_eq!(a.words, b.words);
        for i in 0..64 {
            assert!(a.get_cell(i) <= 5);
        }
        let z = World::from_seed_uniform_capped(64, 4, 9, 0);
        assert_eq!(z.cell_sum(), 0);
    }

    #[test]
    fn one_bit_world_backward_compatible_layout() {
        // k=1: layout bit lama — cell i = bit i
        let mut w = World::zeros(70, 1);
        w.set_cell(64, 1);
        assert_eq!(w.get_cell(64), 1);
        assert_eq!(w.get_cell(63), 0);
        assert_eq!(w.cell_sum(), 1);
    }
}
