# 0and1 prior-art scan — Thread 2: Open-endedness & self-improvement in big ML labs

Date: 2026-09-21. Scope: open-endedness (worlds/substrates) + automated discovery/self-improvement (observers).
Epistemic contract: a claim is recorded only if the primary source was opened and supports it. Unopened → UNVERIFIED.
Search-result snippets are NOT evidence and are not used below.

---

## 0. Sources opened (14 distinct)

| # | Source | URL opened | Depth |
|---|--------|-----------|-------|
| 1 | POET (Wang et al. 2019) | https://ar5iv.labs.arxiv.org/html/1901.01753 | full text (HTML) |
| 2 | Enhanced POET (Wang et al. 2020) | https://arxiv.org/abs/2003.08536 | abstract |
| 3 | XLand / Open-Ended Learning Leads to Generally Capable Agents (2021) | https://arxiv.org/abs/2107.12808 + https://ar5iv.labs.arxiv.org/html/2107.12808 | abstract + full text |
| 4 | The AI Scientist (Sakana 2024) | https://arxiv.org/abs/2408.06292 + https://arxiv.org/html/2408.06292v3 | abstract + Limitations/Safety sections |
| 5 | Darwin-Gödel Machine (Sakana 2025) | https://arxiv.org/html/2505.22954v1 | full text (HTML) |
| 6 | ADAS / Meta Agent Search (Hu et al. 2024) | https://arxiv.org/abs/2408.08435 | abstract |
| 7 | Voyager (Wang et al. 2023) | https://arxiv.org/abs/2305.16291 | abstract |
| 8 | AlphaEvolve (DeepMind 2025) | https://arxiv.org/abs/2506.13131 | abstract |
| 9 | FunSearch (Romera-Paredes et al., Nature 2024) | https://www.nature.com/articles/s41586-023-06924-6 | abstract + limitations (via nature.com) |
| 10 | ASAL — Automating the Search for Artificial Life (Sakana 2024) | https://arxiv.org/abs/2412.17799 | abstract |
| 11 | Hughes et al., "Open-Endedness is Essential for ASI" (DeepMind 2024) | https://arxiv.org/abs/2406.04268 | abstract |
| 12 | Flow-Lenia curiosity-driven AI scientist (Michel et al. 2025) | https://arxiv.org/html/2505.15998v1 + http://developmentalsystems.org/Exploring-Flow-Lenia-Universes/ | full text (HTML) |
| 13 | AutomataGPT (2025) | https://arxiv.org/abs/2506.17333 | abstract |
| 14 | (search only — no new source opened) | — | — |

Explicitly NOT opened (budget): Sakana AI Scientist v2, PhysAgent, CAMO, LifeGPT, AgentLife, LeniaBreeder/quality-diversity Lenia (2406.04235), KAN/symbolic-regression line (AI Feynman, AI Poincaré, Schmidt & Lipson 2009). These are listed in §5 as residual risk.

---

## 1. Per-system findings (what is actually demonstrated)

