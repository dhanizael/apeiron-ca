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

---

## 003 — M1: K3 PASS — semesta pertama yang tidak kita tanam (2026-09-22)

**Apa:** Pencarian fisika 3 tahap atas keluarga flow (k=2,4): 20.000 kandidat acak
seeded → mutasi re-clip (hill-climbing) → horizon H = 10⁶ langkah. Kriteria K3
dibekukan SEBELUM pencarian (spec §9 amendemen M1).

**Verdict: K3-PASS.** 6.087/20.000 kandidat lolos filter tahap A; 5 juara lolos
horizon penuh — semua k=4 hasil mutasi tahap B:

- **Partikel:** 4.024–4.050 objek hidup di AKHIR horizon, lifetime 100/100
  observasi = bertahan seluruh 10⁶ langkah (definisi: merge/pisasah = mati objek —
  rantai yang tak pernah merge 10⁶ langkah adalah objek persisten sesuai
  definisi beku).
- **Tanpa competitive exclusion:** massa top-3 pola = 2.947–2.978 / 16.384 ≈ 0,18
  (ambang exclusion 0,8); exclusion streak maksimum = 0 — tidak pernah sekali pun.
- **Kontras rezim (kalibrasi):** Rule 184 pada skala sama runtuh ke top-3 = 0,989
  (platoon); juara kita hidup di rezim yang benar-benar berbeda.
- Reproduksi: `python experiments/m1/search.py` (manifest per juara di
  `experiments/m1/result/champ_*/`, tabel hukum = `rule.bin` + rule_fnv).

**Dua bug satuan yang tertangkap disiplin atribusi (berharga):**
1. Run 1: kriteria `lifetime ≥ 500` dalam satuan OBSERVASI (maks 21) — mustahil
   by construction; "hasil negatif" pertama adalah bug kriteria, bukan fisika.
2. Run 2: T_persist skala horizon (5×10⁴ langkah) diterapkan pada probe 2×10⁴
   langkah — mustahil untuk kedua kalinya.
Fix: T_persist dalam langkah fisika, skala per tahap (A: 25% horizon probe;
C: 5% horizon H). Pelajaran metodologi: **kriteria harus terdefinisi mungkin
di skala pengukurannya** — dan hasil negatif wajib diatribusikan sebelum
dipercaya. Keduanya tertangkap dalam hitungan menit karena distribusi penuh
(20.000 baris) dilaporkan, bukan hanya survivors.

**Temuan ilmiah kecil:** 30% kandidat acak keluarga flow lolos konjungsi
partikel+keberagaman di skala probe — ruang ini jauh lebih kaya daripada yang
graveyard (Tierra/Echo/Lenia) sarankan, kemungkinan karena konservasi
by construction + komponen bergantung-state (Adams 2017) yang inheren di F.

**Batas jujur:** "partikel" = definisi operasional beku kita (blob ≤8 sel dari
background mode yang tak pernah merge/pisasah), bukan klaim struktur ala computational mechanics — itu kerja Newton di M3
computational mechanics; H = 10⁶ langkah terukur, bukan keabadian. M2 (replikator)
dan M3 (Newton memulihkan hukum semesta juara) adalah ujian berikutnya.

---

## 004 — M3-percepatan: Newton memulihkan hukum semesta yang tidak ditanam (2026-09-22)

**Apa:** Newton v0 diarahkan ke dua juara M1 (k=4, tabel 4.096 entri, hukum hanya
pegangan kita sebagai rule.bin). Mikro via **aljabar teleskop konservasi**
(dᵢ = vᵢ − newᵢ = fᵢ − fᵢ₋₁ → prefix-sum, konstanta dikunci edge aliran-nol) —
bukan enumerasi.

**Verdict: MICRO-PASS 3/3 + makro PASS.**

- **3a:** tabel pulihan ≡ GT **eksak 4.096/4.096 entri** di KEDUA juara
  (observasi lintas-3-seed; nol ambigu; nol konflik).
- **3b:** tabel pulihan mereproduksi dinamika RELAKSASI (t=20.000) bit-identik —
  hukum yang dipelajari dari transien t=0 memprediksi termal.
- **3c:** counterfactual law shift — dua semesta → dua tabel berbeda, masing-masing
  cocok GT-nya. Hafalan mustahil.
- **Makro:** J(ρ) juara #1 dari sweep --init-cap: tumbuh linier J≈15ρ (rezim bebas)
  lalu **jenuh ~5,9** (onset kemacetan) — diagram fundamental emergen; fit
  piecewise-linear MDL 2 segmen, **hold-out MAE = 0.0** (ε dari lantai derau
  terukur 0,011).
- Reproduksi: `python experiments/m3/recover.py` (butuh hasil M1).

