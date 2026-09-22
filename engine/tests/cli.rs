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
    assert_eq!(read_field(&ma, "rule_id"), "184");
    assert_eq!(read_field(&ma, "n_cells"), "64");
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
