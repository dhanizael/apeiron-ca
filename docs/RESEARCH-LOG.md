# RESEARCH-LOG — 0and1

Log riset berurutan proyek **Semesta + Newton**. Aturan penulisan: setiap entri
berisi angka, klaim yang dibatasi bukti, dan perintah reproduksi. Bahasa klaim
mengikuti batas kejujuran spec §3 (cakupan sumber yang dibuka — bukan systematic
review, dan itu dinyatakan).

---

## 001 — LM-1: angka pertama (2026-09-22)

**Apa:** Loop end-to-end hidup pertama — engine semesta (Rust, Rule 184, 1D ring)
→ Newton v0 (Python) → oracle eksak → meter T1. Milestone LM0, hasil LM-1.

**Angka:**
- **Mikro:** rule table dipulihkan **eksa** — kandidat unik dari 256 aturan ECA
  (1 dari 256), terverifikasi bit-identical atas seluruh window transien.
- **Makro:** fundamental diagram **J(ρ) = piecewise-linear 2 segmen**
  (J ≈ ρ untuk ρ rendah, J ≈ 1−ρ di atasnya; breakpoint terfit 0.55 pada grid 0.05);
  MAE held-out **7.58e-05** < eps 0.02, dinilai terhadap ground truth **terukur**
  dari run panjang (bukan rumus yang diberi tahu).
- **Meter T1:** 8 bit (rule table) + 136 bit (model makro) = **144 bit** pada
  t = 20000. Kurva yang di M4 nanti harus tumbuh persisten agar semusta
  disebut open-ended.
- **K1 dua arah:** re-run bit-identical lintas proses DAN lintas implementasi
  (engine Rust ≡ CA referensi Python; n = 4096, 2000 langkah).
- **Bench informasional:** 2.67e10 cell-update/detik single-thread (Rule 184;
  bukan klaim K2 — benchmark formal milik M0).

**Temuan eksperimental (kelas kegagalan F1):** window pasca-relaksasi menyisakan
fase ter-order (mobil dalam platoon) yang miskin keragaman neighborhood — dari
situ 64 aturan tetap konsisten dan Newton jujur menolak memilih. Protokol mikro
dipindah ke **window transien** (init acak, keragaman maksimal) → kandidat runtuh
ke 1. Pelajaran yang layak dihafal: *transien acak adalah teman Newton; kesetaraan
termal adalah musuhnya.* Pengetahuan ini tentang kapan penemuan hukum BISA bekerja.

**Klaim kebaruan (dibatasi bukti):** dalam prior-art yang kami telaah (~60 sumber
primer, 4 agen), kami tidak menemukan instrumen yang memverifikasi penemuan hukum
secara eksak terhadap **ground truth yang bergerak**, ataupun yang menutup umpan
balik temuan → substrat. Bukan systematic review.

**Batas jujur:** Rule 184 adalah hukum yang sengaja ditanam — LM-1 membuktikan
instrumennya bekerja end-to-end, bukan open-endedness. Taruhan sesungguhnya (R1,
R3) menunggu di M1–M4.

**Reproduksi:**
```
cargo build --release          # di engine/
.venv/bin/pytest analysis -q   # 27 test, termasuk K1 lintas implementasi
.venv/bin/python experiments/lm1/run_lm1.py
```
Manifest per-run: `experiments/lm1/result/` (seed 7, n 4096, 20000 langkah).

---

## 002 — M0: K2, angka throughput formal (2026-09-22)

**Apa:** Engine NCCA tergeneralisasi (keluarga flow, k∈{1,2,4,8}) + benchmark formal
sesuai protokol K2 yang dibekukan di spec §5.

**Angka (protokol beku: k=4, n=2²⁷, 100 langkah, median 5 run setelah 1 warmup,
jalur LUT generik, 20 thread, x86_64):**

- **median_cell_updates_per_detik = 2.31e9** (min 2.24e9, max 2.45e9)
- Target K2 ≥ 1e9 → **PASS** (2.3× di atas target)
- table_fnv `b1f9b6ea85176634` (tabel acak seeded 20260922); fnv_final `634cbc0425e53c88`
- Reproduksi: `engine/target/release/engine bench --protocol k2`

**Jalan menuju angka itu (berharga untuk metodologi):**
1. Angka jujur pertama: **5.39e8** — di bawah target. Diagnosis: hot loop melakukan
   6 pembagian integer (modulo ring) per sel × 134 juta sel × 100 langkah.
2. Restrukturisasi: per worker, lane dimaterialisasi sekali ke buffer lokal
   (satu modulo di inisialisasi, lanjut dengan conditional wrap) → nol pembagian
   di hot loop → **2.31e9** (4.3×), dengan `fnv_final` identik bit-per-bit.
3. Pelajaran: pengukuran formal mengubah "kira-kira cukup cepat" menjadi
   target yang bisa digagalkan — dan gagal dulu di muka monitor. Itu fungsinya.

**Kontrak M0 yang terpenuhi:**
- **K1′:** bit-identical lintas thread (1≡4; sweep 2,3,7,16) DAN lintas
  implementasi (Rust ≡ Python, k=1/2/4).
- **Regresi LM-1:** engine M0 mereproduksi fnv_final LM-1 ter-commit persis
  (20000 langkah) — generalisasi tidak menyentuh semantika k=1.
- Konservasi by construction teruji untuk k=1,2,4,8 (100 langkah × tabel acak).
- Snapshot v2 + manifest v2 (rule.bin + rule_fnv) + window budget; v1 tetap terbaca.
- Test suite: Rust 56 + Python 30, hijau.

**Batas jujur:** angka K2 adalah untuk jalur generik LUT pada k=4 di satu node
(i9-12900H, 20 thread); bukan klaim atas semua k/aturan, dan bukan jalur
bit-parallel khusus (Rule 184 legacy: 2.6e10 cell-updates/detik, konteks saja).

**Reproduksi:**
```
cd engine && cargo build --release && ./target/release/engine bench --protocol k2
cargo test && ../.venv/bin/pytest ../analysis -q
```
