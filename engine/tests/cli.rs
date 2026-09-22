use std::process::Command;

fn run_engine(outdir: &str, n: &str, cars: &str, steps: &str, window: &str) {
    let s = Command::new(env!("CARGO_BIN_EXE_engine"))
        .args([
            "run", "--n", n, "--cars", cars, "--seed", "7", "--steps", steps, "--window", window,
            "--outdir", outdir,
        ])
        .status()
        .unwrap();
    assert!(s.success());
}

fn read_field(manifest: &str, key: &str) -> String {
    manifest
        .lines()
        .find(|l| l.contains(&format!("\"{}\":", key)))
        .unwrap()
        .split(':')
        .nth(1)
        .unwrap()
        .trim()
        .trim_end_matches(',')
        .to_string()
}

#[test]
fn run_produces_seam_files_deterministic() {
    let base = std::env::temp_dir().join(format!("lm0_cli_{}", std::process::id()));
    let a = base.join("a");
    let b = base.join("b");
    run_engine(a.to_str().unwrap(), "64", "32", "128", "16");
    run_engine(b.to_str().unwrap(), "64", "32", "128", "16");
    for d in [&a, &b] {
        for f in ["manifest.json", "final.bin", "window.bin"] {
            assert!(d.join(f).exists(), "{} hilang di {:?}", f, d);
        }
    }
    let ma = std::fs::read_to_string(a.join("manifest.json")).unwrap();
    let mb = std::fs::read_to_string(b.join("manifest.json")).unwrap();
    assert!(ma.contains("\"rule\": \"builtin:184\""));
    assert!(ma.contains("\"n_cells\": 64"));
    assert_eq!(read_field(&ma, "window_states"), "17");
    assert_eq!(read_field(&ma, "fnv_final"), read_field(&mb, "fnv_final"));
    // window: 17 state × 1 word × 8 byte
    assert_eq!(
        std::fs::metadata(a.join("window.bin")).unwrap().len(),
        17 * 8
    );
    // konservasi partikel lintas seluruh run: final snapshot popcount = cars
    let snap = engine::snapshot::read_snapshot(&a.join("final.bin")).unwrap();
    let w = engine::lattice::World {
        n: snap.n_cells,
        k: 1,
        words: snap.words,
    };
    assert_eq!(w.popcount(), 32);
}

#[test]
fn bad_args_rejected() {
    let s = Command::new(env!("CARGO_BIN_EXE_engine"))
        .args([
            "run",
            "--n",
            "100",
            "--cars",
            "50",
            "--outdir",
            "/tmp/x_lm0",
        ])
        .status()
        .unwrap();
    assert!(!s.success(), "n bukan kelipatan 64 harus ditolak");
}

#[test]
fn run_v2_flow_table_manifest_and_rule_bin() {
    // tabel k=2: 64 entri deterministik; jalur --rule-table
    let base = std::env::temp_dir().join(format!("m0_cli_v2_{}", std::process::id()));
    std::fs::create_dir_all(&base).unwrap();
    let rule_path = base.join("rule.bin");
    let raw: Vec<u8> = (0..64u32).map(|i| (i * 7 + 3) as u8).collect();
    std::fs::write(&rule_path, &raw).unwrap();
    let out = base.join("run");
    let s = Command::new(env!("CARGO_BIN_EXE_engine"))
        .args([
            "run",
            "--n",
            "256",
            "--k",
            "2",
            "--uniform",
            "--seed",
            "3",
            "--steps",
            "64",
            "--window",
            "8",
            "--rule-table",
            rule_path.to_str().unwrap(),
            "--threads",
            "2",
            "--outdir",
            out.to_str().unwrap(),
        ])
        .status()
        .unwrap();
    assert!(s.success());
    let m = std::fs::read_to_string(out.join("manifest.json")).unwrap();
    assert!(m.contains("\"rule\": \"flow-table\""));
    assert!(m.contains("\"k\": 2"));
    assert!(m.contains("\"threads\": 2"));
    assert!(out.join("rule.bin").exists());
    let expect = engine::flow::FlowRule::from_table(2, &raw).table_fnv();
    assert!(m.contains(&format!("{:016x}", expect)));
}

#[test]
fn run_v2_window_budget_clamps() {
    // n=256 k=4 → 16 word = 128 byte/state; budget 384 byte → muat 3 state
    let base = std::env::temp_dir().join(format!("m0_cli_bud_{}", std::process::id()));
    let out = base.join("run");
    let s = Command::new(env!("CARGO_BIN_EXE_engine"))
        .args([
            "run",
            "--n",
            "256",
            "--k",
            "4",
            "--uniform",
            "--rule",
            "random",
            "--seed",
            "1",
            "--steps",
            "32",
            "--window",
            "16",
            "--window-budget-bytes",
            "384",
            "--outdir",
            out.to_str().unwrap(),
        ])
        .status()
        .unwrap();
    assert!(s.success());
    let m = std::fs::read_to_string(out.join("manifest.json")).unwrap();
    assert!(
        m.contains("\"window_states\": 3"),
        "budget harus memotong window: {}",
        m
    );
    assert_eq!(
        std::fs::metadata(out.join("window.bin")).unwrap().len(),
        3 * 128
    );
}
