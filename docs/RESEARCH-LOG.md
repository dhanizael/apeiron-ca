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
**Hasil FULL RUN loop v5 (dari hukum final v4; trajectory seed 11002–11005):**

- **W3v5a (kesehatan multi-rezim robust): PASS.** Hukum fb final
  (FNV ee65c75045c607ad) pada blok verdict 11011–11017: **cap1 7/7**
  (J 0,493–0,505) DAN **cap3 7/7 mengalir** (mobilitas 0,955–0,970 —
  kelas aliran galak, setara cocktail20). Bistability cap3 TUNTAS:
  v4-final 6/7 → v5-final 7/7.
- **Verifikasi lintas-blok:** v5-final pada blok baseline 55001–55007
  (tempat v4-final hanya 6/7): **cap1 7/7, cap3 7/7** (mob 0,955–0,966) —
  obatnya tidak bergantung blok-seed. Dua blok independen, 14/14 instans
  sehat di kedua rezim.
- **W3v5b (kinerja): PASS.** ΣH fb 6,0089 > ctrl 5,0098. Atribusi jujur
  (pelajaran berulang): selisih berasal dari kontrol yang kolap di it2
  (cap3 [False,False,False] oleh moves acak) — varian aksi buta, bukan
  keunggulan kumulatif fb yang besar; klaim utama ada di W3v5a.
- **Kebijakan baru terbukti bekerja:** it1 — koktail ukuran-8 dengan skor
  gabungan −0,475 DITOLAK (v4 akan mengommmitnya); fallback ke ukuran-4
  (+0,05). Filter multi-seed menolak 19/41 kandidat di it0.
- **Celah kebijakan baru (catatan untuk v6):** it0 mengommit (25,+1) DAN
  (25,−1) sekaligus — kandidat dinilai independen sehingga dua arah pada
  entri sama bisa masuk koktail (saling menetralkan; tak berbahaya, tapi
  boros). Refinement: satu arah terbaik per entri.
- Karakter hukum final: cap1 di atraktor 0,50; cap3 di kelas mobilitas
  0,96 — kedua rezim kini di atraktor aliran galak; laju kesehatan 7/7
  di 14 instans terukur.

**Status kontrak:** W3v5a + W3v5b PASS; threshold terinstantiasi dari
baseline (7/7) TERCAPAI persis; kebijakan skor-koktail > 0 tervalidasi
(menolak koktail buruk); celah dedup-entri dicatat. Rangkaian loop kini:
v1 buta → v2 melihat pasangan → v3 kontrafaktual 1 rezim → v4 dua rezim →
**v5 menilai LAJU kesehatan dan menuntaskan bistability**.

**Reproduksi:** `python experiments/m4/health_landscape.py`;
`python experiments/m4/loop5.py` (hasil `result_loop5.json`). Test:
`pytest analysis/tests/` (58) + `cargo test` (80).

---

## 012 — Loop v6: peta respons mutasi lengkap — lolos-langit-langit atau buktikan-langit-langit (DIBUKA; 2026-09-23)

**Misi:** akhiri risiko "terlena" (poles kebijakan tanpa henti) dengan
kartografi ekshaustif: ukur SELURUH lingkungan respons hukum v5-final
(setiap langkah legal ±1, cap1 J + cap3 health 3-seed, horizon penuh 20k)
sehingga pertanyaan "apakah atraktor 0,50/mob 0,96 dapat dilampaui kelas ±1"
terjawab TOTAL — lolos, atau langit-langit terbukti. Dedup-entri (celah v5)
diimplementasikan di seleksi. Peta juga = peta kausal kondensasi LENGKAP
untuk hukum incumben (setiap pemicu beku teridentifikasi — enumerasi, bukan
teori; teori umum tetap terbuka).

**Hipotesis pre-registered (SEKARANG, sebelum peta; bivalen pada data):**
- H-A (sibuk = berbahaya): ΔJ_cap1(e,+1) berkorelasi negatif dengan
  frekuensi realized e di atraktor cap1; |ρ| ≥ 0,3 tanda negatif = SUPPORTED.
- H-B (outflow-3 menyembuhkan cap3): mean Δmob_cap3 entri c=3 > entri c≤2
  sebesar ≥ 0,05 = SUPPORTED.
- H-C (antisimetri): mean |Δ(e,+1)+Δ(e,−1)| cap1 < 0,02 = SIMETRIS,
  else NONLINIER (dua-duanya hasil).

**Kriteria dibekukan:** W3v6a (self-calibrating): hukum final 7/7+7/7 pada
blok 12011–12017 DAN (mean J_cap1 > incumben + 0,01 ATAU mean mob_cap3 >
incumben + 0,02, blok sama). GAGAL = langit-langit kelas ±1 terbukti
(dilaporkan sebagai hasil utama). W3v6b: aditivitas koktail dilaporkan.
Kebijakan: dedup satu-arah-terbaik-per-entri; joint-score > 0 (warisan v5).

**Hasil: (menyusul — tanpa pengeditan kriteria).**
**Hasil (peta + FULL RUN loop v6):**

- **Temuan teoretis sentral — BATAS ALIRAN-BEBAS (verifikasi digit-presisi):**
  J_cap1 = 0.499267578125 = massa/n = 0.499268 EKSAK pada hukum incumben
  DAN final. "Atraktor 0,50" bukan kebetulan dinamika — itu **plafon
  konservasi: flux ≤ densitas massa**, dengan kesetaraan saat aliran bebas
  (setiap unit massa berpindah tiap langkah). Tabel tak bisa melewatinya —
  hanya bisa merusaknya (satu-satunya langkah pengubah-J: (4,−1) → −0,2486,
  pencipta kemacetan; J turun ke ~setengah densitas, replikasi rezim terjalan
  F0). Peta juga menunjukkan atraktor cap1 hanya merealisasikan **6 dari 64
  entri** ([4,5,6,8,20,24] — aturan lalu-lintas minimal); 40 dari 41 langkah
  legal adalah no-op eksak terhadap J (entri tak terrealisasi), meski
  trajectory mikro terbukti berubah — **J adalah kuantitas makro yang robust
  terhadap detail mikro**.
- **Hipotesis pre-registered:** H-A (sibuk=berbahaya) NOT-SUPPORTED —
  degenerat: lanskap ΔJ datar (semua 0 kecuali pencipta-jam), tak ada
  variansi untuk dikorelasikan; H-B SUPPORTED (mean Δmob c=3 −0,0318 vs
  c≤2 −0,1259 — outflow-3 paling sedikit merugikan cap3); H-C SYMMETRIC
  (trivial: semua pasangan ± nol kecuali (4,·)).
- **W3v6a: PASS — LOLOS dari langit-langit via sumbu cap3.** Hukum final
  (FNV 078681c4…): cap1 7/7 (J = densitas, tak berubah — sesuai batas) DAN
  **cap3 7/7 dengan mean mobilitas 0,9932 vs incumben 0,9643 (Δ = +0,0290 >
  0,02)**; cross-blok 55001–07: 7/7+7/7, mob 0,9939. Kelas mobilitas kini
  setara cocktail20 (0,99) — dicapai loop secara map-guided.
