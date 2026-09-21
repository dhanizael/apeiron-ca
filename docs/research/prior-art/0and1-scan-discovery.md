# 0and1 — Prior-art scan, Thread 3: Machine Law Discovery
Tanggal: 2026-09-21. Metode: sumber primer dibuka satu per satu; setiap klaim di bawah punya kutipan + URL.
Snippet pencarian TIDAK dipakai sebagai bukti. Yang tidak dibuka → UNVERIFIED.

Aturan: PDF mentah tidak bisa dibaca langsung oleh fetcher; dipakai proxy teks (r.jina.ai) atau versi
HTML/ar5iv. Semua kutipan di bawah berasal dari teks yang benar-benar ter-retrieve.

---

## 0. Daftar sumber yang DIBUKA (16)

**14 inti (dikutip di pesan balasan):**
| # | Sumber | URL | Isi yang diambil |
|---|---|---|---|
| 1 | Schmidt & Lipson, Science 2009 | https://cdanfort.w3.uvm.edu/courses/237/schmidt-lipson-2009.pdf (via r.jina.ai) | algoritma, testbed, limitasi |
| 2 | AI Feynman (Udrescu & Tegmark 2020) | https://ar5iv.labs.arxiv.org/html/1905.11481 | noise, dimensi, basis, cara skor |
| 3 | Bayesian machine scientist (Guimerà dkk. 2020) | https://arxiv.org/abs/2004.12157 (+ fulltext r.jina.ai) | MDL/posterior, benchmark, limitasi |
| 4 | Cranmer dkk., orbital mechanics 2020 | https://arxiv.org/abs/2202.02306 | klaim & status verifikasi |
| 5 | DreamCoder (Ellis dkk.) | https://arxiv.org/abs/2006.08381 | library learning, domain |
| 6 | FunSearch (Romera-Paredes dkk., Nature 2023/24) | https://www.nature.com/articles/s41586-023-06924-6 | hasil, evaluator, limitasi |
| 7 | AlphaEvolve 2025 | https://arxiv.org/abs/2506.13131 | hasil & mode verifikasi |
| 8 | SINDy (Brunton dkk., PNAS 2016) | https://ar5iv.labs.arxiv.org/html/1509.03580 | noise, library, skala |
| 9 | PySR / SymbolicRegression.jl (Cranmer 2023) | https://arxiv.org/abs/2305.01582 | algoritma, EmpiricalBench |
| 10 | AutomataGPT (2025) | https://arxiv.org/html/2506.17333 | aturan CA dari data, akurasi |
| 11 | Hanson & Crutchfield, ECA rule 54 (1997) | https://csc.ucdavis.edu/~cmg/compmech/pubs/ECA54TitlePage.html | hukum makro dari mikro |
| 12 | AI Physicist (Wu & Tegmark 2018) | https://arxiv.org/abs/1810.10525 | dunia sintetik, parameter eksak |
| 13 | NewtonBench (ICLR 2026) | https://ar5iv.labs.arxiv.org/html/2510.07172 | benchmark hukum, ground truth |
| 14 | DiscoverPhysics (2026) | https://arxiv.org/abs/2605.26087 | 22 dunia N-body, skor |

**2 tambahan (juga dibuka, dipakai di bagian (c)):**
| 15 | ASAL (Sakana dkk. 2024) | https://arxiv.org/abs/2412.17799 | pencarian substrat ALife |
| 16 | Open-ended local emergent conservation laws (ALIFE 2024) | https://arxiv.org/abs/2407.03345 | aturan emergen & open-endedness (konseptual) |

Dibuka sebagian / metadata saja (tidak dipakai untuk klaim kuat): AI Poincaré (Liu & Tegmark) via arXiv API
metadata — ada, tapi tidak saya jadikan sandaran klaim.

---

## 1. (a) State of the art — kelas hukum & batasannya

### 1.1 Kelas fungsi yang bisa ditemukan

