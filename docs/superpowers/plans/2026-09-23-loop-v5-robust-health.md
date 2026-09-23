# Plan — Loop v5: robustness multi-seed sebagai kriteria + kebijakan skor-koktail

Tanggal: 2026-09-23. Log riset: 011 (dibuka pra-run). Branch: `loop-v5` → merge main.
Doktrin: GeniusMind + meta-quality Tier 3. TDD ketat.

## Latar (mengapa v5)

Log 010: loop v4 memperbaiki rezim mati v3 (cap3 0→1,0233 pada instans verdict)
tetapi pulih cap3 bersifat instance-bergantung — **bistability cap3** (2/6 seed
segar mengalir; 3/7 termasuk verdict). Kriteria v2–v4 semuanya level-instans;
v5 menaikkan kelas kriteria: **laju kesehatan** (distribusional). Dua upgrade
tercatat: (1) kebijakan komit — skor koktail gabungan WAJIB > 0 (v4 it2 pernah
mengommit −0,059); (2) kontrafaktual multi-seed — keputusan diambil dari laju
kesehatan, bukan satu instans yang bisa beruntung.

## Kontrak keberhasilan (beku sebelum eksekusi)

Requirement wajib (W):
- W1 (baseline lanskap — gerbang + instantiasi): 4 hukum known {F0, cocktail20,
  v3-final, v4-final} × 7 seed segar (blok 55001–55007, tak tersentuh) × 2
  rezim (cap1, cap3) × 2 horizon {5000, 20000} → kesehatan per (hukum, rezim,
  seed): cap1 = J terukur > 0 / mobilitas > 0 bila FM-E; cap3 = mobilitas > 0
  (J dilaporkan bila terukur — FM-E jujur). Fungsi gerbang: horizon 5000 harus
  menyetujui 20000 pada SELURUH baseline (ketidakcocokan → eskalasi horizon
  10000, kalibrasi ulang, disklosikan). Fungsi kedua: lanskap kesehatan
  (adakah hukum known yang cap3-nya 7/7? seberapa buruk v4-final?).
- W2 (aturan threshold — DIBEKUKAN SEKARANG, sebelum baseline dijalankan;
  hanya INSTANSIASinya yang datang dari data, disklosikan di log):
  - W3v5a (kesehatan multi-rezim robust): hukum fb final pada 7 seed verdict
    segar (blok 11001+): cap1 mengalir **7/7** DAN cap3 mengalir
    **rate ≥ max(6/7, laju-terbaik-baseline)** DAN laju cap3 **> laju
    v4-final** (diukur protokol sama di baseline).
  - W3v5b (kinerja): Σ_i H_fb > Σ_i H_ctrl dengan H = J_cap1 + rate_cap3
    (3 seed paired per iterasi), K=4.
- W3 (harness loop5): dari hukum final v4 (kontinuitas; assert FNV). Per
  iterasi: pool legal ±1; kontrafaktual kandidat = cap1 (1 seed, J, window 512
  — instrumen warisan) + cap3 (3 seed, mobilitas window 64 — metrik BARU v5);
  filter: cap1-safe (warisan r_min) DAN cap3 3/3 mengalir; rank ΔJ_cap1 +
  Δmean-mobility_cap3; komit top-8 → validasi koktail: cap1-safe DAN cap3 3/3
  DAN **skor gabungan > 0 (kebijakan baru, wajib)** → fallback 8/4/2/1 → hold.
  Kontrol: 8 acak uniform dari pool yang sama (warisan v4), pengukuran penuh
  sama. K=4, seed verdict 11002+.
- W4 (anti-kuota): harness MENGHAPUS window.bin/final.bin segera setelah
  metrik dihitung (pelajaran kuota 010 diinstitusikan).
- W5: mini deterministik byte-identik; suite hijau penuh.

Preferensi: `experiments/m4/{health_landscape,loop5}.py`; loop4 tak diubah.
Mobilitas = ada pasangan state berurutan yang berbeda di window akhir (window
64; "mengalir di ujung horizon"). Definisi kesehatan cap1: J > 0 bila terukur;
bila FM-E (J=None): mobilitas > 0 — dilaporkan mana yang dipakai.

Batas eksternal: parameter beku keluarga tak diubah; intervensi ±1; horizon
verdict 20k; single-thread.

## Kriteria penyelesaian (bivalen)

- K1: test health/mobility + loop5 mini hijau deterministik.
- K2: baseline lanskap ter-commit; gerbang W1 lolos (atau eskalasi
  terdokumentasi); threshold W3v5a terinstantiasi & ditulis di log sebelum
  verdict.
- K3: FULL RUN selesai; verdict W3v5a/b bivalen + audit + verifikasi ketahanan.
- K4: log 011 jujur; now.md + memory; merge main; suite hijau.

## Out of scope

- Peta kausal mutasi→kondensasi; klaim OEE; M2; MAP.

## Pre-mortem (teratas + tandingan)

1. Tak ada kandidat lolos filter cap3 3/3 → hold berulang → laju tak naik →
   W3v5a FAIL jujur (atribusi: basin kristal cap3 tak terjangkau kelas ±1
   dalam K=4 — laporkan lanskap sebagai bukti).
2. Gerbang horizon gagal (kristalisasi cap3 lebih lambat dari 5000) →
   eskalasi 10000 terdokumentasi sebelum verdict.
3. Filter 3/3 terlalu ketat vs laju baseline (mis. terbaik hanya 5/7) →
   kandidat 3/3 tetap sah (lebih ketat dari kriteria tak masalah); bila
   nol kandidat → lihat (1).
4. cap1 terkorban demi cap3 → guard parent-hidup + kriteria 7/7 cap1
   menahan; pelanggaran = FAIL jujur.
5. Kuota disk → W4 (hapus window segera); monitoring du saat run.

## Eksekusi

Baseline (TDD ringan: fungsi mobilitas/health) → instantiasi threshold di
log → loop5 TDD → FULL RUN → verifikasi 7-seed final → log 011 + now +
memory + merge. Commit per checkpoint.