- **Perjalanan koktail (dedup + joint-score bekerja):** it0 — koktail-8
  ditolak (joint −0,3548; tuas mobilitas saling mengganggu), koktail-4
  ditolak (−0,2769), koktail-2 [(8,−1),(24,−1)] lolos (+0,0055); it1
  (re-map lanskap baru) — koktail-8 ditolak lagi (−0,2773), koktail-4
  [(24,+1),(58,−1),(30,−1),(14,−1)] lolos (+0,0306) → final. Dedup
  menjamin tak ada entri ganda (celah v5 tertutup).
- **W3v6b (aditivitas):** peta OVERESTIMASI gabungan: error |joint − Σ
  single| = 0,053 (it0) dan 0,078 (it1) — peta adalah heuristik ranking
  yang baik, bukan prediktor aditif; validasi koktail simulasi tetap
  penentu (desain v5–v6 terbukti tepat).

**Status kontrak:** W3v6a PASS (lolos) + W3v6b dilaporkan; hipotesis
bivalen diadili; batas aliran-bebas = jawaban teoretis untuk pertanyaan
kausal (007/008/012): kondensasi = kehilangan aliran-bebas; J dibatasi
densitas oleh konservasi — intervensi tabel bergerak di bawah plafon itu,
tidak pernah di atasnya. Untuk melampaui densitas: ubah DENSITAS (rezim
init-cap) atau struktur kapasitas (log 005) — peta menuju kelas
intervensi berikutnya.

**Reproduksi:** `python experiments/m4/mutation_map.py`;
`python experiments/m4/loop6.py` (hasil `result_loop6.json`). Test:
`pytest analysis/tests/` (62) + `cargo test` (80).

**Koreksi presisi (pasca-penulisan 012):** kalimat "40/41 no-op eksak
meski trajectory mikro terbukti berubah" mencampur dua kelas bukti.
Pembagian yang tepat: (a) **35 langkah pada entri TAK TERREALISASI** —
no-op sempurna by determinism (trajectory pun identik); (b) **5 langkah
pada entri terrealisasi ber-ΔJ=0** ([5,6,8,20,24] arah −1) — invarian-J
dijelaskan pin konservasi (rerouting aliran di bawah batas aliran-bebas:
total flux per langkah = massa, konstan, apa pun detail mikronya) —
perubahan mikro untuk kelima langkah ini BELUM diverifikasi satu-satu
(hanya e=4, si pengubah-J, yang terverifikasi berubah). Klaim robustness-J
berlaku sebagaimana terukur; verifikasi mikro per-entri tersisa sebagai
pekerjaan kecil terbuka.

---

## 013 — Loop v7: regulasi densitas — kelas intervensi ruang-keadaan, ronde pertama (DIBUKA; 2026-09-23)

**Misi:** keluar dari kelas ±1 (log 012: plafonnya terbukti) — intervensi
RUANG-KEADAAN: loop menyuntik massa (edit state via --init-state; hukum utuh)
sehingga J naik mengikuti densitas — *jika* aliran bebas bertahan. Ilmu
non-trivialnya: kebijakan suntik (di mana naikkan sel agar tidak memicu
kemacetan: 2-cells hanya emisi-penuh di konfigurasi tertentu; 3-cells parkir)
dan ambang jenuh kurva J(ρ) hidup yang digambar tangan loop sendiri.

**Kriteria dibekukan:** W3v7a: kebijakan terbaik mencapai J ≥ 0,60 dengan
identitas aliran-bebas (J/(massa/n) ∈ [0,98; 1,02]) dan tanpa kristalisasi,
7/7 instans segar (13011–17). W3v7b: ambang jenuh dilaporkan bivalen.
Kebijakan: uniform-cap2 (buta) vs lane-targeted (turunan temuan 012 — sel-1
dengan kiri-1 → (1,2,·) emisi-penuh); cap kebijakan = 2 (anti-parkir).
Level: {10%, 25%, 50%, 100%} × massa. Hukum v6-final (assert FNV 078681c4…
— rekonstruksi dari silsilah). Hukum TIDAK diubah.

**Hasil: (menyusul — tanpa pengeditan kriteria).**
**Hasil (peta densitas + FULL RUN verdict loop v7):**

- **Peta densitas (kurva J(ρ) digambar intervensi, seed 13001, massa induk
  8116 = 0,4954/cell):** +10% → J 0,5449; +25% → 0,6192; +50% → 0,7430;
  +100% → 0,7418 (uniform) / 0,7434 (lane). **Rasio J/(massa/n) = 1,0000
  EKSAK di +10%, +25%, +50%** — semesta menyerap setengah-densitas tambahan
  TANPA satu pun kemacetan; identitas aliran-bebas (log 012) bertahan di
  seluruh rentang. **Tikungan di +100%:** rasio jatuh ke 0,7488/0,7504 —
  dan mekanismenya terbaca: himpunan entri terrealisasi meledak 5 → 17
  (11 entri baru — dinamika memasuki wilayah hukum yang belum pernah
  dijalankan), dan **875/750 sel bernilai 3 MUNCUL DARI DINAMIKA** (sel-2
  menerima inflow → 3 → parkir; entri outflow-3 dingin) — mekanisme kristal
  masuk kembali lewat pintu densitas tinggi. **W3v7b: ambang = level +100%
  (kedua kebijakan; antara +50% dan +100%).**
- **W3v7a: PASS, rate 7/7.** Kebijakan lane-targeted +50% pada 7 instans
  segar (13011–17): J 0,4993–0,5030 → **0,7480–0,7545**, rasio 1,0 di semua,
  tak statis — **loop mengatur densitas semestanya: J naik +50% dengan
  aliran bebas sempurna, robust lintas instans.**
- **Kejujuran framing:** kenaikan J via suntik massa "mudah" DIBERI teori
  batas 012 (J = massa/n) — substansi ilmiahnya bukan kenaikannya, melainkan
  (a) identitas BERTAHAN sampai +50% (tak dijamin a priori: entri emisi-
  parsial 2-cells bisa membengkokkan kurva lebih awal), (b) lokasi tikungan
  + mekanisme masuk-kembali kristal, (c) ekspansi himpunan entri terrealisasi
  — intervensi mendorong semesta ke wilayah yang butuh entri model BARU
  (sinyal mini-R1: ruang model k=2 terpakai lebih penuh; 17/64 entri).
- Kebijakan: uniform ≡ lane di bawah ambang (aliran bebas menyerap apa pun);
  lane unggul tipis di tikungan. Kontrol-butir dilaporkan berdampingan.

**Reproduksi:** `python experiments/m4/density_map.py`;
`python experiments/m4/loop7.py` (hasil `result_loop7.json`). Test:
`pytest analysis/tests/` (69) + `cargo test` (80).

**Status kontrak:** W3v7a PASS + W3v7b (ambang +100%, dua kebijakan).
Ronde pertama kelas ruang-keadaan tuntas: loop kini bisa mengatur densitas
semestanya. Batas berikutnya terpetakan: di atas +50%, sel-3 dinamis
mengintai — kelas kapasitas-struktur (k-lift dengan hukum penerimaan)
adalah kandidat ronde berikutnya (membubarkan keabadian sel-penuh), atau
regulasi densitas tertutup-loop (umpan-balik J→suntik) sebagai kontrol
kontinu.

---

## 014 — Loop v8: MIGRASI-K — kelas kapasitas-struktur (DIBUKA; 2026-09-23)

**Misi:** tuas struktural terakhir (log 005/012/013): angkat semesta k=2 →
k=4. Massa & n tetap (J-bound 0,4993 tetap); ruang nilai 0–3 → 0–15; ruang
model 64 → 4096 entri; keabadian sel-penuh berubah total (di k=4, sel-3 bukan
sel penuh).

