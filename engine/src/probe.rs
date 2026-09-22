/// Probe: jalankan semesta + observasi berkala (spec §9 amendemen M1).
/// Output JSON deterministik — series pola, interface, partikel, identitas.
use crate::detect::{observe_world, ParticleTracker};
use crate::flow::FlowRule;
use crate::lattice::World;
use crate::metrics::frame_metrics;

pub struct ProbeReport {
    pub k: u8,
    pub n: u32,
    pub seed: u64,
    pub steps: u64,
    pub rule_fnv: u64,
    pub fnv_final: u64,
    pub top3_series: Vec<(u64, u64, u64)>, // (t, top3_count, total)
    pub interface_series: Vec<(u64, u64, u64)>, // (t, ifc, n)
    pub particles_final: usize,
    pub max_lifetime: u64,
    pub mass_final: u64,
}

impl ProbeReport {
    pub fn to_json(&self) -> String {
        let ser = |v: &[(u64, u64, u64)]| -> String {
            let items: Vec<String> = v
                .iter()
                .map(|(a, b, c)| format!("[{},{},{}]", a, b, c))
                .collect();
            format!("[{}]", items.join(","))
        };
        format!(
            "{{\"k\": {}, \"n\": {}, \"seed\": {}, \"steps\": {}, \"rule_fnv\": \"{:016x}\", \
             \"fnv_final\": \"{:016x}\", \"top3_series\": {}, \"interface_series\": {}, \
             \"particles_final\": {}, \"max_lifetime\": {}, \"mass_final\": {}}}",
            self.k,
            self.n,
            self.seed,
            self.steps,
            self.rule_fnv,
            self.fnv_final,
            ser(&self.top3_series),
            ser(&self.interface_series),
            self.particles_final,
            self.max_lifetime,
            self.mass_final
        )
    }
}

pub fn run(
    w0: World,
    rule: &FlowRule,
    threads: usize,
    steps: u64,
    probe_every: u64,
    w_max: usize,
) -> ProbeReport {
    assert_eq!(w0.k, rule.k, "k world ≠ k rule");
    let n = w0.n as usize;
    let max_shift = (1usize << w0.k) - 1; // aliran maksimum per langkah
    let mut counts = vec![0u64; 1usize << (3 * rule.k as usize)];
    let mut tracker = ParticleTracker::new(w_max, max_shift);
    let mut top3_series = Vec::new();
    let mut interface_series = Vec::new();
    let mut cur = w0;
    for t in 0..=steps {
        if t % probe_every == 0 || t == steps {
            let ((top, tot), (ifc, tot_n)) = frame_metrics(&cur, &mut counts);
            top3_series.push((t, top, tot));
            interface_series.push((t, ifc, tot_n));
            observe_world(&mut tracker, &cur);
        }
        if t < steps {
            cur = crate::flow::step_words(&cur, rule, threads);
        }
    }
    ProbeReport {
        k: rule.k,
        n: n as u32,
        seed: 0, // diisi pemanggil (CLI) bila perlu
        steps,
        rule_fnv: rule.table_fnv(),
        fnv_final: cur.fnv1a(),
        top3_series,
        interface_series,
        particles_final: tracker.count_alive(),
        max_lifetime: tracker.max_lifetime(),
        mass_final: cur.cell_sum(),
    }
}
