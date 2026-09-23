use std::process::Command;

fn engine() -> Command {
    Command::new(env!("CARGO_BIN_EXE_engine"))
}

fn write_rule(base: &std::path::Path) -> std::path::PathBuf {
    let rule_path = base.join("rule.bin");
    let raw: Vec<u8> = (0..64u32).map(|i| (i * 7 + 3) as u8).collect();
    std::fs::write(&rule_path, &raw).unwrap();
    rule_path
}

fn read_fnv(outdir: &std::path::Path) -> String {
    let m = std::fs::read_to_string(outdir.join("manifest.json")).unwrap();
    m.lines()
        .find(|l| l.contains("\"fnv_final\":"))
        .unwrap()
        .split(':')
        .nth(1)
        .unwrap()
        .trim()
        .trim_end_matches(',')
        .trim_matches('"')
        .to_string()
}

/// IDENTITAS KELANJUTAN-PREFIKS: final(A: seed, T1) → (B: init-state final-A,
/// T2) ≡ final(C: seed, T1+T2) — hukum sama, bit-identik. Inilah jaminan
/// --init-state adalah kelanjukan run yang sama, bukan semesta baru.
#[test]
fn init_state_prefix_continuation_identity() {
    let base = std::env::temp_dir().join(format!("v4_init_{}", std::process::id()));
    std::fs::create_dir_all(&base).unwrap();
    let rule = write_rule(&base);

    let run = |outdir: &std::path::Path, steps: &str, init_state: Option<&std::path::Path>| {
        let mut args = vec![
            "run".to_string(),
            "--n".into(),
            "256".into(),
            "--k".into(),
            "2".into(),
            "--uniform".into(),
            "--seed".into(),
            "3".into(),
        ];
        if let Some(p) = init_state {
            args.extend(["--init-state".into(), p.to_str().unwrap().into()]);
        }
        args.extend([
            "--steps".into(),
            steps.into(),
            "--window".into(),
            "8".into(),
            "--rule-table".into(),
            rule.to_str().unwrap().into(),
            "--threads".into(),
            "1".into(),
            "--outdir".into(),
            outdir.to_str().unwrap().into(),
        ]);
        let st = engine().args(&args).status().unwrap();
        assert!(st.success(), "run gagal: {:?}", args);
    };

    let a = base.join("a");
    run(&a, "500", None); // T1 = 500
    let final_a = a.join("final.bin");
    assert!(final_a.exists());

    let b = base.join("b");
    run(&b, "300", Some(&final_a));

    let b2 = base.join("b2");
    run(&b2, "300", Some(&final_a));
    assert_eq!(
        read_fnv(&b),
        read_fnv(&b2),
        "init-state harus deterministik"
    );

    let b3 = base.join("b3");
    run(&b3, "800", Some(&final_a));
    let c = base.join("c");
    run(&c, "1300", None); // T1 + T2 penuh
    assert_eq!(
        read_fnv(&b3),
        read_fnv(&c),
        "kelanjutan prefiks (500+800) harus bit-identik dengan run penuh 1300"
    );

    let mb = std::fs::read_to_string(b.join("manifest.json")).unwrap();
    assert!(mb.contains("\"init_source\": \"snapshot\""));
}

#[test]
fn init_state_rejects_mismatch() {
    let base = std::env::temp_dir().join(format!("v4_initm_{}", std::process::id()));
    std::fs::create_dir_all(&base).unwrap();
    let rule = write_rule(&base);
    let a = base.join("a");
    let st = engine()
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
            rule.to_str().unwrap(),
            "--threads",
            "1",
            "--outdir",
            a.to_str().unwrap(),
        ])
        .status()
        .unwrap();
    assert!(st.success());
    let final_a = a.join("final.bin");

    // n mismatch: snapshot 256 sel, run menuntut 512
    let bad_n = base.join("bad_n");
    let st = engine()
        .args([
            "run",
            "--n",
            "512",
            "--k",
            "2",
            "--uniform",
            "--seed",
            "3",
            "--steps",
            "8",
            "--window",
            "2",
            "--rule-table",
            rule.to_str().unwrap(),
            "--init-state",
            final_a.to_str().unwrap(),
            "--threads",
            "1",
            "--outdir",
            bad_n.to_str().unwrap(),
        ])
        .status()
        .unwrap();
    assert!(!st.success(), "n mismatch harus ditolak");

    // k mismatch: butuh tabel 4096-entri agar resolve_rule sah, lalu
    // penolakan terjadi di validasi init-state (snap.k=2 ≠ --k 4)
    let rule4 = base.join("rule4.bin");
    let raw4: Vec<u8> = (0..4096u32).map(|i| (i * 13 + 7) as u8).collect();
    std::fs::write(&rule4, &raw4).unwrap();
    let bad_k = base.join("bad_k");
    let st = engine()
        .args([
            "run",
            "--n",
            "256",
            "--k",
            "4",
            "--uniform",
            "--seed",
            "3",
            "--steps",
            "8",
            "--window",
            "2",
            "--rule-table",
            rule4.to_str().unwrap(),
            "--init-state",
            final_a.to_str().unwrap(),
            "--threads",
            "1",
            "--outdir",
            bad_k.to_str().unwrap(),
        ])
        .status()
        .unwrap();
    assert!(!st.success(), "k mismatch harus ditolak");
}