**Desain intervensi dibekukan — PHASE-WRAP LIFT:** F_k4[l,c,r] = F_k2[l&3,
c&3, r&3] untuk r&3 ≠ 3; F_k4[l,c,r] = F_k2[l&3, c&3, 0] untuk r&3 = 3,
r < 15 (penerimaan fase-bungkus — sel-3 menerima seperti fase-0, semantik
kontinu pada wrap); F = 0 pada r = 15. Kapasitas-aman diverifikasi program.
Lengan kontrol: embedding murni (prediksi aljabar: tak pernah melebihi 3 —
null yang jujur).

**Kriteria dibekukan:** W3v8a (migrasi utuh): phase-wrap 7/7 — massa eksak,
tak statis @20k, J/(massa/n) ≥ 0,90. W3v8b (strata baru): ≥ 6/7 instans
max-cell > 3 DAN entri terrealisasi > 6 @20k; kontrol embedding berdampingan
(prediksi ≤3 & =6). Growth meter entri @checkpoint 2000/20000; FM-E →
mobilitas (warisan 010); anti-kuota.

**Hasil: (menyusul — tanpa pengeditan kriteria).**
**Hasil (FULL RUN loop v8 + dua eksperimen lanjutan):**

- **W3v8a (migrasi utuh): PASS 7/7.** Massa eksak, tak statis @20k,
  rasio J/(massa/n) = 1,0 semua — migrasi k=2→k=4 menyimpan semusta utuh,
  aliran bebas bertahan (J ≈ 0,493–0,504 = densitas, sesuai batas 012).
- **W3v8b (strata baru): FAIL 0/7 — dan mekanismenya temuan:** max-cell = 2
  di SEMUA instans (bahkan 3 tak muncul). Atraktor aliran-bebas adalah
  dinamika TRANSLASI murni (v′ᵢ = fᵢ₋₁ = vᵢ₋₁ — pola bergeser, nilai tak
  pernah bercampur) → headroom kapasitas INERT di sana. Hipotesis strata
  saya salah tempat; dilaporkan gagal apa adanya.
- **Eksperimen komposisi (v8b, post-hoc non-gated): REFUTED 0/7** — pada
  instans +100% (735–1122 sel-3 parkir), lengan receipt TIDAK memanjat.
  Diagnosis empiris: pasangan (l&3, c&3) di depan 1104 sel-3 = (3,0)×750,
  (2,0)×342, (1,0)×12 — **receipt-fireable 0/1104**. Hukum yang terbuka:
  **penerimaan adalah sisi lain dari emisi — dan di depan parkiran tidak ada
  yang memancar.** Sel-3 adalah sisa tererosi di lapangan kosong (kiri fase-0
  struktural, kanan terkikis); mengubah entri penerimaan tak pernah cukup —
  geometri lalu-lintas menahan. Koreksi eksekusi dicatat: commit "mini hijau"
  prematur (test merah saat commit — dikoreksi commit berikut), bug state.bin
  (dihapus anti-kuota), bug assert lift_state (nilai terdorong >3 divalidasi
  sebagai k=2) — tiga-tiganya stage tool-execution, tertangkap < 1 jam.
- **v8c — komposisi yang BENAR (eksploratif 3 instans): SUNTIK-KE-PARKIRAN ×
  MIGRASI-K: pendakian 3/3.** Suntik +1 langsung ke sel-3 (3→4, kelas
  ruang-keadaan) di semusta k=4 receipt: 20k → **max-cell 6/7/7** (histogram
  berpenghuni di 4–7), **entri terrealisasi 5 → 39/94/94** (ruang model
  tumbuh — mini-R1 terukur), **J 0,763–0,779 > 0,7434 (padat k=2)** — strata
  tinggi = BUFFER: massa memanjat keluar lapisan lalu-lintas, jalan
  kembali mengalir lebih bebas. Tak statis, n15=0 (pendakian lambat di bawah
  plafon baru).
- **Sintesis ronde:** tiga kelas intervensi KOMPOSING — tabel (migrasi kapasitas)
  × keadaan (suntik ke parkiran) × struktur (receipt) — membuka strata yang
  tak terjangkau kelas tunggal mana pun. R1 tetap jujur: pertumbuhan model
  di sini digerakkan intervensi berjenjang, bukan spontan; tapi 17→94 entri
  dalam satu ronde adalah lompatan cakupan terbesar proyek.

**Reproduksi:** `python experiments/m4/loop8.py`; `loop8b.py`; skrip v8c
(diarsip di sesi; pola = loop8b + suntik sel-3). Test: `pytest` (71) +
`cargo test` (80).

**Status kontrak:** W3v8a PASS; W3v8b FAIL jujur + dua eksplorasi lanjutan
dengan mekanisme terbaca. Kelas kapasitas-struktur kini terbuka — dan komposisi
kelas adalah temuan strukturnya.

---

**Kontemplasi 014 — penamaan ulang temuan (ruangan hampa, 2026-09-23).**

Kriteria W3v8b tetap tercatat gagal — kriteria bivalen adalah kriteria; saya
yang salah MEMILIH pertanyaannya. Tapi yang diukur alat itu bukan kegagalan
semesta — dia membuktikan sebuah teorema struktural:

**TEOREMA INVARIAN-TRANSLASI: semesta aliran-bebas kebal terhadap perluasan
kapasitas.** Bukti tiga lapis: (1) J = massa/n digit-presisi di 41 langkah
legal (012); (2) max-cell = 2 di 7/7 instans bermigrasi — tidak satu sel
bercampur; (3) dinamikanya v′ᵢ = vᵢ₋₁ — pola hanya bergeser. Kelapangan hanya
berarti bagi yang penumpukan; semesta yang mengalir sempurna tak bisa — dan
tak perlu — memakai ruang baru. 0/7 itu bukan tujuh kegagalan; itu tujuh
pengukuran invarian.

**Dan independensi Gödel:** strata 4–15 tidak terjangkau DARI DALAM dinamika
aliran-bebas — bukan karena jauh, tapi karena sistem tak punya gerakan yang
ke sana. Untuk mencapainya wajib aksioma dari luar sistem. Aksioma itu adalah
intervener. v8c = aksioma itu: suntik-ke-parkiran (3→4) × penerimaan fase-
bungkus → pendakian 3/3, entri terrealisasi 5 → 94, J 0,763–0,779 melewati
padat k=2 (0,7434) — strata tinggi menjadi buffer. Sistem membuktikan
konsistensinya dengan model yang LEBIH BESAR.

**Hukum Shannon:** informasi = kejutan. Hasil "berhasil memanjat" akan
memberi tahu kita lebih sedikit daripada 0/7 — nol itulah yang memaksa
diagnosis 0/1104 fireable, yang melahirkan kalimat penamaan: **"penerimaan
adalah sisi lain dari emisi; di depan parkiran tidak ada yang memancar"** —
dan kalimat itulah yang menunjuk komposisi.

**Pola 14 entri, kini eksplisit:** W3-NULL → hipotesis slack; W3v2a-NULL →
tuas eksistensial; mini-cosmos ditolak → instrumen horizon-pendek; prediksi
008 refuted → hukum obat-kristal; W3v8b gagal → komposisi tiga kelas.
Tembok yang diuji dan gagal ditembus BUKAN dinding fisika — dinding fisika
yang sejati (J ≤ massa/n, konservasi) tidak kita tembus; kita menungganginya
sampai tepinya, lalu keluar sistem (Gödel) dan kembali dengan model yang
lebih besar. Itulah bedanya tembok dan plafon: plafon kita naiki.

