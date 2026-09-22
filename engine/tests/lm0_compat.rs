use std::process::Command;

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
        .trim_matches('"')
        .to_string()
}

/// Regresi LM0: run konfigurasi identik dengan LM-1 (rho 0.5) harus menghasilkan
/// fnv_final bit-identical dengan manifest yang ter-commit — bukti evolusi engine
/// tidak mengubah semantik k=1.
#[test]
fn lm1_full_run_reproduces_committed_fnv() {
    let committed = std::fs::read_to_string(concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../experiments/lm1/result/rho0.500/manifest.json"
    ))
    .expect("manifest LM-1 ter-commit tidak ditemukan");
    let expected = read_field(&committed, "fnv_final");
    assert_eq!(
        committed
            .lines()
            .filter(|l| l.contains("\"seed\":"))
            .count(),
        1
    );

    let out = std::env::temp_dir().join(format!("m0_lm1_compat_{}", std::process::id()));
    let s = Command::new(env!("CARGO_BIN_EXE_engine"))
        .args([
            "run",
            "--n",
            "4096",
            "--cars",
            "2048",
            "--seed",
            "7",
            "--steps",
            "20000",
            "--window",
            "512",
            "--threads",
            "1",
            "--outdir",
            out.to_str().unwrap(),
        ])
        .status()
        .unwrap();
    assert!(s.success());
    let fresh = std::fs::read_to_string(out.join("manifest.json")).unwrap();
    assert_eq!(
        read_field(&fresh, "fnv_final"),
        expected,
        "fnv_final ≠ LM-1"
    );
}
