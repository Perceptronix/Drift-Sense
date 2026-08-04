# 04 — DRAM vs. FinFET: Comparative Geometric Analysis

This file synthesizes [02_dram_research.md](02_dram_research.md) and [03_finfet_research.md](03_finfet_research.md) into a direct comparison, focused specifically on what matters for (a) procedural generation and (b) Navigation-Error Recovery localization difficulty. Citation keys resolve in [09_complete_reference_list.md](09_complete_reference_list.md).

---

## 1. Geometry comparison

| Dimension | DRAM (6F² array) | FinFET (standard-cell logic) |
|---|---|---|
| Base structure | Single repeating unit cell tiled over a huge, uniform mat `[Kwon-Thesis-UCBerkeley]` | Library of distinct standard cells abutted in rows on a shared fin/gate grid `[ASAP7-2016]` |
| Primary line families | Word lines (pitch 3F) ⊥ Bit lines (pitch 2F) `[US7349232B2]` | Fins (pitch = fin pitch) ⊥ Gate lines (pitch = CPP) `[FinFET-CGP-DRC2017]` |
| Distinguishing sub-cell feature | Contact/landing-pad dot at a fixed diagonal offset, present in **every** unit cell `[DRAM-EUV-SNLP-Patterning]` | Fin cuts / gate cuts — present only **sparsely and irregularly** `[US9337099-FinFET-NonUniform]` |
| Active-area orientation | Diagonal (tilted ~20–80° relative to WL/BL, patent-sourced range) `[US20060281250A1]` | Axis-aligned (fins parallel to one axis, gates perpendicular) `[ASAP7-2016]` |
| Repeat unit size (order of magnitude) | Small — 6F² ≈ tens to low-hundreds of nm² at modern nodes; many full unit cells fit in a 1 µm² tile | Larger and more variable — one standard cell may span several hundred nm to > 1 µm depending on cell type and track height `[ASAP7-2016]` |
| Symmetry class | 2D periodic lattice (both axes strictly periodic, oblique unit cell) | Quasi-1D-periodic in each axis independently (fin axis and gate axis have *different*, non-commensurate pitches), with row-wise but not fully 2D translational symmetry `[FinFET-CGP-DRC2017]` |
| 3D relevance to top-down 2D image | Buried word line is a surface-invisible depth feature but leaves a surface contrast band `[Kim2003-6F2-BuriedWL]` | Tri-gate wraparound is not visible top-down at all; fins read as flat rectangles `[Intel22nm-IEDM2012]` |

---

## 2. Periodicity comparison

| Aspect | DRAM | FinFET |
|---|---|---|
| Periodic directions | 2 (fully 2D lattice) `[US7349232B2]` | 2 (fin axis + gate axis), but pitches differ and are frequently non-integer multiples of each other `[FinFET-CGP-DRC2017]` |
| Local uniqueness within one repeat cell | High — contact dot breaks translational ambiguity in *both* directions at sub-cell scale `[DRAM-EUV-SNLP-Patterning]` | Low — a bare fin segment between two gates is visually near-identical to its neighbor fin at the same row `[FinFET-CGP-DRC2017]` |
| Scale of exact-periodicity region | Very large (full mat, potentially 100s–1000s of cells before a break) `[Kwon-Thesis-UCBerkeley]` | Smaller and interrupted more often (standard-cell row boundaries, mixed cell types) `[ASAP7-2016]` |
| Dominant spatial-frequency content | Few, very sharp Fourier peaks (near-ideal 2D grating + dot lattice) | Few, very sharp Fourier peaks in the fin direction; weaker/more variable peaks in the gate direction due to cell-to-cell CPP-multiple variation |

**[Inference]** Both architectures are "highly periodic" in the sense the problem statement uses `[PS-DriftSense]`, but the *character* of the periodicity differs: DRAM is periodicity with a strong per-cell landmark (harder to confuse two DIFFERENT cells once you find any landmark, but many cells look identical to each other); FinFET is periodicity with a weak per-cell landmark (harder to disambiguate positions along the fin axis at all, because plain fin segments carry almost no unique local signal).

---

## 3. Complexity comparison (for a procedural generator)

| Aspect | DRAM | FinFET |
|---|---|---|
| Number of distinct primitive types needed | Low (2 line families + 1 dot layer + occasional mat-boundary break) | Also low at the abstraction level specified by the problem statement (fins + 1-2 gate bars), but real designs add fin/gate cuts and MOL offsets for higher fidelity `[US9337099-FinFET-NonUniform]` |
| Geometric rule complexity | Moderate — diagonal active area requires an angle parameter and correct dot placement at the AA/WL/BL intersection `[Orthogonal-6F2-Trench]` | Low — pure axis-aligned rectangles; complexity only increases if fin/gate cuts and MOL are added for realism |
| Randomization surface (what can vary while staying physically plausible) | Pitch (F), tilt angle, contact diameter, landing-pad size, mat-boundary placement | Fin pitch, CPP, fin count/length, number and position of gate bars, cut positions |
| Risk of visually implausible output if parameters are chosen carelessly | Moderate (wrong tilt angle or dot spacing looks obviously synthetic) | Lower (parallel lines are forgiving; the main risk is unrealistic pitch ratios between fin and gate axes) |

**[Inference]** FinFET is the **geometrically simpler architecture to implement well** at the abstraction level the hackathon problem statement specifies (parallel lines + crossing bars), while DRAM requires modeling one additional non-trivial primitive (the diagonal active area and its associated contact placement) to look authentic.