**AI Feynman** — basis operator eksplisit: "add, multiply, subtract, divide, increment, decrement, negate,
sqrt, exp, pi, ln, invert, cos, abs, arcsin, arctan, sin". Persamaan Feynman memakai
"+, −, *, /, sqrt, exp, log, sin, cos, arcsin and tanh". Jumlah variabel bebas: "between 1 and 9
independent variables". Persamaan yang melibatkan turunan atau integral **dikecualikan**.
→ Batas kelas: fungsi aljabar/transendental elementer, ≤9 variabel, tanpa kalkulus.

**SINDy** — pustaka kandidat yang harus ditentukan manusia: "constants, polynomials, trig terms";
"combine[s] sparsity-promoting techniques and machine learning with nonlinear dynamical systems to
discover governing physical equations from measurement data". Bisa ODE dan PDE (wake silinder, Navier–Stokes Re=100).
→ Batas kelas: dinamika yang **sparse** dalam pustaka yang sudah dipilih; menemukan istilah yang tidak ada di pustaka = mustahil.

**Bayesian machine scientist** — bentuk tertutup (closed-form) apa pun, dicari lewat MCMC; prior
dipelajari dari "a corpus of 4080 mathematical expressions that are included in Wikipedia entries".
→ Batas kelas: ekspresi closed-form; bukan sistem dinamis/PDE.

**AutomataGPT** — bukan persamaan tapi **tabel aturan diskret**: "each RM is a 2×18 binary matrix with
one valid next state per metastate". Substrat: "2D binary deterministic cellular automata on toroidal
16×16 grids with an r=1 Moore neighborhood".
→ Batas kelas: CA biner deterministik 2D saja.

**NewtonBench / DiscoverPhysics** — persamaan hukum (LLM agent), termasuk bentuk non-fisik:
"screened and fractional-power gravity, multi-species couplings, hidden dark-matter-like particles,
non-coordinate-free physics, and time-varying interactions".

### 1.2 Noise

- **AI Feynman**: noise Gaussian ditambahkan pada variabel terikat; "We initially set the relative noise
  level ε=10−6, then repeatedly multiplied ε by 10 until the AI Feynman algorithm could no longer solve
  the mystery." Hasil: "most of the equations can still be recovered exactly with an ε-value of 10−4 or
  less", sementara "almost half of them are still solved for ε=10−2". Penulis mengakui ambang itu
  "were not optimized for each mystery individually", dan kerja lanjutan perlu menguji "noise added to
  the independent variables, as well as directly on real-world data".
  → **Dinding noise riil: ~10⁻⁴ untuk recovery eksak; ~10⁻² untuk separuhnya.**
- **SINDy**: "the algorithm is remarkably robust to noise", TETAPI "When the noise is too large, the
  structure identification fails before the coefficients become too inaccurate." Pada sistem Hopf dengan
  data ber-noise, "the actual values of the cubic terms are off by almost 8%".
- **Bayesian machine scientist**: pada noise tinggi, mesin memilih ekspresi yang merupakan versi
  "regularized" dari model eksak — bukan model eksak.
- **NewtonBench**: "a noise level of 0.0001 caused a 13-15% reduction in accuracy".
  → **Bahkan noise 10⁻⁴ menghancurkan ~1/7 akurasi LLM agent.**
- **Schmidt & Lipson**: "The impact of noise also couples with these factors"; dataset simulasi tanpa
  noise "took ~1/10th of the computational effort."

### 1.3 Dimensi & biaya komputasi

- **Schmidt & Lipson** (limitasi paling eksplisit di seluruh literatur): "the time to converge on the law
  equations depends exponentially on the complexity of the law expression itself and roughly
  quadratically on the system dimensionality." Waktu nyata: menit (osilator harmonik) sampai
  **30 jam (double pendulum)**.
- **SINDy**: "factorial growth of Θ in n" → prohibitive untuk dimensi besar; diakali dengan reduksi
  dimensi (SVD/POD).
- **BMS**: "when the number of experimental points is small, the approximation may fail";
  "it may be necessary to develop more efficient approaches for very large datasets."
- **AutomataGPT**: 100 aturan dilatih = "less than 0.04% of all possible rules" (2^18).

### 1.4 Plafon kemampuan pada benchmark ground-truth

