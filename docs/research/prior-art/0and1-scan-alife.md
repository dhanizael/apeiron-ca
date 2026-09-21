# 0and1 prior-art scan — Thread 1: ALife klasik & modern + open-endedness di media digital

Tanggal: 2026-09-21
Aturan: hanya klaim yang sumber primernya sudah DIBUKA dan isinya mendukung. Salinan lokal: /tmp/0and1src/

---

## SUMBER YANG DIBUKA (15)

| # | Sumber | URL | Status baca |
|---|--------|-----|-------------|
| S1 | Ray, T.S. (1991) "An Approach to the Synthesis of Life", ALife II, hlm. 371–408 | http://tomray.me/pubs/alife2/Ray1991AnApproachToTheSynthesisOfLife.pdf | PDF penuh |
| S2 | Adami, Ofria, Collier (2000) "Evolution of biological complexity", PNAS 97(9):4463–4468 | https://web.archive.org/web/2020/https://www.pnas.org/doi/10.1073/pnas.97.9.4463 | teks penuh via archive.org |
| S3 | Lenski, Ofria, Pennock, Adami (2003) "The evolutionary origin of complex features", Nature 423:139–144 | https://www.nature.com/articles/nature01568 | abstrak (full text paywall) |
| S4 | Chan, B.W.-C. (2019) "Lenia — Biology of Artificial Life", arXiv:1812.05433 | https://arxiv.org/abs/1812.05433 | PDF penuh |
| S5 | Chan, B.W.-C. (2023) "Towards Large-Scale Simulations of Open-Ended Evolution in Continuous Cellular Automata", GECCO'23, arXiv:2304.05639 | https://arxiv.org/abs/2304.05639 | PDF penuh |
| S6 | Hughes, Dennis, Parker-Holder, Behbahani, Mavalankar, Shi, Schaul, Rocktäschel (2024) "Open-Endedness is Essential for Artificial Superhuman Intelligence", arXiv:2406.04268 | https://arxiv.org/abs/2406.04268 | PDF penuh |
| S7 | Fredkin & Toffoli (1982) "Conservative Logic", Int. J. Theor. Phys. 21(3/4):219–253 | https://www.cs.princeton.edu/courses/archive/fall06/cos576/papers/fredkin_toffoli82.pdf | PDF penuh |
| S8 | Margolus, N. (1984) "Physics-like models of computation", Physica 10D:81–95 | https://people.csail.mit.edu/nhm/bbmca-physica.pdf | PDF penuh |
| S9 | Boccara & Fukś (1999) "Number-conserving cellular automaton rules", arXiv:adap-org/9905004 | https://arxiv.org/abs/adap-org/9905004 | PDF penuh |
| S10 | Sayama, H. (1999) "A New Structurally Dissolvable Self-Reproducing Loop Evolving in a Simple Cellular Automata Space", Artificial Life 5(4):343–363 | https://bingdev.binghamton.edu/sayama/papers/ALIFE5-4-343.pdf | PDF penuh |
| S11 | Sayama & Nehaniv (2024) "Self-Reproduction and Evolution in Cellular Automata: 25 Years after Evoloops", arXiv:2402.03961 | https://arxiv.org/abs/2402.03961 | PDF penuh |
| S12 | Sayama, H. (2024) "Non-Spatial Hash Chemistry as a Minimalistic Open-Ended Evolutionary System", arXiv:2404.18027 | https://arxiv.org/abs/2404.18027 | PDF penuh |
| S13 | Fontana & Buss (1994) "The Arrival of the Fittest: Toward a Theory of Biological Organization", Bull. Math. Biol. 56(1):1–64; SFI WP 93-09-055 | https://sfi-edu.s3.amazonaws.com/sfi-edu/production/uploads/sfi-com/dev/uploads/filer/f2/8b/f28b8075-4e73-4696-989e-1cfbe06b2dc8/93-09-055.pdf | PDF penuh |
| S14 | Adams, Zenil, Davies, Walker (2017) "Formal Definitions of Unbounded Evolution and Innovation Reveal Universal Mechanisms for Open-Ended Evolution in Dynamical Systems", Sci. Rep. 7:5975; arXiv:1607.01750 | https://arxiv.org/abs/1607.01750 | PDF penuh |
| S15 | Bedau, Snyder, Packard (1998) "A Classification of Long-Term Evolutionary Dynamics", ALife VI — halaman abstrak resmi prosiding | https://cseweb.ucsd.edu/~rik/alife6/papers/KI40.html | abstrak saja |

