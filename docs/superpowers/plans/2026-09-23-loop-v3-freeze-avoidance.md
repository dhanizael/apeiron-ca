# Plan — Loop v3: intervensi penghindar-fixed-point (W3 round-3)

Tanggal: 2026-09-23. Log riset: 009 (dibuka pra-run sebagai "008"; dinomori
ulang saat rekonsiliasi dengan entri 008 sesi review — mekanisme kristal;
kriteria tidak diubah, didisklosikan di log 009).
Branch: `loop-v3` → merge main. Doktrin: GeniusMind + meta-quality Tier 3. TDD ketat.

## Latar (mengapa v3, dan urutan ilmiahnya)

Log 007: tuas level-tabel bersifat EKSISTENSIAL — satu mutasi +1 dapat membekukan
semesta (fixed point dinamis sungguhan, 0/512 window berubah), dan loop v2
menghidupkan kembali semesta beku hasil intevensinya sendiri (0→0,33, stabil
3 seed). Keamanan mutasi TAK-LOKAL (margin hukum gagal memprediksi). Pertanyaan
terbuka (8): mekanisme fixed point oleh +1 tunggal. Next yang disepakati:
loop v3 = intervensi penghindar-fixed-point.

Urutan yang dibekukan (ilmiah, bukan langsung lari):
1. **Anatomi fixed point dulu** (jawab 8 pada level state): karakterisasi
   struktur keadaan beku — histogram nilai sel, entri terrealisasi + verifikasi
   semua F=0 (lock set), waktu beku via binary search final-state.
2. **Kalibrasi instrumen counterfactual**: kekuatan baru loop v3 = Newton
   menguji hukum-kandidat pada kosmos mini sebelum berkomitmen (model-based
   control; kelanjutan natural M3 — Newton TAHU hukumnya). Mini (n=256) harus
   memprediksi verdict full-scale (n=16384) pada 13 mutasi tunggal berlabel;
   GATE: nol freeze-miss (mini bilang aman, full membeku). Gagal → eskalasi n
   mini (representasi/protokol, murah), kalibrasi ulang, disklosikan.
3. **Loop v3 verdict** dengan kriteria yang dibekukan di bawah.

## Kontrak keberhasilan (beku sebelum eksekusi)

Requirement wajib (W):
- W1: Anatomi fixed point dieksekusi dan dilaporkan SEBELUM verdict v3
  (hasil: JSON anatomi + interval waktu-beku; invarian "semua entri
  terrealisasi di keadaan beku bernilai F=0 pada hukum beku" diverifikasi —
  pelanggaran = kegagalan keras pengukuran).
- W2: Kalibrasi mini-vs-full pada ≥13 mutasi tunggal berlabel (freeze/drop/
  raise/flat), confusion matrix + jumlah freeze-miss dilaporkan; gate nol
  freeze-miss dipenuhi (atau eskalasi terdokumentasi) SEBELUM verdict.
- W3: loop3.py per iterasi (K=4): kandidat = semua langkah legal pada tabel
  (+1 jika table[e]<cap(e); −1 jika table[e]>0 — mutasi dua arah, pelajaran
  M1v2); Newton mengevaluasi SETIAP kandidat via simulasi kosmos mini segar
  (n=256, seed instrumen 6600, dipasangkan dengan J_mini induk); REJECT
  kandidat yang mini-beku (J_mini=0); komit top-8 ber-skor mini-positif
  (aturan hold: jika tak ada kandidat positif → tidak berbuat apa-apa,
  dilaporkan); kontrol = 8 longgar-acak disjoint TANPA filter (null: tanpa
  kekuatan counterfactual); ukur ΔJ pasangan-seed-sama di semesta penuh
  (n=16384, 20k langkah, init_cap=1) + j_by_cap[3] atribusi. Deterministik.
- W4: Kriteria verdict DIBEKUKAN sekarang, sebelum full run:
  - **W3v3a (keselamatan):** min_i J_fb_after_i > 0 untuk semua iterasi —
    cabang feedback tidak pernah membekukan semesta sendiri.
  - **W3v3b (kinerja):** Σ_i J_fb_after_i > Σ_i J_ctrl_after_i (kumulatif
    K=4) — seleksi ber-model mengalahkan aksi acak tanpa model.
  Keduanya dilaporkan apa adanya; PASS total ⟺ keduanya PASS. Kegagalan
  salah satu = hasil sah, dilaporkan jujur dengan atribusi, TIDAK dipoles.
