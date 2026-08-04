# 08 — Open Questions, Uncertain Values, and Literature Conflicts

This file consolidates every flag raised across `02`–`07` into one place, so future phases know exactly which numbers are solid and which need more work before being trusted as "fact" in a submission. Citation keys resolve in [09_complete_reference_list.md](09_complete_reference_list.md).

---

## 1. Values resting on a single source (need independent corroboration)

| Value | Current source | Status | Recommended next step |
|---|---|---|---|
| `active_area_tilt_angle` range (20–80°) for 6F² DRAM | `[US20060281250A1]` (one patent) | **Single-sourced.** Other patents (`[Orthogonal-6F2-Trench]`, `[US7349232B2]`) confirm the *existence and direction* of the tilt (each AA stripe crosses 1 BL and 2 WLs) but do not independently state a numeric angle range. | Locate a peer-reviewed DRAM array layout paper or textbook figure (e.g., Itoh, *VLSI Memory Chip Design*) with a dimensioned top-down 6F² array drawing to confirm a typical angle, or accept the patent range but narrow the *recommended sampling band* conservatively (as already done in `[06_randomization_strategy.md]`, Section 3). |
| `fin_width` ≈ 5–6 nm at 7 nm-class nodes | `[FinFET-CGP-DRC2017]` (one synthesizing source, itself citing IEDM-era projections not independently re-verified here) | **Single literature family.** | Cross-check directly against `[IBM-7nmFinFET-EUV]` or `[Intel22nm-IEDM2012]`-style primary IEDM papers for an explicitly stated fin-width figure at a specific node. |
| ASAP7 exact fin pitch / CPP numeric values | `[ASAP7-2016]` — **access-restricted (HTTP 403) during this research pass; only indirectly triangulated from surrounding 7 nm-class literature, not read directly** | **Unverified — flagged explicitly.** | Retrieve the ASAP7 PDK directly from its open GitHub repository (the design-rule deck is open-source even though the ScienceDirect paper is paywalled) before any generator default is finalized on this number. |
| Word-line/bit-line/fin/gate **width** as a fraction of pitch (0.35–0.6×) | **[Inference]** only — no directly quantified source found | **Inferred from general lithographic practice, not literature-confirmed for DRAM/FinFET specifically.** | Search CD-SEM metrology papers (e.g., further NIST publications in the `[NIST-DetectionLimitsSEM-2025]` family) for explicitly reported line-CD-to-pitch ratios at named nodes. |
| Typical DRAM array **mat size** (cells before a deliberate symmetry break) | `[Kwon-Thesis-UCBerkeley]` (qualitative only — no specific cell-count figure found) | **Qualitative fact, no quantitative figure sourced.** | Locate a DRAM array-architecture paper that states typical sub-array/mat dimensions (commonly discussed in DRAM circuit-design textbooks, e.g., in terms of number of word lines per mat). |
| Typical fin-cut / gate-cut density in real standard-cell layouts | **[Inference]** from general design practice | **Inferred, not quantified.** | Would require access to a real or academic standard-cell library layout statistics paper (e.g., an ASAP7-based layout-density study) to state a defensible probability range instead of an inferred placeholder. |

---

## 2. Conflicting or imprecise literature values

| Topic | Conflict | Resolution taken in this report |
|---|---|---|
| TSMC N5 (5 nm) fin pitch | `[WikiChip-TSMC5nm]` reports ~28 nm confirmed on production silicon; the same source also notes early estimates of ~25–26 nm from an alternate analysis (`[Angstronomics-TSMC5nm]`-adjacent commentary) | Reported **both** values explicitly as a range with the disagreement flagged, rather than picking one (Section 2, `[03_finfet_research.md]`) |
| "1α DRAM half-pitch" | Sourced material states a broad "10–19 nm" band for a single named generation `[Micron-1alpha-Blog]` — unusually wide for one node label | Flagged explicitly as likely reflecting vendor-to-vendor naming inconsistency rather than a single precise design rule; recommended treating F as order-of-magnitude only for "modern DRAM" (Section 5, `[02_dram_research.md]`) |
| 6F² cell area at "68 nm design rule" (0.028 µm²) vs. algebraic 6F² formula using F = 34 nm (≈0.0069 µm²) | The two don't match by roughly 4×, because "design rule" node labels and the literal F in the 6F² formula are not the same number by convention | Flagged explicitly in Section 5 of `[02_dram_research.md]`; recommendation is to treat F as an independently tunable parameter rather than deriving it algebraically from a marketing node name |
| CXMT 4F2/VCT 18 nm DRAM claim | Appears only in secondary press summarized during search, not confirmed against a primary technical source in this survey | Explicitly marked "unconfirmed by a primary technical source" in Section 2.2 of `[02_dram_research.md]`; 4F² is otherwise treated as "not in mainstream mass production" per the stronger-sourced claim |