---

## 4. Advantages and disadvantages (as a hackathon dataset choice)

| | DRAM | FinFET |
|---|---|---|
| **Advantages** | Strong, literature-consistent, unique per-cell landmark (contact dot) gives the localization algorithm *something* to lock onto once ambiguity is resolved; well-documented F-based scaling rule simplifies parameterization; visually iconic "SEM of memory array" look | Simpler primitive set (lines + crossing bars only, per problem statement's own suggested prompt `[PS-DriftSense]`) is faster to implement correctly and less likely to contain subtle geometric errors; genuinely harder localization problem, which may be more interesting/defensible for the "difficulty" and "failure case" grading criteria (30%+10% of the rubric relates to realism and failure-case explainability `[PS-DriftSense]`) |
| **Disadvantages** | Diagonal active-area geometry and multi-layer contact/landing-pad placement is more implementation-prone to error; risk of the localization task becoming "too easy" if the contact-dot landmark is rendered too crisply, undermining the intended difficulty | Weak per-cell landmarks make it **harder to construct a well-posed test case with a single defensible ground-truth answer** — the problem statement itself allows "if more than one region matches, whichever is closest to the search image's center" `[PS-DriftSense]`, which is a tacit acknowledgment that periodic layouts can have genuinely ambiguous multiple matches; over-simplified fin-only layouts (no cuts at all) could become under-constrained (literally infinite equally valid matches along a repeat direction) |

---

## 5. Difficulty for localization — direct comparison

**[Inference, synthesizing Sections 7 of `02_dram_research.md` and `03_finfet_research.md`]**

- **DRAM** localization difficulty is dominated by **repeat-cell ambiguity**: many candidate positions produce an equally strong match because the *entire* cell (grid + dot) repeats exactly. Once a matching algorithm restricts its search to "candidate cell-aligned positions," however, the strong 2D landmark (contact dot) makes fine sub-pixel localization comparatively easy and accurate *conditional on* picking the right repeat instance.
- **FinFET** localization difficulty is dominated by **weak intra-cell distinctiveness along the fin axis**: even after correctly identifying which gate "row" a reference tile came from, sliding the match along the fin direction between two gate lines may produce a near-flat, ambiguous correlation response (the aperture-problem-like behavior noted in Section 7 of `03_finfet_research.md`) unless a fin cut or gate cut happens to fall inside the tile.
- **[Recommendation]** Both are legitimate, literature-defensible choices per the problem statement, which explicitly states the choice is "judged equally either way" `[PS-DriftSense]`. FinFET is somewhat easier to implement correctly at the specified abstraction level and produces a more genuinely open-ended localization-ambiguity story (useful for the failure-case-explainability portion of the grading rubric); DRAM is more visually iconic and requires one extra geometric primitive (diagonal active area + contact) to be authentic.

---

## 6. Difficulty for synthetic generation — direct comparison

| Generation sub-task | DRAM | FinFET |
|---|---|---|
| Base grid (2 line families) | Straightforward: two sets of parallel lines at fixed pitches, one horizontal one vertical | Identical in structure: two sets of parallel lines at fixed pitches, one horizontal one vertical |
| Extra primitive needed for authenticity | Diagonal active-area stripes + contact dots at the correct sub-cell registration (non-trivial: must respect the 6F² tiling rule, not just be randomly scattered) `[Orthogonal-6F2-Trench]` | Fin/gate cuts (optional refinement; the problem statement's own reference prompt does not require them `[PS-DriftSense]`) |
| Multi-scale consistency requirement (10× search vs. 1× reference, same underlying layout) | Must tile the *same* mask cell across both the small reference window and the 10×-larger search window so the pattern is provably self-consistent at both scales `[PS-DriftSense]` | Same requirement, but simpler to satisfy correctly since the base primitive (parallel line pair) is inherently easier to render self-consistently at any crop/scale than the diagonal DRAM AA+dot motif |
| Risk of an implementation bug producing a "too easy" or "too hard" dataset | Moderate — an accidentally too-crisp contact dot could make the task trivial; accidentally missing the diagonal tilt makes the DRAM sample geometrically wrong (not literature-consistent) | Low — hard to get "just parallel lines crossed by bars" visibly wrong; main risk is choosing an implausible fin-pitch-to-gate-pitch ratio |

---

## 7. Summary recommendation

**[Recommendation]** This survey does not mandate one architecture over the other — the problem statement is explicit that the choice is judged equally `[PS-DriftSense]` — but based on the geometric analysis above:

- Choose **DRAM** if the team wants a visually iconic, instantly recognizable "memory array" dataset and is willing to implement the diagonal active-area/contact-lattice primitive carefully (getting the 6F² tiling geometrically right, per Section 2 of `02_dram_research.md`, is the single highest-risk implementation detail).
- Choose **FinFET** if the team wants the simpler primitive set explicitly suggested in the problem statement's own sample prompt (`[PS-DriftSense]`, Section on "Sample Prompt to Generate data") and wants a dataset whose localization-ambiguity failure mode is easier to reason about and explain in the required failure-case analysis (10% of grading rubric).

Both architectures require the same core generator infrastructure (parametric parallel-line grids at controllable pitch, exact 10× multi-scale consistency between reference and search windows, and an explicit parameter/randomization framework) — detailed next in [05_generator_parameters.md](05_generator_parameters.md) and [07_layout_generator_specification.md](07_layout_generator_specification.md).
