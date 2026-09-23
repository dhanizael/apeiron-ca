# Plan — Loop v4: kontrafaktual multi-rezim + pelelehan dinding tepat-waktu

Tanggal: 2026-09-23. Log riset: 010 (dibuka pra-run, kriteria dibekukan).
Branch: `loop-v4` → merge main. Doktrin: GeniusMind + meta-quality Tier 3. TDD ketat.

## Latar (mengapa v4)

Log 009: loop v3 aman & terarah (W3v3a+b PASS) tetapi instrumennya LOKAL-REZIM —
hukum hasil v3 unggul di cap=1 tetapi J(cap=3)=0 (rezim padat mati; koktail v2:
1,49). Log 008 (sesi review): mekanisme beku = kristal aliran-nol; indikator
awal = penirisan massa nilai antara; prediksi falsifiabel: "pelelehan tepat-
waktu menjaga J>0; terlambat → kristal permanen" — BELUM diuji (dan anekdot
v2-it1 justru melelehkan kristal penuh → kontradiksi tersisa yang wajib
diselesaikan data). Next tercatat: v4 = multi-rezim + pelelehan tepat-waktu.

## Kontrak keberhasilan (beku sebelum eksekusi)

Requirement wajib (W):
- W1 (engine): flag `--init-state <path>` — mulai run dari snapshot final.bin
  (read_snapshot; validasi n & k cocok; mengesampingkan --seed/--uniform/
  --init-cap; manifest "init_source": "snapshot"). Verifikasi kekuatan:
  IDENTITAS KELANJUTAN-PREFIKS bit-identik — final(run A: seed s, T₁) lalu
  (run B: init-state final-A, T₂) ≡ final(run C: seed s, T₁+T₂), hukum sama.
- W2 (Part B — sweep jendela kritis): hukum pembeku v2-it0 (FNV
  4f2f83084da03371, seed 4401 — silsilah anatomi, disklosikan). Grid
  T ∈ {250, 500, 1000, 2000, 3000, 5000, 10000, 20000}: beku T langkah →
  S_T → leleh = +1 pada M dinding teramati tersebar (entri realized ∩
  cap>0, terbanyak; M menyesuaikan ukuran set) vs kontrol +1 pada M dinding
  acak disjoint (paired via S_T sama) → lanjut 20.000 langkah dari S_T
  (--init-state, hukum lelehan) → recovery = J_akhir > 0 dan tak statis.
  Baseline tanpa-leleh (T=3000, hukum tetap) wajib J=0 (sanity harness).
  Kronologi massa nilai antara (1&2) di S_T tiap T tercatat (indikator 008).
  Prediksi 008 diadili jujur: ada/tidaknya jendela kritis.
- W3 (Part A — loop multi-rezim): mulai dari hukum final loop v3
  (rekonstruksi F0 + komitmen v3; assert FNV vs result.json v3). Per iterasi
  (K=4, seed 8802+): observasi induk (binding stats cap1 + J kedua rezim);
  pool = langkah legal tabel ±1; kontrafaktual TIAP kandidat di KEDUA rezim
  (horizon-pendek 5000, window 512, r_min=0,3 — instrumen terkalibrasi 009);
  keselamatan = tanpa kolaps di salah satu rezim (ratio diukur hanya bila
  parent rezim itu > 0); skor = Δ(J_c1 + J_c3); komit top-8 positif +
  validasi koktail dua-rezim + fallback 8/4/2/1 (hold bila semua gagal);
  kontrol = 8 acak uniform dari pool legal yang SAMA (kelas aksi sama, tanpa
  kontrafaktual; perubahan dari v2/v3 yang loose-observed — didisklosikan:
  loose-observed kosong di induk v3 → kontrol v2-style degenerate), disjoint
  dari terarah; ΔJ pasangan-seed-sama 20k di kedua rezim.
- W4 (kriteria verdict, dibekukan SEKARANG):
  - W3v4a (perbaikan multi-rezim): hukum fb final J_cap1 > 0 DAN J_cap3 > 0.
  - W3v4b (kinerja multi-rezim): Σ_i (J_c1+J_c3)_fb > Σ_i (J_c1+J_c3)_ctrl.
  Kegagalan = hasil sah, dilaporkan jujur dengan atribusi (termasuk komponen:
  keahlian model vs sialnya kontrol; per-regime sums dilaporkan terpisah).
- W5: mini harness deterministik byte-identik; guard init_cap < 2^k; suite
  hijau penuh (Rust + Python).

Preferensi: file baru `experiments/m4/{sweep_melt,loop4}.py`; loop3 tidak
diubah (diimpor). Instrumen kontrafaktual = warisan 009 (short-horizon
full-scale + detektor kolaps) diperluas ke dua rezim — TIDAK dikalibrasi
ulang penuh (warisan validasi 009; batas didisklosikan: validasi kalibrasi
adalah pada rezim cap1; cap3 memakai predikat sama).

Batas eksternal: parameter beku keluarga tak diubah; intervensi ±1 nilai
tabel; horizon pengukuran 20k; single-thread.

## Kriteria penyelesaian (bivalen)

- K1: test Rust --init-state (identitas prefiks + penolakan mismatch) hijau.
- K2: sweep Part B selesai — kurva recovery(T) + kronologi mid-value +
  adjudikasi prediksi 008, terarsip + ter-commit.
- K3: loop4 mini hijau deterministik; FULL RUN selesai; verdict W3v4a/b
  bivalen + audit per iterasi.
- K4: log 010 jujur; now.md + memory; merge main; suite hijau.

## Out of scope

- Peta kausal level-hukum mutasi→kondensasi (tetap terbuka).
- Klaim OEE; M2; MAP publish; kalibrasi penuh instrumen di rezim cap3.

## Pre-mortem (teratas + tandingan)

1. Tidak ada koktail ≤8 yang menghidupkan cap3 tanpa membunuh cap1 → hold
   berulang → W3v4a FAIL jujur (atribusi: trade-off nyata di kelas ±1;
   budget 32 komitmen 4 iterasi mungkin kurang — laporkan, jangan perpanjang
   kriteria diam-diam).
2. Skor multi-rezim didominasi cap3 (rentang 0-1,5 vs cap1 ≤0,5) — memang
   misi perbaikan; cap1 boleh turun non-kolap (dilaporkan per rezim).
3. Bug --init-state → identitas prefiks menangkapnya SEBELUM sweep; kegagalan
   = dinding tooling, diperbaiki di tempat (bukan dipeleskan).
4. Lelehan sukses lalu re-kristalisasi (J_akhir=0 walau sempat mengalir) —
   metrik recovery pakai keadaan akhir (≡ "J>0 sepanjang horizon" 008);
   recovery transien tak terlihat — didisklosikan.
5. Kontrol acak-dari-pool bisa sangat buruk (termasuk −1 destruktif) →
   W3v4b menang "murahan" — komponen dilaporkan terpisah (jumlah per rezim,
   event beku kontrol) seperti pelajaran 009.

## Eksekusi

Engine --init-state (TDD) → Part B sweep (murah, dulu — memvalidasi fitur
engine sekaligus mengadili 008) → Part A loop4 (TDD mini → FULL RUN) →
log 010 + now.md + memory + merge. Commit per checkpoint.