**Cerita metodologi (semua tertangkap gerbang, bukan keberuntungan):**
1. Coverage 4090/4096 dua run berturut — 6 entri langka tak dikunjungi satu
   transien → solusi jujur: observasi lintas-3-seed (hukum sama, transien beda).
2. **Counterfactual gate menangkap bug silsilah M1:** kelima "juara" ternyata
   SATU hukum (tahap B meregenerasi base dari seed, bukan tabel induk). Gerbang
   anti-hafalan menolak — bukti ia bekerja. M1 diperbaiki + diulang; kini ≥2
   hukum berbeda. (Koreksi entri 003: klaim "5 juara" berlaku sebagai ≥1 hukum
   lolos horizon; keragaman lintas-juara baru nyata pasca-fix.)
3. Fit makro pertama gagal karena GRID [0..1] vs data [0.07..0.47] → grid
   dibatasi rentang data train + 10 kap (MDL dengan 5 titik tak sanggup membeli
   segmen kedua — data diperbanyak, bukan kriteria dilonggarkan).

**Makna:** kriteria W2 spec — "Newton memulihkan aturan mikro, diverifikasi eksak
vs source code" — **terpenuhi di semesta yang tidak kita tanam**, dengan
counterfactual. Bandingkan AutomataGPT (82% exact, aturan biner 2D tetap): kita
100% eksak pada 4.096 entri k=4 dengan aturan BERGERAK (juara hasil pencarian).
M4 (loop tertutup + kurva growth-rate lintas rezim) tinggal satu milestone.

**Batas jujur:** pemulihan mikro memanfaatkan struktur keluarga flow (teleskop
konservasi) — keunggulan eksak ini spesifik-keluarga, bukan penginderaan umum;
makro diukur pada satu juara; H tetap 10⁶ langkah.

---

## 005 — M4: kurva growth-rate terukur (K5-PASS) + loop tiga run yang jujur (W3-NULL teratribusi) (2026-09-22)

**K5 — PASS.** model_bits(t) = k × entri teramati diukur pada t ∈ {10³, 10⁴, 10⁶}
untuk TIGA rezim (juara A, juara B, 184-k=1). Pembacaan jujur instrumen:
**ketiga rezim SATURASI** — model Newton mengunci seluruh hukum (4.096 entri /
8 entri) jauh sebelum 10⁶ dan tak bertambah: semesta flow finit adalah
kelas-2-like menurut definisi operasional kita. R1 tetap terbuka — kini DENGAN
alat ukurnya. Kompresi window (zlib) dilaporkan per checkpoint (W4).

**W3 — tiga run, tiga atribusi, satu temuan struktural:**
1. Run 1 (W3-NULL): ΔJ membandingkan seed init BERBEDA — derau seed (±0,27)
   menelan efek mutasi (~0,02). Perbaikan: pasangan seed-sama (semusta
   deterministik → efek mutasi murni, nol derau).
2. Run 2 (W3-NULL, Δ fb = Δ ctrl identik): hanya **14 dari 4.096 entri** punya
   longgar; M=256 dengan pengembalian → kontrol ≈ terarah (himpunan sama).
   Ditambah: J diukur di rezim jenuh (cap 14) — medan aliran diklip kapasitas,
   **J tak peka terhadap mutasi tabel apa pun**.
3. Run 3 (W3-NULL, Δ = 0.0000 eksak): entri longgar yang teramati pada init
   rentang-penuh TAK PERNAH teramati pada dinamika init-cap-6 → mutasi tak
   pernah menembak; kontrol disjoint dari terarah = kosong.

**Temuan struktural (hasil ilmiah sah):** semesta juara berjalan ~100% pada
kapasitas — perilaku makronya ditentukan GEOMETRI KAPASITAS (pola min(c, max−r)),
bukan nilai tabel di bawah cap. Konsekuensi: tuas loop di level nilai tabel
hampir kosong; umpan balik yang berarti harus bertindak pada struktur kapasitas
sendiri (ubah k/topologi/kapasitas-b bergantung-state) — di luar parameter beku
keluarga saat ini. Loop terbangun, berjalan, terukur; benda kerjanya sudah
teridentifikasi persis. W3 dilaporkan NULL-teratribusi — bukan dipoles.

**Reproduksi:** `python experiments/m4/loop.py` + `python experiments/m4/growth.py`.

**Status kontrak:** K1–K5 PASS; W3 null-teratribusi dengan tuas teridentifikasi
(satu-satunya klaim spec yang tetap terbuka — dan kini kita tahu persis MENGAPA
dan DI MANA gagangnya). M2 (replikator) menyusul di luar sesi ini.


---

## 006 — M1v2: hipotesis slack (dari ilham W3-NULL) + koreksi 003 (2026-09-22)

