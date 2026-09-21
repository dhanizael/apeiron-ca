# 0and1 — Prior-art scan: agentic discovery / moving law space
Date: 2026-09-21. Method: arXiv abs pages opened directly (primary), arXiv API metadata search
(https, rate-limited ~3.5 s/query), ChinaXiv + lab project pages for non-arXiv items.
Epistemic rule applied: a claim is stated only after the primary page was opened and its abstract
body supports it. Items not opened are labelled UNVERIFIED with reason.

---

## 0. Executive answer

No work was found that combines (i) a substrate whose *law space itself* moves, (ii) an automatic
law-discovery engine on top, (iii) verification against a ground truth that also moves, (iv) feedback
of discovered law into the substrate. Conditions (i)+(ii) never co-occur in one system; (iii) and
(iv) occur **nowhere at all** in the opened literature.

The single strongest near-miss for (i) is LOGOS-CA (2602.00036): rules are natural-language strings
executed by an LLM, explicitly to "transcend the constraints of ... fixed rules". It has no
law-discovery engine, no ground-truth verification, no feedback.
The strongest near-miss for (ii) is SciExplorer (2509.24978): an LLM agent that explores an unknown
system and recovers its equations of motion / Hamiltonian. Ground truth is static, the system is not
a substrate we control, no feedback.

The novelty claim survives this scan. See §5 for the mandatory related-work list.

---

## 1. Verification of the explicitly listed items

### 1.1 "PhysAgent" — name collision, THREE unrelated works
| arXiv | Title | Verdict |
|---|---|---|
| 2607.16355 | PhysAgent: Reflective Agentic Physics Control for Physically Plausible Video Generation (2026-07-17) | VERIFIED, but irrelevant: physics-program generation + repair for **video synthesis**, not law discovery |
| 2606.08688 | PhysAgent: Automating Physics-Based 4D Synthesis via Trajectory-Grounded Multi-Agent Feedback (2026-06-07) | exists (arXiv API metadata only; abstract not opened → UNVERIFIED detail); 4D synthesis, not law discovery |
| 2608.00066 | PhysAgent: A Multi-Agent Framework for Reliable Remote Heart Rate Estimation (2026-07-29) | exists; unrelated (rPPG) |

The PhysAgent the snippet meant — "multi-agent, automated discovery of physical laws" — is **not on
arXiv**. Primary source: Han, Gao, Lu, Guo, *PhysAgent: A Multi-Agent Approach to Automated Discovery
of Physical Laws*, ChinaXiv chinaxiv-202508.00189, submitted 2025-07-30.
https://chinarxiv.org/items/chinaxiv-202508.00189 (mirrored on Qeios J2MXUW)
Opened content: Mentor / Student / Leader agents; integrates Quantum ESPRESSO, VASP; "demonstrate its
capability to autonomously derive physical laws without prior knowledge — for example, deriving
Kepler's laws from orbital data and Newton's second law from forced motion experiments".
Coupling check: ground truth = textbook laws, **static**. No substrate, no law-space evolution, no
feedback of discovered law into any world. Closes none of (i)-(iv).

### 1.2 "CAMO" — VERIFIED = arXiv 2604.14691
CAMO: An Agentic Framework for Automated Causal Discovery from Micro Behaviors to Macro Emergence in
LLM Agent Simulations (2026-04-16). (Search results also show an ACL Findings 2026 PDF at
aclanthology.org/2026.findings-acl.1224.pdf — that page was NOT opened, so the venue is UNVERIFIED;
the arXiv abs page was opened and is the basis for everything below.)
Opened abstract: converts mechanistic hypotheses into computable factors grounded in simulation
records; learns a compact causal representation centered on emergent target Y; outputs a computable
Markov boundary + minimal upstream explanatory subgraph; "uses simulator-internal counterfactual
probing to orient ambiguous edges and revise hypotheses when evidence contradicts the current view".
Coupling check: substrate = LLM-agent social simulation with **fixed source code**; the discovered
object is a *statistical causal graph*, not the substrate's generative rule in symbolic form; there is
no ground-truth rule source to verify against (so not our "Newton vs source code" test); no feedback
into the simulator. Closes (ii) partially, in a different sense (causal, not generative-law).

### 1.3 "AgenticSciML" — VERIFIED = arXiv 2511.07262
AgenticSciML: Collaborative Multi-Agent Systems for Emergent Discovery in Scientific Machine Learning
(2025-11-10). Opened abstract: >10 specialized agents propose/critique/refine SciML *solutions*
(architectures, loss formulations, training strategies) with structured debate, retrieval-augmented
method memory, ensemble-guided evolutionary search.
Coupling check: the discovered object is a **solver design**, not the law of a world. Ground truth =
fixed benchmark tasks (physics-informed learning, operator learning). No substrate, no moving law
space, no feedback. Closes nothing.