- W5: Seed didisklosikan: anatomi seed 4401 (warisan verifikasi 007);
  label kalibrasi full-scale pakai seed 1093/1094 (sudah terkontaminasi
  probe — justru itu fungsinya: kasus berlabel); verdict v3 seed segar
  5501+; seed instrumen mini 6600 beku. Guard init_cap < 2^k tetap.
- W6: Mini harness deterministik byte-identik; test suite hijau penuh.

Preferensi (bukan requirement): harness Python + engine Rust sama; file baru
`experiments/m4/{frozen_anatomy,calibrate_freeze,loop3}.py`; loop2.py tidak
diubah (dipakai ulang via import: binding_stats, select_control, mutate).

Instrumen: engine release 650k; tabel champ RICH `rule_H_RICH_5700010.bin`
(FNV 85eba35fbd113e83); Python .venv; single-thread.

Batas eksternal: parameter beku keluarga flow tak diubah; intervensi hanya
nilai tabel ±1 per entri; observasi & intervensi di rezim linier init_cap=1
(sama dengan v2); horizon pengukuran 20.000 langkah.

## Kriteria penyelesaian (bivalen)

- K1: test_frozen_anatomy + test_freeze_calibration + test_m4_loop3 hijau
  (RED→GREEN), determinisme byte-identik.
- K2: anatomi JSON + kalibrasi JSON ter-commit; gate W2 terpenuhi.
- K3: FULL RUN v3 selesai, verdict W3v3a/W3v3b bivalen + audit per iterasi.
- K4: log 008 ditutup jujur; now.md + memory; merge main; suite hijau.

## Out of scope

- Kausal penuh "mengapa mutasi X memilih kristal Y" (anatomi memberi bukti
  level state; rantai kausal dinamika tetap terbuka — dilaporkan demikian).
- Klaim open-endedness; M2; MAP publish.

## Pre-mortem (kegagalan teratas + tandingan)

1. Mini tak memprediksi full (freeze-miss) → eskalasi n mini (512/1024),
   kalibrasi ulang; jika tetap gagal → instrumen counterfactual dinyatakan
   belum layak, verdict v3 DITUNDA (bukan dipaksakan) — dan itu temuan sah
   (finite-size scaling of the freeze attractor).
2. Kedua cabang lompat ke atraktor 0,5 sejak it0 → W3v3b seri/gagal →
   laporkan jujur "keselamatan tanpa keunggulan di atraktor"; baseline
   historis v2 (fb v2: ΣJ=1,33 vs ctrl 1,99) tetap dipublikasikan sebagai
   pembanding.
3. Semua kandidat di-reject filter → hold (Δ=0) → laporkan; konservatisme
   instrumen adalah temuan, bukan kegagalan senyap.
4. J_mini=0 tapi tak statis (artefak FM-E di skala mini) → predikat beku
   mini = J==0 DAN window mini statis (murah, eksak).

## Eksekusi

Task 1 anatomi → Task 2 kalibrasi (GATE) → Task 3 loop3 TDD → Task 4 FULL
RUN → Task 5 log/now/memory/merge. Commit per checkpoint di branch loop-v3.

## Addendum kalibrasi (2026-09-23, dieksekusi sesuai pre-mortem #1 — didisklosikan)

Evolusi instrumen counterfactual, tiga langkah berbasis data:
1. mini n=256/2000-langkah: GATE-FAIL (4 freeze-miss).
2. mini n=1024/500k-langkah/3-seed: GATE-FAIL (2 freeze-miss, e=9/41) —
   temuan ilmiah: BASIN ATRAKTOR BEKU BERGANTUNG SKALA (e=9/41 metastabil
   mengalir J≈0,09 di n=1024 walau beku di n=16384). Mengecilkan semesta
   mengubah fisika → instrumen mini-cosmos DITOLAK.
3. PIVOT (Langkah 4): kontrafaktual horizon-pendek SKALA PENUH (n=16384,
   5000 langkah, seed = seed label — prefeks deterministik run 20k) +
   detektor kolaps (J/J_parent < 0,3; kondensasi berlangsung bertahap —
   J≈0,05 di 5k untuk kasus yang nol eksak di 20k; threshold dari set
   kalibrasi, didisklosikan). Hasil: GATE-PASS — freeze_miss=0/13,
   agreement 0,85; sisa ketidaksesuaian hanya kelas jinak (flat↔raise).
Batas validasi: instrumen tervalidasi pada MUTASI TUNGGAL; kandidat koktail
divalidasi terpisah oleh loop (uji koktail + fallback prefix — lihat loop3).