**NewtonBench** (324 task, 12 domain fisika, 108 hukum yang digeser):
- Model non-reasoning: GPT-4.1-mini, GPT-4.1, DeepSeek-V3 → "overall symbolic accuracies below 10%".
- Frontier reasoning: GPT-5 "72.9% average symbolic accuracy"; Gemini-2.5-pro 65.0%.
- Setting tersulit: GPT-5 29.9%, Gemini-2.5-pro 13.9%, sisanya "below 5%".
- Ringkasan penulis: **"a clear but fragile capability."**
- Bantuan kode berdampak "dichotomous": menolong model lemah, "paradoxically hinders stronger models"
  via "premature shift from exploration to exploitation".

**DiscoverPhysics** (22 dunia N-body): "the strongest agents pass only half of the worlds and
consistently fail on those where latent structure must be uncovered"; model open-source "lag
substantially behind commercial models"; **"good predictive accuracy does not guarantee high
explanation quality."**

### 1.5 Cacat metodologis yang harus dihindari

- Schmidt & Lipson: tanpa suku sin/cos, algoritma menghasilkan aproksimasi Taylor — dan menghapus
  cosinus justru memaksa konvergensi pada cos(q)=sin(q+π/2). → basis operator menentukan jawaban.
- Schmidt & Lipson: "we cannot know with certainty the units of bulk constants in the law expressions."
- Schmidt & Lipson: diberi hanya data chaotik berenergi tinggi, algoritma "fixated" pada aproksimasi
  konservasi momentum sudut. → **seleksi data menentukan hukum yang "ditemukan".**
- AI Feynman: neural-network fitting sendiri menyumbang "significant de facto noise".
- NewtonBench: sebagian hukum hasil mutasi "may be physically implausible in our universe" — sengaja
  sebagai stress test, bukan klaim fisika.

---

## 2. (b) KRITIS — adakah verifikasi penemuan hukum terhadap semesta simulasi dengan hukum mikro diketahui?

**Jawaban: ADA — tetapi hanya dalam tiga bentuk, dan tidak ada satupun yang persis "semesta bit + mesin penemu hukum emergen + verifikasi eksak".**

### Bentuk 1 — Inferensi ATURAN MIKRO pada substrat diskret (paling dekat ke 0and1)

**AutomataGPT** (Berkovich, David, Buehler 2025) — arXiv:2506.17333
- Substrat sintetik: "a decoder-only transformer pretrained on ~1 million simulated trajectories that
  span 100 distinct two-dimensional binary deterministic CA rules on toroidal grids".
- Ground truth diketahui persis by construction (tabel aturan 2×18).
- Hasil inferensi aturan: "reconstructs the governing update rule with up to **96% functional
  (application) accuracy and 82% exact rule-matrix match**", plus "98.5% perfect one-step forecasts".
- Limitasi yang diakui penulis: hanya CA biner deterministik 2D; kerja lanjutan perlu
  "larger grid sizes, more cell states, and higher dimensionalities"; "it is not clear exactly how large
  future versions of AutomataGPT would have to be to capture the complexity present across a plethora
  of physical systems." Penerapan ke sistem nyata (coarse-grained) secara eksplisit
  **"beyond the scope of this paper."**
- **Catatan penting:** ini menemukan **aturan mikro itu sendiri**, bukan hukum makro/emergen di atasnya.

### Bentuk 2 — Derivasi HUKUM MAKRO dari aturan mikro CA (klasik, dan ini justru inti "emergence")

**Hanson & Crutchfield, "Computational Mechanics of Cellular Automata: An Example"** (Physica D 103, 1997)
— https://csc.ucdavis.edu/~cmg/compmech/pubs/ECA54TitlePage.html
- Objek: "elementary one-dimensional cellular automaton rule 54".
- Yang diekstrak (abstrak verbatim): "The CA's dominant regular domain is identified and a domain filter
  is constructed to locate and classify defects in the domain. The primary particles are identified and a
  range of interparticle interactions is studied. **The deterministic equation of motion of the filtered
  space-time behavior is derived.**" Juga: "We define the emergence time at which the space-time behavior
  condenses into configurations consisting only of domains, particles, and particle interactions."