---

## 3. Technology-node-dependent parameters (not a "conflict," but must never be treated as single fixed constants)

Per the task's explicit instruction to flag node-dependent parameters rather than presenting one number as universal:

- **DRAM F (half-pitch):** varies roughly 10–40 nm depending on generation (1x through 1γ vs. older nodes) — see Section 5, `[02_dram_research.md]`.
- **FinFET fin_pitch:** varies roughly 25–90 nm depending on generation (22 nm-class down to 5 nm-class) — see Section 2, `[03_finfet_research.md]`.
- **FinFET CPP/gate_pitch:** varies roughly 36–90+ nm depending on generation — see Section 3, `[03_finfet_research.md]`.
- **FinFET gate_length:** varies roughly 12–34 nm depending on generation — see Section 3, `[03_finfet_research.md]`.

**[Recommendation]** The generator specification in [05_generator_parameters.md](05_generator_parameters.md) and [06_randomization_strategy.md](06_randomization_strategy.md) already treats all four of these as randomized/node-profile-coupled parameters rather than hard-coded constants, specifically to respect this node-dependence rather than presenting one generation's numbers as if universal.

---

## 4. Explicit scope boundaries flagged during this research (not gaps — deliberate exclusions per task instructions)

- **SEM imaging physics** (noise models, edge blooming, charging, contrast inversion) was intentionally researched only lightly, and only insofar as it explains *why* certain geometric features (e.g., a single fin cut) are more or less likely to be visually recoverable — the task instructions explicitly state "We are NOT studying SEM physics. We are ONLY studying layout geometry." The literature family (`[NIST-Charging-SPIE]`, `[arXiv-BeamCrossSections-2025]`, `[arXiv-ShotNoiseICAM-2023]`, `[NatSciRep-SEMDenoising2025]`, `[NIST-DetectionLimitsSEM-2025]`, and the physics-based Monte Carlo SEM simulator `[NIST-JMONSEL]` identified in `[SEM-Dataset-Survey]` as the recommended rendering engine) is recorded in the reference list for hand-off to the phase that will own that work.
- **Fabrication process** (lithography sequence, etch, deposition) was intentionally excluded, per the same instruction ("We are NOT studying fabrication").
- **Gate-all-around (GAA) / nanosheet architectures**, the FinFET successor beyond ~3 nm, were noted (Section 9, `[03_finfet_research.md]`) but not researched in depth, since the problem statement restricts the architecture choice to DRAM or FinFET specifically `[PS-DriftSense]`.
- **4F² vertical-channel DRAM** was noted as a boundary case but not adopted as the recommended default, since it is not confirmed as mainstream by a primary source in this survey (Section 1, this file).

---

## 5. Questions that require a team engineering decision, not further literature search

These are not "unknowns to research more" — they are genuine **design choices** the hackathon team must make, flagged here so they are made consciously rather than by accident:

1. **Should the dataset mix DRAM and FinFET samples, or commit to one architecture?** The problem statement allows either, judged equally `[PS-DriftSense]`. This report recommends (Section 7, `[04_comparison.md]`) committing to one architecture for implementation-risk reasons, but this is a team call, not a literature question.
2. **How wide should the global `line_orientation_offset` (die rotation) distribution be?** Section 4 of `[06_randomization_strategy.md]` recommends keeping it small (±0–5°) by default and treating larger rotations as a separate stress-test subset — but the exact cutoff is an engineering/grading-strategy decision, not a sourced fact.
3. **How aggressively should mat-boundary / non-periodic landmarks be injected into DRAM crops?** Section 4 of `[06_randomization_strategy.md]` recommends ~10–20% of samples, chosen to balance "genuine difficulty" against "at least one honest documented failure case," per the rubric requirement `[PS-DriftSense]` — but the exact probability is a grading-strategy choice.
4. **Whether to pursue the RGB/optical-microscope bonus track** — explicitly a "bonus, provided the core SEM-based solution is completed first" per the problem statement `[PS-DriftSense]`; out of scope for this geometry-only phase but worth flagging early since it would add a third architecture-independent parameter family (RGB channel/color response) not covered in this report.
