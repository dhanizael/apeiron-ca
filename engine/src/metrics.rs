/// Metrik frame untuk probe (spec §9 amendemen M1) — integer murni, k ≤ 4.
/// top-3 massa = fraksi sel yang neighborhood-nya termasuk 3 pola terbanyak
/// (proxy exclusion); interface = edge dengan v_i ≠ v_{i+1} (aktivitas struktur).
use crate::lattice::World;

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

/// Isi `counts` (panjang 2^(3k), wajib di-nol-kan dulu) untuk frame ini dan
/// kembalikan ((top3_count, total), (interface_count, n)).
pub fn frame_metrics(w: &World, counts: &mut Vec<u64>) -> ((u64, u64), (u64, u64)) {
    let n = w.n as usize;
    let ks = w.k as usize;
    counts.iter_mut().for_each(|c| *c = 0);
    let mut interfaces = 0u64;
    let prev: Vec<u8> = (0..n).map(|i| cell_bits(w, i)).collect();
    for i in 0..n {
        let l = prev[(i + n - 1) % n] as usize;
        let c = prev[i] as usize;
        let r = prev[(i + 1) % n] as usize;
        counts[(l << (2 * ks)) | (c << ks) | r] += 1;
        if prev[i] != prev[(i + 1) % n] {
            interfaces += 1;
        }
    }
    let total = n as u64;
    // tiga terbesar; tie → index terkecil (deterministik)
    let mut order: Vec<usize> = (0..counts.len()).collect();
    order.sort_unstable_by(|&a, &b| counts[b].cmp(&counts[a]).then(a.cmp(&b)));
    let top3: u64 = order.iter().take(3).map(|&i| counts[i]).sum();
    ((top3, total), (interfaces, total))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn uniform_frame_has_no_interface_and_full_top3() {
        let mut w = World::zeros(64, 4);
        for i in 0..64 {
            w.set_cell(i, 5);
        }
        let mut counts = vec![0u64; 1 << 12];
        let ((top3, total), (ifc, n)) = frame_metrics(&w, &mut counts);
        assert_eq!((top3, total), (64, 64)); // satu pola dominan penuh
        assert_eq!((ifc, n), (0, 64));
    }

    #[test]
    fn single_blob_frame() {
        let mut w = World::zeros(32, 2);
        w.set_cell(10, 3);
        w.set_cell(11, 1);
        let mut counts = vec![0u64; 1 << 6];
        let ((top3, total), (ifc, n)) = frame_metrics(&w, &mut counts);
        assert_eq!(total, 32);
        assert_eq!(ifc, 3); // 0→3, 3→1, 1→0 (blob dua nilai berbeda)
        assert!(top3 >= 30); // background dominan
    }
}
