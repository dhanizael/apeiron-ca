use std::process::Command;

fn run_probe(engine: &str, extra: &[&str]) -> String {
    let out = Command::new(engine)
        .args(["probe", "--threads", "1"])
        .args(extra)
        .output()
        .unwrap();
    assert!(
        out.status.success(),
        "probe gagal: {}",
        String::from_utf8_lossy(&out.stderr)
    );
    String::from_utf8_lossy(&out.stdout).trim().to_string()
}

/// Ekstrak elemen terakhir seri [t,top,total] dari JSON probe.
fn last_series(json: &str, key: &str) -> (u64, u64, u64) {
    let start = json.find(key).unwrap();
    let seg = &json[start..];
    // batasi sampai key berikutnya (pemisah \"], \") agar rfind tidak menerjang seri lain
    let end = seg.find("], \"").map(|p| p + 1).unwrap_or(seg.len());
    let seg = &seg[..end];
    let open = seg.rfind('[').unwrap(); // '[' item terakhir
    let close = seg[open..].find(']').unwrap() + open; // ']' pertama setelahnya (penutup item)
    let body = &seg[open + 1..close];
    let nums: Vec<u64> = body.split(',').map(|x| x.trim().parse().unwrap()).collect();
    (nums[0], nums[1], nums[2])
}

/// Kalibrasi baseline (F1): 184 pasca-transien runtuh ke beberapa pola —
/// top-3 massa ≥ 4/5. Ini memastikan metrik exclusion MELIHAT collapse.
#[test]
fn probe_184_shows_collapse() {
    let json = run_probe(
        env!("CARGO_BIN_EXE_engine"),
        &[
            "--n",
            "4096",
            "--k",
            "1",
            "--seed",
            "7",
            "--steps",
            "2000",
            "--probe-every",
            "1000",
        ],
    );
    let (_t, top, total) = last_series(&json, "\"top3_series\"");
    eprintln!(
        "DEBUG last=(t,top,total)=({}, {}, {}) json_len={}",
        _t,
        top,
        total,
        json.len()
    );
    assert!(
        top * 5 >= total * 4,
        "184 harus runtuh: top3={}/{}",
        top,
        total
    );
}

#[test]
fn probe_json_keys_and_determinism() {
    let a = run_probe(
        env!("CARGO_BIN_EXE_engine"),
        &[
            "--n",
            "256",
            "--k",
            "2",
            "--seed",
            "3",
            "--steps",
            "64",
            "--probe-every",
            "32",
            "--rule",
            "random",
        ],
    );
    let b = run_probe(
        env!("CARGO_BIN_EXE_engine"),
        &[
            "--n",
            "256",
            "--k",
            "2",
            "--seed",
            "3",
            "--steps",
            "64",
            "--probe-every",
            "32",
            "--rule",
            "random",
        ],
    );
    for key in [
        "\"k\": 2",
        "\"n\": 256",
        "\"rule_fnv\": \"",
        "\"fnv_final\": \"",
        "\"top3_series\": ",
        "\"interface_series\": ",
        "\"particles_final\": ",
        "\"max_lifetime\": ",
        "\"mass_final\": ",
    ] {
        assert!(a.contains(key), "key {} hilang", key);
    }
    assert_eq!(a, b, "probe harus deterministik");
}
