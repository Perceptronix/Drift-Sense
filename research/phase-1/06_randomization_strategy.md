# 06 — Randomization Strategy

Determines which of the parameters catalogued in [05_generator_parameters.md](05_generator_parameters.md) should be **fixed per dataset**, which should be **randomized per sample**, and what ranges keep randomized output physically plausible. No implementation code — this is a specification. Citation keys resolve in [09_complete_reference_list.md](09_complete_reference_list.md).

---

## 1. Guiding principle

**[Recommendation]** The problem statement requires the generator to be run across **at least 30 randomized test cases** with a measurable success rate `[PS-DriftSense]`, and requires every augmentation/noise/geometry choice to be justified against literature `[PS-DriftSense]`. This creates two competing goals that the randomization strategy must balance:

1. **Enough variation** across the 30+ generated samples that the reported success rate reflects genuine robustness, not memorization of one fixed layout.
2. **Enough physical realism** in every sample that a reviewer checking against DRAM/FinFET literature would accept it as a plausible (if simplified) rendering of a real die region — not an arbitrary abstract pattern that happens to look grid-like.

The following classification applies that principle parameter-by-parameter.

---

## 2. Parameters that should remain FIXED (per generated dataset, or globally)

| Parameter | Why fixed |
|---|---|
| `reference_image_size`, `search_image_size` (1000×1000 px) | Contractually fixed by the problem statement `[PS-DriftSense]` — not a content choice at all |
| `scale_ratio` (10×) | Contractually fixed — this is the entire premise of the task `[PS-DriftSense]` |
| `word_line_pitch : bit_line_pitch` ratio (3F : 2F, DRAM) | This ratio is what makes it *6F² DRAM* rather than an arbitrary grid — changing it silently breaks the literature grounding the task requires `[US7349232B2]` |
| Architecture choice (DRAM vs. FinFET) *within one generated pair* | The reference and search image of a single sample must depict the same underlying die architecture — the problem statement's zoom-consistency requirement (same pattern, shrunk 10×) mandates this `[PS-DriftSense]` |
| Cell topology class (6F² for DRAM; fin-and-gate grid for FinFET) | Changing the *topology* (e.g., switching from 6F² to 8F² mid-dataset) is a legitimate cross-dataset variable but should not vary *within* a single reference/search pair, since real dies do not change cell architecture within a 10 µm neighborhood |

---

## 3. Parameters that SHOULD be randomized (per sample), with justified ranges

