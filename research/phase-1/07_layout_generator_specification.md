# 07 — Layout Generator Specification

This file covers two of the original task objectives together, since they are naturally the same document: **(6) Mathematical Representation** — how DRAM and FinFET layouts should be represented procedurally — and **(7) Generator Requirements** — the complete input/output/reproducibility/metadata specification for the future generator. No implementation code, no Python, no neural network design — this is strictly a specification document, per project constraints.

Citation keys resolve in [09_complete_reference_list.md](09_complete_reference_list.md).

---

## PART A — Mathematical Representation

### A.1 Candidate representation families

| Representation | Description | Fit for DRAM | Fit for FinFET |
|---|---|---|---|
| **Regular grid / raster field** | Layout stored as a 2D array of material/layer labels at native design resolution, later downsampled for rendering | Simple for the line grid; awkward for the diagonal active area (aliasing on a raster grid) | Simple — fins/gates are axis-aligned, so a raster grid is a very natural fit |
| **Parametric primitives (lines, rectangles, tilted rectangles, circles/ellipses)** | Layout stored as a list of analytic shapes with exact parametric geometry (start/end points, width, angle, radius) | **Best fit** — word lines, bit lines, and the diagonal AA stripes are all exactly representable as rectangles (axis-aligned or tilted); contacts as circles/ellipses | Excellent fit — fins and gates are axis-aligned rectangles; cuts are simply omitted or shortened rectangles |
| **Vector/polygon collections (GDSII-style)** | Industry-standard IC layout representation: named layers, each containing a list of polygons | Best fit for *authenticity* — this is literally how real DRAM masks are represented; directly compatible with professional EDA tools | Same — this is also how real FinFET/standard-cell layouts are represented in industry |
| **Graph representation** | Layout stored as a graph: nodes = devices/contacts/cells, edges = connectivity or adjacency | Poor fit for *pure geometry* generation (a graph naturally encodes topology/connectivity, not exact coordinates) — more suited to a *netlist*, which this phase explicitly does not need | Same — graphs are the natural representation for standard-cell *placement and routing* logic, not raw geometric rendering |

### A.2 Recommendation

**[Recommendation]** Represent both DRAM and FinFET layouts as a **parametric-primitive / vector-polygon hybrid**, organized exactly like a simplified GDSII layer stack:

- A small number of named **layers** (e.g., `WORD_LINE`, `BIT_LINE`, `ACTIVE_AREA`, `CONTACT` for DRAM; `FIN`, `GATE` for FinFET).
- Each layer holds a list of **parametric shape instances** (axis-aligned rectangle, rotated rectangle, circle/ellipse), each fully described by closed-form parameters (center, width, height, angle) rather than by explicit polygon vertex lists.
- Shape instances are **generated procedurally by tiling a single unit-cell template** across the physical extent needed (large enough to cover the 10 µm search FOV), using the pitch/count relationships defined in [05_generator_parameters.md](05_generator_parameters.md) — this is mathematically a **2D lattice generation** problem (place one motif at every point of a 2D Bravais-like lattice defined by two pitch vectors), which is exactly how the real fabrication masks are algorithmically generated in EDA tools such as `[gdsfactory-repo]`.

**[Fact]** This layered, parametric approach mirrors both the real industry representation (GDSII: named layers of polygons) `[gdsfactory-repo]` and the representation implicitly assumed by the survey document's recommended synthetic pipeline, which names `gdsfactory` specifically as the recommended CAD/GDSII layout engine for procedurally synthesizing DRAM and FinFET geometry `[SEM-Dataset-Survey]`.

### A.3 Why not raw raster generation

**[Inference]** Generating the layout directly as a pixel raster (rather than as parametric shapes later rasterized) would conflate two distinct concerns — *exact geometric ground truth* (needed for the precise ground-truth center offset the task requires `[PS-DriftSense]`) and *pixel-level rendering* (needed only for the final image, and properly the concern of a later SEM-rendering phase). Keeping the geometry parametric until the final rendering step preserves sub-pixel-exact ground truth and lets the *same* parametric layout be sampled at two different pixel densities (1 nm/px reference, 10 nm/px search) with guaranteed self-consistency — directly satisfying the scale-ratio requirement in Section 0 of [05_generator_parameters.md](05_generator_parameters.md).