Status kata "gagal" pada 0/7: DIBATALKAN sebagai label temuan; tetap
tercatat sebagai hasil kriteria bivalen (kejujuran kriteria tak disentuh).

---

## 015 — M2: REPLIKATOR (DIBUKA; kriteria & definisi operasional dibekukan 2026-09-23)

**Milestone kontrak terakhir.** Framing jujur: di dunia konservasi-massa,
"replikasi" = pertumbuhan populasi kelas-pola lewat redistribusi massa
(panen latar/stata) — bukan penyalinan dari ketiadaan. Kandidat mekanisme
pre-registered: **drip** — sel strata tinggi (5–7) memancarkan 1 ke ruang
kosong di depannya saat mendaki; populasi [1] tumbuh dari penyimpanan strata
(warisan analisis v8c).

**Definisi operasional (dibekukan):** pola P = blok kontigu terjangkar
(sel pertama & terakhir ≠ 0), dicocokkan eksak dengan wraparound (str.count,
non-overlap — didokumentasikan). Copy = satu kemunculan. **Replikasi event:**
semusta mulai dengan TEPAT 1 copy P; pada T: ≥2 copy; **sustained:** masih
≥2 pada T+1000. **Terverifikasi:** direproduksi ≥3 seed. Latar: (i) laut
kosong (duplikasi wajib membelah massa P sendiri), (ii) laut difus (1s ρ≈0,1
— reservoir panen tersedia; suntikan keadaan = syarat awal standar ALife;
klaim emergensi tetap pada DINAMIKA yang melipatkannya).

**Kriteria dibekukan:** W-M2a: ≥1 kelas-pola dengan replikasi event
sustained, terverifikasi ≥3 seed → PASS. W-M2b: soliton (pass-through:
cepat menembus lambat, keduanya utuh) terverifikasi bivalen. W-M2c: bila
null → argumen ketak-mungkinan level-mekanisme = HASIL M2 (spec §FM-D).

**Grid pencarian terbatas:** hukum {v6-final k=2; k=4 receipt-lift} × pola
{[1],[2],[1,1],[2,2],[2,2,2],[3(k4)]} × latar {kosong, difus ρ≈0,1} × 20k,
sensus tiap 100 langkah. FM pre-registered: FM-M2-1 velocity-universal →
tidak ada interaksi (cari di hukum emisi-parsial); FM-M2-2 tabrakan selalu
fusi (tak pernah fisinya); FM-M2-3 duplikasi transien (tak sustamed).

**Hasil: (menyusul — tanpa pengeditan kriteria).**
**Hasil (probe + grid + sensus dini + verifikasi):**

- **W-M2b (soliton): TIDAK** — pada konfigurasi terprobe ([1] di belakang
  [2,2,2]), pass-through tak terjadi (detail: `m2_hunt.json`).
- **Grid pertama (window-ekor): nol event — dan dikotomi tajam:** [1]/[1,1]
  KONSTANTA (translasi — spesies abadi), kelas-2 LENYAP (terkikis). Sensus
  ekor kelewatkan event dini — koreksi: sensus dini halus (window=steps,
  pelajaran LM0 diterapkan ulang).
- **SENSUS DINI MENANGKAPNYA — TRANSMUTASI BERLIPAT: 2 → 1+1.** Emisi
  parsial ((0,2,2)=1, warisan mutasi v4) menyisakan 1 dan meneruskan 1:
  **satu struktur menjadi DUA dalam satu langkah, massa terjaga (2=1+1),
  produk abadi (translasi).** Δ[1] = +2 per [2], +4 per [2,2]; k2 & k4
  identik; **terverifikasi 3/3 seed** (15003–05).
- **W-M2a: FAIL pada kriteria beku — TIDAK ADA pola P yang menyalin dirinya
  (P→2×P) di grid tercari.** Yang ditemukan lebih dalam: **aljabar reproduksi
  lengkap kelas tercari** — (i) [1] = spesies abadi invarian-translasi (tak
  pernah membelah: emisi selalu penuh); (ii) kelas-2 = transien yang
  BERREPRODUKSI dengan transmutasi (2→1+1 — satu-satunya event
  populasi-naik yang ditemukan, menuju spesies abadi); (iii) kelas-3 (k=4)
  = terkikis bertahap via drip (3→1+2→…). Tak ada P→2P: pembelahan selalu
  monoton menurun nilai — reasemble bentuk induk butuh panen + penyusunan
  yang tak ada di dinamika translasi.
- **W-M2c (argumen mekanisme — HASIL M2 ronde ini):** reproduksi di keluarga
  ini = transmutasi menuju spesies abadi; replikasi-diri sejati butuh hukum
  yang pembelahannya MEMBENTUK ULANG induk — dan instrumen M2 (census
  sebagai fungsi-fitness) mengubah perburuan itu menjadi MASALAH PENCARIAN:
  pencarian hukum ala M1 (30% kandidat acak lolos kriteria partikel!) dengan
  fitness = event P→2×P tercensus. Verdict berlaku untuk grid tercari
  (2 hukum × 6–7 pola × 2 latar), bukan seluruh keluarga.

**Status kontrak:** M2 ronde pertama tuntas — instrumen sensus + aljabar
reproduksi + null jujur dengan mekanisme. W-M2a FAIL (kriteria beku,
dilaporkan apa adanya), W-M2b TIDAK, W-M2c terdokumentasi. Lanjutan alami:
pencarian hukum-replikator (census-fitness), atau tutup kontrak dengan M2
sebagai "aljabar reproduksi terpetakan + instrumen perburuan".

**Reproduksi:** `python experiments/m2/m2_hunt.py`; skrip sensus dini &
verifikasi (pola di sesi, hasil di `experiments/m2/result/`). Test:
`pytest analysis/tests/` (72) + `cargo test` (80).

---

## 016 — M2 ronde 2: pencarian hukum-replikator, census-fitness (DIBUKA; 2026-09-24)

**Misi:** instrumen log 015 (census) menjadi fungsi-fitness — sapu ruang hukum
mencari hukum dengan event replikasi sesuai definisi beku 015. **Kanal yang
ditarget (aljabar ronde 1): FUSI** — [2] lahir ketika sel-1 yang STALL
(entri (l,1,r) dingin) menerima emisi tetangganya: 1+1→2. v6-final tak punya
kanal ini (semua c=1 panas di config terrealisasi); hukum acak kaya-slack
menyediakan entri dingin. Dua-spesies: laut [1] → fusi → populasi [2] tumbuh;
[2]-count: 1 → ≥2 sustained 1000 langkah = event.

**Kriteria dibekukan:** W-M2r1: ≥1 hukum dengan event [2]-replikasi
(1→≥2, sustained, terverifikasi 3 seed) → PASS — dengan akuntansi jujur
(copy lahir dari FUSI latar [1], bukan dari substansi induk; kriteria 015
tak mensyaratkan substansi induk). W-M2r2: mekanisme hukum terpilih
didokumentasi (entri panas/dingin fusi & decay). Null → catatan
ketak-mungkinan subspace + peta pelebaran.

