# Plan — Loop v8: MIGRASI-K (kelas kapasitas-struktur — phase-wrap lift k=2 → k=4)

Tanggal: 2026-09-23. Log riset: 014 (dibuka pra-run). Branch: `loop-v8` → main.
Doktrin: GeniusMind + meta-quality Tier 3. TDD ketat.

## Latar (mengapa v8)

Log 012: plafon tabel terbukti (J = massa/n). Log 013: pintu ruang-keadaan
terbuka (suntik massa; kristal kembali lewat pintu densitas — sel-3 dinamis).
Sisa tuas struktural (log 005): **ubah struktur kapasitas itu sendiri**. v8 =
migrasi semesta k=2 → k=4: massa & n tetap (J-bound tetap 0,4993), tetapi
ruang nilai meluas 0–3 → 0–15 dan ruang model 64 → 4096 entri. Keabadian
sel-penuh (r=max⟹cap=0, log 009) berubah total: di k=4, sel-3 BUKAN sel
penuh lagi.

## Desain intervensi (dibeiktukan — phase-wrap lift)

- **Hukum** (4096 entri): F_k4[l,c,r] = F_k2[l&3, c&3, r&3] untuk r&3 ≠ 3;
  F_k4[l,c,r] = F_k2[l&3, c&3, 0] untuk r&3 = 3, r < 15 (penerimaan fase-
  bungkus: sel-3 menerima seperti fase-0 — semantik kontinu pada wrap);
  F = 0 pada r = 15 (penuh — struktural). Kapasitas-aman: F_k2(·,·,0) ≤
  min(c&3,3) ≤ min(c,15−r) untuk r ≤ 14 (diverifikasi program).
- **State**: baca snapshot k=2 (attractor 20k) → repack k=4 (nilai sel sama)
  → --init-state (engine validasi n & k).
- **Lengan kontrol**: embedding MURNI (tanpa fase-bungkus: r&3=3 tetap 0) —
  null yang jujur: prediksi aljabar saya = embedding tidak akan pernah
  melebihi 3 (3-cells abadi terbawa); perbedaan receipt vs embedding =
  bukti efek intervensi.

## Kontrak keberhasilan (beku sebelum eksekusi)

- W1 (instrumen): `lift_k.py` — lift hukum (verifikasi: embedding cocok
  F_k2 pada semua r&3≠3; kapasitas-aman semua entri; konservasi by clip) +
  migrasi state (massa eksak sama) + TDD.
- W2 (protokol): 7 instans segar (14001–07): atraktor induk 20k (hukum
  v6-final, cap1) → migrasi → lanjut 20k DI BAWAH HUKUM LIFT — dua lengan
  (phase-wrap vs embedding) per instans, seed-sama (paired). Pengukuran:
  massa (eksak), J, rasio J/(massa/n), statis, max-cell, histogram nilai,
  entri terrealisasi (growth meter: checkpoint 2000 & 20000), jumlah sel-15.
- W3 (kriteria dibekukan):
  - W3v8a (migrasi utuh): lengan phase-wrap 7/7 instans: massa eksak sama,
    TAK STATIS di 20k, J/(massa/n) ≥ 0,90 (klaim keabadian sel-3 dibubarkan
    = aliran bertahan saat strata tinggi terisi; jatuh < 0,90 dilaporkan
    jujur sebagai biaya pendakian).
  - W3v8b (strata baru): lengan phase-wrap ≥ 6/7 instans menunjukkan
    max-cell > 3 DAN entri terrealisasi > 6 pada 20k; lengan kontrol
    embedding dilaporkan berdampingan (prediksi: ≤3 & =6 — kontras = bukti).
- W4: mini deterministik; anti-kuota; suite hijau; FM-E di J k=4 dilaporkan
  (mobilitas = verifikator cadangan, warisan 010).

## Kriteria penyelesaian

K1 test lift hijau; K2 FULL RUN dua lengan; K3 W3v8a/b bivalen + audit;
K4 log 014 + now + memory + merge.

## Out of scope

Teori umum kondensasi; M2; MAP; klaim OEE (pertumbuhan model di sini
digerakkan intervensi — dilaporkan jujur sebagai mini-R1, bukan R1).

## Pre-mortem

1. Pendakian strata membenturkan massa ke 15 (eternal di k=4) → kristal-k4
   baru → J jatuh < 0,90 → W3v8a FAIL jujur; temuan: plafon baru — peta
   menuju desain receipt berikutnya.
2. Pendakian terlalu lambat untuk 20k (max-cell ≤ 3) → W3v8b FAIL jujur
   (basin pendakian lebih lambat dari horizon — laporkan laju).
3. FM-E J k=4 → mobilitas verifikator (warisan 010).
4. Checksum snapshot k=4 salah → TDD cross-impl (warisan 013) menangkap.
5. Kuota → window-cleanup.

## Eksekusi

lift_k TDD → loop8 TDD mini → FULL RUN → audit → log 014 + now + memory +
merge. Commit per checkpoint.