**Koreksi 003 (ditangkap saat merancang v2):** kriteria juara M1 dinilai pada
probe 10⁵ langkah, bukan horizon 10⁶ (run 10⁶ hanya menghasilkan manifest/window).
Klaim "lolos horizon penuh" dikoreksi menjadi "lolos probe 10⁵ + run 10⁶";
M1v2 menilai kriteria LANGSUNG di horizon 10⁶.

**Hipotesis (vektor serang pertama R1):** akar capacity-bound bukan hanya arah
mutasi — generator `random_table` menggambar 0..255 lalu clip ke cap → entri
lahir menempel kapasitas. Jika **slack** (entri F < cap) adalah prasyarat
menjadi-baik, maka arm slack-rich (uniform [0, cap] per entri) harus menunjukkan
pass-rate K3 lebih tinggi daripada arm slack-poor (generator lama) — dan juara
slack-rich memberi loop v2 tuas level-tabel yang nyata.

**Hasil M1v2 (12.000 kandidat, dua lengan):**

- **Hipotesis slack: SUPPORTED.** Pass-rate tahap A: RICH 0,670 vs POOR 0,310
  (2,16×). Penyintas: 4.017/6.000 vs 1.861/6.000.
- **Dan strukturnya hidup-vs-mati di horizon 10⁶:**
  - Juara RICH (slack 61,1%): partikel hidup di akhir horizon, lifetime
    **1000/1000 observasi = seluruh 10⁶ langkah**, exclusion streak = **0**
    (tak pernah sekali pun runtuh).
  - Juara POOR (slack 2,1%): partikel masih ada, lifetime 999/1000 — tetapi
    **exclusion streak = 995/1000**: semestanya RUNTUH ke ≤3 pola dan TIDAK
    BANGUN lagi. Mati oleh competitive exclusion, persis pola pemakaman.
- V1 (kedua lengan lolos horizon) = false, dan sebabnya adalah temuan itu
  sendiri: lengan POOR PUNAH di horizon. Kriteria "kedua lengan" salah rangka —
  asimetri itulah hasilnya.
- **Gagang loop v2 kini ada:** juara RICH slack 61% → intervensi level-tabel
  punya bahan. Kandidat baru: champ RICH k=2 (seed 5700010/11).

**Kalimat penutup hari ini, kini dengan data:** ruangan hampa itu bukan tempat
kontemplasi saja — dia adalah perbedaan antara semesta yang runtuh dan semesta
yang bertahan. Slack = ruang untuk menjadi.
## 007 — W3 round-2: loop v2 di semesta RICH — tuas eksistensial, kebangkitan dari beku (2026-09-23)

**Setup:** loop v2 (`experiments/m4/loop2.py`) pada juara RICH k=2 seed
5700010 (slack 61%, FNV 85eba35fbd113e83 — tak pernah runtuh di horizon 10⁶,
log 006). Per iterasi K=4: Newton mengamati medan aliran pada init_cap=1
(rezim linier) → intervensi terarah +1 pada M=8 longgar tersibuk; kontrol
+1 pada 8 longgar acak disjoint → pasangan seed-sama (ΔJ = J(F′,s) − J(F,s),
nol derau seed). Juga J di cap=3 (atribusi rezim jenuh). Harness mini
deterministik byte-identik; guard `init_cap < 2^k` ditambahkan (kegagalan
run-1 full: caps v1 [6,14] tidak valid untuk k=2 → engine exit 101 — atribusi:
planning, bukan requirement).

**Kontaminasi kalibrasi, didisklosikan:** sebelum kriteria dibekukan, probe
pada seed 1093/1094 menemukan mutasi tunggal dapat MEMBEKUKAN semesta
(J → 0.0000 eksak, amb=0/512 — aliran sungguhan, bukan artefak FM-E).
Seed verdict digeser ke 2201+. Kriteria dibekukan dua-sisi: W3v2a (arah:
mean ΔJ_fb > ΔJ_ctrl, semua ΔJ_fb ≥ 0) dan W3v2b (magnitudo: mean |ΔJ_fb| >
mean |ΔJ_ctrl|).

**Hasil FULL RUN (seed 2201–2205, n=16384, 20.000 langkah):**

- **W3v2a: NULL.** mean ΔJ_fb 0,0616 vs ctrl 0,0636. Arah naive "busiest-slack
  +1 menaikkan J" TERBANTAHKAN — di it0, intervensi terarah Justru MEMBEKUKAN
  semesta: J 0,2486 → 0.0000 eksak.
- **W3v2b: PASS.** mean |Δ| fb 0,186 vs ctrl 0,064 (≈3×): tuas turunan-temuan
  jauh lebih berdampak daripada acak.