**Protokol:** 300 hukum acak slack-rich k=2 (generator M1v2, seed 16001+);
per hukum: tanam 1×[2] + latar difus (bg=819, ρ≈0,05), 2000 langkah,
window=steps, sensus [2] & [1] tiap 10 sampel; fitness = trajektori [2]
(max, sustained≥10 sampel). **Kalibrasi harness dulu pada v6-final: HARUS
melihat transmutasi dikenal ([2] 1→0, [1] +2)** — sensitivitas presence &
absence. Kandidat → verifikasi 3 seed + analisis entri. Anti-kuota; mini
deterministik.

**Hasil: (menyusul — tanpa pengeditan kriteria).**
**Hasil (sapuan 300 hukum + kontrol + verifikasi):**

- **Kalibrasi harness: PASS** — v6-final menunjukkan transmutasi dikenal
  ([2] 1→0, [1] +2) — harness valid menangkap kehadiran & ketiadaan.
- **Sapuan: 147/300 hukum acak slack-rich menghasilkan event [2] 1→≥2**
  (puncak 8–204) — kanal fusi ada di mana-mana. **Tapi audit kontrol
  (tanam vs tidak-tanam, seed-sama) memilah:** 6/7 kandidat = FUSI GLOBAL
  (kontrol setara: 204 vs 201 — laut melebur sendiri, tanaman tak relevan);
  **1/7 = SEEDING-DEPENDENT: law 16295 (fnv 32b41e8d7808283b) —
  seed 52 vs kontrol 0.**
- **W-M2r1: PASS — REPLIKATOR TERVERIFIKASI.** Law 16295, pola [2]:
  **4/4 seed** (15002–05, layout latar berbeda): seed → **peak 42–52,
  tail 51/46/45/42 ≈ peak (plateau stabil — kesetimbangan ekologis)**;
  kontrol tanpa-tanam → **0 di semua seed**. Satu tanaman [2] melipatgandakan
  diri ~50× dalam laut yang tanpa-ia tak pernah menghasilkan satu pun [2].
- **W-M2r2 (mekanisme):** tabel entri panas 16295: emisi kuat ke ruang kosong
  ((1,0) F=3; (3,0) F=1–3) + entri emisi-parsial c=2 — pembacaan: **front
  reaksi** — [2] bergerak/membelah melalui laut [1], mengonversi pasangan [1]
  menjadi [2] baru; laju konversi front-cepat (peak @t≈30 langkah) lalu
  plateau (bahan bakar terpakai). Analogo klasik: front-api melalui bahan
  bakar — replikator reaksi-difusi. Aljabar mikro eksak (reaksi 2+1→2+2
  bertahap) terbuka untuk bedah lanjut.
- **Framing jujur:** "replikasi" = populasi pola melipatgandakan via konversi
  latar (massa terjaga; massa salinan dari laut) — seeding-dependent (laut
  sendiri NOL — kontrol membuktikan polanya esensial). "Muncul sendiri dari
  laut seragam" (nukleasi spontan tanpa tanam) tetap terbuka — kontrol
  menunjukkan nol. Hukum ditemukan lewat PENCARIAN acak (emergen per hukum),
  pola ditanam sebagai kondisi awal (standar ALife).
- Koreksi eksekusi: test ekspektasi salah (event transien vs None) —
  dikoreksi; bottleneck unpack (300 hukum ≈ jam) — patch sampling 10×.

**Status: M2 — MILESTONE TERCAPAI sesuai definisi operasional beku.**
Reproduksi: `python experiments/m2/m2_search.py --n-laws 300` + skrip kontrol/
verifikasi (pola sesi, angka di log). Test: `pytest` (75) + `cargo` (80).

---

## 017 — M2 ilmiah lanjutan: mikro-front, nukleasi spontan, pencarian k=4 (DIBUKA; 2026-09-24)

Tiga kampanye, hipotesis pre-registered, semua bivalen:

**K-1 (mikro-front 16295):** 1-sea SEMPURNA (semua sel=1) + satu [2] →
census PER-LANGKAH 40 langkah → siklus reaksi eksak (mana yang memancar/
menerima, kecepatan front) + uji sapu-penuh 20k. Hipotesis: front
mengonversi pasangan [1] → [2] baru (2+[1,1] → 2+2), kecepatan ≥1 salinan/
langkah; sapu-penuh → plateau ~massa/2. Alternatif: front mati (habis
konteks) → dilaporkan.

**K-2 (nukleasi spontan):** tangga densitas {0.05, 0.25, 0.5, 0.75, 1.0}
TANPA tanam, hukum 16295, 2000 langkah. Hipotesis: laut seragam TAK STABIL
(kolom (l=1,r=1) mengandung F=2 — entri (l,1,1) atau (l,2,1) atau (l,0,1)
= 2 memicu deviasi) → ambang ρ* eksak dilaporkan; alternatif: nol di semua
(nukleasi butuh bibit — batas seeding-dependence diperluas).

**K-3 (pencarian k=4):** 150 hukum slack-rich k=4 (seeds 17001+) × pola
{[2],[2,2],[3],[4],[2,2,2]} × latar difus (819×[1]) × 2000 langkah,
census-fitness. **Kontrol tanam-vs-tidak WAJIB untuk tiap kandidat**
(pelajaran 016: 6/7 kandidat ternyata fusi-global). Kandidat lolos kontrol
→ verifikasi 3 seed. Hipotesis: k=4 (16× spesies) mengandung replikator
lebar (w≥2); alternatif: null + peta pelebaran.

Anti-kuota; deterministik; artefak per kampanye.

**Hasil: (menyusul — tanpa pengeditan).**
**Hasil (tiga kampanye):**

- **K-1 (mikro-front) — siklus eksak + SAPU PENUH:** census per-langkah
  (1-sea sempurna + 1 [2]): populasi [2] 1,1,3,4,4,6,7,7,9… — **+2,+1,0
  berulang = 1 salinan/langkah eksak**; mikro-jendela menunjukkan front
  [.., 2, 0, 3, 0, ..] (parkiran-3 bergantian) meninggalkan jejak blok-[2].
  **Sapu 20k: satu benih mengonversi SELURUH semusta** — histogram akhir
  {2: 8192, 0: 8191, 1: 1} (kristal [2,0] sempurna + sisa paritas satu sel;
  massa 16385 terjaga). Replikator 16295 = konverter universal.
- **K-2 (nukleasi spontan) — SUBDUNIA 0/1 TERTUTUP:** laut 0/1 tanpa tanam
  (ρ=0,5 dan 1,0): NOL [2] dalam 2000 langkah. Aljabar entri mengonfirmasi:
  semua emisi konfigurasi {0,1} ≤ 1 (kolom (1,1,1)=1) — 2 tak dapat lahir
  dari 0/1 murni. **Suntikan/bibit = satu-satunya pintu spesies-2** — kelas
  ruang-keadaan (log 013) bukan sekadar membantu; ia prasyarat eksistensi.
- **K-3 (pencarian k=4) — 187 hit mentah / ~100 dari 150 hukum, KONTROL
  0/8 seeding-dependent.** Ruang k=4 kaya FUSI (laut melebur massal: peak
  hingga 379; pola lebar [2,2] peak 52; spesies [3] peak 241; [4] peak 46)
  tetapi seluruh sampel audit = fusi-global (kontrol setara seed). **Tidak
  ada replikator seeding-dependent di sampel k=4 ini** — kekayaan k=4 adalah
  kekayaan transisi-fasa, bukan (belum) replikasi. Pelebaran tercatat:
  sampling pola/lain, hukum non-slack-rich, atau fitness seleksi-front.