### A.4 DRAM as a 2D lattice — formal sketch (description only, no code)

A 6F² DRAM array is mathematically a 2D lattice with two primitive translation vectors corresponding to the word-line and bit-line pitches, with a **basis** (the repeated motif placed at every lattice point) consisting of: one word-line segment, one bit-line segment, one diagonal active-area stripe at the specified tilt angle, and one contact dot at the AA/line intersection. This is directly analogous to a crystallographic unit cell with a multi-atom basis — a well-established mathematical abstraction, here applied to layout geometry rather than atomic structure. **[Inference]** This framing is useful because it makes explicit *why* the periodicity-ambiguity problem exists mathematically: any two lattice points related by an integer combination of the primitive translation vectors are, by construction, indistinguishable within one motif's extent (Section 6, [02_dram_research.md](02_dram_research.md)).

### A.5 FinFET as a two-family line lattice — formal sketch

A FinFET region is mathematically the **union of two independent 1D periodic line families on orthogonal axes** (fins at `fin_pitch` along X, gates at `gate_pitch` along Y), *not* a single 2D lattice with a rich basis like DRAM — because, unlike DRAM's per-cell contact, there is no motif element repeating with *both* periods simultaneously in the simplified representation. Fin/gate cuts are modeled as **local exceptions** (a Bernoulli/point-process draw per fin or per gate segment) rather than as part of the periodic lattice itself — mathematically, this is a "periodic signal plus sparse random defect process," a representation directly analogous to how crystallographic defects are modeled in materials science (a periodic lattice plus a low-density point-defect process), which is an appropriate and literature-consistent way to represent the sparse fin-cut/gate-cut irregularity discussed in Section 5, [03_finfet_research.md](03_finfet_research.md).

---

## PART B — Generator Requirements

### B.1 Inputs

| Input category | Contents |
|---|---|
| Architecture selection | `DRAM` or `FinFET` (mutually exclusive per sample, per [06_randomization_strategy.md](06_randomization_strategy.md) Section 2) |
| Node profile | A literature-bounded parameter tuple (see [05_generator_parameters.md](05_generator_parameters.md)): for DRAM, `F`; for FinFET, matched `(fin_pitch, gate_pitch, gate_length)` |
| Structural randomization seeds | Values for all Section-3-of-`06_randomization_strategy.md` randomized parameters (tilt angle, contact diameter, num_gate_bars, cut probabilities, etc.) |
| Global RNG seed | A single top-level seed controlling all downstream random draws, for reproducibility (Section B.4) |
| Imaging-geometry constants | The fixed values from Section 0 of [05_generator_parameters.md](05_generator_parameters.md) (1000×1000 px, 10× scale ratio, etc.) — inputs in the sense that they are configurable constants, even though the problem statement fixes their *values* |

### B.2 Outputs

| Output | Description |
|---|---|
| Reference image (pre-noise) | The exact 1000×1000, 1 nm/px parametric-layout render of the 1 µm × 1 µm reference window |
| Search image (pre-noise) | The exact 1000×1000, 10 nm/px parametric-layout render of the 10 µm × 10 µm search window, containing the same underlying layout as the reference |
| Ground-truth center offset `(x, y)` | Sub-pixel-precision location of the reference pattern's center within the search image, in search-image pixel coordinates |
| Full parameter record (metadata) | Every input parameter and every randomly-drawn value used to generate this specific sample (Section B.5) |
| *(Deferred to a later phase)* Noise-augmented reference/search images | SEM-realistic noisy renders — explicitly out of scope for this geometry-only phase, per task instructions, but the pre-noise outputs above are the designed hand-off point to that later stage |

