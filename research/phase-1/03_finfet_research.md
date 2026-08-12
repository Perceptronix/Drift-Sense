# 03 — FinFET Layout Geometry Research

Scope: pure layout geometry of FinFET logic arrays — not fabrication process, not device electrostatics, not SEM optics. All claims tagged **[Fact]**, **[Inference]**, or **[Recommendation]**. Citation keys resolve in [09_complete_reference_list.md](09_complete_reference_list.md).

---

## 1. What a FinFET layout actually is, geometrically

Unlike DRAM, a FinFET **logic** layout is not one repeating cell tiled over a huge area — it is a **standard-cell-based** layout: a library of small rectangular cells (inverters, NAND/NOR gates, flip-flops, etc.) abutted edge-to-edge into rows, each row built on a common template of two orthogonal, extremely regular grids `[ASAP7-2016]`, `[US9337099-FinFET-NonUniform]`. The problem statement's FinFET description simplifies this to its core repeating skeleton: **"a dense set of parallel vertical fin lines, crossed by one or two horizontal gate bars"** `[PS-DriftSense]` — which is exactly the geometric core of every real FinFET standard cell, before contacts/metal are added.

The two dominant geometric grids in any FinFET layout are:

1. **Fins** — thin, tall silicon ridges, all parallel, all on a single fixed pitch, running in one direction (call it vertical/Y) `[FinFET-CGP-DRC2017]`.
2. **Gates (poly/metal gate lines)** — conductors that run perpendicular to the fins (horizontal/X), each wrapping over every fin it crosses, also on a single fixed pitch — the **contacted poly pitch (CPP)**, also called **contacted gate pitch (CGP)** `[FinFET-CGP-DRC2017]`, `[ASAP7-2016]`.

A transistor exists wherever an *active* gate line crosses one or more *active* fins; source/drain regions sit in the gaps between adjacent gates along a fin.

---

## 2. The fin grid

**[Fact]** Fins are patterned as a **single, technology-fixed pitch grid** across nearly the entire chip (not per-device custom pitches) because sub-lithographic patterning techniques (self-aligned double/quadruple patterning, SADP/SAQP) used to print fins below the optical resolution limit require a strictly periodic "sacrificial grating" that is then selectively cut — this is a *process* reason but it has a **first-order geometric consequence**: fin pitch is essentially constant across a design, and individual devices are built by *selecting how many consecutive fins to keep* (1, 2, 3, …) rather than by choosing an arbitrary fin position `[FinFET-CGP-DRC2017]`, `[ASAP7-2016]`.

**[Fact]** Fin pitch and fin height/width by generation, drawn from primary vendor/peer-reviewed sources:

| Node | Fin pitch | Fin width | Fin height | Source |
|---|---|---|---|---|
| Intel 22 nm (first commercial tri-gate) | **fin pitch = fin height = 42 nm** (both reported as ~42 nm) | not separately isolated in survey sources | ~42 nm (see pitch) | `[Intel-Bohr-14nm-IDF2014]` (comparative table), `[RealWorldTech-Intel22nm]` |
| Intel 14 nm | tighter than 22 nm; fin pitch reduced substantially (∼2nd-generation FinFET scaling) | — | increased fin height vs. 22 nm for higher drive current | `[Intel-Bohr-14nm-IDF2014]` |
| ~7 nm class (industry projection, IBM commentary) | **~30 nm** (projected/typical) | **~5–6 nm** (near physical limit of a stable fin) | **~30 nm** (projected) | `[FinFET-CGP-DRC2017]` (synthesizing IBM/IEDM-era projections) |
| TSMC N5 (5 nm) | **~25–28 nm** (estimates vary by source/measurement; ~28 nm confirmed on production silicon per one analysis, ~25–26 nm per another) | not isolated in survey sources | not isolated in survey sources | `[WikiChip-TSMC5nm]`, `[Angstronomics-TSMC5nm]` — **flagged: two independent secondary-press sources disagree by ~2–3 nm; no single authoritative peer-reviewed value found in this survey** |

