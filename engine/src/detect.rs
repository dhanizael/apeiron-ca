/// Detektor partikel — fungsi murni atas sekuens state (spec §9 amendemen M1).
/// Partikel = run kontigu sel ≠ background (mode), lebar ≤ w_max, terbungkus background.
/// Tracker = pencocokan greedy antar frame (interval overlap setelah geser ≤ max_shift);
/// merge/pisasah = mati objek lama — jujur dilaporkan sebagai kehilangan individu.
use crate::lattice::World;

pub fn background(cells: &[u8]) -> u8 {
    // mode; tie → nilai terkecil (deterministik)
    let mut counts = [0usize; 256];
    for &c in cells {
        counts[c as usize] += 1;
    }
    let mut best = 0usize;
    for v in 1..256 {
        if counts[v] > counts[best] {
            best = v;
        }
    }
    best as u8
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Particle {
    pub start: usize, // indeks awal dalam orientasi scan (bisa > ring bila wrap)
    pub width: usize,
    pub mass: u64,
}

/// Partikel pada satu frame. Ring-aware: blob yang membungkus indeks 0 = satu objek.
pub fn particles_at(cells: &[u8], w_max: usize) -> Vec<Particle> {
    let n = cells.len();
    if n == 0 {
        return vec![];
    }
    let b = background(cells);
    // cari titik mulai: sel background pertama (agar scan linear tak memotong blob wrap)
    let start0 = (0..n).find(|&i| cells[i] == b);
    let start0 = match start0 {
        Some(i) => i,
        None => return vec![], // tanpa background = satu blob se-ring → pasti > w_max
    };
    let mut out = Vec::new();
    let mut i = 0usize;
    while i < n {
        let idx = (start0 + i) % n;
        if cells[idx] != b {
            let run_start = i;
            let mut mass = 0u64;
            while i < n && cells[(start0 + i) % n] != b {
                mass += cells[(start0 + i) % n] as u64;
                i += 1;
            }
            let width = i - run_start;
            if width <= w_max {
                out.push(Particle {
                    start: run_start,
                    width,
                    mass,
                });
            }
        } else {
            i += 1;
        }
    }
    out
}

/// Pelacak objek antar frame. Satu `update` = satu langkah observasi (bukan langkah fisika).
pub struct ParticleTracker {
    w_max: usize,
    max_shift: usize,
    prev: Vec<Particle>,
    ages: Vec<u64>,
    max_lifetime: u64,
    count_alive: usize,
}

impl ParticleTracker {
    pub fn new(w_max: usize, max_shift: usize) -> ParticleTracker {
        ParticleTracker {
            w_max,
            max_shift,
            prev: vec![],
            ages: vec![],
            max_lifetime: 0,
            count_alive: 0,
        }
    }

    pub fn count_alive(&self) -> usize {
        self.count_alive
    }

    pub fn max_lifetime(&self) -> u64 {
        self.max_lifetime
    }

    pub fn update(&mut self, cells: &[u8]) {
        let cur = particles_at(cells, self.w_max);
        let mut new_ages: Vec<u64> = vec![0; cur.len()];
        // greedy dua pointer; keduanya terurut berdasarkan start
        let (mut pi, mut ci) = (0usize, 0usize);
        while pi < self.prev.len() && ci < cur.len() {
            let p = &self.prev[pi];
            let q = &cur[ci];
            // interval: prev menempati [p.start, p.start+p.width), cur [q.start, ...)
            // match bila overlap setelah geser ≤ max_shift
            let overlap = p.start < q.start + q.width + self.max_shift
                && q.start < p.start + p.width + self.max_shift;
            if overlap {
                let age = self.ages[pi] + 1;
                new_ages[ci] = age;
                if age > self.max_lifetime {
                    self.max_lifetime = age;
                }
                pi += 1;
                ci += 1;
            } else if p.start < q.start {
                pi += 1;
            } else {
                ci += 1;
            }
        }
        self.prev = cur;
        self.ages = new_ages;
        // objek hidup pada frame ini = semua entri ages (age 0 = baru lahir)
        self.count_alive = self.ages.len();
    }
}

/// Utilitas probe: hitung partikel + tracker sekaligus pada satu world.
pub fn observe_world(tracker: &mut ParticleTracker, w: &World) {
    let cells: Vec<u8> = (0..w.n).map(|i| w.get_cell(i)).collect();
    tracker.update(&cells);
}

#[cfg(test)]
mod tests {
    use super::*;

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
        c[10] = 2;
        c[11] = 2;
        c[12] = 1;
        let ps = particles_at(&c, 8);
        assert_eq!(ps.len(), 1);
        assert_eq!((ps[0].start, ps[0].width, ps[0].mass), (10, 3, 5));
    }

    #[test]
    fn wide_blob_is_not_particle() {
        let mut c = vec![0u8; 32];
        for x in c.iter_mut().take(20) {
            *x = 1;
        }
        assert_eq!(particles_at(&c, 8).len(), 0);
    }

    #[test]
    fn no_background_no_particle() {
        let c = vec![1u8; 32];
        assert_eq!(particles_at(&c, 8).len(), 0);
    }

    #[test]
    fn wrap_around_ring_detected_once() {
        let mut c = vec![0u8; 8];
        c[7] = 1;
        c[0] = 1; // blob membungkus ring
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
            c[pos] = 3;
            c[pos + 1] = 1;
            tr.update(&c);
        }
        assert_eq!(tr.count_alive(), 1);
        assert_eq!(tr.max_lifetime(), 9);
    }

    #[test]
    fn tracker_merge_kills_old_object() {
        let mut tr = ParticleTracker::new(8, 4);
        let mut a = vec![0u8; 32];
        a[5] = 1;
        a[20] = 1;
        tr.update(&a);
        let mut b = vec![0u8; 32];
        b[6] = 1;
        b[7] = 1; // partikel di 20 hilang; 5 bergeser
        tr.update(&b);
        assert_eq!(tr.count_alive(), 1);
    }

    #[test]
    fn tracker_counts_two_distinct() {
        let mut tr = ParticleTracker::new(8, 4);
        let mut c = vec![0u8; 32];
        c[5] = 1;
        c[20] = 1;
        tr.update(&c);
        tr.update(&c);
        assert_eq!(tr.count_alive(), 2);
        assert_eq!(tr.max_lifetime(), 1);
    }
}