### B.3 How randomness should work

**[Recommendation]**, synthesizing [06_randomization_strategy.md](06_randomization_strategy.md):

- All randomness must flow from a **single seeded RNG stream per sample**, so that re-running the generator with the same seed reproduces an identical sample (Section B.4).
- Randomness should be applied in the fixed conceptual order given in Section 6 of [06_randomization_strategy.md](06_randomization_strategy.md): architecture → node profile → structural parameters → large-layout synthesis → crop origin/phase → (deferred) noise instances.
- Coupled parameters (e.g., FinFET `fin_pitch`/`gate_pitch`) must be drawn **jointly** (as a node-profile tuple or interpolation between two profiles), never as fully independent draws, to avoid the unrealistic combinations flagged in Section 5 of [06_randomization_strategy.md](06_randomization_strategy.md).
- The **noise draw** for the reference image and the noise draw for the search image must use **distinct** random sub-streams, per the explicit problem-statement requirement that the two images not reuse the same noise `[PS-DriftSense]`.

### B.4 How reproducibility should work

**[Recommendation]**:

- Every generated sample must be fully reproducible from **one top-level integer seed** plus the chosen architecture and node-profile selection — i.e., `generate(seed, architecture, node_profile) → (reference_image, search_image, ground_truth, metadata)` must be a deterministic function (conceptually; no implementation prescribed here).
- The metadata record (Section B.5) must itself be sufficient to regenerate the sample byte-for-byte, meaning every randomly-drawn parameter value (not just the seed) should be recorded — this guards against reproducibility breaking silently if the generator's internal random-draw *order* ever changes between versions (a well-known reproducibility hazard with seeded RNG pipelines).
- The 30+ required test cases `[PS-DriftSense]` should each use a distinct, recorded seed so the reported success rate is itself reproducible and auditable by graders.

### B.5 What metadata should be saved

| Metadata field | Purpose |
|---|---|
| `sample_id`, `seed` | Reproducibility (Section B.4) |
| `architecture` (DRAM / FinFET) | Records the top-level design choice |
| `node_profile` (F, or fin_pitch/gate_pitch/gate_length) | Records which literature-bounded generation this sample represents — essential for later literature-justification writeups per the grading rubric's 30%-weighted "justify against literature" requirement `[PS-DriftSense]` |
| All structural parameter values actually drawn (tilt angle, contact diameter, num_gate_bars, cut positions, etc.) | Full audit trail; needed to reproduce and to analyze *why* a given sample was easy or hard (supports the required failure-case explainability, 10% of grading rubric `[PS-DriftSense]`) |
| `crop_origin`, `pattern_phase_alignment` | Together with the layout parameters, these fully determine the ground truth |
| `ground_truth_center (x, y)` | The label itself |
| Noise-model parameters *(recorded here even though generation is deferred)* | So that later phases' noise choices are still traceable per-sample once implemented |
| Literature citation keys used to justify this sample's parameter choices | Directly supports the rubric requirement to justify every augmentation/geometry choice against ≥2–3 credible public sources `[PS-DriftSense]` |

---

## PART C — Traceability to the grading rubric

**[Fact]** The problem statement specifies the following grading weights: 50% localization accuracy (including computation time), 30% "Augmentation code which can create real-like SEM images of FinFET/DRAM stack based on literature study," 10% root-cause/explainability on failure cases, plus bonus credit for RGB/optical generalization `[PS-DriftSense]`. **[Inference]** This phase-1 specification is deliberately structured to feed directly into the 30% literature-grounded-realism component (via the per-parameter citation discipline in [05_generator_parameters.md](05_generator_parameters.md)) and the 10% explainability component (via the metadata-driven difficulty traceability in Section B.5 above, and the explicit periodicity-ambiguity analysis in [02_dram_research.md](02_dram_research.md)/[03_finfet_research.md](03_finfet_research.md) Section 7 of each, which pre-identifies *why* certain crops will be inherently hard — the honest example of failure the rubric requires).
