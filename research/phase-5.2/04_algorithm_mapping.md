# Algorithm Mapping

**Research Phase:** 5.2
**Document:** 04_algorithm_mapping.md
**Date:** 2026-07-30

---

## 1. Mapping Convention

Every implementation algorithm below maps directly to a **Frozen Specification** (Phases 3.1–3.4, 4.2). Three markers are used throughout:

- **Frozen Specification** — the certified requirement (cannot change).
- **Implementation Decision** — the algorithm chosen here (frozen for this phase).
- **Future Optimization** — a faster variant noted but deferred.

---

## 2. Algorithm A1: GDSII → PixelMask Rasterization

| Aspect | Specification |
|---|---|
| **Frozen Spec** | I1 contract: GDSII file + layer + (M, N, pixel_size_nm) → PixelMask (M×N uint8 ∈ {0,1}) |
| **Inputs** | Flattened polygon list (nm), M, N, pixel_size_nm, origin |
| **Outputs** | Coverage map (float32) → PixelMask (uint8) |
| **Algorithm** | **Edge-function supersampling fill** (Implementation Decision): for each pixel, test 8×8 sub-sample points; coverage = fraction inside polygon; threshold ≥ 0.5 → 1 |
| **Complexity** | O(P × S²) where P = polygons × edges intersecting, S = 8 sub-samples. For CD-SEM FOV: < 50 ms |
| **Numerical considerations** | Use int64 coordinates (nm → integer lattice) to avoid float non-determinism; even-odd fill rule for holes |
| **Validation** | Golden: unit square at origin → exact coverage; property: Σ coverage = area / pixel_area ± 1 px²; translation/rotation invariance (90°) |

**Future Optimization:** Sweep-line scan conversion (O(P + pixels)) with sub-pixel antialiasing — deferred until profiling demands.

---

## 3. Algorithm A2: Height Field Generation

| Aspect | Specification |
|---|---|
| **Frozen Spec** | I2: PixelMask + LayerStack → HeightField_det (float64 nm), MaterialMap_det (uint8) |
| **Inputs** | PixelMask, LayerStack, ProcessConfig |
| **Outputs** | HeightField_det, MaterialMap_det |
| **Algorithm** | **Ordered process-plan execution** (Implementation Decision): layer_stack resolves plan; each process step (deposition, litho, etch, cmp, corner) mutates HeightField + MaterialMap; final assembly validates I2 postconditions |
| **Complexity** | O(M × N) per step; O(M × N × steps) total. ~10 steps × 1024² = ~10⁷ ops < 100 ms |
| **Numerical considerations** | Float64 throughout; substrate baseline Z=0; heights monotonic (no negative); NaN/Inf banned by validation |
| **Validation** | Per-structure golden profiles; I2 postconditions (dimensions, finiteness, trapezoid invariant) |

---

## 4. Algorithm A3: Trapezoidal Profile Synthesis (Etch Sidewall)

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 3.2: etch produces trapezoidal cross-section with sidewall_angle ∈ [80°, 90°], top_CD ≤ bottom_CD |
| **Inputs** | Mask edge positions, depth_nm, sidewall_angle_deg, layer material stack |
| **Outputs** | Height field carving with sloped walls |
| **Algorithm** | **Per-column trapezoid carving** (Implementation Decision): horizontal sidewall run `Δx = depth / tan(angle)`. For each mask-edge column, height transitions linearly from top to bottom over Δx. `bottom_CD = top_CD + 2·depth/tan(angle)` (line); contact holes become inverted truncated cones |
| **Complexity** | O(M × N) — each column written once |
| **Numerical considerations** | Angle → slope = 1/tan(θ); for θ = 90°, Δx = 0 (vertical). Guard tan(θ) ≈ 0 → treat as vertical. Integer pixel edges mapped to float heights |
| **Validation** | Cross-section: measured top_CD, bottom_CD within 0.1 nm of analytic trapezoid; angle measured from profile within 0.1° |

**Future Optimization:** Distance-transform-based signed offset (single pass, vectorized) — deferred.

---