- **Temuan sentral — dua mekanisme eksistensial di level tabel:**
  1. **Beku oleh satu entri:** +1 pada entri busiest (mis. idx 12/28/41) →
     semesta berhenti mengalir TOTAL (J=0, 512/512, nol ambiguitas). Beku
     tidak terprediksi dari margin hukum: +60 (margin 2, tetap slack) dan
     +9 (0→1, tetap slack) juga membekukan (probe seed 1093/1094); +20
     (0→1, menyentuh cap) justru +0,25. Keamanan mutasi tak lokal — aljabar
     konservasi mengkopel seluruh tabel.
  2. **Kebangkitan oleh loop:** it1 — Newton mengamati semesta BEKU hasil
     intervensinya sendiri, menemukan 5 entri longgar yang tersisa, +1 pada
     kelimanya → J 0 → 0,3303 (diverifikasi 3 seed segar: 0,3315/0,3366/
     0,3360). it2 melanjutkan 0,3335 → 0,4982.
- **Konvergensi:** kedua cabang (fb & ctrl) menuju atraktor J≈0,50 — sama
  dengan atraktor cocktail-20 (J 0,25→0,50) yang juga MEMBUKA rezim jenuh
  (J cap=3: 0 → 1,49). Intervensi tabel besar membuka dinamika yang tadinya
  terkunci.

**Koreksi framing log 006:** "tuas level-tabel hidup kembali" benar, tetapi
karakternya bukan penyetel halus (fine-tuning) — dia **tuas eksistensial**:
mutasi bit-level tunggal dapat memindahkan semesta antara tiga fase (mengalir,
terdorong, beku), dan pemetaan mutasi→fase TIDAK terbaca dari hukum margin
lokal — hanya dari observasi Newton pada semesta itu sendiri. Ini memperkuat
alasan loop tertutup: keputusan intervensi harus lahir dari pengamatan.

**Status kontrak:** W3 round-2 selesai — NULL pada arah (jujur dilaporkan),
PASS pada magnitudo + dua temuan mekanistik baru (beku-eksak; kebangkitan
terarah dari kebekuan). Loop v2 terbukti punya tuas nyata; pertanyaan berikut
(8): mengapa satu entri membekukan — hipotesis kerja: entri +1 merusak rantai
kunci aliran-nol (referensi FM-E), membunuh kunci konstanta → medan tak
lagi solvable → J=0 terukur padahal partikel masih bergerak. UJI SEBELUM
DIKLAIM: cek particles_final / dinamika beku vs solvable.

**Reproduksi:** `python experiments/m4/loop2.py` (full), `--mini` (harness),
test: `pytest analysis/tests/test_m4_loop2.py`.

**Koreksi pasca-penulisan (hipotesis kerja "beku = FM-E" DITOLAK):** run
verifikasi pada semesta beku (tabel FNV 4f2f83084da03371, seed 4401, 20.000
langkah, init_cap=1): seluruh 512/512 window state IDENTIK — semesta mencapai
fixed point dinamis dan diam total (ρ=0,165; bandingkan F0 pada cap=1 yang
mengalir J=0,25 pada ρ serupa). Jadi J=0 bukan "partikel bergerak tanpa
solusi medan" — partikel benar-benar BERHENTI. Satu entri tabel +1 mendorong
semesta ke fixed point absolut. Pertanyaan (8) direvisi: MEKANISME apa yang
membuat +1 pada entri tertentu menciptakan fixed point global sementara
entri lain tidak — kandidat: rantai kunci flow-nol (FM-E) kini mengunci
MEDAN KE NOL, dan konservasi menyebarkan kebekuan ke seluruh ring. Uji
sebelum klaim.

**Verifikasi independen (sesi review, 2026-09-23):** rerun loop2 → result.json
identik byte-per-byte (determinisme ✓). Angka inti cocok (mean Δ 0,0616/0,0636;
|Δ| 0,186 vs 0,064 ≈ 3×). Klaim beku & kebangkitan kini DIVERIFIKASI dari arsip
bersih: **beku = 0/512 transisi berubah, J=0.0000, ambigu 0** (fixed point
dinamis sungguhan — FM-E resmi ditolak); **kebangkitan 3 seed segar =
0,3372/0,3386/0,3309** (~0,33 ✓). Satu bug infrastruktur ditemukan & diperbaiki
review: dir arsip `u_{seed}_{cap}` dipakai bergantian parent/child fb & ctrl
(last-writer-wins → arsip tak reproducible; pengukuran AMAN — terbukti
result.json identik pasca-fix, kini dir unik per peran). Klaim beku/kebangkitan
semula probe ad-hoc tanpa artefak — kini terarsip + terverifikasi.

---