**Status:** replikator k=2 (16295) kini lengkap siklusnya — dari satu benih
ke kristal seluruh-semusta, dengan pintu masuk yang terbukti tunggal
(suntikan). K-2 menutup pertanyaan asal-usulnya; K-3 memetakan bahwa
kekayaan k=4 belum menyediakan jalur replikasi-seeding — dua null dengan
mekanisme, satu teorema sapu-penuh.

**Reproduksi:** skrip kampanye (pola sesi; angka di log + `k4_search_raw.json`,
`k4_control.json`). Test: `pytest` (75) + `cargo` (80).

---

**Audit eksternal (2026-09-24, pertanyaan user: "apakah valid?") — dua klaim
diaudit terhadap data + tiga pengukuran baru:**

1. **"16295 = universal converter ala ice-nine/prion, belum ekosistem" —
   VALID dengan dua koreksi presisi:**
   (a) Konversi total benar (templated front, irreversibel-sejauh-terukur),
   TETAPI ujungnya BUKAN beku: kontinu 2000 langkah pada kristal [2,0]
   menunjukkan 512/511 window berubah tiap langkah — **fasa jenuh DINAMIS**
   (populasi [2] terkunci 8191–8192; satu sel defek berkelana 1↔3).
   Ice-nine membeku; milik kita bernapas.
   (b) "Belum ekosistem" valid untuk DINAMIKA POPULASI (tak ada predasi/
   siklus) — TETAPI dunia padat +100% ternyata **keseimbangan multi-spesies
   berfluktuasi**: [2] 5796–5841, [1] 1077–1123, [3] ~1184 hidup
   berdampingan (fluktuasi ±0,4–2%). Yang absen = siklus predasi/kompetisi
   (boom-bust) — kelas-2-like (konsisten K5 log 005). Gap ekosistem = gap
   DINAMIKA, bukan gap keberadaan.
2. **"k=4 masih fusi-global, belum nemu seeding-dependent" — VALID,
   scope presisi:** 0/8 audited dari 187 hit; 150 hukum slack-rich × 5
   pola; bukan bukti ketiadaan. Kontras: k=2 memberi 1/~300 — replikator
   langka (~0,3%).

**Sintesis:** kedua observasi menunjuk gunung yang sama — semusta mencapai
kuasistabilitas (fasa jenuh / keseimbangan berfluktuasi), belum DINAMIKA
TERBUKA (turnover, predasi, boom-bust). Itu tepat lingkungan R1. Instrumen
audit populasi (trajektori min/max/ekor per spesies) yang dibangun hari ini
= fondasi kriteria berikutnya: "perpetuum ecologis" — populasi hidup dengan
turnover di horizon panjang, tanpa absorpsi.

---

## 018 — PERPETUUM ECOLOGIS: mencari hukum yang tak pernah selesai (DIBUKA; kriteria dibekukan 2026-09-24)

**Misi (dari audit 017):** semua dunia kita mencapai kuasistabilitas (fasa
jenuh; keseimbangan kaku ±0,4–2%). Yang diburu: hukum + keadaan awal yang
populasinya TETAP HIDUP dengan turnover — tak padam, tak beku, tak terkunci.

**Definisi operasional (dibekukan SEKARANG):** sensus populasi per spesies
nilai p_v(t) (str.count per char, sampel tiap-10 state). **PERPETUUM pada
horizon H:** (a) koeksistensi — ≥2 spesies dengan mean ≥ 10; (b) amplitudo
((max−min)/mean) ≥ 0,3 pada ≥1 spesies **di sepertiga TERAKHIR horizon**
(dinamika bertahan, bukan transien); (c) tak statis — ≥1 pasangan state
berurutan berbeda di sepertiga akhir. **Tanda predasi (W-P2, stretch, bukan
gate):** korelasi trajektori dua spesies ≤ −0,5 di sepertiga akhir (satu naik
saat yang lain turun — tanda Lotka-Volterra). **Baseline kuasistabil
(W-P3):** dunia known (v6-final difus; padat +100%; 16295-difus) diukur meter
sama — prediksi amplitudo < 0,1 (referensi pemisah perpetuum vs keseimbangan).

**Pintu murah (aljabar):** laut seragam TAK STABIL bila F(c,c,c) ≠ c — hukum
acak menyediakannya; yang menentukan nasibnya: runtuh → kristal (absorpsi),
runtuh → pulsa global (tersaring: butuh koeksistensi), atau runtuh →
DINAMIKA HIDUP (perpetuum!). IC murah tanpa tanam: all-1s, all-2s, (k=4:
+all-3s), difus-0,5.

**Protokol:** sapu k=2: 300 hukum slack-rich (19001+) × IC {all-1, all-2,
difus} × 2000 langkah; k=4: 150 hukum (19501+) × IC {all-1, all-2, all-3,
difus}; sensus penuh p_v. Kandidat → **verifikasi 3 seed × 20k langkah**
(kriteria (a)-(c) dievaluasi di sepertiga akhir 20k). FM pre-registered:
FM-P1 osilator teredam (amplitudo menurun — dilaporkan sebagai transien);
FM-P2 pulsa global seragam (tersaring koeksistensi); FM-P3 nol kandidat
(taksonomi nasib = hasil: absorpsi/pulsa/hidup).

**Hasil: (menyusul — tanpa pengeditan).**
**Hasil (sapuan 1500 run + verifikasi):**

- **Sapuan:** k=2 NOL kandidat (900 run: 1189-2=... nasib total 1500 —
  absorpsi 1189, hidup-lemah 233, pulsa 0) — konsisten penutupan subdunia
  0/1 (log 017). **k=4: 78 kandidat, SEMUA dari latar difus** (laut seragam
  runtuh-absorpsi), amplitudo 1,2–2,0, koeksistensi hingga 13 spesies.
- **W-P1: PASS — 3/3 instans independen @20k** (law 19631, fnv dicatat di
  sweep JSON): amplitudo 1,91–2,09 di sepertiga akhir 20k, 10 spesies
  berkoeksistensi, tak statis. Koreksi eksekusi didisklosikan: verifikasi
  pertama memakai IC-seed sama (3 salinan 1 trajektori) — diperbaiki menjadi
  3 laut difus independen (21001–03).
- **W-P2: PASS (stretch) — TANDA PREDASI:** pasangan [0,1] berkorelasi
  −0,745 / −0,834 / −0,887 di ketiga instans — spesies-0 dan spesies-1
  berayunan ANTI-FASE (satu naik saat yang lain turun) — tanda tangan
  Lotka-Volterra dalam semesta konservasi-massa.
- **W-P3: PASS — baseline terpisah bersih:** v6-final difus amp 0,0 (statis);
  16295 difus amp 0,0 (statis); padat +100% amp 0,32 (non-statis). Perpetuum
  1,9–2,1 = **6× amplitudo keseimbangan terkuat yang dikenal** — kelas
  dinamika yang berbeda sungguhan.
- **Framing jujur:** mikro-mekanisme osilator 19631 terbuka (apa yang
  membuat [0]/[1] berayunan anti-fase — kandidat: front 0↔1 yang memantul);
  amplitudo-ekor diukur pada census tiap-5-state, window 6000 dari 20k;
  "ekosistem" di sini = populasi multi-spesies hidup dengan fluktuasi besar
  — siklus boom-bust penuh & turnover spesies (extinction/recovery) masih
  di depan.