## 5. Algorithm A4: Sidewall Angle Computation (Measurement)

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 3.4: sidewall angle derived from CD_top, CD_bottom, height |
| **Inputs** | HeightField, feature edges |
| **Outputs** | sidewall_angle_deg per feature |
| **Algorithm** | **Profile-fit** (Implementation Decision): extract column profile through feature center; fit trapezoid; θ = arctan(2·height / (CD_bottom − CD_top)) |
| **Complexity** | O(height × width of profile window) — negligible |
| **Numerical considerations** | Degenerate case CD_bottom = CD_top → θ = 90°; guard division |
| **Validation** | Golden trapezoid → angle recovered within 0.1° |

---

## 6. Algorithm A5: Conformal Deposition

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 3.2: conformal film thickness t on all surfaces (walls + floor + top) |
| **Inputs** | Current HeightField, deposition mask, thickness_nm, material_id |
| **Outputs** | Updated HeightField (film grown), MaterialMap |
| **Algorithm** | **Chebyshev isosurface offset** (Implementation Decision): compute Chebyshev distance transform d(x) from the "exposed surface" set; add material where d ≤ t; H_new = max(H, baseline + t − d) |
| **Complexity** | O(M × N) via distance_transform_edt (two-pass chamfer) |
| **Numerical considerations** | Chamfer metric approximates Chebyshev (±1 px); for 2.5D fine; thickness uniform along surface normal within the 2.5D approximation |
| **Validation** | Known trench: conformal thickness on walls measured = t ± 0.1 nm |

**Future Optimization:** Exact Euclidean 3D offset via EDT — deferred; 2.5D approximation sufficient for planar CD-SEM structures.

---

## 7. Algorithm A6: CMP Planarization

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 3.2: global + local planarization to target height, optional over-polish |
| **Inputs** | HeightField, target_height_nm, over_polish_nm, window_px |
| **Outputs** | Planarized HeightField |
| **Algorithm** | **Clip + local erosion** (Implementation Decision): H = min(H, target). If local window > 1: H = min(H, uniform_filter(H, window)); then min(H, target − over_polish) |
| **Complexity** | O(M × N) |
| **Numerical considerations** | uniform_filter padding = 'reflect' (deterministic); erosion never increases height |
| **Validation** | Planar top within 0.1 nm; over-polish removes exactly over_polish_nm below target |

---

## 8. Algorithm A7: LER Generation (Exponential ACF)

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 3.3: LER with exponential ACF, parameters 3σ, ξ (correlation length), ρ (left–right correlation); mean zero |
| **Inputs** | Edge pixel sets, edge orientation, (3σ_nm, ξ_nm, ρ), seed |
| **Outputs** | Per-edge normal displacement array (nm) |
| **Algorithm** | **1D spectral synthesis** (Implementation Decision): for each line edge, PSD(k) = (2·ξ·σ²)/(1 + (ξ·k)²) (exponential ACF Fourier pair); sample complex Gaussian FFT coefficients from seeded RNG (rng_utils); inverse FFT → real correlated profile; normalize to exact σ; scale to 3σ; apply −ρ correlation between paired left/right edges |
| **Complexity** | O(L log L) per edge (FFT), L = edge length in px |
| **Numerical considerations** | σ² must use the single-sided PSD normalization; enforce zero mean by subtracting mean; use np.fft with explicit seed; edge length must exceed ~4ξ for statistically valid samples |
| **Validation** | Measured 3σ ∈ configured ± 0.3 nm; measured ξ ∈ ±10%; ρ ∈ ±0.05; mean ≈ 0 (±0.05 nm); power spectral density shape matches exponential ACF (fit test) |

**Future Optimization:** Precompute PSD templates; reuse across edges of identical length — deferred.

---

## 9. Algorithm A8: Overlay Application

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 3.3: overlay = translational shift (dx, dy) sampled per structure from seeded normal; shift entire topography |
| **Inputs** | HeightField, MaterialMap, dx_nm, dy_nm, seed |
| **Outputs** | Shifted HeightField, MaterialMap |
| **Algorithm** | **Separable spline translation** (Implementation Decision): decompose shift into integer + fractional pixel parts; apply integer shift by slicing (lossless); apply fractional part via scipy.ndimage.shift(order=1, mode='constant') |
| **Complexity** | O(M × N) |
| **Numerical considerations** | order=1 (bilinear) is deterministic; order>1 can overshoot (ringing) — rejected. mode='constant' (zero fill) keeps out-of-FOV unambiguous. MaterialMap shifted with order=0 (nearest) to preserve integer IDs |
| **Validation** | Known feature at (x₀, y₀) → after shift at (x₀+dx, y₀+dy) ± 0.1 nm; material IDs intact |