## 008 — Mekanisme beku terpecahkan: kristal aliran-nol + indikator awal (2026-09-23)

**Pertanyaan 007:** mengapa +1 pada SATU entri membekukan semusta? Dua hipotesis
diuji, DUA-DUANYA DITOLAK, mekanisme sebenarnya terkonfirmasi di level tabel:

1. **Ditolak (hipotesis 007):** "J=0 terukur padahal partikel bergerak" —
   verifikasi 0/512 transisi berubah membuktikan semusta benar-benar STATIS.
2. **Ditolak (hipotesis homogenisasi):** state akhir BUKAN seragam — kristal
   non-uniform {0: 13496, 1: 197, 2: 26, 3: 2665}.
3. **Terkonfirmasi:** 0/16384 edge di kristal memiliki F≠0 — **kristal
   aliran-nol**: konfigurasi statis ter-segregasi (domain 0 dan domain 3) yang
   dinding-dindingnya seluruhnya menempel entri F=0.

**Kronologi:** t=100 mengalir penuh (32/32; nilai antara 1:3986, 2:1418) →
t=300 segregasi berjalan (1:1332, 2:558) → t=1000 nyaris terkunci (1:209, 2:26)
→ t≤3000 beku total. **Indikator awal: massa nilai ANTARA (1 dan 2) menirus** —
sinyal yang bisa Newton amati SEBELUM terkunci. Kebangkitan 007 terjelaskan:
+1 pada entri longgar tersisa melelehkan kristal (menyuntik aliran kembali di
dinding) → 0 → 0,33.

**Desain loop v3 kini tidak buta:** (a) metrik bahaya = laju penirisan nilai
antara; (b) intervensi = pelelehan dinding sebelum terkunci; (c) prediksi
falsifiabel: pelelehan tepat-waktu menjaga J>0 sepanjang horizon; terlambat →
kristal permanen.

**Reproduksi:** tabel beku `u_fb_child_2202_1` vs hidup `u_fb_child_2203_1`
(arsip loop v2, role-unique hasil review); analisis di sesi review.
*(Catatan rekonsiliasi 2026-09-23: entri ini sempat terduplikasi dua kali —
duplikat dengan repro `/tmp` volatile dihapus; versi repro durabel dipertahankan.
Anatomi mandiri loop-v3 pada instans beku berbeda (seed 4401, log 009) mereplikasi
struktur yang sama: {0: 13558, 1: 166, 2: 28, 3: 2632}, 17 entri terrealisasi
seluruhnya F=0 di kedua hukum.)*

---

## 009 — Loop v3: intervensi penghindar-fixed-point — PASS dua sisi (2026-09-23)

*(Penomoran: dibuka pra-run sebagai "008", dinomori ulang 009 saat rekonsiliasi
dengan entri mekanisme sesi review — kriteria TIDAK diubah, urutan peristiwa
terjaga di git. Entri ini mengutip temuan 008: kristal aliran-nol + indikator
awal penirisan nilai antara.)*

**Hipotesis (semula: uji hukum-kandidat pada kosmos mini; setelah kalibrasi
gagal — lihat addendum plan — instrumen berpijar ke kontrafaktual horizon-
pendek skala penuh):** Newton (yang kini tahu hukum semusta — warisan M3)
menguji setiap langkah kandidat pada horizon-pendek skala penuh SEBELUM
berkomitmen, lalu bertindak hanya pada langkah yang modelnya prediksikan
memperbaiki aliran tanpa membekukan. Prediksi: cabang feedback v3 tidak
mengulang bencana it0 v2 (membekukan semusta sendiri, J 0,2486→0) dan
mengungguli kontrol acak kumulatif.

**Kriteria dibekukan SEBELUM run (plan 2026-09-23-loop-v3-freeze-avoidance.md):**
- W3v3a (keselamatan): min_i J_fb_after_i > 0, K=4.
- W3v3b (kinerja): Σ J_fb_after > Σ J_ctrl_after (kumulatif).
- Gerbang instrumen (W2): simulasi mini n=256 harus nol freeze-miss vs
  full-scale pada ≥13 mutasi tunggal berlabel — sebelum verdict dijalankan.
  *(Evaluasi gerbang akhirnya memakai instrumen hasil pivot — addendum plan:
  mini-cosmos ditolak karena basin beku bergantung skala; gerbang tetap
  "nol freeze-miss pada 13 label" dan terpenuhi oleh instrumen final.)*
- Urutan wajib: anatomi fixed point (pertanyaan 8 log 007) → kalibrasi → verdict.
- Seed: anatomi 4401 (warisan 007, disklosikan); label kalibrasi 1093/1094
  (kontaminasi terkontrol — fungsinya kasus berlabel); verdict segar 5501+;
  seed instrumen mini 6600.