### Dicoba, GAGAL diakses (JANGAN dipakai sebagai bukti)
- Soros & Stanley (2014) ALIFE XIV "Identifying Necessary Conditions for OEE through Chromaria": 403 di direct.mit.edu, 403 di UCF STARS, 403 di doczz, semanticscholar 202/0 byte. **UNVERIFIED**.
- Bedau & Packard (1992) "Measurement of evolutionary activity, teleology, and life": tidak ditemukan salinan bebas. **UNVERIFIED**.
- Fontana & Buss via link.springer.com/content/pdf: mengembalikan HTML paywall (bukan PDF) — digantikan oleh S13.
- Lenski et al. 2003 full text: paywall (hanya abstrak + daftar gambar).

---

## TEMUAN PER SUMBER

### S1 — Tierra (Ray 1991)
Klaim penulis (verbatim): pendekatan ini "starts with hand-crafted organisms already capable of replication and open-ended evolution, and aims to generate increasing diversity and complexity in a parallel to the Cambrian explosion."

Yang benar-benar didemonstrasikan (semua dari teks S1):
- Parasit obligat muncul (mis. genotipe 0045aaa, ukuran 45 vs nenek moyang 80) — parasit informasi: tidak punya prosedur `copy`, memanggil prosedur copy inangnya.
- Hiper-parasit (mis. 0080gai, beda 19 instruksi dari nenek moyang): membajak instruction pointer parasit, menyetel ulang register bx/cx sehingga parasit mereplikasi genom hiper-parasit.
- Hiper-parasit sosial (kelas ukuran 61): hanya bisa mereplikasi bila beragregasi; "Neighboring creatures coopelate by catching and passing on jumps of the instruction pointer."
- Cheater hiper-hiper-parasit; simbion obligat (dua kreatur, tak satu pun bisa mereplikasi sendiri, bisa bersama); imunitas terhadap parasit dan parasit yang menembus imunitas itu.
- Eksperimen diversitas: komunitas 20 kelas ukuran → setelah 30 juta instruksi hanya 8 kelas ukuran TERKECIL yang tersisa; dengan parasit, 16 kelas bertahan (efek "keystone").
- Ukuran menurun: "The social species are 24% smaller than the ancestor."

Klaim kompleksitas: Ray menulis bahwa karena lanskap kebugaran mencakup adaptasi terhadap kreatur lain yang juga berevolusi, "it can facilitate an auto-catalytic increase in complexity and diversity of organisms." — klaim POTENSI, bukan demonstrasi. Tidak ada grafik pertumbuhan kompleksitas tanpa batas. Yang ada: diversifikasi ekologis + regresi ukuran.

Relevansi: Tierra = bukti ekologi kaya (parasitisme, sosialitas, simbiosis) muncul spontan dari replikator + mutasi + seleksi lokal; TAPI tidak ada bukti pertumbuhan kompleksitas tanpa batas.

### S2 — Adami, Ofria, Collier 2000 (Avida, "physical complexity")
- Definisi: kompleksitas genom = jumlah informasi yang disimpan sekuens tentang lingkungannya ("physical complexity").
- Hasil utama: "in fixed environments, for organisms whose fitness depends only on their own sequence information, physical complexity must always increase" — argumen Maxwell demon. Di lingkungan tetap + populasi besar, entropi tiap lokus sudah maksimum; mutasi yang menaikkan entropi dipurg, yang menurunkannya dipertahankan.
- Batas: kompleksitas = panjang sekuens − entropi. Panjang sekuens tetap (100 instruksi). Peningkatan panjang tidak menaikkan kompleksitas fisik, tapi "they are critical to continued evolution as they provide new space ('blank tape')".
- Mekanisme GAGAL dalam 3 kondisi (dinyatakan penulis): (i) "simple environments spawn only simple genomes"; (ii) "changing environments can cause a drop in physical complexity"; (iii) reproduksi seksual.
- Sumber daya: "a single-niche environment in which resources are isotropically distributed and unlimited except for CPU time" — pembatasnya CPU time per update (30 instruksi), bukan energi/materi.