**[Fact — single strongest peer-reviewed data point]** The ASAP7 7 nm **predictive** PDK, a peer-reviewed, openly published academic process design kit explicitly built to approximate real 7 nm FinFET geometry for research use, is the most citable *complete, self-consistent* numeric geometry source found in this survey `[ASAP7-2016]`; it is designed specifically so that every geometric rule is internally consistent (unlike scattered individual vendor disclosures). ASAP7 target values (drawn from the same 7 nm-class literature landscape summarized above) are consistent with fin pitch in the **24–27 nm** range and CPP in the **54–56 nm** range for that generation — **[Inference]** the exact ASAP7 published values were not independently re-verified inside this document because the primary ScienceDirect page returned an access-restricted (HTTP 403) response during research; the "ASAP7" project is nonetheless flagged in [08_open_questions.md](08_open_questions.md) as the **highest-priority source to consult directly (open-source repository, not paywalled) before finalizing generator defaults**, since its layout rule deck is publicly downloadable independent of the paywalled paper.

**[Recommendation]** Because published fin-pitch numbers vary node-to-node and even source-to-source at the same node, the generator should **not hard-code a single fin pitch**; it should draw fin pitch from a technology-node-labeled range (see [05_generator_parameters.md](05_generator_parameters.md)) and clearly document which "node era" a given synthetic sample is meant to represent.

---

## 3. The gate grid and Contacted Poly/Gate Pitch (CPP/CGP)

**[Fact]** CPP is the single most-cited FinFET scaling metric in the literature because it (together with fin count per cell and metal pitch) determines standard-cell area and therefore overall logic density `[FinFET-CGP-DRC2017]`. Reported CPP/gate-pitch values by node:

| Node | CPP (contacted poly/gate pitch) | Source |
|---|---|---|
| 14 nm (industry-wide reference figure) | **~72 nm** | `[FinFET-CGP-DRC2017]` |
| 10 nm | **~64 nm** | `[FinFET-CGP-DRC2017]` |
| 7 nm (tightest reported) | **~44–48 nm** | `[FinFET-CGP-DRC2017]` |
| 7 nm (IBM projection, alternate estimate) | **~45–55 nm** | `[IBM-10nmFinFET]`-era commentary, cross-referenced discussion in `[FinFET-CGP-DRC2017]` |
| Intel 22 nm SoC (first-gen tri-gate, IEDM 2012 paper) | **90 nm** device pitch, with **30 nm / 34 nm gate lengths** (high-performance / standard-performance variants) | `[Intel22nm-IEDM2012]` |

**[Fact]** At the 7 nm/5 nm generation, expected **gate length** compresses to roughly **12–14 nm** to keep pace with the shrinking contacted pitch, per IBM commentary synthesized in the DRC 2017 survey `[FinFET-CGP-DRC2017]`. **[Inference]** Gate length is therefore always substantially *smaller* than CPP — the gate line itself only occupies a fraction of its pitch, with the remainder allocated to spacers and the source/drain contact.

**[Fact]** TSMC's 7 nm CMOS platform reported an effective gate length (Leff) centered around **16.5 nm**, and TSMC's 5 nm node (N5) reportedly holds **poly pitch ≈ 48 nm** and **metal pitch ≈ 30 nm** even while fin pitch tightened further, illustrating that CPP and fin pitch do **not** scale at the same rate between generations `[WikiChip-TSMC5nm]`.

---

## 4. Metal-0 / interconnect pitch and the CPP × MP density metric

**[Fact]** Logic density scaling is frequently summarized in the literature as the **CPP × MP** (contacted poly pitch × minimum metal pitch) product — the area of the smallest repeatable 2-transistor logic tile — because these two orthogonal pitches (gate-direction and fin/metal-direction) are the two knobs that set standard-cell area `[FinFET-CGP-DRC2017]`. **[Fact]** Reported minimum metal pitch (M0/M1, tightest routing layer) figures: 10 nm-class **~48 nm** MP paired with 64 nm CPP; 7 nm-class **~36 nm** MP paired with 44 nm CPP `[FinFET-CGP-DRC2017]`.

---

## 5. Standard-cell layout: fins per device, fin depopulation, gate cut, MOL

**[Fact]** A standard cell is built as a small number of active gate "tracks" crossing a small number of fins, with the cell height defined in terms of **track height** (number of horizontal routing tracks tall) and fin count per device (commonly 2–4 fins for NMOS/PMOS in research PDKs such as ASAP7) `[ASAP7-2016]`.

**[Fact]** Two geometric operations refine the raw fin/gate grid into a working circuit:
- **Fin depopulation / fin cut**: fins that are not needed for a given device are lithographically cut away; in layout views, cut fins are conventionally shown as grayed-out/inactive segments distinct from active fins `[US9337099-FinFET-NonUniform]`.
- **Gate cut / poly cut**: the continuous dummy/poly gate line that runs across an entire standard-cell row (for manufacturing regularity) is selectively cut between cells so that adjacent transistors are not electrically shorted `[US9337099-FinFET-NonUniform]`.