**Hasil (FULL RUN, seed 5502–5505, n=16384, 20k langkah — kriteria tak diubah):**

- **W3v3a (keselamatan): PASS.** min J_fb_after = 0,4957 > 0 — feedback tidak
  pernah membekukan semusta (bencana it0 v2 tak terulang).
- **W3v3b (kinerja): PASS.** ΣJ fb 1,9966 > ΣJ ctrl 1,4956.
- **it0 — prediksi kontrafaktunal akurat nyaris eksak:** filter menolak
  21/43 kandidat berbahaya; komit 8 (termasuk **(12,−1)** — loop MENURUNKAN
  entri pembeku v2, dan (20,+1) Δshort +0,274); validasi koktail lolos
  langsung (J_short 0,501) → J_20k sungguhan **0,5010**. Kontrol acak-8
  → BEKU (J→0) — mode gagal v2-fb kini dialami cabang buta.
- **it1–3 — hold rasional:** slack habis (loose=0), seluruh 48 langkah
  sisa (semua −1) tak ada yang positif → loop menahan diri. Kedua cabang
  konvergen ke atraktor keluarga **J≈0,50** (fb J 3 seed segar:
  0,4944/0,5018/0,4997; tabel final fb & ctrl setara J-nya).
- **Atribusi jujur kemenangan (dua komponen):** (1) keterampilan model —
  lompatan langsung ke atraktor dengan prediksi tervalidasi; (2) kontrol
  sial (koktail buta mengenai kombinasi pembeku — varian). Pembanding
  bersih lintas-versi: v3-fb 1,9966 vs v2-fb 1,3258 (+0,67) dengan risiko
  beku nol vs bencana nyata.
- **Temuan baru — instrumen kontrafaktunal LOKAL-REZIM:** hukum v3 unggul
  di cap=1 tetapi J(cap=3) = 0,0000 (koktail v2: 1,49) — kontrafaktual
  hanya mengevaluasi rezim intervensi; konsekuensi rezim lain tak terlihat.
  Perluasan pelajaran run-2 v2 ("amati rezim yang kau intervensi") →
  "simulasi rezim yang kau putuskan; rezim lain tetap gelap".
- **Jawaban pertanyaan (8) level state:** beku = KONDENSASI menjadi parkiran
  sel-3 eternal; 82,8% nol + 16,1% tiga; waktu beku langkah (1250, 2500];
  seluruh 17 entri terrealisasi bernilai F=0 di KEDUA hukum (kristal =
  fixed point umum pra-ada; dinamika termutasi jatuh ke dalamnya). Struktur
  fundamental: r = max_cell ⟹ cap = 0 ⟹ F ≡ 0 pada SEMUA tabel flow —
  sel penuh absolut abadi (tak bisa pernah menerima). Peta kausal level
  hukum (mutasi mana memicu kondensasi) tetap terbuka.
- **Batas tercapai:** dengan kelas intervensi ±1 pada tabel dan slack
  habis, J≈0,50 adalah optimum lokal — loop menahan diri saat tak ada
  langkah positif (bukan berhenti diam-diam; keputusan hold TERSIMPAN di
  trajectory). R1 tetap terbuka, konsisten dengan K5 (saturasi).

**Reproduksi:** `python experiments/m4/frozen_anatomy.py`;
`python experiments/m4/calibrate_freeze.py --instrument short`;
`python experiments/m4/loop3.py`; test `pytest analysis/tests/`.

**Status kontrak:** W3v3a + W3v3b PASS; instrumen tervalidasi (freeze_miss
0/13); batas instrumen (lokal-rezim, validasi tunggal-per-kandidat, koktail
divalidasi terpisah) didisklosikan. Loop v3 menutup singkat: aman, terarah,
dan jujur tentang batasnya.

---

## 010 — Loop v4: kontrafaktual multi-rezim + pelelehan dinding tepat-waktu (DIBUKA; kriteria dibekukan pra-run 2026-09-23)

**Dua pilar (plan 2026-09-23-loop-v4-multi-regime.md):**
1. **Part A — loop multi-rezim:** memperbaiki batas lokal-rezim v3 (hukum v3:
   cap1 0,50 / cap3 0,00). Kontrafaktual tiap kandidat di KEDUA rezim;
   keselamatan = tanpa kolaps di salah satu; skor = Δ(J_c1+J_c3); validasi
   koktail dua-rezim + fallback. Mulai dari hukum final v3 (kontinuitas loop).