**Status: W-P1 + W-P2 + W-P3 PASS — PERPETUUM ECOLOGIS DITEMUKAN.**
Semesta pertama yang populasinya tak pernah selesai: 10 spesies, ayunan
3×, predasi anti-fase, 20.000 langkah tanpa absorpsi.

**Reproduksi:** `python experiments/m2/perpetuum_search.py`;
`--verify-law 19631 --verify-k 4 --verify-ic difus`; skrip independen
(pola sesi; angka di log + `perpetuum_verify_independent.json`).

---

## 019 — Meter OEE pada dunia perpetuum: model belum jenuh sampai 10⁶ (2026-09-24)

**Pertanyaan user (benar):** perpetuum ≠ OEE sejati. Ukur dengan alat proyek
sendiri: **model_bits(t) = k × entri aktif di window ~t** (protokol K5,
log 005), checkpoint 10³→10⁶ (run terpanjang proyek), dunia perpetuum 19631
+ dua baseline.

**Hasil (oee_meter.json):**
- **perpetuum 19631 (k=4): coverage 1850 → 2128 → 2190 → 2264 entri;
  model_bits 7400 → 8512 → 8760 → 9056 dari plafon 16384** — MASIH NAIK
  di 10⁶, tanpa jenuh. Laju melambat log-like (+1112/+248/+74 per dekade).
  Tail tak statis di semua checkpoint (dunia tetap hidup di 10⁶).
- **Baseline: v6-final & 16295 (laut difus 0/1): coverage = 1 entri,
  model_bits = 2/128, STATIS di semua checkpoint** — dunia-dunia itu
  membeku ke fixed point (laut difus setengah-densitas berada di bawah
  rezim aliran).

**Verdict atas klaim user: KONFIRMASI dengan angka.** Perpetuum ≠ OEE sejati
— TETAPI ini dunia pertama proyek yang modelnya belum jenuh di horizon:
pertumbuhan bertahan sampai 10⁶. Gap ke OEE sejati terkuantifikasi dua lapis:
(1) plafon hingga — ruang entri k=4 terbatas 4096 (16384 bit); laju log-like
menuju jenuh di bawah plafon; (2) OEE sejati = kebaruan TAK TERBATAS —
butuh ruang model itu sendiri tumbuh.

**Arsitektur yang mengikuti:** semusta-saja terbatas pada k beku; **sistem
terbuka adalah LOOP (semusta + Newton + intervener)** — dan tuas
k-lift-bertahap (k=4→8→…; mesin migrasi sudah ada, log 014) adalah kandidat
pertama pertumbuhan plafon berkelanjutan: unbounded-in-time melalui
ekspansi bertahap, masing-masing tahap terukur (model_bits melompat saat
migrasi, lalu tumbuh lagi). North star proyek — "Semesta + Newton dalam
loop tertutup" — memang arsitektur OEE-nya.

**Reproduksi:** `python experiments/m2/oee_meter.py`. Test: `pytest` (75) +
`cargo` (80).

---

**Kontemplasi 019 — Apakah OEE sejati mustahil di semesta tertutup berdimensi tetap? (2026-09-24)**

**Tiga dinding yang harus dibedakan — jawabannya berbeda untuk masing-masing:**

1. **Dinding pigeonhole (formal):** semusta tertutup berdimensi tetap punya
   ruang keadaan hingga. k=4, n=16384: 16^16384 = 2^65536 ≈ 10^19728 keadaan.
   Dinamika deterministik ⇒ trajektori AKHIRNYA periodik. Kebaruan abadi
   formal: mustahil. TETAPI waktu rekurensi ≥ ~10^19723 detik (dengan laju
   kita 1,4×10^5 langkah/detik) ≈ **10^19705× umur alam semesta**. Dinding
   ini ada, sungguh ada — dan tak relevan bagi pengamat mana pun.
2. **Dinding model (terukur, milik kita):** model Newton jenuh jauh lebih
   awal — bukan karena keadaan habis, tapi karena HUKUM adalah objek hingga
   dan cakupan merambat di ruang itu. Terukur: 9.056 bit naik log-like di
   10⁶; jenuh diperkirakan ribuan-jutaan langkah. Di sini OEE memang belum.
3. **Dinding kedalaman (tempat jawaban tinggal):** deskripsi atas dunia
   hingga TIDAK hingga. Teori bilangan bulat adalah teori struktur tetap —
   dan tak terhabitasi oleh aksioma apa pun yang tetap (Gödel). Jadi
   pertanyaannya bergeser: **apakah dinamika semusta mendukung komposisi tak
   terbatas** — apakah ia mesin hitung universal? Bila ya: model Newton
   tumbuh selama horizon praktis apa pun (kedalaman komputasi, bukan fisika
   baru). Bila tidak: jenuh adalah nasibnya. **Terukur dan terbuka: apakah
   keluarga flow universal pada suatu k tetap?**

**Bahan-bahannya sudah terukur ada di dunia receipt (v8c/017): MEMORI
(sel strata menyimpan 4–7 — terverifikasi), SINYAL (translasi 1 —
terverifikasi), INTERAKSI (front reaksi — terverifikasi). Memori + sinyal +
interaksi = tiga bahan komputasi. Yang belum dibuktikan: sebuah GERBANG.**

**Dan loop:** komposit (semusta + Newton + intervener) juga tertutup —
tak ada input luar — namun 18 ronde membuktikan kebaruan genuinnya dalam
fakta. Keterbukaan tinggal di RELASI, bukan substrat sendirian. North star
proyek memang menyimpulkan ini sejak hari pertama.

**Verdict:** OEE sejati tak-terbatas-forever — mustahil (finitude); OEE
sejati pada horizon praktis mana pun — MUNGKIL, bersyarat universalitas
dinamika; di loop — terjadi dalam fakta. Dinding kemustahilan ilahi yang
tunggal adalah finitude sendiri — dan dia memberi kita ukuran, bukan larangan.

**Pertanyaan terbuka terbaru & tertajam: universalitas keluarga flow pada k
tetap. Langkah pertama yang terukur: satu gerbang logika di dunia receipt.**

---

## 020 — GERBANG PERTAMA: gerbang logika di semusta flow (DIBUKA; aljabar pre-computed 2026-09-24)

**Target kontemplasi 019:** satu gerbang logika di dunia receipt — membuktikan
bahan komputasi (memori/sinyal/interaksi) tersusun menjadi fungsi Boolean.

**Desain gerbang (aljabar pre-computed terhadap tabel v6-final sesungguhnya —
semua entri dicek):** dunia k=4 phase-wrap receipt. **Memori:** parkiran-3 di
posisi P + penjaga-1 di P+1 — stabil diam: emisi parkiran (0,3,1)=0, penjaga
(3,1,0)=0, penjaga tak menguras (3,1,0)... [entri: F_k4(0,3,1)=F2[13]=0;
F_k4(3,1,0)=F2[52]=0]. **Input:** pulsa-1 disuntik di kiri (state surgery);
berjalan (0,1,0)=1; tiba di P−1: **menyetor** ke parkiran (l,1,3)→(l,1,0)=1
(pulsa terkonsumsi: 1−1+0=0); parkiran 3→4 (stabil diam: (0,4,1)=F2[1]=0).
Setoran kedua → 5 → **MEMANCAR** (0,5,1)=F2[5]=1: parkiran 5→4, penjaga
1→2; penjaga melepas pulsa output (4,2,0)=F2[8]=1 → berjalan ke kanan
(1,1,0)=F2[20]=1. **Semantik: output = AND(A,B)** (ambang 2 setoran).
Pulsa A di P−10, B di P−14 (tiba berurutan; tanda tangan waktu berbeda).