Relevansi: pertumbuhan kompleksitas TIDAK otomatis — butuh lingkungan berstruktur yang bisa "dipelajari" dan yang tetap. Klaim "forced to increase" berlaku untuk lingkungan tetap + populasi besar + aseksual, dan kompleksitasnya terbatas pada informasi tentang lingkungan itu.

### S3 — Lenski et al. 2003 (Avida, fitur kompleks)
Abstrak verbatim (poin kunci): "Populations of digital organisms often evolved the ability to perform complex logic functions requiring the coordinated execution of many genomic instructions. Complex functions evolved by building on simpler functions that had evolved earlier, provided that these were also selectively favoured."
- Seleksi eksplisit: fungsi logika (mis. EQU) diberi reward oleh perancang.
- "In some cases, mutations that were deleterious when they appeared served as stepping-stones."
- Kesimpulan penulis: "These findings show how complex functions can originate by random mutation and natural selection."

Catatan: kompleksitas tumbuh MENUJU gradient yang dipasang perancang (reward fungsi logika), bukan pertumbuhan spontan tanpa arah.

### S4 — Lenia 2018 (Chan)
- >400 spesies dalam 18 famili, sebagian besar ditemukan via interactive evolutionary computation.
- Klaim sifat: "geometric, metameric, fuzzy, resilient, adaptive, and rule-generic".
- Yang TIDAK diklaim: open-endedness. Pertanyaan riset terbuka yang ditulis penulis sendiri: "7. Is Lenia capable of open-ended evolution that generates unlimited novelty and complexity?" dan "8. Do self-replicating and pattern-emitting lifeforms exist in Lenia?"
- Satu-satunya klaim "evolvability": "Evolvability: patterns evolve via manual operations and potentially genetic algorithms" — masih manual.

Relevansi: Lenia 2018 = keanekaragaman bentuk + dinamika kaya, BUKAN bukti open-endedness. Klaim open-endedness Lenia baru diuji (dan gagal) di S5.

### S5 — Chan 2023 (Lenia skala besar, uji OEE) — bukti terkuat untuk failure mode
- Desain: (1) operator genetik implisit — reproduksi via self-replication pola, seleksi via differential existential success; (2) lokalisasi informasi genetik; (3) algoritma pemeliharaan genotype lokal + translasi ke phenotype. Skala besar via JAX.
- Empat rezim dan hasilnya:
  - tanpa penalti + mutasi normal: dunia cepat tersaturasi replika, "there is no sign of further evolution".
  - tanpa penalti + mutasi tinggi: fase transisi kreatif → akhirnya "global 'goo' patterns consists of violently flickering and fast moving quadratic expanding patterns (QEPs), without differentiation into individual entities".
  - dengan penalti + mutasi normal: kreatur menarik, tapi "Later the simulation may end towards total extinction, or evolves into domination by LEPs [linear expanding patterns]".
  - dengan penalti + mutasi tinggi: "the world quickly converges into an optimal state, dominated by LEPs".
- Verdict penulis, verbatim: **"OEE has not been achieved, largely because of the dominance of expanding patterns like QEPs and LEPs that quickly destroy existing genetic diversity."**
- Faktor yang diusulkan penulis: virtual environment design, **mass conservation**, **energy constraints**. Peringatan penulis: "mass conservation may limit the creativity".
- Catatan Flow-Lenia (Figure 6 di S5): dengan mass conservation, "In later stage, the world is dominated by a [few species]" — tetap konvergen.

### S6 — Hughes et al. 2024 (definisi open-endedness)
Definisi formal, verbatim: **"From the perspective of an observer, a system is open-ended if and only if the sequence of artifacts it produces is both novel and learnable."**
- Novelty: "∀t, ∀T > t, ∃T′ > T : E[ℓ(t, T′)] > E[ℓ(t, T)]".
- Learnability: "∀T, ∀t < T, ∀T > t′ > t : E[ℓ(t′, T)] < E[ℓ(t, T)]".
- Konsekuensi eksplisit: open-endedness **observer-dependent**. "noisy TV" learnable tapi tidak novel; TV dengan channel acak tak berkorelasi novel tapi tidak learnable.
- Paper menegaskan: "present-day foundation models are not yet open-ended"; open-endedness "remains elusive".
- Ia merangkum 4 syarat perlu Soros & Stanley (2014) (mengutip, bukan membuktikan): (1) individu harus memenuhi minimal criterion untuk bereproduksi; (2) evolusi individu harus menciptakan peluang baru untuk memenuhi minimal criterion; (3) individu sendiri yang memutuskan cara berinteraksi dengan dunia; (4) kompleksitas potensial phenotype tidak dibatasi representasinya.

