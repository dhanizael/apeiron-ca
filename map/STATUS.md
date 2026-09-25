# Milestone Status — APEIRON (2026-09-24)

Every number below traces to `docs/RESEARCH-LOG.md` entries 001–023 (dates,
protocols, reproduction commands). Engine: Rust, bit-identical deterministic;
analysis: Python; suites green at every merge.

| # | Milestone | Result | Log |
|---|---|---|---|
| 001 | LM-0 loop miniature | Rule 184 recovered exactly (unique among 256 candidates); J(ρ) 2-segment MDL, held-out MAE 7.58e-05 | 001 |
| 002 | M0 engine | **2.31×10⁹ cell-updates/s** (frozen protocol; first honest run failed at 5.39×10⁸) | 002 |
| 003 | M1 physics search | Unplanted universes with persistent particles; 30% of random candidates pass at probe scale | 003 |
| 004 | M3 law recovery | **4096/4096 entries exact** from raw states; macro J(ρ) held-out MAE 0.0 | 004 |
| 005 | M4 closed loop v1 | Growth meter (K5): three regimes saturate; W3-NULL fully attributed (capacity-bound) | 005 |
| 006 | M1v2 slack hypothesis | SUPPORTED 2.16× (RICH 0.67 vs POOR 0.31); sparse-sea universes survive, dense ones die by exclusion | 006 |
| 007–009 | W3 rounds: existence-level levers | v2: single +1 can FREEZE the universe (true fixed point) and the loop revived it (0→0.33); v3: counterfactual instrument (freeze_miss 0/13) — direction NULL, magnitude 3× random | 007–009 |
| 010 | OEE meter (first) | Perpetuum 19631: model_bits 7400→9056 by 10⁶, **not saturated**; baselines frozen at 2 bits | 019 |
| 011–013 | M2 replicator | Transmutation duplication 2→1+1 (3/3 seeds); **law 16295: one seed → 42–52 copies (stable plateau) in a sea that otherwise yields zero (control 0, 4/4 seeds)** — reaction-front mechanism | 015–016 |
| 014–015 | M2 science | The front is a **universal converter**: one seed → whole-universe [2,0] crystal ({2:8192, 0:8191, 1:1}); the 0/1 subworld is **closed** (no spontaneous nucleation at any density — injection is the only door); k=4 search: 187 events, control audit 0/8 seeding-dependent | 017 |
| 016–017 | Perpetuum ecologis | **Law 19631: 10 species coexisting, amplitude 1.91–2.09 on the last third of 20k steps, anti-phase predation signature ρ = −0.75…−0.89 (3/3 independent instances); baselines 6× separated** | 018 |
| 018 | External audit | Ice-nine corrected: the crystal is a *dynamic* saturated phase (one wandering defect); the dense world is a fluctuating multi-species equilibrium | 017 |
| 019–020 | First gates | Regenerative OR (1-deposit → emit-and-restore, inputs consumed, deterministic) | 020 |
| 021 | AND gate | **Law 22126: column [0,0,0,1] exact; memory 6→7→8→emit (ONE-SHOT: the gate collapses after emitting — an external audit caught our earlier 'reusable' claim; errata log 027); re-run identical** — found by empirical census after the algebra filter over-predicted 3× | 021, 023 |
| 022 | Two-gate circuit | **(A∧B)∧C exact, 8/8 truth-table rows + deterministic re-run**; 76-cell wire; wait-behavior as theorized | 022 |

## The discovered constants and theorems

- **Free-flow bound**: J = mass/n, digit-precise (0.499267578125 = 0.499268)
  — the "attractor" is a conservation ceiling; table interventions move
  below it, never above. (Log 012)
- **Translation-invariance of free flow**: a perfect free-flow universe is
  invariant to capacity expansion (7/7 migrated instances, max-cell 2). (Log 014)
- **Subworld closure**: the 0/1 subworld cannot produce the 2-species at any
  density — injection is the only door. (Log 017)
- **"Receipt is the other side of emission; in front of parking lots
  nothing emits."** — the mechanism that refuted the naive de-eternalization. (Log 017)

## Reproduction (one command each)

```
python experiments/m2/gate.py            # first gate: 4 truth-table runs
python experiments/m2/circuit.py         # two-gate circuit: 8 rows
python experiments/m2/perpetuum_search.py --verify-law 19631 --verify-k 4 --verify-ic difus
python experiments/m2/oee_meter.py       # open-endedness meter to 10^6 steps
cargo test --release && pytest analysis/tests/   # full suites
```

## Status of the map

- **Reached**: everything in the table.
- **Open**: universality of the flow family at fixed k (sharpest open
  question); full boom-bust and species turnover; the k-lift cascade
  (k=4→8→…) as the staged route to unbounded ceiling growth.
- **Held back**: the technical BLUEPRINT ships with the running code, as
  planned; this MAP stakes the direction and the measured position.
