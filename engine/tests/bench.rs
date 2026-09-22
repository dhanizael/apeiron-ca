use std::process::Command;

/// Smoke test protokol K2 (parameter dikecilkan; protokol penuh dijalankan manual).
#[test]
fn bench_k2_smoke() {
    let out = Command::new(env!("CARGO_BIN_EXE_engine"))
        .args([
            "bench",
            "--protocol",
            "k2",
            "--n",
            "65536",
            "--steps",
            "4",
            "--runs",
            "2",
            "--threads",
            "2",
        ])
        .output()
        .unwrap();
    assert!(out.status.success());
    let s = String::from_utf8_lossy(&out.stdout);
    assert!(s.contains("protocol=k2"), "{}", s);
    assert!(s.contains("median_cell_updates_per_detik="), "{}", s);
    assert!(s.contains("table_fnv="), "{}", s);
}
