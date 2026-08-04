# 01 — Executive Summary

**Project:** Drift-Sense — Navigation-Error Recovery for Semiconductor SEM Inspection
**Phase:** 1 of N — Scientific specification of the semiconductor layout geometry to be synthetically generated
**Scope of this phase:** Layout geometry only. Not fabrication, not SEM physics, not code, not neural network design.

---

## 1. The problem this phase serves

The hackathon task (`docs/Copy of Problem Statement 02...pptx`, cited throughout this report as `[PS-DriftSense]`) requires finding a small, high-resolution "reference" SEM image (1000×1000 px, 1 nm/pixel, 1 µm × 1 µm field of view) inside a larger, lower-resolution "search" SEM image (1000×1000 px, 10 nm/pixel, 10 µm × 10 µm field of view) — an exact 10× linear / 100× areal scale disparity. Both images depict the **same underlying die region**, captured at two magnifications ("100x" and "10x" optics). The chosen die architecture must be either **DRAM-style** (periodic word-line/bit-line/contact arrays) or **FinFET-style** (parallel fin lines crossed by gate bars) — participant's choice, judged equally. No proprietary dataset exists; participants must build their own synthetic-but-literature-justified generator.

Before any generator, noise model, or localization algorithm can be built, the underlying **layout geometry** must be understood and specified precisely enough to be procedurally generated and defended against public literature (2–3 credible sources per augmentation/geometry choice, per the grading rubric). That specification is the entire deliverable of this phase.

## 2. What this phase produced

Ten documents in `research/phase-1/`:

| File | Content |
|---|---|
| `02_dram_research.md` | Full geometric anatomy of 6F² DRAM arrays: word/bit line pitch (3F/2F), diagonal active area, contact/landing-pad lattice, cell-size scaling across DRAM generations, and why the array is a true 2D-periodic lattice |
| `03_finfet_research.md` | Full geometric anatomy of FinFET standard-cell logic: fin pitch, contacted poly/gate pitch (CPP), gate length, fin/gate cuts, and why the fin-axis is *less* locally distinctive than DRAM despite comparable 2D periodicity |
| `04_comparison.md` | Direct DRAM-vs-FinFET comparison across geometry, periodicity, complexity, generation difficulty, and localization difficulty |
| `05_generator_parameters.md` | Every parameter needed to build the generator — name, typical value, range, unit, rationale, and ≥1–2 supporting references each |
| `06_randomization_strategy.md` | Which parameters must stay fixed, which should be randomized (and how — including which must be *jointly* rather than independently randomized), and which randomizations would break physical realism |
| `07_layout_generator_specification.md` | Proposed mathematical representation (parametric-primitive / vector-polygon lattice, GDSII-style) and the complete generator I/O, reproducibility, and metadata specification |
| `08_open_questions.md` | Every single-sourced value, literature conflict, and node-dependent parameter flagged explicitly, plus the team-level engineering decisions still outstanding |
| `09_complete_reference_list.md` | ~45 citation keys across primary problem-statement documents, IRDS/ITRS roadmaps, peer-reviewed papers (ASAP7, IEDM/IBM/Intel), vendor publications, patents, and corroborating press |
| `10_phase1_final_report.md` | Synthesis: what is now known, what remains uncertain, and the recommended path into Phase 2 |

## 3. Headline findings

1. **Both architectures are legitimately "highly periodic," but differently so.** DRAM is a true 2D crystallographic-style lattice with a strong per-cell landmark (the contact/landing-pad dot), which makes wrong-cell matches strong-but-wrong and correct-cell sub-pixel localization comparatively easy once the right repeat instance is found. FinFET is periodic in two directions at two different, non-commensurate pitches, but has a *weak* intra-cell landmark — long runs of parallel fins are nearly self-similar even *within* one repeat unit — making it structurally harder to localize precisely even after coarse matching (`04_comparison.md`, Section 5).
2. **The task's core geometric constraint is the exact 10× scale relationship, not any specific semiconductor parameter.** The single highest-priority generator requirement is rendering *one* continuous physical layout at two exactly-related sampling densities (1 nm/px and 10 nm/px) so the reference and search images are provably the same pattern — this dominates the specification more than any individual DRAM/FinFET dimension (`05_generator_parameters.md`, Section 0).
3. **Every DRAM/FinFET dimension is strongly technology-node dependent** (DRAM half-pitch spans roughly 10–40 nm across generations; FinFET fin pitch spans roughly 25–90 nm; CPP spans roughly 36–90+ nm). No single "typical value" is defensible as universal — the generator must expose these as randomized, literature-bounded, and (for FinFET) *jointly* sampled parameters, never independently randomized absolute values (`06_randomization_strategy.md`).
4. **A meaningful minority of parameters are not directly quantified in the surveyed open literature** (e.g., exact line-width-to-pitch ratios, DRAM active-area tilt angle beyond one patent's claim range, typical fin/gate cut density). These are explicitly flagged rather than invented, per task instructions — see `08_open_questions.md`.
5. **DRAM requires one materially harder-to-implement primitive** (the diagonal active area + contact lattice, which must respect exact 6F² tiling geometry) than FinFET (which is well-served by the simplified "parallel lines + 1-2 crossing bars" abstraction the problem statement's own sample prompt suggests). This is a relevant, literature-grounded input to the team's architecture choice, though the problem statement itself does not favor either (`04_comparison.md`, Section 7).

## 4. What this phase deliberately did not do

Per explicit task instructions: no dataset-generation code, no Python, no neural network design. SEM imaging physics (noise, edge blooming, charging, contrast inversion) and fabrication process detail were intentionally scoped out — this phase is layout geometry only, with SEM-physics literature recorded in the reference list purely as a hand-off pointer for the phase that will own it (`08_open_questions.md`, Section 4).

## 5. Recommended immediate next step

Resolve the single highest-leverage open item — the ASAP7 PDK's exact fin-pitch/CPP numeric values, currently unverified because the primary paper was access-restricted during this research pass (`08_open_questions.md`, Section 1) — by pulling the open-source ASAP7 design-rule repository directly, then proceed to Phase 2 (mathematical/procedural design detail and, eventually, SEM-realistic rendering), using this report as the fixed geometric contract.