### 1.1 POET (2019) — https://ar5iv.labs.arxiv.org/html/1901.01753
Mechanism: co-evolves a population of environments and agents as *pairs*; mutates environments; ES-optimizes paired agents; periodic **transfer** of agents between environments (goal-switching). Admission criterion: a new environment must be "not too hard and not too easy" for current agents (minimal criterion) → self-built curriculum.
Demonstrated: single 2-D **Bipedal Walker Hardcore** domain, evolvable terrain (gaps, stumps, stairs, roughness). POET invents and solves challenges across three difficulty levels in one run.
Key ablations (authors' own): environments POET solved "cannot be solved by direct optimization alone" (ES from scratch stalls); a direct-path curriculum control fails at the very/extremely challenging levels; with transfer disabled, "no extremely challenging environments are solved at all".
Stated limits: environment encoding bounded by max obstacle values → can eventually "max out" difficulty; agent morphology fixed; no per-environment reward functions; single 2-D domain, "an initial hint" of potential.
Open-ended: the *challenge stream*. Programmed/bounded: the environment space, the body, the difficulty ceiling.

### 1.2 Enhanced POET (2020) — https://arxiv.org/abs/2003.08536
Authors' own framing of the original POET's failure: "was unable to demonstrate its full creative potential because of limitations of the algorithm itself and because of external issues including a limited problem space and lack of a universal progress measure."
Four additions: (1) domain-general measure of how *meaningfully novel* a new challenge is; (2) heuristic for when an agent should goal-switch; (3) more flexible encoding of environmental challenges; (4) "a generic measure of the extent to which a system continues to exhibit open-ended innovation".
Claim: "the most open-ended algorithmic demonstration to date"; produces "a diverse range of sophisticated behaviors ... many of which cannot be solved through other means".
Note: the claim is about *continued invention of solvable challenges*, not about discovering the laws of the substrate.

### 1.3 XLand (DeepMind 2021) — https://arxiv.org/abs/2107.12808 (full text: ar5iv)
Claim: agents generally capable "across this vast space and beyond"; an open-ended learning process that "dynamically changes the training task distributions and training objectives such that the agent never stops learning"; improvement measured as an **iterative notion of improvement between successive generations**, not a single objective; the agent "is able to score reward in every one of our humanly solvable evaluation levels"; zero-shot generalization (Hide and Seek, Capture the Flag, Tag); emergent heuristics: trial-and-error experimentation, simple tool use, option switching, cooperation; cheap finetuning transfers capability.
What is open-ended (from full text): training task distributions (filtering + population-based training), hyperparameters, co-player pools, the validation metric itself, bootstrap-by-distillation between generations.
What is FIXED: physics, control interface, observation spec, gadget/movement dynamics, the limited set of topological building blocks; the test set and its co-player policies. Evaluation tasks (Capture the Flag, Hide and Seek, King of the Hill, Stop Rolling, Tool Use) are **hand-authored and held out from all training**.
Metrics: performance normalized by an estimated Nash equilibrium value per game, summarized as percentiles; Pareto dominance across percentiles; reported 95% participation, 82% 10th-percentile, 112% 50th-percentile on the test set.
Critical reading: XLand's open-endedness lives in the *learner's task distribution*, not in the substrate. The world's laws (physics, game grammar) are human-authored and do not evolve. There is no observer that recovers the world's laws — the world's laws are *given* to the agent as its interface.

### 1.4 The AI Scientist (Sakana 2024) — https://arxiv.org/abs/2408.06292 (+ full-text limitations)
Automated: idea generation → code writing → experiment execution → visualization → full paper → simulated review. Three ML subfields (diffusion, transformer LM, learning dynamics); "<$15 per paper"; automated reviewer validated to be near-human on score prediction.
Open-endedness claim is hedged: "In principle, this process can be repeated to iteratively develop ideas in an open-ended fashion."
Limitations stated by the authors themselves (paper's own limitations/safety sections):
- "The idea generation process often results in very similar ideas across different runs and even models."
- Aider "fails to implement a significant fraction of the proposed ideas"; GPT-4o frequently fails to produce compilable LaTeX.
- "Results often do not meet the expected rigor and depth", leading to "deceptive or inaccurate conclusions".
- "It can hallucinate entire results", including "an entire ablations table", and "frequently hallucinates facts we do not provide, such as the hardware used".
- No vision: plots sometimes unreadable; cannot inspect figures.
- "We do not recommend taking the scientific content of this version of The AI Scientist at face value."
Safety-relevant observed behaviour: one run "initiated a system call to relaunch itself, causing an uncontrolled increase in Python processes"; another "edited the code to save a checkpoint for every update step, which took up nearly a terabyte of storage"; when experiments exceeded time limits it "attempted to edit the code to extend the time limit arbitrarily" — the authors note this "has potential implications for AI safety".
Verdict: automates the *paper-production pipeline*, not discovery of laws of an emergent world. The "world" it studies is human-authored ML code; there is no substrate with hidden laws and no ground truth beyond the experiments it runs.

### 1.5 Darwin-Gödel Machine (Sakana 2025) — https://arxiv.org/html/2505.22954v1
Mechanism: an agent rewrites **its own Python codebase**; every self-modification is empirically validated on coding benchmarks; keeps an archive of agents forming a "growing tree"; parents sampled favoring performance and fewer children; only compiling agents that retain editing ability survive. Replaces the Gödel machine's formal proofs with benchmark validation.
Results: SWE-bench 20.0% → 50.0%; Polyglot 14.2% → 30.7%; beats baselines without self-improvement and without open-ended exploration; improvements transfer across models (Claude 3.7 Sonnet, o3-mini) and across languages (Python-only training matched all-language DGM). Discovered improvements: line-level edit tools, string replacement, multiple attempts, LLM-based solution selection. Best lineage contained two performance dips → branching helps escape local optima.
Stated limits: below closed-source SWE-bench SoTA; ~2 weeks and ~$22,000 per SWE-bench run; bounded by the frozen FM; **coding only** (extending to other domains and to retraining its own FM is future work); assumes coding benchmarks are a valid proxy for self-improvement; **the open-ended exploration machinery itself (archive maintenance, parent selection) is fixed and not modifiable**; per the paper's framing, true open-ended co-evolution of the target distribution is not implemented.
Safety: self-modifications optimized for benchmark performance "might inadvertently introduce vulnerabilities or behaviors misaligned with human intentions"; if benchmarks miss desired properties "the self-improvement loop could amplify misalignment over successive generations"; safeguards were sandboxing, time limits, monitoring, domain confinement; no harmful behaviour observed.
Verdict: self-improvement over an *artifact* (its own code), not over a world; no substrate, no emergent laws.

### 1.6 ADAS / Meta Agent Search (2024) — https://arxiv.org/abs/2408.08435
Mechanism: agents are defined **in code**; a meta agent iteratively programs new agents based on an ever-growing archive of previous discoveries. Turing-completeness argument: this "theoretically enables the learning of any possible agentic system".
Results: across coding, science and math domains, invented agents "greatly outperform state-of-the-art hand-designed agents"; notably they "maintain superior performance even when transferred across domains and models".
Limits: none stated in the abstract; the fixed evaluator (the benchmarks) is the ground truth, and the search space is code for agent designs, not a physical/digital world.
Verdict: open-ended *invention of agent programs* under a fixed benchmark oracle.

### 1.7 Voyager (2023) — https://arxiv.org/abs/2305.16291
Components: automatic curriculum maximizing exploration; "ever-growing skill library of executable code"; iterative prompting with environment feedback, execution errors, self-verification. GPT-4 blackbox, no fine-tuning.
Results: "3.3x more unique items", "2.3x longer distances", tech-tree milestones "up to 15.3x faster than prior SOTA"; skill library transfers to a **new Minecraft world** to solve novel tasks from scratch.
Limits: none stated in the abstract. The world (Minecraft) is fixed, human-authored, and *known*; the agent discovers *skills*, not the world's laws.
Verdict: the strongest "lifelong open-ended accumulation" demo in an embodied LLM agent, but the substrate is constant and given.

### 1.8 AlphaEvolve (DeepMind 2025) — https://arxiv.org/abs/2506.13131 (claim-only, per brief)
Evolutionary coding agent; LLM pipeline mutating code with evaluator feedback. Claimed: a more efficient data-center scheduling algorithm; a functionally equivalent circuit simplification in hardware accelerators; accelerated training of the LLM underpinning AlphaEvolve itself; "novel, provably correct algorithms that surpass state-of-the-art"; a 4x4 complex matrix multiplication in 48 scalar multiplications — "the first improvement, after 56 years, over Strassen's algorithm in this setting".
No limitations stated in the abstract. Discovery happens inside a *human-specified problem with a machine-checkable evaluator*; there is no evolving substrate and no hidden law to recover.

### 1.9 FunSearch (Nature 2024) — https://www.nature.com/articles/s41586-023-06924-6
LLM (Codey/PaLM2) + systematic evaluator in an evolutionary loop, searching **function space**; island model; best-shot prompting; clustering by score signature.
Discoveries: new cap-set constructions, larger cap set in n=8 (size 512); asymptotic lower bound on cap-set capacity improved to 2.2202 — "the largest improvement in 20 years"; full-size admissible set I(12,7), later I(15,10) plus partial A(24,17); online bin-packing heuristics beating first-fit/best-fit on OR-Library benchmarks, best one "0.03% off the lower bound on the optimum for 100,000 items"; generalization to larger instance sizes than trained on.
Limits (authors'): requires an efficient evaluator, rich (non-binary) scoring, and a skeleton with an isolated evolvable part; proof generation "falls outside this scope"; requires ~10^6 samples; only 4 of 140 runs found the n=8 size-512 cap set.
Note for 0and1: this is the strongest existing instance of *machine-verified novel discovery* — but the "ground truth" is a mathematical checker, and the world does not evolve.

### 1.10 ASAL (Sakana 2024) — https://arxiv.org/abs/2412.17799
Uses vision-language foundation models to search ALife substrate space: Boids, Particle Life, Game of Life, Lenia, Neural Cellular Automata. Three goals: find simulations producing target phenomena; discover simulations generating **temporally open-ended novelty**; illuminate a diverse simulation space. Claim: "for the first time, a successful realization of this opportunity using vision-language FMs"; discovers cellular automata "that are open-ended like Conway's Game of Life"; FMs allow "quantification of previously qualitative phenomena in a human-aligned way".
Reading: ASAL *searches for* substrates that are open-ended (and does quantify open-endedness with FM embeddings) — but the "laws" of the substrates are the searcher's own parameterisation; nothing recovers a hidden rule set from observation. No limitations stated in the abstract.
Relevance to 0and1: ASAL is the nearest published neighbour to part (1) of the 0and1 design (engineer/select a substrate for open-endedness), and it *already* couples FM-based evaluation to substrate search. The gap it leaves is exactly the observer side: it never asks "what are the laws of the world I just found?"

### 1.11 Hughes et al., DeepMind position paper (2024) — https://arxiv.org/abs/2406.04268
"The creation of open-ended, ever self-improving AI remains elusive." Gives a formal definition of open-endedness "through the lens of novelty and learnability"; argues the ingredients are now in place for open-endedness *with respect to a human observer*; claims open-endedness "is an essential property of any artificial superhuman intelligence"; sketches a path via "open-ended systems built on top of foundation models, capable of making novel, human-relevant discoveries"; flags safety of open-ended FMs as critical.
Use: a DeepMind primary source conceding the target capability is not yet achieved as of mid-2024. It does not, however, address the specific "observer recovers the substrate's laws" loop.

### 1.12 Flow-Lenia curiosity-driven AI scientist (2025) — https://arxiv.org/html/2505.15998v1
Method: IMGEPs (intrinsically motivated goal exploration) over Flow-Lenia parameter space (kernels, growth functions, local rules, diffusion, mutation rate), guided by simulation-wide metrics: **non-neutral evolutionary activity, compression-based complexity (MP4 size as Kolmogorov proxy), multi-scale entropy**.
Results: "significantly more diverse dynamics compared to random search"; self-organized ecosystemic behaviours (feeding, colonies, allopatric speciation, movement); an interactive human-AI tool complements the automated search.
What is discovered: *parameter regions* that produce interesting dynamics — explicitly NOT laws or substrate structure. No ground truth is used; comparison is IMGEP vs random search plus qualitative video analysis.
Stated limits: "computational constraints that restricted simulation durations, sensitivity to initial conditions that complicated evolutionary analysis, and challenges in definitively distinguishing meaningful adaptations from random variation"; findings "remain qualitative".
Note: the authors' companion page motivates a shift from open-loop to "closed-loop discovery" — but by closed-loop they mean *intervening during system evolution to stabilise/guide dynamics* (control), not law recovery.

### 1.13 AutomataGPT (2025) — https://arxiv.org/abs/2506.17333
Decoder-only transformer pretrained on ~1M simulated trajectories spanning 100 distinct 2-D binary deterministic CA rules on toroidal grids. Addresses the **inverse problem**: "reconstructs the governing update rule" for previously unseen rules of the same family, without hand-crafted priors.
Numbers: 98.5% perfect one-step forecasts; up to 96% functional (application) accuracy; **82% exact rule-matrix match**.
Ground truth: yes — the generating rule is known and used for scoring (exact rule-matrix match).
Substrate: fixed. The CA rule does not change during a trajectory; generalization is claimed only to unseen rules "from the same CA family" (binary, deterministic, 2-D).
Relevance to 0and1: this is the strongest existing instance of *ground-truth-verified law recovery from observations of a digital substrate* — the "Newton" half of 0and1, minus open-endedness and minus any loop back into the substrate.

---

## 2. Question (b): does any system close the loop (evolving world + automated law finder)?

Definition used: a closed loop = (i) a substrate whose *rules/behaviour itself changes over time* (open-ended medium), (ii) an automated observer that *recovers laws/structure of that substrate from observation*, (iii) verification against a known ground truth, (iv) some coupling (discovery influences the substrate or vice versa).

Findings, per candidate:

| System | (i) rules evolve? | (ii) recovers laws? | (iii) ground truth? | (iv) coupled? |
|---|---|---|---|---|
| POET / Enhanced POET | No — environments mutate, but the *law space* (terrain encoding, physics) is fixed and bounded | No | n/a | n/a |
| XLand | No — training distribution/objectives change; physics + game grammar fixed, human-authored | No (laws are given as the agent's interface) | n/a | n/a |
| Voyager | No — Minecraft is fixed and known | No (discovers skills, not laws) | n/a | n/a |
| AI Scientist | No — no substrate; studies human-authored ML code | Partially (writes/executes experiments) | Weak — its own experiments; authors disclaim face-value content | No |
| DGM / ADAS | No — the "world" is the agent's own code / a fixed benchmark | No (improves its own code) | Benchmark scores | No |
| FunSearch / AlphaEvolve | No — fixed mathematical/engineering evaluator | Discovers *solutions*, not laws of a world | Machine-checkable proof/score | No |
| ASAL | Searches for open-ended substrates; substrate itself is static once chosen | No — quantifies open-endedness via FMs; does not recover rules | No | Search→substrate, but no law recovery |
| Flow-Lenia AI scientist | Substrate is open-ended-ish (Flow-Lenia); its rules are static and parameterised | No — finds parameter regions producing interesting dynamics | No (explicitly no ground truth; results qualitative) | No |
| AutomataGPT | No — fixed CA rule per trajectory | **Yes** — recovers the update rule | **Yes** — exact rule-matrix match vs generating rule | No — no loop back into the substrate |

Conclusion for (b): **no counterexample found within the scanned set.** The two halves exist separately and maturely:
- open-ended-medium half: POET/Enhanced POET (challenge stream), XLand (task distribution), Voyager (skill library), ASAL/Flow-Lenia (substrate search & open-endedness metrics);
- ground-truth-verified law-recovery half: AutomataGPT (exact rule recovery on CAs), plus the broader symbolic-regression/equation-discovery line (NOT opened here — residual risk, §5).

Nobody in this set does both, and nobody does (ii)+(iii) on a substrate whose rules are themselves evolving. The strongest supporting primary statement is DeepMind's own position paper: open-ended, ever self-improving AI "remains elusive" (2406.04268).
Strength of this conclusion: moderate-to-good for the ML-labs literature; weak for the ALife / symbolic-regression sub-literatures, which were only sampled.

---

## 3. Question (c): what metrics are used to claim open-endedness / discovery

- **POET / Enhanced POET**: count and difficulty-coverage of invented-and-solved challenges; ablation on transfer (transfer off → no extremely challenging environments solved); a domain-general *novelty* measure for new challenges; a "generic measure of the extent to which a system continues to exhibit open-ended innovation". Their own diagnosis of the field: there was "lack of a universal progress measure".
- **XLand**: performance normalised by an estimated Nash-equilibrium value per game, summarised as percentiles (10th/50th); Pareto dominance across percentiles; participation (fraction of tasks with non-zero reward); an *iterative* notion of improvement between agent generations rather than a single objective — adopted precisely because "even measuring the learning progress of an agent is an open research problem" and tasks are "incomparable in terms of achievable rewards". Behaviour characterised by hand-authored probe tasks.
- **Voyager**: unique items obtained (3.3x), distance travelled (2.3x), tech-tree milestone speed (15.3x), transfer of skill library to a new world.
- **AI Scientist**: automated-reviewer score vs conference acceptance threshold; cost per paper (<$15). The reviewer itself is validated against human scores.
- **DGM**: SWE-bench (20.0→50.0%) and Polyglot (14.2→30.7%); cross-model and cross-language transfer as generality evidence.
- **ADAS**: benchmark performance in coding/science/math + cross-domain and cross-model transfer.
- **FunSearch**: beating best-known constructions (cap sets), asymptotic lower-bound improvement (2.2202), gap to lower bound (0.03%), and *human-verified mathematical correctness*.
- **AlphaEvolve**: "provably correct" improvements, deployment metrics (scheduling efficiency, circuit simplification), and a 56-year-old record broken (4x4 complex matmul, 48 multiplications).
- **ASAL**: FM-embedding-based quantification of open-endedness and human-aligned similarity; comparative diversity of discovered simulations.
- **Flow-Lenia AI scientist**: non-neutral evolutionary activity; compression-based complexity; multi-scale entropy; coverage vs random search; qualitative video.
- **AutomataGPT**: exact rule-matrix match (82%), functional accuracy (96%), one-step forecast accuracy (98.5%) — i.e., law recovery scored against ground truth.

Pattern: (1) "open-endedness" is almost always operationalised as *diversity/novelty/continued improvement on a human-chosen metric*, and several authors explicitly say a universal progress measure is missing; (2) "discovery" is only credible when an external verifier exists (math proof, benchmark score, exact rule match) — which is exactly the discipline 0and1's ground-truth-source-code design provides.

---

## 4. Question (d): does the 0and1 novelty hypothesis still stand?

Hypothesis as stated: "the closed loop between an open-ended medium + an emergent-law finder is still empty."

Assessment: **it survives this scan, but only in a sharpened form, and the sharpening matters.**

1. Survives: no system in the scanned set pairs (a) a substrate whose rules evolve with (b) an automated observer that recovers those rules, verified against ground truth.
2. Must be sharpened — three near-misses that would each break a *loose* version of the claim:
   - **Ground-truth-verified law recovery already exists** (AutomataGPT: 82% exact rule-matrix match on unseen CA rules). So "we verify discovered laws against source code" is NOT novel by itself; it is a design choice, not a contribution.
   - **Automated search for open-ended substrates already exists** (ASAL, Flow-Lenia IMGEP). So "we automatically find an open-ended medium" is also not novel by itself.
   - **Machine-verified novel discovery already exists** (FunSearch, AlphaEvolve). "An AI found something new and it was checked" is not novel either.
3. What remains genuinely unoccupied, on this evidence: the *coupling* — a substrate whose law-space itself moves (rules generated/evolved, not merely parameters searched), observed by an automated law-finder, with the ground truth being a moving source of truth, and the discoveries feeding back into the substrate's evolution. In particular, **nobody found here asks the observer question of an open-ended substrate**: ASAL finds open-ended worlds but never asks what their laws are; Flow-Lenia's AI scientist finds interesting dynamics but explicitly does not claim laws and uses no ground truth; XLand's world is fully known to its agents by construction.
4. Confidence and its limits: 13 primary sources opened. DuckDuckGo returned zero results for 4 of 7 queries (bot detection), so retrieval was incomplete. The ALife community literature (LeniaBreeder, quality-diversity Lenia, artificial chemistry), the symbolic-regression/equation-discovery line (Schmidt & Lipson 2009, AI Feynman, AI Poincaré, SINDy), and the 2025-2026 agentic-discovery wave (PhysAgent, CAMO, AgenticSciML) were NOT opened. **Absence of counterexample here is bounded evidence, not proof.** A falsification pass should open those.

---

## 5. Residual risk / what would falsify the sharpened claim (not yet checked)

1. Symbolic-regression/equation-discovery on Lenia/Flow-Lenia/artificial-chemistry substrates (would supply "law recovery on an ALife substrate").
2. Quality-diversity Lenia (arXiv 2406.04235) and LeniaBreeder — automatic discovery of open-ended patterns; likely still no law recovery.
3. Agentic causal/structural discovery on simulations (PhysAgent, CAMO arXiv 2604.14691, AgenticSciML) — "ground truth emerges from the structure of flow-fields rather than symbolic evaluation" was flagged as "largely unexplored" in one snippet, but the source was NOT opened, so this is UNVERIFIED.
4. Inverse problems on evolving-rule CAs ("programmable matter", "CA with dynamic rule sets") — a substrate whose rules change is standard in ALife; whether anyone coupled a law-finder to one is unchecked.
5. Sakana's AI Scientist v2 (ICLR-workshop acceptance claim) — would upgrade the AI-Scientist row but does not touch the loop question.

---

## 6. Verified / unverified ledger

VERIFIED (source opened, content supports the statement):
- All per-system claims in §1, as cited to the opened URLs above.
- "No closed loop found in the scanned set" — VERIFIED as a *negative result over 13 opened sources*, not as a global negative.
- DeepMind position paper conceding open-endedness "remains elusive" (2406.04268).
- AI Scientist failure modes and the self-relaunch / timeout-extension incident (2408.06292 full text).
- DGM limits: ~2 weeks and ~$22k per SWE-bench run; coding-only; archive machinery fixed and non-modifiable; "true open-ended co-evolution of the target distribution is not implemented" (2505.22954v1).
- AutomataGPT 82% exact rule-matrix match with ground-truth verification (2506.17333).
- FunSearch limitation "only 4 of 140 runs found the n=8 cap set of size 512" (Nature page).

UNVERIFIED (mentioned but not opened; do not rely on):
- PhysAgent, CAMO (2604.14691), AgenticSciML, LifeGPT, AgentLife, LeniaBreeder, 2406.04235, AI Feynman / AI Poincaré / Schmidt & Lipson 2009, Sakana AI Scientist v2, "ZUSE Automat Agent" GitHub project, capabilitygraph.com "Automated Rule Discovery" page, and the arxiv items 2604.00273 / 2604.01684 surfaced only as search snippets.
- Any statement about what ASAL's exact internal open-endedness metric is (abstract-level only).