**Kriteria dibekukan:** W-G1: kolom output 4 run (A,B)∈{00,10,01,11} =
fungsi Boolean DETERMINISTIK (re-run identik). W-G2: fungsi = AND (0,0,0,1)
sesuai aljabar; bila lain — gerbang tetap sah, fungsi aktual dilaporkan.
Pengukuran: trajektori parkiran per-fase, konsumsi pulsa, perjalanan output.

**Hasil: (menyusul — tanpa pengeditan).**
**Hasil (4 run tabel kebenaran + re-run determinisme):**

- **W-G1: PASS — fungsi Boolean deterministik terverifikasi.** Kolom output
  [0,0,0,0] pada tabel kebenaran (A,B)∈{00,10,01,11}, re-run identik eksak,
  input terkonsumsi di semua run.
- **W-G2: fungsi aktual = OR/buffer regeneratif (1-setoran → emit-and-
  restore), BUKAN AND aljabar pratengara.** Koreksi aljabar (atribusi:
  inference — pra-komputasi memakai F0[13]=0; v6-final membawa mutasi v5
  (13,+1) → F2[13]=1): parkiran-3 terkikis [3,2,2,1,0] — rantai stabilisasi
  pratengara runtuh. Dan sapuan aljabar lanjutan atas lanskap mutasi:
  **kisi emisi lift-v6-final LENGKAP — setiap memori genap (4,6,8,10,12,14)
  stabil diam, setiap +1 setoran mendarat di fase ganjil yang SEMUA emisi-
  hotnya (F2[1]/[5]/[9]/[13]) → 1 setoran = 1 emit = pulsa output +
  RESTORE memori.** Gerbang OR regeneratif: repeater sinyal — prasyarat
  transmisi jarak jauh.
- **Peta ke gerbang AND:** akumulasi 2-setoran butuh fase-ganjil dengan satu
  emisi dingin — mustahil di lift-v6-final (kisi lengkap), TERSEDIA di ruang
  hukum k=4 lain (hukum acak dengan emisi fase-ganjil dingin melimpah).
  Pencarian hukum-gerbang (fitness: memori stabil + 2 setoran pra-emit) =
  ronde berikutnya.

**Status: GERBANG PERTAMA TERVERIFIKASI (fungsi Boolean deterministik di
semusta flow — OR regeneratif); AND menunggu hukum yang tepat.**

---

## 021 — Pencarian hukum-gerbang: AND sejati (DIBUKA; kriteria dibekukan 2026-09-24)

**Misi (peta 020):** gerbang multi-setoran — output menyala HANYA setelah ≥2
setoran (AND). Filter aljabar pada tabel hukum (instan), lalu verifikasi
empiris 4-run.

**Kondisi aljabar (untuk pasangan (memori m, penjaga kr)):**
(1) idle: F[0,m,kr]=0; (2) deposit: F[l,1,m]≠0 untuk l∈{0,1}; (3) pasca-
setoran-1: F[0,m+1,kr]=0; (4) emit pasca-2: F[0,m+2,kr]≠0; (5) penjaga
stabil: F[m,kr,0]=0; (6) travel: F[0,1,0]≠0.

**Kriteria dibekukan:** W-G3 (gerbang kedua — multi-setoran): ≥1 hukum
dengan gerbang empiris: kolom output (00,10,01,11) DETERMINISTIK dan
NON-TRIVIAL — out(11) ≠ max(out(10), out(01)) (bergantung kedua input),
reproduksi eksak. W-G4 (AND): kolom = [0,0,0,1]. FM pre-registered:
FM-G1 lolos-aljabar gagal-empiris (dinamika interaksi beda — mekanisme
dilaporkan); FM-G2 semua empiris OR-like → kanal 2-setoran lebih langka
dari aljabar — peta pelebaran.

**Protokol:** 300 hukum slack-rich k=4 (seeds 22001+) → filter aljabar →
empiris 4-run (STEPS=60, tanam memori+penjaga+pulsa sesuai (m,kr)) →
determinisme re-run. Anti-kuota; mini deterministik.

**Hasil: (menyusul — tanpa pengeditan).**
**Hasil (filter 300 hukum + verifikasi empiris 10 hukum):**

- **Filter aljabar: 19/300 hukum lolos** — pola kolom [0,hot,0,hot] melimpah
  (hipotesis 020 terkonfirmasi).
- **Verifikasi empiris 10 hukum: 9 OR-like (trivial), 1 SEEDING-DEPENDENT
  sejati: law 22126 (m=6, kr=2) — kolom [0,0,0,1] EKSAK = AND.**
- **Trajektori memori (run 11): [6×10, 7×4, 8, 6]** — setoran-1 disimpan
  TANPA emit (6→7), setoran-2 → 8 → EMIT → **memori pulih ke 6: gerbang
  REUSABLE.** Run (10)/(01): memori menahan satu setoran selamanya (out=0);
  run (00): konstanta. **Re-run: kolom + trajektori identik-eksak
  (determinisme).**
- **Verdict: W-G3 PASS (gerbang multi-setoran non-trivial: out(11)=1 sementara
  out(10)=out(01)=0) + W-G4 PASS (kolom = [0,0,0,1] AND eksak).**
- Trilogi gerbang: **OR regeneratif (repeater, log 020) + AND akumulatif-
  reusable (ini)** — dua fungsi Boolean berbeda terverifikasi dalam keluarga
  flow. Fan-out & penyusunan sirkuit = peta berikutnya; universalitas
  keluarga flow (Kontemplasi 019) kini punya dua anak tangga terukur.

**Reproduksi:** `python experiments/m2/gate_search.py`; verifikasi law 22126
(m=6, kr=2). Test: `pytest` (76) + `cargo` (80).

---

## 022 — FAN-OUT + SIRKUIT DUA-GERBANG: (A∧B)∧C (DIBUKA; kriteria dibekukan 2026-09-24)

**Misi (anak tangga ketiga menuju universalitas, Kontemplasi 019):** dari
dua gerbang terverifikasi (OR log 020, AND reusable log 021) menjadi
SIRKUT.

**Kriteria dibekukan:**
- **W-F1 (fan-out):** satu pulsa [2] di 0s, law 22126, membelah menjadi
  DUA pulsa [1] yang berjalan (transmutasi 015 direplikasi di hukum ini) —
  bivalen; bila tidak → cari perangkat fan-out lain di entri 22126.
- **W-F2 (sirkuit):** dua gerbang AND 22126 (memori 6, penjaga 2) dirangkai:
  gerbang-1 (A∧B) → kawat → setoran ke gerbang-2; input C menanduk gerbang-2
  lebih dulu (menahan 1 setoran). **Tabel kebenaran 8 baris (A,B,C) ∈ {0,1}³:
  output sirkuit = (A∧B)∧C eksak**, re-run identik. Output dibaca: gerbang-2
  mencapai 8 (memancar).

FM pre-registered: FM-F1 [2] tak membelah di 22126 → perangkat lain dari
entri parsial hukum ini; FM-F2 output teredam di kawat → ukur & laporkan.

**Hasil: (menyusul — tanpa pengeditan).**