2. **Part B — sweep jendela kritis:** mengadili prediksi falsifiabel 008
   ("pelelehan tepat-waktu menjaga J>0; terlambat → kristal permanen") —
   catatan: anekdot v2-it1 (melelehkan kristal penuh) bertentangan dengan
   separuh kedua prediksi; sweep T ∈ {250..20000} dengan leleh dinding
   terarah vs acak (paired via S_T) memutuskan dengan data. Butuh fitur
   engine baru `--init-state` (identitas kelanjutan-prefiks bit-identik
   sebagai verifikasi kekuatan).

**Kriteria dibekukan SEBELUM run:**
- W3v4a (perbaikan multi-rezim): hukum fb final J_cap1 > 0 DAN J_cap3 > 0.
- W3v4b (kinerja multi-rezim): Σ(J_c1+J_c3)_fb > Σ(J_c1+J_c3)_ctrl, K=4.
- Perubahan kontrol didisklosikan pra-run: v3-induk tak punya loose-observed
  (kontrol v2-style degenerate) → kontrol v4 = 8 acak uniform dari pool
  legal yang sama dengan feedback (kelas aksi sama, tanpa kontrafaktual).
- Seed: verdict Part A segar 8802+; Part B seed 4401 (silsilah anatomi,
  disklosikan); instrumen warisan 009 (r_min=0,3, horizon-pendek 5000).

**Hasil: (menyusul — diisi setelah run, tanpa pengeditan kriteria).**
**Hasil Part B — sweep jendela kritis (`experiments/m4/sweep_melt.py`, hukum
pembeku FNV 4f2f83084da03371, seed 4401, T ∈ {250..20000}):**

- **Prediksi 008 REFUTED dua arah, diganti hukum yang lebih tajam:**
  1. "Terlambat → kristal permanen" SALAH — leleh pada kristal penuh
     (T=20000) memulihkan PENUH: **2 entri dinding ([61,52]) cukup** untuk
     J 0 → 0,4955 (atraktor keluarga), identik di seluruh T ≥ 500. Kristal
     adalah struktur yang DAPAT DIBUANG di umur berapa pun — obatnya
     tersimpan dalam tanda tangan dindingnya sendiri (realized ∩ cap>0,
     terurut frekuensi).
  2. "Pelelehan tepat-waktu menjaga J>0" TERBALIK — intervensi paling
     berbahaya justru di MID-FLOW: T=250 (masih mengalir, mid=3029),
     leleh busiest-8 → BEKU (J=0); leleh acak-8 di T yang sama → selamat
     (J=0,2486). Entri tersebus di dunia mengalir = kelas pembeku (replikasi
     bencana v2-it0); dinding baru menjadi obat setelah massa terkonsentrasi.
  - Baseline tanpa-leleh (T=3000): J=0,0000 ✓ sanity harness.
  - Kronologi nilai antara (indikator 008) terkonfirmasi lebih halus:
    3029 (T=250) → 1125 (500) → 294 (1000) → 194 (2000+) — beku total ±2000.
  - Hukum struktural tambahan: dinding = entri realized dengan c>0 —
    (2,0,2) realized tetapi c=0 ⟹ cap=0 ⟹ bukan dinding (sel kosong tak
    bisa memancar).

**Hasil Part A — FULL RUN loop v4 (seed 8802–8805, dua rezim, dari hukum
final v3 — kontinuitas loop):**

- **W3v4a (perbaikan multi-rezim): PASS.** Hukum fb final: **cap1 0,4984
  (dipertahankan) DAN cap3 1,0233** — rezim mati warisan v3 DIHIDUPKAN.
- **W3v4b (kinerja multi-rezim): PASS.** ΣJ fb 5,0232 > ctrl 2,0070
  (per rezim: fb cap1 2,000 / cap3 3,023; ctrl cap1 1,489 / cap3 0,518).
- **it0 — penemuan-ulang independen:** hanya 2 kandidat ber-skor positif:
  (52,+1) dan (61,+1) — TEPAT dua dinding kristal dari Part B. Kontrafaktual
  dua-rezim menemukan resep leleh tanpa diberi tahu. cap3: 0 → 0,3766.
- it1 → 0,8472 (rej=5 — guard dua-rezim menolak pembunuh-cap1); it2 komit
  koktail ber-skor gabungan −0,059 (aturan komit mensyaratkan safety, bukan
  skor gabungan positif — **catatan kebijakan** untuk loop berikut: wajibkan
  skor koktail > 0); it3 → **1,0233**.
- Kontrol acak-dari-pool: cap3 nyaris selalu 0 (sekali beruntung 0,5183,
  hilang lagi); cap1 beku di it3 (J→0) — varians aksi buta (pelajaran 009
  berulang). Atribusi dua komponen dilaporkan: keahlian model (perbaikan
  cap3 terarah) + sialnya kontrol.
