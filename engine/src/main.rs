mod detect;
mod flow;
mod hash;
mod lattice;
mod metrics;
mod probe;
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

fn resolve_rule(
    args: &[String],
    k: u8,
    seed: u64,
) -> Result<(flow::FlowRule, &'static str, u32), String> {
    let rule_spec = flag(args, "--rule", "builtin:184");
    let rule_table_path = flag(args, "--rule-table", "");
    if !rule_table_path.is_empty() {
        let bytes = std::fs::read(&rule_table_path)
            .map_err(|e| format!("rule-table tidak terbaca: {}", e))?;
        Ok((flow::FlowRule::from_table(k, &bytes), "flow-table", 0))
    } else if rule_spec == "builtin:184" {
        if k != 1 {
            return Err("builtin:184 butuh --k 1".into());
        }
        Ok((flow::FlowRule::builtin184(), "builtin:184", 184))
    } else if rule_spec == "random" {
        Ok((flow::FlowRule::random(k, seed), "random", 0))
    } else {
        Err(format!(
            "--rule tidak dikenal: {} (pakai builtin:184|random|--rule-table)",
            rule_spec
        ))
    }
}

fn cmd_run(args: &[String]) -> i32 {
    let n: u32 = flag(args, "--n", "4096").parse().unwrap();
    let k: u8 = flag(args, "--k", "1").parse().unwrap();
    let cars: u32 = flag(args, "--cars", "2048").parse().unwrap();
    let uniform = has_flag(args, "--uniform");
    let init_cap: u8 = flag(args, "--init-cap", "0").parse().unwrap();
    let seed: u64 = flag(args, "--seed", "1").parse().unwrap();
    let steps: u64 = flag(args, "--steps", "20000").parse().unwrap();
    let window: usize = flag(args, "--window", "512").parse().unwrap();
    let budget: usize = flag(args, "--window-budget-bytes", "268435456")
        .parse()
        .unwrap();
    let threads_req: usize = flag(args, "--threads", "0").parse().unwrap();
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

    let (rule, rule_label, rule_id) = match resolve_rule(args, k, seed) {
        Ok(r) => r,
        Err(e) => {
            eprintln!("{}", e);
            return 1;
        }
    };
    std::fs::write(Path::new(&outdir).join("rule.bin"), &rule.table).unwrap();

    let mut cur = if init_cap > 0 {
        lattice::World::from_seed_uniform_capped(n, k, seed, init_cap)
    } else if uniform || k > 1 {
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
        ("init_cap", init_cap.to_string()),
        (
            "init",
            if init_cap > 0 {
                format!("\"capped:{}\"", init_cap)
            } else if uniform || k > 1 {
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
    if has_flag(args, "--protocol") && flag(args, "--protocol", "") == "k2" {
        return cmd_bench_k2(args);
    }
    // mode legacy LM0 (bitwise k=1)
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

/// Protokol K2 (dibekukan, spec §5 amendemen M0): jalur generik LUT, k=4,
/// n=2^27, 100 langkah, median 5 run setelah 1 warmup, tabel acak seeded.
/// Parameter override (--n/--steps/--runs) HANYA untuk smoke test.
fn cmd_bench_k2(args: &[String]) -> i32 {
    let k: u8 = flag(args, "--k", "4").parse().unwrap();
    let n: u32 = flag(args, "--n", "134217728").parse().unwrap(); // 2^27
    let steps: u64 = flag(args, "--steps", "100").parse().unwrap();
    let runs: usize = flag(args, "--runs", "5").parse().unwrap();
    let seed: u64 = flag(args, "--seed", "20260922").parse().unwrap();
    let threads_req: usize = flag(args, "--threads", "0").parse().unwrap();
    if n == 0 || n % 64 != 0 {
        eprintln!("--n harus kelipatan 64 dan > 0");
        return 1;
    }
    let threads = if threads_req == 0 {
        std::thread::available_parallelism()
            .map(|v| v.get())
            .unwrap_or(1)
    } else {
        threads_req
    };
    let rule = flow::FlowRule::random(k, seed);

    // warmup (1 run penuh, tidak diukur)
    let mut cur = lattice::World::from_seed_uniform(n, k, seed);
    for _ in 0..steps {
        cur = flow::step_words(&cur, &rule, threads);
    }

    let mut ups: Vec<u64> = Vec::with_capacity(runs);
    for _ in 0..runs {
        let mut w = lattice::World::from_seed_uniform(n, k, seed);
        let t0 = std::time::Instant::now();
        for _ in 0..steps {
            w = flow::step_words(&w, &rule, threads);
        }
        let dt = t0.elapsed().as_secs_f64();
        let updates = n as u64 * steps;
        ups.push((updates as f64 / dt) as u64);
        cur = w;
    }
    ups.sort_unstable();
    let median = ups[ups.len() / 2];
    let min = ups[0];
    let max = ups[ups.len() - 1];
    println!(
        "protocol=k2 k={} n={} steps={} runs={} threads={} arch={}",
        k,
        n,
        steps,
        runs,
        threads,
        std::env::consts::ARCH
    );
    println!("table_fnv={:016x} seed={}", rule.table_fnv(), seed);
    println!(
        "median_cell_updates_per_detik={} min={} max={}",
        median, min, max
    );
    println!("fnv_final={:016x}", cur.fnv1a());
    0
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let code = match args.get(1).map(|s| s.as_str()) {
        Some("run") => cmd_run(&args),
        Some("bench") => cmd_bench(&args),
        Some("probe") => cmd_probe(&args),
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

fn cmd_probe(args: &[String]) -> i32 {
    let n: u32 = flag(args, "--n", "4096").parse().unwrap();
    let k: u8 = flag(args, "--k", "2").parse().unwrap();
    let seed: u64 = flag(args, "--seed", "1").parse().unwrap();
    let steps: u64 = flag(args, "--steps", "20000").parse().unwrap();
    let probe_every: u64 = flag(args, "--probe-every", "1000").parse().unwrap();
    let w_max: usize = flag(args, "--w-max", "8").parse().unwrap();
    let threads_req: usize = flag(args, "--threads", "0").parse().unwrap();
    if n == 0 || n % 64 != 0 {
        eprintln!("--n harus kelipatan 64 dan > 0");
        return 1;
    }
    if probe_every == 0 {
        eprintln!("--probe-every harus > 0");
        return 1;
    }
    let threads = if threads_req == 0 {
        std::thread::available_parallelism().map(|v| v.get()).unwrap_or(1)
    } else {
        threads_req
    };
    let rule = match resolve_rule(args, k, seed) {
        Ok((r, _, _)) => r,
        Err(e) => {
            eprintln!("{}", e);
            return 1;
        }
    };
    let w0 = lattice::World::from_seed_uniform(n, k, seed);
    let mut rep = probe::run(w0, &rule, threads, steps, probe_every, w_max);
    rep.seed = seed;
    println!("{}", rep.to_json());
    0
}