- → Ini adalah preseden langsung untuk "dari mikro (aturan CA) ke hukum makro (persamaan gerak partikel
  pada spacetime yang difilter)", **dengan substrat yang aturannya diketahui persis**.
- **Caveat yang harus jujur:** sumber yang saya buka TIDAK memuat pernyataan eksplisit tentang validasi
  eksperimental (mis. pembandingan terhadap simulasi brute-force). Klaim validasi eksplisit = UNVERIFIED.
  Selain itu filter domain/partikel di sini **dibangun tangan**, bukan ditemukan otomatis oleh mesin
  pencari hukum. Ini bukan "law discovery engine" — ini "computational mechanics" dengan analisis manual.

### Bentuk 3 — Dunia simulasi dengan HUKUM TERSEMBUNYI, diskor terhadap ground truth

**NewtonBench** (ICLR 2026) — https://ar5iv.labs.arxiv.org/html/2510.07172
- "324 scientific law discovery tasks across 12 physics domains", dari 108 hukum yang digeser.
- Mekanisme kunci — **counterfactual / metaphysical shifts**: "systematic alterations of canonical laws"
  berupa mutasi pada expression tree (operator/konstanta), menghasilkan hukum "novel yet physically
  plausible". Karena digeser dari hukum kanonik oleh manusia, **persamaan hasil geser itu disimpan
  sebagai ground truth**.
- Verifikasi: "one equation f_target is designated as the hidden physical law"; Symbolic Accuracy
  mengecek apakah persamaan temuan "is mathematically equivalent to the ground-truth law f_target".
  Pengecekan ekuivalensi "intentionally disregards the values of physical constants".
- Sifat anti-hafalan: shift membuat task "memorization-resistant" karena "cannot be solved by recall".
- Limitasi: tidak dimaksudkan sebagai dataset latih; metode symbolic regression tradisional
  dikecualikan "outside the scope"; observasi exploration/exploitation "correlational and should be
  interpreted as suggestive rather than causal".

**DiscoverPhysics** (2026) — https://arxiv.org/abs/2605.26087
- "an interactive benchmark that asks a LLM agent to discover the laws of motion of a simulated world
  whose physics deliberately deviates from our own. We construct 22 worlds..."
- Agent berinteraksi: "proposes several rounds of experiments, observes raw trajectory data, and
  ultimately submits both a natural-language explanation of the world's physics and a Python
  implementation of the inferred law."
- Karena semua trajektori dihasilkan runtime oleh simulator, "the benchmark depends on no static data
  products and can be extended to arbitrary force laws, noise levels, and particle counts."
- Skoring: "trajectory MSE on held-out particles" + "an LLM-judged explanation score following an
  expert-written rubric".
- Substrat = **N-body/partikel**, bukan substrat bit.

**AI Physicist** (Wu & Tegmark 2018) — https://arxiv.org/abs/1810.10525
- Dunia sintetik: "a suite of increasingly complex physics environments" dengan
  "random combinations of gravity, electromagnetism, harmonic motion and elastic bounces".
- Verifikasi terhadap ground truth: agent "typically recovering integer and rational theory parameters
  exactly"; error prediksi "about a billion times smaller than a standard feedforward neural net".
- Juga "successfully identifies domains with different laws of motion also for a nonlinear chaotic double
  pendulum in a piecewise constant force field." → **identifikasi rezim hukum (domain) yang berbeda.**
- Penulis menyebut ini "toy" implementation.

### Yang TIDAK ditemukan dalam sumber yang dibuka

Tidak ditemukan pekerjaan yang:
1. menjadikan **semesta substrat bit / artificial chemistry / CA** sebagai objek,
2. dijalankan oleh **mesin penemu hukum otomatis** (symbolic regression / program induction),
3. untuk menemukan **hukum makro/emergen di atas** aturan mikro,
4. dengan **verifikasi eksak terhadap aturan mikro pembangkit**.

