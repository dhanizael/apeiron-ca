/// xorshift64* — deterministik, u64 murni, mirror 1:1 dengan Python (analysis/semesta/ca.py).
pub struct Rng(u64);

impl Rng {
    pub fn new(seed: u64) -> Rng {
        Rng(if seed == 0 {
            0x9E37_79B9_7F4A_7C15
        } else {
            seed
        })
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