| Parameter | Randomization range | Physically realistic? | Rationale |
|---|---|---|---|
| `F` (DRAM half-pitch) | Uniform over 10–19 nm (modern node band), optionally extended to ~35–40 nm to also represent older/coarser illustrative generations | Yes, within the quoted node bands `[Micron-1alpha-Product]` | Node-to-node variation is real and literature-documented (Section 5, `[02_dram_research.md]`); randomizing it forces the localization algorithm to be robust to absolute-scale variation, not just to one hard-coded pitch |
| `fin_pitch`, `gate_pitch` (FinFET) | Jointly sampled from node-consistent pairs (e.g., 14 nm-class: fin ~42 nm / CPP ~72 nm; 7 nm-class: fin ~30 nm / CPP ~44–48 nm) rather than independently, since real nodes constrain both together | Yes, if sampled as **correlated pairs**, not independently | Independently randomizing fin_pitch and gate_pitch could produce a physically implausible ratio never seen at any real node (see Section 5, this file, for why independence is the wrong model here) |
| `crop_origin (x, y)` | Uniform over the full valid interior of the synthesized large layout | Yes — this is the ground-truth-generating randomization and has no realism constraint beyond staying inside bounds | This is *the* label-producing randomness; every sample must get an independent random crop location, else the dataset trivially leaks the answer |
| `pattern_phase_alignment` | Uniform over one full unit-cell period, both axes | Yes | Prevents the reference tile from always starting at a "clean" cell boundary, which would be an unrealistic and exploitable shortcut |
| `active_area_tilt_angle` (DRAM) | Sample from the literature-bounded range, e.g., 50–70° (a conservative sub-range of the wider 20–80° patent-claim range flagged in `05_generator_parameters.md`) | Plausible if kept within the sourced range; **[Recommendation]**: do not sample the full 20–80° range without an additional corroborating source, since only one patent family was found supporting the extremes | Real fabs settle on one tilt angle per generation, but that angle varies across vendors/generations, so a bounded random draw represents "which vendor/generation" variability without inventing physically absurd geometries |
| `contact_diameter`, `landing_pad_diameter` (DRAM) | Uniform over the fraction-of-F ranges given in `05_generator_parameters.md` | Plausible within stated bounds, though those bounds are themselves inferred (flagged) rather than directly literature-quantified | Represents realistic CD variation across a wafer and across process generations |
| `num_gate_bars` (FinFET) | Discrete choice, weighted toward 1–2 (per the problem statement's own suggested prompt `[PS-DriftSense]`), with occasional 0 (pure fin field, no gate crossing at all in the tile) and occasional 3+ (denser standard-cell row) | Yes — all are realistic depending on where exactly the crop lands relative to a standard-cell row | Directly controls localization difficulty (Section 7, `[03_finfet_research.md]`); randomizing it is essential to generating a spread of difficulty levels across the 30+ required test cases, supporting a meaningful "success rate" and a genuine failure-case example |
| `fin_cut_probability`, `gate_cut_probability` | Low probability per fin/gate (e.g., 0.1–0.3) | Yes, matches sparse real standard-cell irregularity | Controls how often a disambiguating landmark appears — a key axis of difficulty variation |
| Independent sensor noise (reference vs. search) | Independently re-sampled noise instance for each of the two images, even though they depict the same underlying layout | Mandated explicitly by the problem statement: "don't reuse the same noise on both — they're two separate captures" `[PS-DriftSense]` | Explicit requirement, not a discretionary choice |
| Search-image noise **level** relative to reference | Search image should default to a *higher* noise level than the reference | Mandated: "you should assume wide-search image will be more noisier in test data to check algorithm robustness" `[PS-DriftSense]` (FAQ slide) | Explicit requirement — reflects that a fast, wide-FOV scan is typically noisier than a slow, high-resolution capture in real SEM operation |

---

## 4. Parameters that should be randomized only WITHIN a narrow band, or held semi-fixed to avoid unrealistic output

| Parameter | Concern | Recommended handling |
|---|---|---|
| `line_orientation_offset` (global grid rotation) | A large rotation (e.g., 45°) is geometrically valid but visually atypical for how DRAM/FinFET arrays are normally captured in top-down SEM (dies are conventionally imaged axis-aligned to the scan raster) | **[Recommendation]** Keep near 0° (±0–5°) by default to represent realistic stage/notch misalignment; treat larger rotations (up to arbitrary angles) as an explicitly-labeled "stress test" subset, not the default distribution — mixing them silently into the main 30-sample set would conflate two different difficulty axes (periodicity ambiguity vs. rotational robustness) |
| `word_line_width`, `bit_line_width`, `fin_width`, `gate_length` as *independent* draws | Because these are only loosely bounded by inference rather than hard literature values (flagged in `05_generator_parameters.md`), fully independent wide-range randomization risks producing a duty cycle (line:space ratio) never seen in practice (e.g., lines 90% of the pitch, leaving almost no visible space) | **[Recommendation]** Randomize as a fraction of pitch within the stated 0.35–0.6× band, not as an absolute nanometer value independent of the sampled pitch |
| `fin_pitch` / `gate_pitch` sampled *independently of each other* | As noted in Section 3, real nodes couple these two values; sampling them fully independently could invert the normal relationship (e.g., CPP smaller than fin pitch, which does not occur at any surveyed node — CPP ≥ fin pitch in every table in `03_finfet_research.md`) | **[Recommendation]** Sample a "node profile" (a matched fin_pitch/CPP/gate_length tuple representing one of the surveyed generations) rather than each parameter independently; optionally interpolate *between* two adjacent literature node profiles for finer-grained variation, but never extrapolate outside the literature-bounded envelope |
| `array_mat_size` / mat-boundary appearance (DRAM) | If mat boundaries appear too frequently within crops, most reference tiles would contain an easy non-periodic landmark, artificially deflating task difficulty; if they never appear, the dataset never tests the "genuinely no unique local answer" edge case the problem statement calls out as an expected honest failure mode `[PS-DriftSense]` | **[Recommendation]** Make mat-boundary presence a deliberately controlled, low-probability event (e.g., ~10–20% of samples), not left to emerge accidentally from an unconstrained crop_origin draw over an unbounded array |

---

## 5. Randomizations that would become UNREALISTIC (must be avoided or explicitly flagged as stress-test-only)

| Randomization | Why it would be unrealistic |
|---|---|
| Independently randomizing `fin_pitch` and `gate_pitch` without a node-coupling constraint | Could produce CPP < fin_pitch, contradicting every surveyed data point (Section 3, `[03_finfet_research.md]`) |
| Randomizing `word_line_pitch : bit_line_pitch` away from the 3:2 ratio for a "6F² DRAM" sample | By definition changes the cell topology away from 6F²; if the generator's metadata still labels it "6F² DRAM," this is a literature-inconsistency bug, not a valid variation |
| Setting `active_area_tilt_angle` to 0° or 90° | Removes the diagonal AA that is the defining geometric signature of the 6F² cell (Section 2.3, `[02_dram_research.md]`); at 0°/90° the layout topologically degenerates toward an axis-aligned (8F²-like) cell, which is a different, unlabeled architecture |
| Extremely high `fin_cut_probability` / `gate_cut_probability` (e.g., > 0.5) | Real standard-cell layouts have sparse, not dense, cuts (Section 5, `[03_finfet_research.md]`); a high cut rate would make the FinFET sample resemble random noise rather than a recognizable logic layout, undermining the "realistic" requirement in the grading rubric (30% of marks are for creating "real-like SEM images of FinFET/DRAM stack based on literature study" `[PS-DriftSense]`) |
| Contact/landing-pad diameter exceeding pitch | Physically impossible — contacts cannot overlap into adjacent cells' contacts under the assumed pitch; must always be constrained to a fraction of the governing pitch, not an independent absolute value |
| Reusing identical noise instances between reference and search images | Explicitly disallowed by the problem statement `[PS-DriftSense]` |
| Rotating reference and search layouts by *different* amounts within the same sample pair | Breaks the "same underlying physical layout observed at two scales" premise that the whole task depends on; any global rotation must be applied identically before the two different crops/resamplings are taken |

---

## 6. Suggested per-sample randomization pipeline (conceptual order, not code)

1. Choose architecture (DRAM or FinFET) — fixed for the dataset, or randomized per sample if the team wants a mixed dataset (not required by the problem statement, which allows either architecture as a whole-dataset choice `[PS-DriftSense]`).
2. Draw a **node profile** (a matched, literature-bounded parameter tuple — F for DRAM, or fin_pitch/CPP/gate_length for FinFET).
3. Draw architecture-specific structural randoms within realistic bounds (tilt angle, contact diameter, num_gate_bars, cut probabilities) as catalogued in Section 3.
4. Synthesize one large, internally consistent physical layout at this parameter set.
5. Draw `crop_origin` and `pattern_phase_alignment` to select the reference window; this same physical region, scaled 10×, becomes the ground-truth-labeled location inside the search window.
6. Independently draw two separate noise instances (reference-image noise, search-image noise, search noisier by default) — this stage is explicitly the domain of SEM-physics modeling deferred to a later phase (see [05_generator_parameters.md](05_generator_parameters.md) Section 4), but the *requirement* that they be drawn independently is a randomization-strategy decision recorded here.
7. Record all drawn parameter values plus the ground-truth center offset as sample metadata (see [07_layout_generator_specification.md](07_layout_generator_specification.md) for the full metadata schema).
