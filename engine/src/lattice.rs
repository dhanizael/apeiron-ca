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
        World {
            n,
            words: vec![0u64; Self::n_words(n)],
        }
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