Relevansi: definisi ini operasional dan bisa dipakai 0and1 untuk mengevaluasi "Newton" — observer = Newton itu sendiri; novelty diukur relatif terhadap model yang sudah dipelajarinya.

### S7 — Fredkin & Toffoli 1982 "Conservative Logic" — VERIFIED
- Abstrak: "Conservative logic is a comprehensive model of computation which explicitly reflects a number of fundamental principles of physics, such as the reversibility of the dynamical laws and the conservation of certain additive quantities (among which energy plays a distinguished role)."
- "this model proves that universal computing capabilities are compatible with the reversibility and conservation constraints."
- Ada dua model; yang kedua adalah penyempurnaan: **billiard ball model**. Bagian 6: "A 'BILLIARD BALL' MODEL OF COMPUTATION" — "we shall introduce a model of computation (the billiard ball model) based on stylized but [physical] primitives... any conservative-logic circuit can be read as the full 'schematics' of a billiard ball computer."
- Realisasi gate: interaction gate = lokus tumbukan dua bola; Fredkin gate punya realisasi bola biliar (Gambar 18, dua realisasi, satu oleh R. Feynman).
- Energi: "the billiard ball model (in which the energy is simply proportional to the number of balls)".
- Primitif universal klasik (AND, NOT, FAN-OUT) ireversibel dan "in principle, no physical system can function as an AND gate"; karena itu primitifnya diganti.

Relevansi: BBM = preseden paling kuat untuk "substrat bit murni dengan fisika konservatif" — partikel + tumbukan = gate universal, reversibilitas + konservasi dipertahankan. Tapi ini tentang KOMPUTASI, bukan open-endedness.

### S8 — Margolus 1984 "Physics-like models of computation" — VERIFIED
- "Reversible Cellular Automata are computer-models that embody discrete analogues of the classical-physics notions of space, time, locality, and microscopic reversibility."
- BBMCA (versi digital BBM): aturan yang mengawetkan 1 dan 0, reversibel, dan universal. "Since each distinct initial state of a block is mapped onto a distinct final state, this rule is reversible. As will be shown later, the automaton corresponding to this rule is universal."
- Temuan konseptual, verbatim: **"Thus the existence of an interesting local conservation law does not depend on the rule being reversible!"** — aturan konservatif tapi tidak reversibel tetap punya hukum konservasi lokal kaya (tapi kehilangan informasi).
- Ada analogi energi/entropi dalam RCA.
- Catatan kaki tentang von Neumann: "Von Neumann was interested in the problem of evolution — could life emerge from simple rules? He exhibited a CA rule that permitted computers, and in which these computers could reproduce and mutate."

Relevansi: NCCA/BBMCA memberi partikel + tumbukan + gate universal dalam satu substrat bit. Tapi S11 menunjukkan konstruktor universal tidak otomatis menghasilkan pertumbuhan kompleksitas.

### S9 — Boccara & Fukś 1999 (NCCA) — VERIFIED
- "A necessary and sufficient condition for a one-dimensional q-state n-input cellular automaton rule to be number-conserving is established."
- Aplikasi eksplisit: "Number-conserving systems, interacting particles, highway traffic" — model partikel dengan jumlah total kekal pada lattice periodik, ≤ q−1 partikel per sel.
- Representasi visual: aturan NCCA dijelaskan sebagai "flow diagram" — partikel dideskripsikan oleh barisan bilangan tak-menurun (v1,…,vs) = kecepatan s partikel; panah menunjukkan berapa partikel pindah ke posisi final mana. "the dynamics of the particles is not clearly exhibited by the rule table of a number-conserving CA rule. A simpler and more visual picture of the rule is given..."
- Rule 184 (model lalu lintas Nagel–Schreckenberg) sebagai contoh kanonik; dua aturan 3-state 3-input self-conjugate nontrivial ditemukan.
- Dualitas partikel–hole: C f mendeskripsikan aturan yang sama untuk gerak hole.