- **Ketahanan:** cap1 di 3 seed segar 0,4900/0,4994/0,5051 ✓. cap3: J tak
  terukur di seed segar (FM-E — seluruh 512 pasangan ambigu, tak ada edge
  aliran-nol; instrumen J terbatas di rezim padat mengalir) → verifikasi
  via mobilitas: **2/6 seed segar mengalir** (+ seed verdict mengalir =
  3/7) — pulihnya cap3 NYATA tetapi instance-bergantung: rezim padat
  bersifat bistable di bawah hukum baru (mengalir / kristal tergantung
  kondisi awal). Batas terbuka berikutnya.

**Pelajaran lingkungan (durable):** kuota disk (bukan disk penuh) — arsip
window.bin (1,6G, regenerable-deterministik) kini di-gitignore penuh;
"panic" engine 9903 = write_snapshot kena kuota, bukan bug dinamika.

**Reproduksi:** `python experiments/m4/sweep_melt.py`;
`python experiments/m4/loop4.py` (hasil: `result_loop4.json` — penamaan
per-loop dimulai kali ini setelah v4 sempat menimpa result.json v3;
keduanya utuh di git). Test: `pytest analysis/tests/` (55) +
`cargo test` (80).

**Status kontrak:** W3v4a + W3v4b PASS; Part B mengadili 008 dengan data;
batas baru didisklosikan (bistability cap3; FM-E di rezim padat; kebijakan
skor-koktail). Loop kini: aman (v3), melihat dua rezim (v4), dan tahu
cara melelehkan kristal — untuk selanjutnya: loop v5 (kandidat: kebijakan
skor-koktail + multi-seed robustness sebagai kriteria, menuju hukum yang
sehat di kedua rezim pada SEMUA instans), M2 replikator, MAP publish.

---

## 011 — Loop v5: robustness multi-seed sebagai kriteria (DIBUKA; 2026-09-23)

**Misi:** atasi bistability cap3 (log 010: pulihan instance-bergantung, 2/6
seed segar) — hukum sehat di KEDUA rezim pada sebanyak mungkin instans.
Upgrade kelas kriteria: dari level-instans (v2–v4) ke LAJU (distribusional);
upgrade kebijakan: skor koktail gabungan wajib > 0 (koreksi kelemahan v4);
kontrafaktual multi-seed (cap3 dinilai dari 3 seed via mobilitas — J tak
terpercaya di rezim padat, FM-E).

**Kriteria dibekukan (aturannya SEKARANG; instantiasinya dari baseline,
sebelum verdict, disklosikan):**
- W3v5a: hukum fb final, 7 seed verdict segar: cap1 mengalir 7/7 DAN cap3
  laju ≥ max(6/7, laju-terbaik-baseline) DAN laju cap3 > laju v4-final
  (protokol sama).
- W3v5b: Σ_i (J_cap1 + rate_cap3)_fb > Σ_i (...)_ctrl, K=4.
- Gerbang instrumen: horizon-pendek 5000 harus menyetujui 20000 pada
  baseline 4 hukum; gagal → eskalasi terdokumentasi.
- Kebijakan komit baru: koktail wajib lolos keselamatan DUA rezim + skor
  gabungan > 0.
- Seed: baseline 55001–55007; verdict 11002+; anti-kuota: window dihapus
  segera pasca-pengukuran.

**Hasil: (menyusul — tanpa pengeditan kriteria).**

**Baseline lanskap (dieksekusi; instantiasi threshold — sesuai aturan
pre-frozen plan):** 4 hukum × 7 seed (55001–55007) × 2 rezim × {5000, 20000}:
F0 cap1 7/7 / cap3 **0/7**; cocktail20 cap1 7/7 / cap3 **7/7** (mob 0,99);
v3-final cap1 7/7 / cap3 **0/7**; v4-final cap1 7/7 / cap3 **6/7** (20k).
**Gerbang instrumen: cap1 lolos (5000≡20000 semua hukum); cap3 GAGAL —
v4-final 7/7@5000 tapi 6/7@20000: ada kristalisasi LAMBAT (blind spot
horizon-pendek — menjelaskan mengapa komit v4 yang valid-5000 menghasilkan
hukum bistable). Eskalasi: metrik health cap3 v5 diukur di horizon penuh
20000 (mobilitas murah — tanpa derive_field); cap1 tetap 5000.**
**Instantiasi W3v5a: cap1 7/7 DAN cap3 7/7 pada blok verdict 11011–11017**
(threshold = max(6/7, terbaik-baseline 7/7) = 7/7; > laju v4-final 6/7 ✓).
Catatan jujur: laju v4-final peka blok-seed (6/7 di 55001-blok vs 2/5 di
9901-blok kemarin; satu seed kemarin ternyata tak terukur karena kuota) —
sample kecil pada rezim bistable; karena itu kriteria laju + blok baru.