Yang ada: (1) AutomataGPT menemukan aturan mikro, bukan hukum emergen; (2) Crutchfield menurunkan
struktur makro dari CA tapi dengan filter buatan tangan, bukan mesin pencari otomatis;
(3) NewtonBench/DiscoverPhysics/AI Physicist memakai dunia partikel kontinu, bukan substrat bit.

**Pernyataan yang tepat: "kombinasi spesifik itu tidak ditemukan dalam sumber yang dibuka" — bukan
"tidak ada di dunia".** Saya tidak melakukan pencarian sistematis atas seluruh literatur (tidak ada
akses Scopus/WoS penuh); ini scan terarah, bukan systematic review.

---

## 3. (c) Law discovery × substrat evolusioner / open-ended

**Tidak ditemukan pekerjaan yang mengawinkan mesin penemu hukum dengan substrat yang berevolusi.**

Yang terdekat, dan batasnya:

**ASAL — "Automating the Search for Artificial Life with Foundation Models"** (Sakana AI dkk., 2024)
— https://arxiv.org/abs/2412.17799
- Melakukan: "(1) finds simulations that produce target phenomena, (2) discovers simulations that
  generate temporally open-ended novelty, and (3) illuminates an entire space of interestingly diverse
  simulations", melintasi "Boids, Particle Life, Game of Life, Lenia, and Neural Cellular Automata".
- Hasil: "the discovery of previously unseen Lenia and Boids lifeforms, as well as cellular automata
  that are open-ended like Conway's Game of Life."