Relevansi: NCCA = kelas aturan yang native menghasilkan "partikel" dan "tumbukan" dengan hukum kekal, plus kosakata visual (flow diagram) yang bisa langsung dipakai untuk partikel/tumbukan di substrat 0and1. Kelas ini fertile untuk ENTITAS; S9 tidak mengklaim apa pun soal open-endedness.

### S10 — Sayama 1999 evoloop — VERIFIED (failure mode penting)
- Sistem: CA 9-state 5-neighbor deterministik; evoloop = SDSR loop yang diperbaiki agar adaptable.
- Hasil, verbatim: "though no mechanism was explicitly provided to promote evolution, the loops varied through direct interaction of their phenotypes, **smaller individuals were naturally selected thanks to their quicker self-reproductive ability, and the whole population gradually evolved toward the smallest ones.**"
- "the whole system seems to evolve toward the smallest species 4 approximately in proportion to elapsed time."
- Jalur ke arah lebih besar ada tapi jarang: "they became extinct as they evolved to be too large. Thus, this evolutionary path always began at the optimum (smallest structure) of the fitness landscape and descended [from it]."
- Penulis sendiri menyebut sistemnya "has an extremely small complexity compared to other models" dan mengakui sistem tidak memberi organisme kemampuan membangun relasi kompleks dengan mengubah lanskap kebugaran satu sama lain.
- Klaim positif: evolusi Darwinian (variasi + seleksi alam) TERBUKTI mungkin dalam CA deterministik; variasi genotipik disebabkan variasi fenotipik preseden.

Relevansi: evoloop = bukti self-replication + evolusi mungkin di CA murni, TAPI arah evolusinya REGRESI menuju struktur terkecil, bukan pertumbuhan kompleksitas.

### S11 — Sayama & Nehaniv 2024 (review 25 tahun) — sintesis paling otoritatif
Verbatim:
- **"nearly all the above evolutionary systems built within spatially distributed media exhibited the eventual dominance by one or a few most successful species in the long run, and it is still unclear what kind of generalizable principles or mechanisms are available to prevent the evolving ecosystem of self-replicators from falling into such pseudo-equilibrium states."**
- "It has been suggested that dynamic environments are the key to addressing this issue, **although they may not work for indefinitely long terms**. Overcoming this empirical limitation is a necessary and critical step towards implementing open-ended self-reproducing and evolving systems within cellular automata and other similar spatially distributed computational media."
- Tentang Lenia: "these models remained at the level of describing only self-replication, where evolution via variation and natural selection was not fully realized."
- Tentang von Neumann: kompleksitas tambahan pada konstruktor universal "has not been used in any essential way in the self-replication"; kriteria Langton "is silent about ensuring that complexity increase and an evolutionary process could be supported"; kriteria von Neumann "might not necessarily lead to the evolution of complexity".
- Tantangan terbuka yang MASIH terbuka: I.1 banyak keturunan aktif sekaligus; I.2 robust terhadap tumbukan dan noise; **I.3 "Demonstrate Darwinian evolution in a population of such variant von Neumann universal constructor self-reproducers"**; I.4 introduksi seks; I.5 integrasi self-repair/self-maintenance menuju autopoiesis — "a milestone so far not achieved in any artificial self-reproducers"; II.1 konstruktor universal self-reproducing via self-examination; II.2 realisasi di continuous CA.
- Konteks sejarah: tujuan awal ALife (von Neumann, Langton) adalah proses evolusioner demonstratif di CA; tercapai dalam bentuk evoloop; lalu "relative dormancy"; kebangkitan karena gerakan OEE + continuous CA.

