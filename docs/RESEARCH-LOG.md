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