### 1.4 "LifeGPT" — VERIFIED = arXiv 2409.12182 (v2)
LifeGPT: Topology-Agnostic Generative Pretrained Transformer Model for Cellular Automata
(2024-09-03; journal version npj s44387-025-00014-w). Opened abstract: decoder-only GPT simulating
Conway's Life on a toroidal grid with no prior knowledge of grid size or boundary conditions; 98.5%+
one-step accuracy; "autoregressive autoregressor" recursion.
Coupling check: it is a **learned forward simulator** of one fixed rule (Life), not symbolic rule
recovery, not an LLM in the language sense (snippet mis-describes it), rule space static, no feedback.
Closes none of (i)-(iv). Relevant only as a substrate-surrogate baseline.

### 1.5 "AgentLife" — NOT ON ARXIV (no paper)
arXiv API `all:"AgentLife"` → 0 entries. Primary source is a lab project page:
https://mpcrlab.com/projects/AgentLife-Artificial-Life-Meets-Agent-LLMs/ (MPCR Lab).
Opened content: "artificial life ecosystems on a cellular automata substrate where each cell is an LLM
agent"; agents undergo mutation (prompt perturbation), selection (fitness), crossover (context
merging); emergent communication protocols. Cost noted as the limiting factor.
Coupling check: what evolves is the **agents**, not the CA transition rule; the page mentions no
automatic rule discovery, no ground-truth rule source, no feedback into the substrate. No arXiv ID,
venue or year on the page. Closes nothing. (Other "AgentLife" hits — agentlife.io, Quaid-Labs
benchmark, Maxwell-AI-lab debugger — are unrelated products/benchmarks.)

### 1.6 "LeniaBreeder" + the QD-Lenia line — VERIFIED = arXiv 2406.04235
Faldor & Cully, Toward Artificial Open-Ended Evolution within Lenia using Quality-Diversity
(2024-06-06). The framework is *named* Leniabreeder in the paper, hence the snippet name.
Opened abstract: QD evolves a large population of diverse lifelike self-organizing patterns in Lenia
(continuous CA), with manually defined or learned diversity criteria.
Coupling check: searches **parameters inside a fixed family** (Lenia); no law recovery engine, no
ground truth, no feedback. Line continues in ASAL / ASAL++ (§2.2, §2.3).

### 1.7 arXiv 2406.04235 — what it actually is
= the Leniabreeder paper above. Not a law-discovery paper. VERIFIED.

### 1.8 "AI Scientist v2" — VERIFIED = arXiv 2504.08066
The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search (Sakana,
2025-04-10). Opened abstract: end-to-end agentic system producing the first entirely AI-generated
peer-review-accepted workshop paper; progressive agentic tree search with an experiment-manager agent;
VLM feedback loop for figures; no reliance on human-authored templates.
Coupling check: the "world" is ML research; ground truth = experimental results of a static benchmark,
not a generative-law source; no substrate whose laws move; no feedback into a substrate. Closes
nothing of (i)-(iv). It is a *process* analogue of our Newton engine, not a structural one.

### 1.9 arXiv 2604.00273 — VERIFIED (exists), content = CA law *analysis*, static
Pita, How local rules generate emergent structure in cellular automata (2026-03-31).
Opened abstract: shows the ECA look-up table "contains a readable causal architecture"; formalizes
pairwise interactions as tiles; a finite-state tiling transducer composes tiles across the lattice;
the count of local configurations where coupling is structurally impossible predicts dynamically
decoupled regions with Spearman rho = 0.89 (p < 1e-31).
Coupling check: direction is **rule -> structure** (forward analysis of a known rule), not
observation -> rule. Static rule set, no agent, no ground truth that moves, no feedback. It is a
useful *static* prior for "what a readable law looks like", and a possible citation for "existing
tools reconstruct structure from observed dynamics" (their framing).

### 1.10 arXiv 2604.01684 — VERIFIED to EXIST, but the claimed content is FALSE
Actual title: Zhang, Feng, An, *Smoluchowski Coagulation Equation and the Evolution of Primordial
Black Hole Clusters* (2026-04-02). Pure astrophysics; nothing to do with CA / ALife / law discovery.
=> The snippet that pointed at this ID was a hallucination / mismatched reference. Treat that snippet
source as unreliable for ID-level claims.

---

## 2. Items found while scanning that the list missed (question c)