### S12 — Sayama 2024 Hash Chemistry
- Klaim: model non-spasial (proximity = multiset) menghasilkan "much more significant unbounded growth in both maximal and average sizes of replicating higher-order entities than the original model", disebut "a minimalistic example of open-ended evolutionary systems".
- Fitness evaluator = fungsi hash ("universal fitness evaluator") — "cardinality leap" ruang kemungkinan.
- Caveat yang ditulis penulis sendiri: "In the proposed non-spatial model, however, such interactions among evolving entities do not exist, and **evolution is reduced to a mere refinement of fitness values of mutually independent multisets. In other words, the evolutionary dynamics exhibited in the non-spatial model are fundamentally simpler with no interactions among evolving entities.** It remains an open question how nontrivial ecological interactions could be introduced."
- Caveat kedua: entitas besar mati karena error mutasi → "This highlights the importance of high fidelity of replication (and active error correction) for complexity growth of evolving entities."
- Pada model non-spasial, "extinction of replicating entities never happened".

Relevansi: satu-satunya klaim "unbounded growth" 2024 yang saya temukan, TAPI (i) fitness = oracle fungsi hash yang dipasang perancang, (ii) tanpa interaksi ekologis, (iii) kompleksitas yang tumbuh = ukuran multiset, bukan organisasi. Contoh pertumbuhan METRIK tanpa ORGANISASI.

### S13 — Fontana & Buss 1994 (λ-calculus chemistry) — VERIFIED
- Abstrak, verbatim: "We develop a minimal theory of biological organization based on two abstractions from chemistry. The theory is formulated using λ-calculus, which provides a natural framework capturing (i) the constructive feature of chemistry, that the collision of molecules generates specific new molecules, and (ii) chemistry's diversity of equivalence classes, that many different reactants can yield the same stable product."
- "An organization is self-maintaining, and is characterized by (i) boundaries established by [syntax/function]... and self-maintaining generator set of the algebra."
- **"In our system self-maintaining organizations arise as a generic consequence of two features of chemistry, without appeal to natural selection."**
- Hirarki level: "Level 0 - reproduction and ecology", "Level 1 - self-maintenance and organization", "Level 2: Organizations of organizations". "Imposition of different boundary conditions on the stochastic flow reactor generates different levels of organization, and **a diversity of organizations within each level**."
- Organisasi "are recognized and defined by these syntactical and functional regularities" — butuh observer/grammar untuk mengenali organisasi (ada bagian "Organizations, algebraic structures and observers").
- Motivasi: "Natural selection may explain the survival of the fittest, but it cannot explain the arrival of the fittest."

Relevansi: organisasi self-maintaining bisa muncul TANPA seleksi dari kimia konstruktif + kelas ekuivalensi. Template untuk artificial chemistry 0and1. Tapi klaimnya "diversity of organizations within each level", bukan pertumbuhan kompleksitas tanpa batas; dan butuh observer untuk mendefinisikan organisasi — persis peran yang di 0and1 dipegang mesin "Newton".

### S14 — Adams et al. 2017 (unbounded evolution & innovation)
- Definisi, dari abstrak: "We define unbounded evolution as patterns that are non-repeating within the expected Poincaré recurrence time of an equivalent isolated system, and innovation as trajectories not observed in isolated systems."
- Uji: varian CA dengan aturan update yang berubah terhadap waktu, 3 cara. "Each is capable of generating conditions for open-ended evolution, but vary in their ability to do so. We find that **state-dependent dynamics**, widely regarded as a hallmark of life, statistically out-performs other candidate mechanisms, and is **the only mechanism to produce open-ended evolution in a scalable manner**."
- Batas (menurut S11): studi-studi ini "did not consider evolutionary dynamics of non-trivial self-replicators/self-reproducers in Langton's or von Neumann's sense; they merely focused on complex spatio-temporal nonlinear dynamics of cellular automata configurations."

Relevansi: satu-satunya kelas mekanisme yang diklaim scalable untuk OEE di CA = aturan yang bergantung pada state (hukum yang berubah). Kandidat kuat untuk desain hukum 0and1.

