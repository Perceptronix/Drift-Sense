# 02 — DRAM Layout Geometry Research

Scope: pure layout geometry of DRAM memory arrays — not fabrication process, not device physics, not SEM optics. All claims tagged **[Fact]**, **[Inference]**, or **[Recommendation]**. Citation keys resolve in [09_complete_reference_list.md](09_complete_reference_list.md).

---

## 1. What a DRAM array actually is, geometrically

A DRAM chip is dominated by area by its **cell array** (also called the "mat" or "sub-array"): a large, near-perfectly repeating 2D grid of unit memory cells, each holding one bit as charge on a capacitor gated by one access transistor (the "1T1C" cell). **[Fact]** The array is bordered by much less regular **peripheral circuitry** (row decoders, sense amplifiers, column decoders, I/O) — but the SEM navigation-error problem, per the problem statement, concerns finding a small tile *inside* a periodic array, so this report concentrates on the array interior `[PS-DriftSense]`.

Geometrically, the array is built from two orthogonal families of parallel conductive lines:

- **Word lines (WL)** — run in one direction (call it rows), gate the access transistors, typically implemented as **buried word lines (bWL)** in modern nodes (recessed into the substrate rather than running on the surface) `[Kim2003-6F2-BuriedWL]`, `[Kwon-Thesis-UCBerkeley]`.
- **Bit lines (BL)**, also called **digit lines** — run perpendicular to word lines (columns), carry the sensed charge to the sense amplifiers `[Stanford-DRAM-Notes]`, `[US7349232B2]`. The open-bit-line sensing scheme that pairs with the 6F² cell is independently corroborated at the circuit level by `[MultiGb-6F2-OpenBL]`.

At the geometric intersections of the (implicit) word-line/bit-line grid, **contacts** connect the active-area diffusion to either the bit line (bit-line contact, BLC) or to the storage capacitor (storage-node contact, SNC), each mediated by a **landing pad** in many generations `[DRAM-EUV-SNLP-Patterning]`, `[US2021320106-SNLP-Airgap]`. It is this dense field of periodic contact/via dots superimposed on a periodic line grid that gives DRAM SEM images their unmistakable "polka-dot-on-graph-paper" texture.

---

## 2. The unit cell: 6F2, 8F2, and the 4F2 aspiration

### 2.1 The "F" convention

**[Fact]** In DRAM literature, all dimensions are conventionally expressed as multiples of **F**, the minimum lithographically resolvable half-pitch (feature size) of that generation — i.e., F = half the minimum pitch of the tightest repeating line/space pattern the process can print `[ITRS2001-PIDS]`, `[Stanford-DRAM-Notes]`. Expressing cell area as "nF²" (6F², 8F², 4F²) lets engineers compare cell efficiency across process generations independent of the absolute lithography node.

### 2.2 8F2 → 6F2 → (4F2 aspirational)

| Cell type | Cell area | Word-line pitch | Bit-line pitch | Historical status |
|---|---|---|---|---|
| **8F²** (folded bit-line) | 8F² | 2F | 4F | Dominant through ~2007; bit line must "fold" past every other cell for noise cancellation, costing area `[EDN-8F2vs6F2]`, `[US6884676B2]` |
| **6F²** (open bit-line, tilted active area) | 6F² | **3F** | **2F** | Industry-standard since ~2007 (Micron first at 9x nm, Samsung at 80 nm, SK Hynix at 3x nm); dominant cell type today through the 1z/1α/1β generations `[EDN-8F2vs6F2]`, `[Kim2003-6F2-BuriedWL]` |
| **4F²** (vertical/cross-point access device) | 4F² | 2F | 2F | Theoretical density limit; not in mainstream mass production as of the literature surveyed — requires a vertical-channel access transistor (VCT) since a planar transistor cannot fit in 4F² `[EDN-8F2vs6F2]`, `[Kwon-Thesis-UCBerkeley]`. One vendor (CXMT) has been reported pursuing a VCT + 4F² 18 nm design, per secondary press — **flagged as unconfirmed by a primary technical source** in this survey. |

**[Fact]** For the 6F² cell specifically: word-line pitch = **3F**, bit-line pitch = **2F**, and each unit cell spans 6F² of array area `[US7349232B2]` ("6F2 DRAM cell design with 3F-pitch folded digitline sense amplifier" — the name of the patent literally encodes the 3F word-line pitch), corroborated independently by `[US20060281250A1]` and `[Orthogonal-6F2-Trench]`, which both describe a 6F² unit cell with "Y-axial length 6F, X-axial length 2F."