### 2.1 SciExplorer — arXiv 2509.24978 (THE most important related-work item)
Agentic Exploration of Physics Models (2025-09-29; published in Phys. Rev. X, doi 10.1103/xnqc-q6nt).
Opened abstract: "SciExplorer, an agent that leverages large language model tool-use capabilities to
enable exploration of systems without any domain-specific blueprints, applied to physical systems that
are initially unknown to the agent"; minimal tool set, mostly code execution; recovers equations of
motion from observed dynamics and infers Hamiltonians from expectation values; tested on mechanical
dynamical systems, wave evolution, quantum many-body physics; no fine-tuning.
Coupling check: this is the closest published *Newton engine*. But the substrate is a **fixed** physical
model chosen by the researchers, ground truth is static, there is no law-space evolution and no
feedback into the system being studied. It closes (ii) only. It is also the strongest argument that
our Newton engine alone is NOT novel — the novelty must live in the coupling.

### 2.2 ASAL — arXiv 2412.17799 (known near-miss, confirmed)
Automating the Search for Artificial Life with Foundation Models (2024-12-23).
Opened abstract: vision-language FMs (1) find simulations producing target phenomena, (2) discover
simulations generating temporally open-ended novelty, (3) illuminate a diverse space of interesting
simulations; works across Boids, Particle Life, Game of Life, Lenia, Neural CA.
Coupling check: it moves the *substrate configuration* (within each substrate's parameter space) and
uses an FM as the judge of interestingness. No law recovery, no ground-truth rule source, no feedback
from recovered law. Closes (i) partially (substrate search), nothing else.

### 2.3 ASAL++ — arXiv 2509.22447
Guiding Evolution of Artificial Life Using Vision-Language Models (2025-09-26).
Opened abstract: builds on ASAL; a second FM proposes **new evolutionary targets** from a simulation's
visual history, inducing a trajectory of increasingly complex targets (EST vs ETT strategies); tested
in Lenia with Gemma-3.
Coupling check: what moves here is the **target/objective**, not the law space, and still no law
recovery or verification. Closes (i) partially, nothing else.

### 2.4 LOGOS-CA — arXiv 2602.00036 (THE strongest near-miss for (i))
LOGOS-CA: A Cellular Automaton Using Natural Language as State and Rule (2026-01-18).
Opened abstract: "we express cell states and rules in natural language and delegate their updates to an
LLM. Through this approach, cellular automata can transcend the constraints of merely numerical states
and fixed rules, providing us with a richer platform for simulation"; demonstrated on forest-fire
simulation; framed as an ALife subject.
Coupling check: this genuinely opens the law space — rules are arbitrary natural-language strings, not
a member of a fixed parameterized family, so the "space of possible laws" is not fixed in advance.
BUT: no automatic law-discovery engine, no ground-truth rule source (the rule *is* the prompt text),
no verification, no feedback loop. It closes (i) and nothing else — and it is the single paper that
most threatens a carelessly worded novelty claim about "moving law space". Our differentiation must be
stated explicitly against it: we require the law space to move *endogenously* (by evolution/generation
of the substrate's own rules) and to be *recovered and verified* against a moving source.

### 2.5 AutomataGPT — arXiv 2506.17333 (known near-miss, confirmed)
AutomataGPT: Forecasting and Ruleset Inference for Two-Dimensional Cellular Automata (2025-06-19).
Opened abstract: decoder-only transformer pretrained on ~1M trajectories spanning 100 distinct 2D
binary deterministic CA rules on toroidal grids; 98.5% perfect one-step forecasts on unseen rules from
the same family; reconstructs the governing update rule with up to 96% functional accuracy and 82%
exact rule-matrix match.
Coupling check: this is the closest *inverse* result (observation -> rule) and the closest thing to
"verification against a rule source". But the 100 rules are **fixed and enumerated**; the ground truth
never moves; there is no feedback from inference back into the rule space. Closes (ii) and (iii) in
the static case only. Note: its rule space is a *fixed family*, so it is not (i).

### 2.6 SR-Scientist — arXiv 2510.11661
Scientific Equation Discovery With Agentic AI (2025-10-13). Opened abstract: elevates the LLM from
equation proposer to an autonomous agent that writes code to analyze data, implements the equation,
submits it for evaluation, and optimizes from experimental feedback; +6% to +35% absolute over
baselines across four science disciplines.
Coupling check: static datasets, static ground truth, no substrate. Closes (ii) only.

### 2.7 Darwin Godel Machine — arXiv 2505.22954
Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents (2025-05-29). Opened abstract:
a system that iteratively modifies **its own code**, thereby also improving its ability to modify itself;
addresses the fact that the human-designed search space of meta-learning is a limitation.
Coupling check: the object whose "law" moves is the agent's own source, not a simulated universe's
substrate; there is no law-discovery engine (no one recovers a symbolic law and verifies it against
the source), and no substrate feedback. Closes (i) in a different domain (self-modifying code). Worth
citing as the closest precedent for "the ground truth itself moves" — and for the distinction that
nobody has put a *recovery* engine on a moving source.

### 2.8 Other opened-for-completeness items
- OpenLife — arXiv 2606.31046 (2026-06-30). LLM agents with memory/tools/network/payment run in the
  *open social/economic world* for ~12 weeks; open-vocabulary appraisal instead of scalar reward.
  Not a substrate law-space paper. Closes nothing.
- Semantic Lenia — arXiv 2608.11657 (2026-08-12). LLM inference as a closed-loop continuous dynamical
  system in semantic space; homeostatic solitons; parameter sweeps. Not law discovery.
- From AI for Science to Agentic Science: A Survey — arXiv 2508.14111 (2025-08-18). Domain-oriented
  survey of autonomous scientific discovery (life sci, chem, materials, physics); three unified
  perspectives (process, autonomy, mechanism). Useful as the umbrella citation for "agentic science".
- Agentic AI for Scientific Discovery: A Survey — arXiv 2503.08979. Seen in search results only;
  abstract NOT opened → UNVERIFIED, listed for completeness.

### 2.9 Searches that returned NOTHING (evidence of emptiness)
arXiv API queries with zero relevant hits: `all:"artificial chemistry" AND all:"language model"`,
`all:"self-modifying" AND all:"cellular automata"`, `all:"time-varying" AND all:"equation discovery"`,
`all:"symbolic regression" AND all:"non-stationary"`, `all:"co-evolution" AND all:"cellular automata"
AND all:"learning"`, `all:"procedural generation" AND all:"rule discovery"`, `all:"evolving laws"`,
`all:"meta-evolution" AND all:rules` (only unrelated trading/scheduling hits). No query surfaced a
system with a recovery engine over a moving law space.

---

## 3. Structural verdict per coupling condition

| Condition | Who does it | Closest paper | Still missing |
|---|---|---|---|
| (i) law space itself moves | Leniabreeder/ASAL/ASAL++ (params & targets), LOGOS-CA (language rules), DGM (own code) | LOGOS-CA 2602.00036 | endogenous evolution of the substrate's own rules |
| (ii) automatic law finder on top | SciExplorer, SR-Scientist, AutomataGPT, CAMO, PhysAgent, 2604.00273 | SciExplorer 2509.24978 | a finder placed on a substrate whose rules move |
| (iii) verify vs a MOVING ground truth | — nobody — | AutomataGPT (static rule source); DGM (moving source, no finder) | the join: finder + moving source |
| (iv) feed discovery back into substrate | — nobody — | — | entirely absent from the opened literature |

## 4. Caveats on this scan
- arXiv API search covers metadata (title/abstract/comments), not full text. A system named only in a
  paper's body (e.g. a section describing a "feedback loop") could be missed. Google Scholar full-text
  was not accessible from this environment; DDG search was rate-limited/blocked for part of the run.
- Coverage is 2023-09 → 2026-09 as indexed on arXiv; non-arXiv venues (ALIFE conference proceedings,
  GECCO, Artificial Life journal, NeurIPS workshop papers without arXiv preprints) were not swept.
- Three items on the given list turned out to be mis-remembered or mis-attributed (2604.01684 content,
  PhysAgent identity, LifeGPT's "LLM"). The snippet source should not be trusted for ID-level claims.

## 5. Mandatory related work (ranked by threat to the novelty claim)
1. LOGOS-CA — arXiv 2602.00036 — language as state AND rule (open law space) ← strongest threat to (i)
2. Agentic Exploration of Physics Models / SciExplorer — arXiv 2509.24978 (PRX) ← strongest threat to (ii)
3. AutomataGPT — arXiv 2506.17333 ← inverse rule inference + rule-matrix ground truth
4. ASAL — arXiv 2412.17799 ; ASAL++ — arXiv 2509.22447 ← substrate search by FMs
5. Leniabreeder / QD Lenia — arXiv 2406.04235 ← substrate search baseline
6. SR-Scientist — arXiv 2510.11661 ← agentic equation discovery
7. CAMO — arXiv 2604.14691 ← agentic discovery of emergent mechanism in simulations
8. AgenticSciML — arXiv 2511.07262 ← multi-agent discovery of methods
9. PhysAgent (Han et al., ChinaXiv chinaxiv-202508.00189) ← agentic derivation of physical laws
10. How local rules generate emergent structure in CA — arXiv 2604.00273 ← rule→structure analysis
11. The AI Scientist-v2 — arXiv 2504.08066 ← end-to-end agentic discovery process
12. Darwin Godel Machine — arXiv 2505.22954 ← the only "moving ground truth" precedent
13. From AI for Science to Agentic Science — arXiv 2508.14111 ← umbrella survey

Sources opened (abs/repo pages): 2509.24978, 2604.14691, 2511.07262, 2409.12182, 2406.04235,
2504.08066, 2604.00273, 2604.01684, 2412.17799, 2509.22447, 2602.00036, 2506.17333, 2510.11661,
2606.31046, 2608.11657, 2508.14111, 2505.22954, 2607.16355, chinarxiv-202508.00189, mpcrlab AgentLife.