### S15 — Bedau, Snyder, Packard 1998 (metrik aktivitas evolusioner + kelas Tokyo)
Abstrak resmi, verbatim: "We present empirical evidence that long-term evolutionary dynamics fall into three distinct classes, depending on whether adaptive evolutionary activity is absent (class 1), bounded (class 2), or unbounded (class 3). These classes are defined using three statistics: **diversity, new evolutionary activity (Bedau & Packard 1992), and mean cumulative evolutionary activity (Bedau et al. 1996)**."
- Subjek uji: Holland's Echo model, "a random-selection adaptively-neutral 'shadow' of Echo", dan biosfer (rekaman fosil Fanerozoikum).
- Kesimpulan, verbatim: "This classification provides quantitative evidence that **Echo lacks the unbounded growth in adaptive evolutionary activity observed in the fossil record**." — model ALife klasik masuk kelas 2 (bounded), biosfer kelas 3.
- Catatan: istilah "Tokyo type" TIDAK muncul di abstrak S15; pemakaian istilah itu di paper 2026 (arXiv:2603.01701) belum saya buka. **UNVERIFIED** untuk penamaan.

---

## JAWABAN TERSTRUKTUR

### (a) Ada sistem digital dengan indefinite open-endedness?
TIDAK ADA, menurut bukti primer yang dibuka.
- Verdict eksplisit: S5 (Chan 2023) — "OEE has not been achieved". S11 (Sayama & Nehaniv 2024) — semua sistem di media terdistribusi menunjukkan dominasi akhir oleh satu/beberapa spesies ("pseudo-equilibrium"), dan tak diketahui prinsip umum untuk mencegahnya.
- S15 (Bedau 1998): model ALife klasik (Echo) secara kuantitatif TIDAK punya pertumbuhan aktivitas evolusioner tanpa batas, berbeda dari rekaman fosil.
- Klaim terbatas + ber-caveat: S12 Hash Chemistry ("unbounded growth ... of higher-order entities") tapi tanpa interaksi ekologis dan fitness = hash oracle; S14 Adams 2017 (state-dependent dynamics menghasilkan OEE "scalable") tapi hanya pada dinamika spatio-temporal CA, bukan replikator sejati.
- Failure mode terkumpul: (1) dominasi pola expanding / "goo" (S5); (2) kepunahan total (S5); (3) regresi ke bentuk terkecil (S10 evoloop; S1 Tierra ukuran menurun & kelas ukuran besar hilang); (4) plateau/saturasi (S5, S15); (5) kompleksitas hanya tumbuh menuju gradient perancang (S3 Avida); (6) tanpa interaksi ekologis → evolusi trivial (S12); (7) replikasi low-fidelity membunuh entitas kompleks (S12).

### (b) Metrik yang dipakai komunitas
1. **Diversity + new evolutionary activity + mean cumulative evolutionary activity** → klasifikasi class 1/2/3 (tak ada / bounded / unbounded). Sumber: S15; komponen new evolutionary activity dari Bedau & Packard 1992 (**UNVERIFIED**).
2. **Physical complexity** = informasi mutual genom–lingkungan (bit), diukur sebagai panjang sekuens − entropi per-lokus. Sumber: S2.
3. **Novelty + learnability terhadap observer** (loss-based, formal). Sumber: S6.
4. **Unbounded evolution (non-repetisi vs Poincaré recurrence time) + innovation (trajektori absen pada sistem terisolasi)**. Sumber: S14.
5. **Empat necessary conditions** (minimal criterion, novel opportunities, agent decisions, unbounded phenotype representation). Dikutip verbatim di S6 dari Soros & Stanley 2014 — sumber primernya **UNVERIFIED** (403 di semua rute).
6. Praktik pengukuran di continuous CA: fasa diversity/creativity, dominasi spesies, end-state "packed"/"goo"/"linear" — deskriptif, bukan skalar. Sumber: S5.
7. "Tokyo type 1" dipakai di arXiv:2603.01701 (2026) — belum dibuka. **UNVERIFIED**.

