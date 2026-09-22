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
    let fnv = snapshot::write_snapshot(
        &Path::new(&outdir).join("final.bin"),
        final_state,
        184,
        steps,
    )
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
        n,
        cars0,
        steps,
        window + 1,
        fnv
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