- **Batas krusial:** ASAL mencari **konfigurasi/parameter simulasi** ("the configurations of lifelike
  simulations"), **bukan hukum**. Ia tidak menginferensikan hukum; ia menyaring substrat.
- → Jadi: ada mesin yang *mencari substrat open-ended*, tapi tidak ada yang *menemukan hukum* dari
  substrat itu.

**"An Open-Ended Approach to Understanding Local, Emergent Conservation Laws"** (ALIFE 2024)
— https://arxiv.org/abs/2407.03345
- Inilah pernyataan masalahnya, bukan solusinya. Konsep: constraint menghasilkan
  "local, emergent conservation laws (rules)"; constraint "can be characterized as variables whose
  values are either completely conserved, quasi-conserved, or conditionally conserved".
- Penulis menyatakan kesenjangan terbuka secara eksplisit: riset lebih berhasil menemukan mekanisme
  yang menghasilkan **state baru** daripada mekanisme yang menghasilkan **aturan baru**; kuncinya adalah
  "how new, local rules might emerge from within the system".
- Ini paper konseptual/posisi. **Tidak ada verifikasi ground truth** yang dilaporkan. Ia juga mencatat
  bahwa dalam pemodelan saat ini "system constraints are maintained externally", berbeda dengan
  constraint biologis yang dijaga "by dynamics that occur from within the system".

**Kesimpulan (c):** tidak ditemukan dalam sumber yang dibuka. Celah ini nyata dan terkonfirmasi oleh
dua sumber independen: ASAL (mencari substrat, bukan hukum) dan ALIFE 2024 (mendeklarasikan
"aturan baru yang muncul" sebagai masalah terbuka).

---

## 4. (d) Teknik mana yang paling efektif — dengan bukti

### Bukti head-to-head

**AI Feynman vs Eureqa (GP klasik), pada himpunan Feynman yang sama:**
- "Eureqa solved 71% of the 100 basic mysteries, while AI Feynman solved 100%"
- Pada bonus mysteries (lebih sulit): "Eureqa solved 15%" vs "AI Feynman 90%".
- Kunci kemenangannya bukan GP yang lebih baik, tapi **dekomposisi yang dibimbing jaringan saraf**:
  NN dipakai untuk mendeteksi simetri, separabilitas, komposisi → masalah besar dipecah rekursif.
  (Abstrak: "recursive multidimensional symbolic regression algorithm that combines neural network
  fitting with a suite of physics-inspired techniques.")

**Bayesian machine scientist vs Eureqa, EPLEX, EFS, Gaussian processes:**
- Pada ekspresi sintetik F = x1(q1 + x2)cos(x1)/[q2 log(q2)]: "none of these methods are able to
  recover the correct model" — BMS berhasil (bahkan dengan 100 titik data).
- Pada sistem Rössler: metode pembanding "fail to recover the true model and tend to overfit structurally."
- Pada Nikuradse (data nyata): "predictions of the Bayesian machine scientist are significantly more
  accurate than those of all alternative approaches", dan ia memprediksi skala benar (D/r)^(−1/3).
- Mekanismenya: description length — "L(fi) ≈ B(fi)/2 − log p(fi)" (BIC + prior), prior dipelajari dari
  korpus 4080 ekspresi Wikipedia, pencarian MCMC dengan 3 tipe move + parallel tempering, dan
  prediksi dengan "average over the whole ensemble of plausible models".
  → **MDL/posterior marginal + prior empiris mengalahkan fitness heuristik.**

**FunSearch (Nature) — LLM-guided evolutionary search + evaluator program:**
- Arsitektur: "we sample best performing programs and feed them back into prompts for the LLM to
  improve on"; skeleton tetap, hanya bagian logika kritis yang dievolusi; island-based evolution untuk
  keragaman; worker terdistribusi.
- Hasil: cap set n=8 berukuran 512 (lebih besar dari yang diketahui), bound asimtotik baru 2.2202
  (naik dari 2.2180, "the largest improvement in 20 years"); heuristic bin packing baru.
- Verifikasi: "verifiably correct"; melampaui SOTA "provides a clear indication that the discoveries are
  truly new, as opposed to being retrieved from the LLM's training data."
- Limitasi yang diakui penulis: hasil cap set n=8 langka — "only four out of 140 experiments discovering
  a cap set of size 512"; LLM "sometimes suffer from confabulations (or hallucinations)"; hanya cocok
  bila ada "(1) availability of an efficient evaluator; (2) a 'rich' scoring feedback...; and (3) ability
  to provide a skeleton with an isolated part to be evolved"; pembuatan bukti "falls outside this scope,
  because it is unclear how to provide a rich enough scoring signal".
- **Poin epistemik paling penting dari FunSearch:** evaluator program adalah yang "guards against
  confabulations and incorrect ideas" — LLM hanya mengusulkan.

**AlphaEvolve (2025) — arXiv:2506.13131:**
- "an evolutionary coding agent"; hasil: algoritma penjadwalan data center Google; penyederhanaan
  sirkuit akselerator; percepatan training LLM-nya sendiri; dan "a procedure to multiply two 4×4
  complex-valued matrices using 48 scalar multiplications; offering the first improvement, after 56
  years, over Strassen's algorithm in this setting."
- Klaim verifikasi: "novel, provably correct algorithms that surpass state-of-the-art solutions";
  mekanisme: "continuously receiving feedback from one or more evaluators."
- (Catatan: halaman abstrak yang saya buka tidak memuat daftar limitasi eksplisit.)

**DreamCoder — library learning (abstraksi) + neural-guided search:**
- "wake-sleep algorithm alternately extends the language with new symbolic abstractions and trains the
  neural network on imagined and replayed problems"; konsep dibangun "compositionally from those learned
  earlier".
- Hasil: menemukan ulang dasar "modern functional programming, vector algebra and classical physics,
  including Newton's and Coulomb's laws."
- → **Abstraksi/library learning adalah mekanisme yang membuat penemuan berskala** — bukan pencarian
  datar. (Halaman yang saya buka hanya abstrak; detail evaluasi & limitasi = UNVERIFIED.)

**AutomataGPT — pretraining skala besar di atas ruang aturan:**
- Kesimpulan penulis: "large-scale pretraining over wider regions of rule space yields substantial
  generalization in both the forward (state forecasting) and inverse (rule inference) problems, without
  hand-crafted priors."
- → Untuk substrat diskret, **prior yang dipelajari dari distribusi aturan** jauh lebih kuat daripada
  prior buatan tangan.

### Sintesis (d)

Yang terbukti efektif **bukan salah satu keluarga tunggal**, melainkan kombinasi tiga komponen:

1. **Kriteria parsimoni eksplisit** untuk seleksi model — MDL / BIC / posterior marginal (BMS) atau
   Pareto accuracy-vs-complexity (Schmidt & Lipson: hasil akhir disajikan "on an accuracy-parsimony
   Pareto front"). Ini yang membedakan BMS dari fitness heuristik dan membuatnya menang di Rössler.
2. **Distribusi proposal yang dipelajari** untuk memandu pencarian — NN untuk simetri/separabilitas
   (AI Feynman: 71%→100%), library learning (DreamCoder), pretraining lintas aturan (AutomataGPT),
   atau LLM (FunSearch/AlphaEvolve).
3. **Verifier eksak/programatik sebagai gerbang** — evaluator FunSearch, ekuivalensi simbolik NewtonBench,
   atau MSE pada partikel held-out (DiscoverPhysics). Ini yang membunuh halusinasi dan sekaligus
   yang membuat klaim "penemuan baru" bisa dipertahankan.

Yang **lemah sendirian**: GP/EA murni (Eureqa — dikalahkan di kedua perbandingan head-to-head);
sparse library regression (SINDy — cepat dan tahan noise, tapi terkurung pada pustaka yang dipilih dan
tumbuh faktorial terhadap dimensi).

---

## 5. Kutipan yang layak dipakai langsung (verbatim, siap sitasi)

- Schmidt & Lipson: "the time to converge on the law equations depends exponentially on the complexity
  of the law expression itself and roughly quadratically on the system dimensionality."
- Schmidt & Lipson: "we cannot know with certainty the units of bulk constants in the law expressions."
- AI Feynman: "most of the equations can still be recovered exactly with an ε-value of 10−4 or less",
  "almost half of them are still solved for ε=10−2".
- BMS: "none of these methods are able to recover the correct model" (soal pembanding pada ekspresi sintetik).
- FunSearch: "The 'evaluate' function takes as input a candidate solution to the problem, and returns a
  score assessing it"; "only four out of 140 experiments discovering a cap set of size 512".
- AutomataGPT: "reconstructs the governing update rule with up to 96% functional (application) accuracy
  and 82% exact rule-matrix match."
- Crutchfield: "The deterministic equation of motion of the filtered space-time behavior is derived."
- NewtonBench: "a clear but fragile capability."
- DiscoverPhysics: "the strongest agents pass only half of the worlds and consistently fail on those
  where latent structure must be uncovered."
- ALIFE 2024: "how new, local rules might emerge from within the system".

---

## 6. Ringkasan jawaban (untuk pesan balasan)

(a) Kelas: ekspresi closed-form elementer ≤9 variabel (AI Feynman); dinamika sparse dalam pustaka
    terpilih, ODE/PDE (SINDy); tabel aturan diskret (AutomataGPT). Dinding noise: recovery eksak sampai
    ε≈10⁻⁴, separuh sampai ε≈10⁻² (AI Feynman); noise 10⁻⁴ memotong akurasi LLM 13–15% (NewtonBench).
    Biaya eksponensial terhadap kompleksitas hukum, kuadratik terhadap dimensi (Schmidt & Lipson).
    Plafon: GPT-5 72.9% symbolic accuracy rata-rata, 29.9% di setting tersulit; DiscoverPhysics: separuh dunia.
(b) ADA, dalam 3 bentuk: inferensi aturan mikro CA (AutomataGPT, 96%/82%); derivasi hukum makro dari CA
    (Crutchfield rule 54, tapi filter buatan tangan + validasi eksplisit UNVERIFIED); hukum tersembunyi di
    dunia simulasi dengan skor ground truth (NewtonBench, DiscoverPhysics, AI Physicist). Kombinasi
    "semesta bit + mesin penemu hukum emergen otomatis + verifikasi eksak" TIDAK ditemukan.
(c) Tidak ditemukan. ASAL mencari substrat open-ended, bukan hukum. ALIFE 2024 mendeklarasikan
    "aturan baru yang muncul" sebagai masalah terbuka, tanpa verifikasi.
(d) Bukan satu keluarga: parsimoni eksplisit (MDL/posterior atau Pareto) + proposal yang dipelajari
    (NN/library/pretraining/LLM) + verifier eksak sebagai gerbang. GP murni kalah head-to-head.
