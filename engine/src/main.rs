mod flow;
mod hash;
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

fn has_flag(args: &[String], name: &str) -> bool {
    args.iter().any(|a| a == name)
}

fn cmd_run(args: &[String]) -> i32 {
    let n: u32 = flag(args, "--n", "4096").parse().unwrap();
    let k: u8 = flag(args, "--k", "1").parse().unwrap();
    let cars: u32 = flag(args, "--cars", "2048").parse().unwrap();
    let uniform = has_flag(args, "--uniform");
    let seed: u64 = flag(args, "--seed", "1").parse().unwrap();
    let steps: u64 = flag(args, "--steps", "20000").parse().unwrap();
    let window: usize = flag(args, "--window", "512").parse().unwrap();
    let budget: usize = flag(args, "--window-budget-bytes", "268435456")
        .parse()
        .unwrap();
    let threads_req: usize = flag(args, "--threads", "0").parse().unwrap();
    let rule_spec = flag(args, "--rule", "builtin:184");
    let rule_table_path = flag(args, "--rule-table", "");
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
    let threads = if threads_req == 0 {
        std::thread::available_parallelism()
            .map(|v| v.get())
            .unwrap_or(1)
    } else {
        threads_req
    };

    let (rule, rule_label, rule_id) = if !rule_table_path.is_empty() {
        match std::fs::read(&rule_table_path) {
            Ok(bytes) => match flow::FlowRule::from_table(k, &bytes) {
                r => (r, "flow-table", 0u32),
            },
            Err(e) => {
                eprintln!("rule-table tidak terbaca: {}", e);
                return 1;
            }
        }
    } else if rule_spec == "builtin:184" {
        if k != 1 {
            eprintln!("builtin:184 butuh --k 1");
            return 1;
        }
        (flow::FlowRule::builtin184(), "builtin:184", 184u32)
    } else if rule_spec == "random" {
        (flow::FlowRule::random(k, seed), "random", 0u32)
    } else {
        eprintln!(
            "--rule tidak dikenal: {} (pakai builtin:184 atau --rule-table)",
            rule_spec
        );
        return 1;
    };
    std::fs::write(Path::new(&outdir).join("rule.bin"), &rule.table).unwrap();

    let mut cur = if uniform || k > 1 {
        lattice::World::from_seed_uniform(n, k, seed)
    } else {
        lattice::World::from_seed_exact(n, cars, seed)
    };
    let cars0 = cur.popcount();

    // window budget: W aktual = state yang muat dalam budget (min 2)
    let state_bytes = lattice::World::n_words(n, k) * 8;
    let fit = (budget / state_bytes.max(1)).max(2);
    let window_states = (window + 1).min(fit);

    let mut ring: VecDeque<lattice::World> = VecDeque::with_capacity(window_states);
    for t in 0..=steps {
        ring.push_back(cur.clone());
        if ring.len() > window_states {
            ring.pop_front();
        }
        if t < steps {
            cur = flow::step_words(&cur, &rule, threads);
        }
    }
    let states: Vec<lattice::World> = ring.into_iter().collect();
    let final_state = states.last().unwrap();
    let fnv = snapshot::write_snapshot(
        &Path::new(&outdir).join("final.bin"),
        final_state,
        rule_id,
        steps,
    )
    .unwrap();
    snapshot::write_window(&Path::new(&outdir).join("window.bin"), &states).unwrap();
    let manifest = snapshot::manifest_json(&[
        ("schema", "\"0and1-manifest\"".into()),
        ("version", "2".into()),
        ("rule", format!("\"{}\"", rule_label)),
        ("rule_fnv", format!("\"{:016x}\"", rule.table_fnv())),
        ("k", k.to_string()),
        ("n_cells", n.to_string()),
        (
            "init",
            if uniform || k > 1 {
                "\"uniform\"".into()
            } else {
                format!("\"cars:{}\"", cars0)
            },
        ),
        ("seed", seed.to_string()),
        ("steps", steps.to_string()),
        ("window_states", window_states.to_string()),
        ("window_budget", budget.to_string()),
        ("threads", threads.to_string()),
        ("fnv_final", format!("\"{:016x}\"", fnv)),
        ("engine_version", "\"m0.1\"".into()),
    ]);
    std::fs::write(Path::new(&outdir).join("manifest.json"), manifest).unwrap();
    println!(
        "n={} k={} rule={} threads={} steps={} window_states={} fnv_final={:016x}",
        n, k, rule_label, threads, steps, window_states, fnv
    );
    0
}

fn cmd_bench(args: &[String]) -> i32 {
    // mode legacy LM0 (bitwise k=1) — protokol K2 formal menyusul di --protocol k2
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
                "pemakaian: engine run --n N [--k K] [--cars K|--uniform] --seed S --steps T \
                 --window W [--rule builtin:184|--rule-table PATH] [--window-budget-bytes B] \
                 [--threads T] --outdir D | engine bench --n N --steps T"
            );
            2
        }
    };
    std::process::exit(code);
}
