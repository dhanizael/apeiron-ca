# Plan — Loop v7: regulasi densitas (kelas intervensi ruang-keadaan, ronde pertama)

Tanggal: 2026-09-23. Log riset: 013 (dibuka pra-run). Branch: `loop-v7` → merge main.
Doktrin: GeniusMind + meta-quality Tier 3. TDD ketat.

## Latar (mengapa v7)

Log 012 membuktikan batas aliran-bebas (J = massa/n) — intervensi TABEL tak
pernah melampaui densitas. Kelas baru: intervensi RUANG-KEADAAN — loop
menyuntik massa (edit state via --init-state; hukum utuh) sehingga J naik
mengikuti densitas, dengan pertanyaan ilmiah non-trivial: **di mana & bagaimana
menyuntik agar aliran bebas bertahan** (kemacetan/kristal mengintai: 3-cells
parkir; 2-cells hanya mengalir penuh di konfigurasi tertentu). Ronde pertama
kelas baru → deliverable: peta respons densitas hidup (kurva J(ρ) yang
digambar tangan loop sendiri) + ambang kemacetan + kapabilitas kontrol.

## Kontrak keberhasilan (beku sebelum eksekusi)

Requirement wajib (W):
- W1 (instrumen): `state_surgery.py` — penulis snapshot Python (mirror
  format v2 + fnv1a-over-LE-words, TIDAK boleh ditolak checksum engine —
  validasi: engine --init-state membaca hasil tulisan kita dan fnv_final
  manifest konsisten) + operasi suntik massa (+1 pada sel terpilih, batas
  kebijakan ≤ 2; akuntansi massa sebelum/sesudah wajib) + kebijakan suntik:
  uniform-cap2 (acak buta) vs lane-targeted (turunan temuan: naikkan sel-1
  yang kiri-nya 1 → konfigurasi (1,2,·) emisi-penuh — dari struktur entri
  terrealisasi 012).
- W2 (peta densitas): `density_map.py` — kurva J(ρ) hidup: level suntik
  Δ ∈ {10%, 25%, 50%, 100%} × massa × 2 kebijakan, pada hukum v6-final
  (rekonstruksi assert FNV), tiap titik 20k langkah: J, mobilitas, massa/n,
  rasio J/(massa/n) [identitas aliran-bebas], himpunan entri terrealisasi
  (ekspansi?), kemunculan sel-3 (kebijakan cap-2 wajib nol). Ambang jenuh:
  level pertama dengan rasio < 0,98.
- W3 (verdict): W3v7a (kontrol densitas): kebijakan terbaik loop mencapai
  **J ≥ 0,60** (≥ +0,1 di atas 0,499) dengan identitas aliran-bebas
  (J/(massa/n) ∈ [0,98; 1,02]) dan tanpa kristalisasi (window tak statis),
  pada **7/7 instans segar** (blok 13011–13017, kebijakan sama diterapkan
  per instans). W3v7b: ambang jenuh kurva dilaporkan bivalen (ditemukan /
  tak tercapai dalam grid). Kontrol kebijakan: uniform (buta) dilaporkan
  berdampingan — disiplin directed-vs-blind seri.
- W4: mini deterministik byte-identik; anti-kuota; suite hijau.

Preferensi: `experiments/m4/{state_surgery,density_map,loop7}.py`; loop6 tak
diubah. Seed: peta 13001–03; verdict 13011–17. Batas: hukum TIDAK diubah
(intervensi state murni); horizon 20k; single-thread.

## Kriteria penyelesaian (bivalen)

- K1: test snapshot-writer (engine menerbaca) + kebijakan suntik hijau.
- K2: peta densitas ter-commit (kurva + ambang).
- K3: FULL RUN v7; W3v7a bivalen; W3v7b dilaporkan.
- K4: log 013 jujur; now.md + memory; merge main; suite hijau.

## Out of scope

- Struktur-kapasitas (k-lift dengan hukum penerimaan) = ronde berikut;
  M2; MAP; klaim OEE (R1 jujur: k=2 terbatas ruang model — dilaporkan).

## Pre-mortem (teratas + tandingan)

1. Semua suntikan memicu kemacetan (2-cells tak mengalir bebas di densitas
   tinggi) → W3v7a FAIL = ambang aliran-bebas densitas ditemukan LEBIH RENDAH
   dari dugaan — hasil sah (kurva adalah deliverable-nya), atribusi via peta.
2. Snapshot writer checksum salah → engine menolak → TDD menangkap sebelum
   eksperimen; mirror fnv diuji lintas-implementasi (baca file engine-buat,
   tulis ulang, bandingkan).
3. Sel-3 muncul dari dinamika (bukan suntik) di level tinggi → tercatat
   (indikasi kristalisasi) — bagian temuan, bukan kegagalan senyap.
4. Lane-targeted tak lebih baik dari uniform → laporkan jujur (temuan
   kebijakan); kriteria tetap di kebijakan TERBAIK.
5. Kuota → window-cleanup (warisan 011).

## Eksekusi

state_surgery (TDD) → density_map (kurva) → loop7 (TDD mini → FULL RUN) →
log 013 + now + memory + merge. Commit per checkpoint.