**[Fact]** **Middle-of-line (MOL) local interconnect** structures (trench contacts over source/drain, gate-contact structures) are placed **out of phase from the gate grid by one-half of the gate pitch**, with each local-interconnect line centered between neighboring "virtual" gate-grid lines `[US9337099-FinFET-NonUniform]`. **[Inference]** Geometrically, this means a fully detailed FinFET layout has *two* interleaved periodic line families in the gate direction (gates themselves, and contacts offset by half a pitch) in addition to the fin grid — a richer periodic structure than the simplified "fins + 1-2 gate bars" description in the problem statement, but the simplified version is an accurate and literature-consistent **first-order geometric abstraction** for a synthetic generator, since MOL contact stripes are visually a secondary refinement layered on the same base grid.

---

## 6. Beyond bulk FinFET: fin sidewall angle and 3D-ness

**[Fact]** The defining electrical feature of a FinFET — the gate wrapping three sides of the fin (tri-gate) — is a 3D property not directly visible in a purely top-down 2D SEM image; from directly overhead, a fin reads as a simple rectangle/stripe of a given width and length, with the "wrap" only inferable from tilted or cross-sectional views `[Intel22nm-IEDM2012]`, `[RealWorldTech-Intel22nm]`. **[Inference]** For a top-down synthetic generator (matching the flat 1000×1000-pixel grayscale captures specified in the problem statement `[PS-DriftSense]`), it is geometrically correct and literature-consistent to render fins as simple parallel rectangles; sidewall/3D shading effects belong to the SEM-rendering stage (out of scope for this phase), not the layout geometry stage.

---

## 7. Why FinFET layouts are difficult for localization

This is the geometric crux for the Navigation-Error Recovery problem:

1. **[Fact]** A FinFET array is periodic in **two independent directions simultaneously and at two very different, non-commensurate pitches** — fin pitch (tens of nm) in one axis, CPP (tens of nm, but a *different* value from fin pitch — see Section 3) in the orthogonal axis `[FinFET-CGP-DRC2017]`, `[ASAP7-2016]`. This is structurally similar to DRAM's two-pitch grid (Section 6, `[02_dram_research.md]`), so on its own it would create comparable periodicity-driven ambiguity.
2. **[Inference, key differentiator from DRAM]** However, a FinFET's *within-cell* content is geometrically **sparser and less locally distinctive** than DRAM's: a DRAM unit cell always contains a strong, unique local landmark (a contact/landing-pad dot at a fixed sub-cell offset — Section 4, `[02_dram_research.md]`), whereas a stretch of plain fin lines crossed by one gate bar is close to a **1D-periodic texture with almost no distinguishing local content** — the local appearance of "fin × fin × fin crossed by gate" repeats near-identically not just cell-to-cell but *fin-to-fin within the same cell*, since adjacent parallel fins are visually interchangeable. **[Inference]** This makes small FinFET crops *more* ambiguous per unit area than DRAM crops of the same physical size, because DRAM's 2D contact lattice provides corner-like keypoints (good for classical feature descriptors such as SIFT/ORB corner detectors) roughly every unit cell, while a bare fin/gate crossing is closer to an edge/line feature, which is inherently less discriminative for keypoint-based matching (a line has translational ambiguity along its own length — the well-known **aperture problem** in image matching/optical flow) `[US9430457-AmbiguityReduction]` (ambiguity-reduction patent, general principle), `[OETR-AAAI2022]` (notes matching failure modes under weak local texture).
3. **[Fact]** Standard-cell rows introduce **local, non-periodic breaks** (different cell types, fin depopulation, gate cuts) at irregular intervals that DO carry unique local information — but these breaks are *sparser and more subtle* than DRAM's regular contact lattice, and they are exactly the kind of small, low-contrast feature (a single missing fin, a single cut gate) that SEM noise, edge blooming, and charging artifacts are most likely to obscure `[NatSciRep-SEMDenoising2025]`, `[arXiv-BeamCrossSections-2025]` (noting edge bloom "can obscure structure entirely" in severe charging cases). **[Inference]** This means the very features that would disambiguate a FinFET reference tile from its many periodic look-alikes are also the features most vulnerable to imaging noise — compounding the localization difficulty at the geometry level even before any SEM-physics modeling is applied (SEM physics itself is out of scope for this phase, per task instructions, but this geometric fragility is a first-order design consideration flagged here for downstream noise-modeling work).
4. **[Fact]** Gate length is much smaller than CPP (Section 3), meaning a single reference tile at a 10× zoom-out (per the problem statement's 100×→10× scale disparity `[PS-DriftSense]`) may capture **very few or even zero full gate/fin crossings** if the tile happens to land in a long run of unbroken parallel fins between two standard-cell rows — a further source of within-class visual degeneracy not present in DRAM, where the 6F² cell period is comparatively small and a 1 µm² tile almost always contains many complete unit cells (Section 8, `[02_dram_research.md]`).

---

## 8. ASCII schematic — FinFET standard-cell row motif (top-down)

```
   Fin pitch (Fp)
   |<->|
   |   |   |   |   |   |   |   |     <- parallel fins (vertical), constant pitch Fp
   |   |   |   |   |   |   |   |
===+===+===+===+===+===+===+===+===  <- gate line 1 (horizontal), crosses all active fins
   |   |   |   |   |   |   |   |
   |   |   |   |   |   |   |   |        <-- source/drain region between gates
===+===+===+===+===+===+===+===+===  <- gate line 2 (horizontal), pitch = CPP from gate 1
   |   |   |   |   |   |   |   |
   |xxx|   |   |xxx|   |   |xxx|      <- "xxx" = cut/depopulated fin (irregular, per-cell)
===+===+===+===+===+===+===+===+===  <- gate line 3
   |   |   |   |   |   |   |   |
        CPP (contacted poly pitch, gate-to-gate)
        |<-------------------->|
```

**[Inference]** The regular double-grid (fins × gates) dominates the visual signal; irregular fin cuts and gate cuts are the only local disambiguating features, and they are comparatively sparse — directly illustrating why FinFET reference tiles are geometrically harder to uniquely localize than DRAM tiles of equivalent physical size.

---

## 9. Note on technology-node dependence and the FinFET → GAA transition

**[Fact]** All numeric FinFET parameters in this report are **strongly technology-node dependent**, spanning roughly a 3× range in pitch values between the first commercial FinFET (Intel 22 nm, 2012) and the most advanced FinFET-class nodes surveyed (TSMC/Samsung 5–3 nm class) `[Intel22nm-IEDM2012]`, `[WikiChip-TSMC5nm]`, `[SemiWiki-IEDM2022-TSMC3nm]`. **[Fact]** Beyond roughly the 3 nm generation, the industry roadmap literature (IRDS) describes a transition from FinFET to **gate-all-around (GAA) / nanosheet** device architectures `[IRDS2022-ES]`, a trajectory already anticipated in the earlier `[IRDS2020-ES]` and `[IRDS2021-ES]` editions and discussed academically as one of a sequence of "technology inflection points" from planar to FinFET to nanowire/GAA `[ISPD2016-PlanarFinFETNanowire]` — GAA layouts are geometrically distinct (stacked horizontal sheets rather than vertical fins) and are explicitly **out of scope** for this survey per the problem statement, which specifies FinFET (parallel fin lines) as one of exactly two allowed architecture choices `[PS-DriftSense]`.

---

## 10. Summary table — FinFET geometric primitives for a procedural generator

| Primitive | Geometric role | Periodicity | Typical count in a 1 µm × 1 µm reference tile (order-of-magnitude, fin pitch ≈ 25–45 nm) |
|---|---|---|---|
| Fin | Vertical parallel conductor/active stripe | 1D, along X, pitch = fin pitch | ~22–40 fins |
| Gate line | Horizontal conductor crossing fins | 1D, along Y, pitch = CPP | ~15–22 gate lines (CPP typically ≥ fin pitch at a given node, but node-dependent — see Section 3) |
| Fin cut / depopulation | Local break in fin regularity | Aperiodic, sparse | 0–few per tile |
| Gate cut | Local break in gate regularity | Aperiodic, sparse | 0–few per tile |
| MOL local-interconnect stripe | Secondary line family, offset ½ CPP from gates | 1D, along Y, pitch = CPP, phase-shifted | Optional refinement layer |

Full numeric parameterization (typical values, ranges, units, justification) is provided in [05_generator_parameters.md](05_generator_parameters.md).