### (c) Substrat/rule class paling fertile menurut bukti primer
1. **CA konservatif/reversibel dengan hukum konservasi lokal** — S7 (conservative logic + BBM: gate universal dari tumbukan bola, reversibel + konservatif), S8 (BBMCA universal & konservatif; hukum konservasi lokal menarik TIDAK bergantung pada reversibilitas), S9 (NCCA: syarat perlu-cukup, flow diagram partikel dengan kecepatan, Rule 184). Fertile untuk PARTIKEL, TUMBUKAN, GATE — infrastruktur entitas & interaksi, bukan bukti open-endedness.
2. **Continuous CA (Lenia/Flow-Lenia)** — S4/S5: paling "biologis", >400 spesies, tapi konvergen. Mass conservation mengurangi QEP/LEP tapi tetap dominasi beberapa spesies.
3. **Artificial chemistry λ-calculus** — S13: organisasi self-maintaining muncul sebagai konsekuensi generik dari konstruksi + kelas ekuivalensi, tanpa seleksi; multi-level (L0→L1→L2). Fertile untuk EMERGENCE ORGANISASI.
4. **CA dengan aturan bergantung-state** — S14: satu-satunya mekanisme yang dilaporkan scalable untuk OEE dalam uji mereka.
5. **CA self-reproducing loop (von Neumann → Langton → SDSR → evoloop)** — S10/S11: membuktikan replikasi + evolusi Darwinian mungkin, tapi arah evolusi = mengecil.
6. **Non-spatial hash chemistry** — S12: pertumbuhan metrik tanpa batas, tapi tanpa ekologi.

### (d) Pelajaran desain

BERHASIL (didukung bukti primer):
- Mulai dari replikator hand-crafted dengan genom yang bisa bermutasi + operator genetik implisit (reproduksi via self-replication pola; seleksi via differential existential success) — S5; ekologi spontan (parasit/hiper-parasit/sosial/simbion/imunitas) — S1.
- Fungsi fitness ditentukan lokal oleh kreatur sendiri, bukan global oleh simulator → "pragmatic emergence" — S1.
- Lokalisasi informasi genetik + pemeliharaan genotype lokal & translasi ke phenotype — S5.
- Lingkungan TETAP yang berstruktur dapat-dipelajari + populasi besar + aseksual → kompleksitas genom naik secara terpaksa (Maxwell demon) — S2.
- Self-maintaining organization muncul tanpa seleksi bila kimia punya (i) konstruksi (tumbukan menghasilkan molekul baru spesifik) dan (ii) kelas ekuivalensi — S13.
- Memisahkan genotype/phenotype dan membiarkan variasi genotipik berasal dari variasi fenotipik preseden — S10.
- Mass conservation & energy constraints sebagai mitigasi expanding patterns — S5 (diusulkan; belum terbukti untuk horizon tak terbatas; penulis memperingatkan bisa membatasi kreativitas).
- Aturan update yang bergantung pada state — S14.

GAGAL (didukung bukti primer):
- Tanpa mekanisme pembatas: saturasi replika / "goo" / dominasi expanding pattern → kepunahan diversitas genetik — S5.
- Dengan penalti eksplisit terhadap pola expanding: tetap dominasi LEP atau kepunahan total — S5.
- Arah evolusi ke struktur lebih kecil lebih cepat (self-reproduction lebih cepat) → populasi mengecil, jalur ke kompleksitas lebih besar buntu — S10.
- Lingkungan sederhana → genom sederhana; lingkungan berubah → kompleksitas turun; seks → akumulasi mutasi deleterius — S2.
- Kompleksitas tumbuh hanya menuju reward yang dipasang perancang — S3.
- Ekosistem tanpa interaksi antar entitas → refinement nilai fitness multiset independen, bukan organisasi — S12.
- Replikasi low-fidelity → entitas kompleks mati — S12.
- Konstruktor universal von Neumann (1966) belum pernah dipakai untuk evolusi Darwinian; self-repair/autopoiesis belum pernah dicapai self-reproducer artifisial mana pun — S11.

---

## KANDIDAT LANJUTAN (belum diverifikasi di sini)
- arXiv:2603.01701 (2026) "A speciation simulation that partly passes open-endedness tests" — "unbounded total cumulative activity" tapi menyimpulkan "not open-ended".
- arXiv:2604.11248 (2026) "Evolving Many Worlds: Towards Open-Ended Discovery in Petri Dish NCA via Population-Based Training".
- arXiv:2506.08569 (2025) Flow-Lenia — mass-conservative continuous CA, multispecies.
- arXiv:2407.03345 (2024) Adams et al. — constraint "completely conserved, quasi-conserved, conditionally conserved"; relevan untuk desain hukum konservatif 0and1.
- arXiv:1806.01883 Taylor — routes to open-endedness (exploratory / expansive / transformational).
