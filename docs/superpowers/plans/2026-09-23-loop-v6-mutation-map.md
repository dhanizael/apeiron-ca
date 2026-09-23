# Plan — Loop v6: peta respons mutasi lengkap + lolos-langit-langit atau buktikan-langit-langit

Tanggal: 2026-09-23. Log riset: 012 (dibuka pra-run). Branch: `loop-v6` → merge main.
Doktrin: GeniusMind + meta-quality Tier 3. TDD ketat.

## Latar (mengapa v6)

Log 011: hukum v5-final sehat 7/7+7/7 di dua blok — bistability tuntas. Dua
hal terbuka yang tercatat: (1) celah kebijakan dedup-entri (it0 v5 mengommit
(25,+1)+(25,−1) saling menetralkan); (2) peta kausal mutasi→kondensasi
(terbuka sejak 007/008). Risiko "terlena": loop series bisa terjebak poles
kebijakan. v6 mengambil jalan paling ambisius yang jujur: **KARTOGRAFI
LENGKAP** — ukur SELURUH lingkungan respons hukum incumben (setiap langkah
legal ±1, kedua rezim, horizon penuh) sehingga pertanyaan "apakah atraktor
0,50 bisa dilampaui kelas ±1" terjawab secara EKSHAUSTIF: lolos, atau
langit-langit terbukti. Keduanya hasil; keduanya cahaya (batas kelas
intervensi = peta menuju kelas berikutnya untuk R1).

## Kontrak keberhasilan (beku sebelum eksekusi)

Requirement wajib (W):
- W1 (peta): `mutation_map.py` — hukum incumben = v5-final (rekonstruksi
  F0 + komitmen v3+v4+v5; assert FNV ee65c75045c607ad). SEMUA langkah legal
  ±1: cap1 J (20k, window 512, seed 12001) + cap3 health 3-seed (12001–03,
  20k, mobilitas window 64) + baris induk protokol sama. Anti-kuota: window
  dihapus segera. Artefak: mutation_map.json.
- W2 (kausal — HIPOTESIS PRE-REGISTERED SEKARANG, sebelum peta dijalankan;
  bivalen pada data lengkap):
  - H-A (sibuk = berbahaya): ΔJ_cap1(e,+1) berkorelasi NEGATIF dengan
    frekuensi realized e di atraktor cap1 induk; SUPPORTED bila |ρ| ≥ 0,3
    dengan tanda negatif (Pearson pada pasangan (freq, ΔJ) entri terrealisasi).
  - H-B (outflow-3 menyembuhkan cap3): rata-rata Δmob_cap3 untuk entri c=3
    melebihi entri c≤2 sebesar ≥ 0,05 → SUPPORTED.
  - H-C (antisimetri): mean |Δ(e,+1) + Δ(e,−1)| pada cap1 < 0,02 → linier
    (SIMETRIS); else NONLINIER. (Keduanya hasil.)
- W3 (verdict loop v6): K=2 iterasi map-guided (re-map tiap iterasi): seleksi
  top-8 dengan DEDUP (satu arah terbaik per entri — skor gabungan
  ΔJ_cap1 + Δmob_cap3); validasi koktail (cap1-safe warisan + cap3 3/3 +
  skor gabungan > 0); fallback 8/4/2/1; hold. Kontrol: 8 acak dari pool
  (diskontinu dengan terarah). Verdict W3v6a (SELF-CALIBRATING — tanpa
  threshold absolut arbitrer): hukum final 7/7+7/7 pada blok verdict segar
  12011–12017 DAN (mean J_cap1 > mean J_cap1 incumben di blok yang sama
  + 0,01 ATAU mean mob_cap3 > incumben + 0,02). GAGAL = "langit-langit
  kelas ±1 terbukti" (dilaporkan sebagai hasil utama, bukan kegagalan
  senyap). W3v6b: aditivitas koktail — |terukur gabungan − Σ prediksi
  single| untuk koktail terkomit + distribusi non-linieritas dari peta;
  dilaporkan (metrik, tak lolos-gagal).
- W4: mini deterministik byte-identik; suite hijau; anti-kuota.

Preferensi: `experiments/m4/{mutation_map,loop6}.py`; loop5 tak diubah
(fungsi eval diimpor). Seed: peta 12001–03; verdict 12011–17; trajectory
12031+.

Batas eksternal: parameter beku keluarga tak diubah; intervensi ±1; horizon
20k; single-thread.

## Kriteria penyelesaian (bivalen)

- K1: test dedup + map-row hijau; peta lengkap ter-commit.
- K2: H-A/B/C diadili bivalen pada data lengkap (hasil apa pun = data).
- K3: FULL RUN v6; W3v6a bivalen (lolos ATAU langit-langit terbukti dengan
  bukti peta + validasi koktail); W3v6b aditivitas dilaporkan.
- K4: log 012 jujur; now.md + memory; merge main; suite hijau.

## Out of scope

- Teori umum kondensasi lintas-hukum (peta = enumerasi untuk incumben;
  teori tetap terbuka); M2; MAP; klaim OEE.

## Pre-mortem (teratas + tandingan)

1. Peta menunjukkan tak ada langkah yang mengungguli incumben → W3v6a FAIL
   = langit-langit terbukti; wajib disertai bukti (peta lengkap + koktail
   terbaik tetap ≤ incumben) — jangan ulang-ulang sampai hijau.
2. Non-linieritas tinggi (H-C NONLINIER) → prediksi koktail dari peta tak
   andal → validasi koktail (simulasi) jadi penentu; peta tetap layak
   sebagai heuristik + atlas.
3. Re-map it1 menunjukkan lanskap bergeser drastis (hukum baru, peta lama
   basi) → itu temuan (response landscape law-specific); re-map sudah
   dirancang.
4. Kuota disk → anti-kuota window-cleanup (warisan 011).
5. Korelasi H-A tercemar oleh J yang stabil di atraktor (variasi antar-seed
   ±0,008 ≈ sinyal) → gunakan seed sama untuk semua langkah (paired-by-
   seed) sehingga Δ dihitung terhadap induk seed-sama; laporkan noise floor.

## Eksekusi

mutation_map (TDD ringan → run 8 menit) → analisis H-A/B/C → loop6 (TDD
mini → FULL RUN) → log 012 + now + memory + merge. Commit per checkpoint.