---

## 10. Algorithm A9: Material Encoding & Update

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Material IDs uint8 ∈ {0..6}: 0 vacuum, 1 Si, 2 SiO₂, 3 SiN, 4 Cu, 5 W, 6 PR |
| **Inputs** | MaterialMap, edge displacement map (from LER), step results |
| **Outputs** | Updated MaterialMap |
| **Algorithm** | **Edge-adjacent-only update** (Implementation Decision): after each geometry operation, recompute material only within a 2-px band around the changed height-field region; interior pixels carry material from the layer stack ordering (top-most material wins) |
| **Complexity** | O(edge band area) ≪ O(M × N) |
| **Numerical considerations** | ID 0 (vacuum) where H = 0 baseline and not covered; erosion of one material by another follows stack order |
| **Validation** | Material ID agreement with cross-section; no ID outside {0..6}; thin films (1 px) not erased by off-by-one |

---

## 11. Algorithm A10: Distance Transform (for GT-supporting edge maps)

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 4.4 GT: signed distance to nearest edge, 0.1 nm precision |
| **Inputs** | HeightField, edge threshold (0.5 × max_height default) |
| **Outputs** | Signed distance map (float64 nm) |
| **Algorithm** | **EDT on binarized height field** (Implementation Decision): binarize H ≥ threshold; Euclidean distance transform (skimage distance_transform_edt) for interior/exterior; sign: + outside, − inside; scale by pixel_size_nm |
| **Complexity** | O(M × N) |
| **Numerical considerations** | 0.1 nm precision requires float64 and true Euclidean metric (not chamfer) — use distance_transform_edt (exact) |
| **Validation** | Known line → signed distance exact to analytic; zero contour = true edge |

*Note: A10 belongs to data_groundtruth (Phase 5.3+), listed here because edge_detector reuses the same EDT machinery.*

---

## 12. Algorithm Summary Table

| # | Algorithm | Frozen Spec Source | Complexity | Key Numerical Care | Validation |
|---|---|---|---|---|---|
| A1 | GDSII rasterization | Phase 3.1, I1 | O(P·S²) | int64 lattice; even-odd rule | Golden, property |
| A2 | Height field generation | Phase 3.2, I2 | O(M·N·steps) | float64; monotonic heights | Golden profiles |
| A3 | Trapezoid sidewall | Phase 3.2 | O(M·N) | tan(90°) guard | Analytic cross-section |
| A4 | Sidewall angle measure | Phase 3.4 | O(profile) | CD_bottom=CD_top guard | Golden trapezoid |
| A5 | Conformal deposition | Phase 3.2 | O(M·N) | Chebyshev chamfer | Wall thickness |
| A6 | CMP planarization | Phase 3.2 | O(M·N) | reflect padding; no growth | Planar top |
| A7 | LER generation | Phase 3.3 | O(L log L) | PSD normalization; zero mean | Stats 3σ, ξ, ρ; PSD fit |
| A8 | Overlay translation | Phase 3.3 | O(M·N) | order=1 spline; integer+frac split | Shift ±0.1 nm |
| A9 | Material encoding | Phase 1, 3.1 | O(edge band) | stack-order precedence | ID validity |
| A10 | Distance transform | Phase 4.4 | O(M·N) | exact EDT, float64 | Analytic distance |

---

## Sources

- Phase 3.1, 3.2, 3.3, 3.4 — Geometry Engine (all certified).
- Phase 4.2 — Interface contracts I1–I3.
- Phase 4.4 — Ground truth specification (signed-distance edge maps).
- [G2] Foley et al., *Computer Graphics: Principles and Practice*, 3rd ed., 1995 (rasterization).
- [G6] D. J. Higham, *An Introduction to Financial Option Valuation* (numerical care patterns), Cambridge, 2004.
- [G7] A. Papoulis, S. U. Pillai, *Probability, Random Variables, and Stochastic Processes*, 4th ed. McGraw-Hill, 2002 (exponential ACF / PSD pair).
