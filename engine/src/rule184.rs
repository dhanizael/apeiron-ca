use crate::lattice::World;

/// Rule 184 (traffic; number-conserving). Output 1 utk (L,C,R) ∈ {111,101,100,011}.
/// Kanonik scalar; jalur bitwise wajib setara bit-dengan ini (diuji).
pub fn step_scalar(w: &World) -> World {
    let n = w.n;
    let mut out = World::zeros(n, 1);
    for i in 0..n {
        let l = w.get_cell((i + n - 1) % n) as u64;
        let c = w.get_cell(i) as u64;
        let r = w.get_cell((i + 1) % n) as u64;
        let f = (l & r) | (l & !c & !r) | (!l & c & r);
        out.set_cell(i, (f & 1) as u8);
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
        w.k == 1 && w.n % 64 == 0 && w.words.len() == (w.n / 64) as usize,
        "jalur bitwise butuh k=1 dan n kelipatan 64; pakai flow::step_scalar"
    );
    let l = rot(&w.words, true);
    let r = rot(&w.words, false);
    let c = &w.words;
    let mut out = Vec::with_capacity(c.len());
    for j in 0..c.len() {
        out.push((l[j] & r[j]) | (l[j] & !c[j] & !r[j]) | (!l[j] & c[j] & r[j]));
    }
    World {
        n: w.n,
        k: 1,
        words: out,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn single_car_moves_right_one_per_step() {
        let mut w = World::zeros(64, 1);
        w.set_cell(4, 1);
        let mut cur = w;
        for k in 1..=3u32 {
            cur = step_scalar(&cur);
            assert_eq!(cur.popcount(), 1, "partikel hilang/duplikat");
            assert_eq!(cur.get_cell(4 + k), 1, "mobil harus di {}", 4 + k);
        }
    }

    #[test]
    fn jam_leader_moves_hole_propagates() {
        // 1100 → 1010: pemimpin gerombolan maju, celah bergeser (jam wave backward)
        let mut w = World::zeros(64, 1);
        w.set_cell(10, 1);
        w.set_cell(11, 1);
        let n1 = step_scalar(&w);
        assert_eq!(
            (n1.get_cell(10), n1.get_cell(11), n1.get_cell(12)),
            (1, 0, 1)
        );
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