### 2.3 Why the active area is diagonal, not axis-aligned

**[Fact]** In the 6F² cell, the active-area (diffusion) stripe that hosts the transistor is **tilted at an angle relative to both word lines and bit lines** — commonly described in patents as oriented so each active-area stripe crosses exactly one bit line and two word lines `[Orthogonal-6F2-Trench]`, `[US20060281250A1]`. This diagonal-active-area geometry is what allows the 6F² cell to beat the axis-aligned 8F² cell in area while still fitting one transistor per active island. Reported tilt angles in patent claims range broadly (roughly 20°–80° from the bit-line centerline depending on the specific implementation) `[US20060281250A1]` — this is a **patent-only claim range**, not independently corroborated by a peer-reviewed source in this survey, and is flagged accordingly in [08_open_questions.md](08_open_questions.md). **[Inference]** A commonly used and image-plausible value is **~55°–65°** off horizontal, matching the "distinctly diagonal but not near 45°" appearance seen in published cross-sectional/top-down DRAM array micrographs cited across the DRAM patent corpus.

### 2.4 Buried word lines

**[Fact]** From roughly the 6x–5x nm DRAM generations onward, word lines are **buried** — recessed into trenches etched into the silicon rather than routed as a surface gate stack `[Kim2003-6F2-BuriedWL]`, `[Kwon-Thesis-UCBerkeley]`. **[Inference]** For a *top-down* SEM image (the relevant view for this hackathon's navigation problem, since the reference/search images are described as flat 1000×1000 grayscale captures, not cross-sections), buried word lines still project a visible periodic line pattern at the surface because the word-line trench and its isolation collar remain visible as a surface contrast band, even though the conductor itself sits below the silicon surface.

---

## 3. Bit-line architecture: open, folded, twisted

**[Fact]** Three canonical DRAM bit-line array architectures exist, differing in how sense amplifiers pair up bit lines for differential sensing: **open bit-line**, **folded bit-line**, and **twisted bit-line** `[Stanford-DRAM-Notes]`. They trade off array area against sense-amplifier noise immunity:

| Architecture | Area efficiency | Noise immunity | Compatible cell type |
|---|---|---|---|
| Open bit-line | Best (enables 6F²) | Worst (reference and signal BL are in different arrays, more susceptible to coupled noise) | 6F² |
| Folded bit-line | Worse (forces 8F²-class cells) | Best (both BLs of a sense amp run through the same array, common-mode noise cancels) | 8F² |
| Twisted bit-line | Intermediate | Intermediate–good | Either, with added routing complexity |

**[Inference]** Because this hackathon problem cares about *what the SEM sees*, not circuit noise performance, and because 6F² (open bit-line) is the literature-dominant modern cell `[EDN-8F2vs6F2]`, the **6F² open-bit-line array is the recommended geometric template** for the synthetic DRAM generator; a folded/twisted layout would visually manifest mainly as small periodic line offsets that are a secondary-order refinement, not a first-order requirement.

---

## 4. Contacts, landing pads, and capacitors — the "polka dots"

**[Fact]** Two distinct contact types populate a DRAM array, alternating in a periodic pattern along each active-area stripe:

1. **Bit-line contact (BLC)** — connects the shared drain of two adjacent transistors to the bit line above.
2. **Storage-node contact (SNC)**, typically via a **storage-node landing pad (SNLP)** — connects the transistor's other terminal up to the storage capacitor `[DRAM-EUV-SNLP-Patterning]`, `[US2021320106-SNLP-Airgap]`.

**[Fact]** The SNLP exists specifically because the capacitor pitch (set by the 6F² cell's diagonal geometry) does not directly align with the contact directly beneath it; the landing pad is a small conductive island that reconciles the offset, and it is patterned as its own periodic dot array layer, separate from the contact layer beneath it `[DRAM-EUV-SNLP-Patterning]`. **[Inference]** In a top-down SEM image, this SNLP layer is often the *most visually prominent* periodic dot pattern in a DRAM array — more prominent than the finer bit-line contacts — because landing pads are deliberately enlarged relative to the raw contact to relax overlay tolerance.

**[Fact]** Storage capacitors in modern DRAM are overwhelmingly **stacked capacitors positioned above the bit-line level** ("Capacitor-over-Bit-line," COB) rather than trench capacitors in current mainstream nodes `[Kwon-Thesis-UCBerkeley]`. Trench capacitors (etched into the substrate) were the historical alternative and remain relevant to some specialty/embedded DRAM `[US6288422-6F2-Vertical]`-class designs but are not the dominant modern topology. **[Inference]** For a purely *top-down* geometric synthetic generator, COB vs. trench distinction matters only insofar as it determines whether the capacitor footprint appears as a dot at the *top* metallization layer (COB, most common — and this is what a typical top-down SEM inspection captures) — so COB is the recommended default assumption.

---

## 5. Numeric scale: cell size and pitch across DRAM generations

**[Fact]** DRAM technology nodes are named by their **half-pitch** — literally F, half of the minimum active-area/word-line pitch in the array `[Micron-1alpha-Product]`. The naming progressed 1x → 1y → 1z → 1α → 1β → 1γ as node names ran out of round nanometer numbers and Roman/Greek-letter sub-generations were introduced:

| Generation | Approx. half-pitch (F) range | Notes |
|---|---|---|
| 1x nm class | ~19 nm class (upper end of 10 nm-class) | Early "10nm-class" DRAM |
| 1y nm class | ~17–18 nm class | |
| 1z nm class | ~14–16 nm class ("c.13–11nm" reported by one vendor roadmap) | `[Micron-1alpha-Blog]` |
| **1α (1-alpha)** | **10–19 nm half-pitch band** (4th generation of the "10 nm class"); reported ~40% density gain over 1z | `[Micron-1alpha-Blog]`, `[Micron-1alpha-Product]` |
| 1β (1-beta) | Sub-1α, early development/production as of source dates | `[Micron-1alpha-Blog]` |
| 1γ (1-gamma) | Early process integration; EUV-dependent | `[Micron-1alpha-Blog]` |

**[Fact — flagged as broad/approximate]** The **"1α node half-pitch ranges from 10 to 19 nm"** figure is stated directly by the sourced material `[Micron-1alpha-Blog]` but is unusually wide for a single named node; it likely reflects that vendor roadmap naming does not map 1:1 to a single physical dimension across companies (Samsung/SK hynix/Micron each use their own generation labels for roughly comparable but not identical geometries). **[Recommendation]** Treat any specific "1α = X nm" claim as **order-of-magnitude only** (i.e., "low-to-mid teens nanometers half-pitch") rather than a precise design rule, and do not hard-code a single F value for "modern DRAM" in the generator — instead expose F as a randomizable parameter (see [05_generator_parameters.md](05_generator_parameters.md) and [06_randomization_strategy.md](06_randomization_strategy.md)).

**[Fact]** Cell-area history in absolute terms, drawn from the DRAM survey source `[SEM-Dataset-Survey]` (citing NIST/Zenodo-indexed process papers) and corroborated by patent-disclosed values:
- 68 nm design rule 6F² cell: **0.028 µm²** cell area.
- 46 nm buried-word-line 6F² cell: **0.013 µm²** cell area.
- 150 nm-class trench-capacitor DRAM cell (older generation): **0.135 µm²**.

This overall scaling trajectory (steady half-pitch shrink generation over generation, with 6F² remaining the dominant topology across all of it) is independently corroborated by analyst/industry-history sources `[TechInsights-DRAMScaling]`, `[SemiAnalysis-MemoryWall]`, and by device-level teardown commentary on where the 4F²/6F² boundary has actually landed in shipping product `[ChipworksRealChips-4F2v6F2]`. These three numeric data points are internally consistent with the 6F² = 6 × F² formula (e.g., F ≈ 68 nm/2 ≈ 34 nm design-rule-equivalent half-pitch gives 6×(0.034 µm)² ≈ 0.0069 µm², which is roughly half the quoted 0.028 µm² — the discrepancy is expected because "68 nm design rule" refers to a *lithography generation label*, not literally F itself; **[Inference]** vendors' node names and the literal F used in the 6F² formula diverge by generation, another reason to treat F as a tunable/randomizable parameter rather than derive it algebraically from a marketing node name).

---

## 6. Why DRAM produces highly periodic SEM images

This is the central geometric fact that makes DRAM relevant (and hard) for the Navigation-Error Recovery problem:

1. **[Fact]** The array is a true 2D crystallographic-style lattice: word lines repeat with period 3F (in 6F²) along one axis, bit lines repeat with period 2F along the orthogonal axis, and the diagonal active-area/contact motif repeats with the same fundamental cell periodicity `[US7349232B2]`, `[Orthogonal-6F2-Trench]`. Within a single mat, this periodicity is essentially exact — it is generated by a step-and-repeat lithographic exposure of the same mask cell, so translational symmetry is not approximate, it is by construction `[ITRS2001-PIDS]`.
2. **[Fact]** Because the pattern is periodic in *two independent directions* (not just one, as with a simple line/space grating), any local image patch that is smaller than roughly one array pitch in extent is **statistically indistinguishable from every other patch shifted by an integer number of unit cells** — this is a basic aliasing/ambiguity property of any 2D lattice, and it directly produces **multiple equally strong correlation peaks** when a small reference tile is cross-correlated against a larger periodic search image `[US9430457-AmbiguityReduction]` (a patent explicitly addressing "ambiguity reduction" in image alignment for exactly this class of repeating-pattern problem).
3. **[Inference]** The array-vs-periphery structure compounds this: *inside* the array, translational symmetry holds almost perfectly for potentially hundreds to thousands of unit cells in each direction (arrays are commonly organized into large "mats" for sense-amplifier sharing efficiency); only at mat boundaries, redundancy-repair rows/columns, or the transition to peripheral circuitry does the pattern break `[Kwon-Thesis-UCBerkeley]`. A reference tile drawn from deep inside a mat may have **no unique correct match** at all within a 10×10 mat neighborhood other than by using absolute (non-repeating) context outside the array — this is the fundamental reason the Navigation-Error Recovery task explicitly calls out DRAM/FinFET periodicity as "what makes this genuinely hard rather than a simple exact-pixel lookup" `[PS-DriftSense]`.
4. **[Fact]** This periodicity-induced ambiguity is a well-documented general phenomenon in template-matching/registration literature, independent of the semiconductor domain: repeated content produces multiple correlation peaks of similar amplitude, and misregistration by exactly one repeat period can still yield a strong (wrong) correlation score `[US9430457-AmbiguityReduction]`.

---

## 7. ASCII schematic — 6F2 open-bit-line array motif (top-down, one unit cell repeated 3×3)

```
        BL(2F)   BL      BL
          |       |       |
   WL(3F)-+---o---+---o---+---   <- word line 1
          |  /|   |  /|   |
          | / |   | / |   |      "/" = diagonal active area
   WL-----+---+---o---+---o---   <- word line 2  (contacts alternate BLC/SNC)
          |  /|   |  /|   |
          | / |   | / |   |
   WL-----+---o---+---o---+---   <- word line 3
          |       |       |
     each "o" = contact/landing-pad dot (SNC or BLC, alternating along the diagonal AA)
     vertical lines = bit lines (pitch 2F)   horizontal lines = word lines (pitch 3F)
```

**[Inference]** This 2-line-family-plus-dot-lattice structure is precisely why a DRAM SEM crop reads visually as "graph paper with polka dots": the strong, regularly spaced Manhattan line grid provides high-frequency edge content in two orthogonal directions, and the contact/landing-pad dots provide a third, offset periodicity — giving the image very strong, very regular spatial-frequency peaks (i.e., a small number of dominant Fourier components), which is the geometric root cause of both (a) the "highly periodic" visual character called out in the problem statement `[PS-DriftSense]`, and (b) its resulting aliasing/repeat-match ambiguity for localization algorithms `[US9430457-AmbiguityReduction]`.

---

## 8. Summary table — DRAM geometric primitives for a procedural generator

| Primitive | Geometric role | Periodicity | Typical count in a 1 µm × 1 µm reference tile (order-of-magnitude, F ≈ 15–20 nm) |
|---|---|---|---|
| Word line | Horizontal conductor, pitch 3F | 1D, along Y | ~15–22 lines |
| Bit line | Vertical conductor, pitch 2F | 1D, along X | ~25–33 lines |
| Active area (AA) | Diagonal diffusion stripe | 1D, along diagonal, period = cell pitch | ~100s of stripes (short segments) |
| Contact / landing pad | Small dot at AA ∩ WL/BL registration point | 2D lattice, period = 6F² cell | ~100–300 dots |
| Array mat boundary | Local symmetry break | Aperiodic, low frequency | 0–1 per tile (depends on tile placement) |

Full numeric parameterization (typical values, ranges, units, justification) is provided in [05_generator_parameters.md](05_generator_parameters.md).
