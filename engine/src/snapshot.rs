use crate::lattice::World;
use std::io::{Read, Write};
use std::path::Path;

pub const MAGIC: u64 = 0x3044_4E31_304C_4D30;

pub struct Snapshot {
    pub version: u16,
    pub k: u8,
    pub rule_id: u32,
    pub n_cells: u32,
    pub step: u64,
    pub fnv: u64,
    pub words: Vec<u64>,
}

/// Header v2 (LE, 36 byte): magic u64, versi u16, k u8, reserved u8, rule_id u32,
/// n_cells u32, step u64, fnv u64; lalu words. v1 (34 byte, tanpa k) tetap terbaca.
pub fn write_snapshot(path: &Path, w: &World, rule_id: u32, step: u64) -> std::io::Result<u64> {
    let fnv = w.fnv1a();
    let mut f = std::fs::File::create(path)?;
    f.write_all(&MAGIC.to_le_bytes())?;
    f.write_all(&2u16.to_le_bytes())?;
    f.write_all(&[w.k, 0])?; // k, reserved
    f.write_all(&rule_id.to_le_bytes())?;
    f.write_all(&w.n.to_le_bytes())?;
    f.write_all(&step.to_le_bytes())?;
    f.write_all(&fnv.to_le_bytes())?;
    for word in &w.words {
        f.write_all(&word.to_le_bytes())?;
    }
    Ok(fnv)
}

pub fn read_snapshot(path: &Path) -> Result<Snapshot, String> {
    let mut buf = Vec::new();
    std::fs::File::open(path)
        .and_then(|mut f| f.read_to_end(&mut buf))
        .map_err(|e| e.to_string())?;
    let need = |off: usize, len: usize| -> Result<Vec<u8>, String> {
        buf.get(off..off + len)
            .ok_or_else(|| "snapshot terlalu pendek".to_string())
            .map(|s| s.to_vec())
    };
    let q = |v: Vec<u8>| u64::from_le_bytes(v.try_into().unwrap());
    let d = |v: Vec<u8>| u32::from_le_bytes(v.try_into().unwrap());
    if q(need(0, 8)?) != MAGIC {
        return Err("magic salah".into());
    }
    let version = u16::from_le_bytes(need(8, 2)?.try_into().unwrap());
    let (k, rule_id, n_cells, step, fnv, words_off) = match version {
        1 => (
            1u8,
            d(need(10, 4)?),
            d(need(14, 4)?),
            q(need(18, 8)?),
            q(need(26, 8)?),
            34,
        ),
        2 => {
            let k = need(10, 1)?[0];
            let rule_id = d(need(12, 4)?);
            let n_cells = d(need(16, 4)?);
            let step = q(need(20, 8)?);
            let fnv = q(need(28, 8)?);
            (k, rule_id, n_cells, step, fnv, 36)
        }
        v => return Err(format!("versi {} tidak didukung", v)),
    };
    if !matches!(k, 1 | 2 | 4 | 8) {
        return Err(format!("k {} tidak didukung", k));
    }
    let nw = (n_cells as usize * k as usize + 63) / 64;
    let mut words = Vec::with_capacity(nw);
    for j in 0..nw {
        words.push(q(need(words_off + j * 8, 8)?));
    }
    let w = World {
        n: n_cells,
        k,
        words,
    };
    if w.fnv1a() != fnv {
        return Err("checksum fnv tidak cocok".into());
    }
    Ok(Snapshot {
        version,
        k,
        rule_id,
        n_cells,
        step,
        fnv,
        words: w.words,
    })
}

/// Window: states berturutan tanpa header (count ada di manifest).
pub fn write_window(path: &Path, states: &[World]) -> std::io::Result<()> {
    let mut f = std::fs::File::create(path)?;
    for w in states {
        for word in &w.words {
            f.write_all(&word.to_le_bytes())?;
        }
    }
    Ok(())
}

/// Manifest JSON deterministik (urutan kunci = urutan argumen, tanpa wall-clock).
pub fn manifest_json(kv: &[(&str, String)]) -> String {
    let body: Vec<String> = kv
        .iter()
        .map(|(k, v)| format!("  \"{}\": {}", k, v))
        .collect();
    format!("{{\n{}\n}}\n", body.join(",\n"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn snapshot_roundtrip_v2_and_checksum() {
        let w = World::from_seed_uniform(128, 4, 5);
        let dir = std::env::temp_dir().join(format!("m0_snap_{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let p = dir.join("s.bin");
        let fnv = write_snapshot(&p, &w, 0, 123).unwrap();
        let s = read_snapshot(&p).unwrap();
        assert_eq!(
            (s.version, s.k, s.rule_id, s.n_cells, s.step, s.fnv),
            (2, 4, 0, 128, 123, fnv)
        );
        assert_eq!(s.words, w.words);
    }

    #[test]
    fn v1_file_still_readable() {
        // file v1 sintetis: magic, ver=1, rule_id=184, n=64, step=0, fnv, 1 word
        let w = World::from_seed_exact(64, 30, 1);
        let dir = std::env::temp_dir().join(format!("m0_snapv1_{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let p = dir.join("v1.bin");
        let mut b = Vec::new();
        b.extend_from_slice(&MAGIC.to_le_bytes());
        b.extend_from_slice(&1u16.to_le_bytes());
        b.extend_from_slice(&184u32.to_le_bytes());
        b.extend_from_slice(&64u32.to_le_bytes());
        b.extend_from_slice(&0u64.to_le_bytes());
        b.extend_from_slice(&w.fnv1a().to_le_bytes());
        b.extend_from_slice(&w.words[0].to_le_bytes());
        std::fs::write(&p, b).unwrap();
        let s = read_snapshot(&p).unwrap();
        assert_eq!((s.version, s.k, s.rule_id, s.n_cells), (1, 1, 184, 64));
        assert_eq!(s.words, w.words);
    }

    #[test]
    fn corrupt_byte_rejected() {
        let w = World::zeros(64, 1);
        let dir = std::env::temp_dir().join(format!("m0_snapc_{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let p = dir.join("s.bin");
        write_snapshot(&p, &w, 184, 0).unwrap();
        let mut b = std::fs::read(&p).unwrap();
        let last = b.len() - 1;
        b[last] ^= 0xff;
        std::fs::write(&p, b).unwrap();
        assert!(
            read_snapshot(&p).is_err(),
            "korupsi harus tertolak checksum"
        );
    }

    #[test]
    fn window_roundtrip_size() {
        let states: Vec<_> = (0..5)
            .map(|i| World::from_seed_uniform(128, 4, i))
            .collect();
        let dir = std::env::temp_dir().join(format!("m0_win_{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let p = dir.join("w.bin");
        write_window(&p, &states).unwrap();
        assert_eq!(std::fs::metadata(&p).unwrap().len() as usize, 5 * 8 * 8); // 128 sel k=4 = 8 word
    }

    #[test]
    fn manifest_format() {
        let m = manifest_json(&[
            ("rule_id", "184".into()),
            ("seed", "7".into()),
            ("note", "\"apapun\"".into()),
        ]);
        assert!(m.contains("\"rule_id\": 184"));
        assert!(m.contains("\"note\": \"apapun\""));
        assert!(!m.contains('\r'));
    }
}
