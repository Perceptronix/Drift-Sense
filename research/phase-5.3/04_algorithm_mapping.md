# Algorithm Mapping

**Research Phase:** 5.3
**Document:** 04_algorithm_mapping.md
**Date:** 2026-07-30

---

## 1. Mapping Convention

Every implementation algorithm maps directly to a **Frozen Specification** (Phases 2.1–2.5, 4.2). Markers:

- **Frozen Specification** — certified requirement (cannot change).
- **Implementation Decision** — the algorithm chosen here (frozen for this phase).
- **Future Optimization** — faster variant, deferred.

---

## 2. Algorithm P1: Surface Normal & Incidence Angle

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 2.3: topographic contrast uses local incidence angle θ vs beam axis |
| **Inputs** | HeightField (float64 nm), pixel_size_nm |
| **Outputs** | cosθ map (float64 ∈ (0,1]), surface normal (nx, ny, nz) |
| **Algorithm** | Central differences: gx = (H[i,j+1] − H[i,j−1])/(2·pixel); gy likewise. Normal n = (−gx, −gy, 1)/‖·‖. cosθ = nz = 1/√(1 + gx² + gy²) |
| **Complexity** | O(M×N), 4 array ops |
| **Stability** | Clamp cosθ to [1e-6, 1] to avoid div-by-zero; reflect padding at borders |
| **Validation** | Flat → cosθ = 1.0 ± 1e-9; slope at 45° → cosθ = 0.7071 ± 0.5%; vertical wall → cosθ → 1e-6 clamp |

---

## 3. Algorithm P2: Universal SE Yield

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 2.2/2.3: universal SE yield curve — δ(θ) = δ₀·(cosθ)^(−f)·exp(Λ·(1−cosθ)) with material params δ₀, Λ, tilt exponent f (default 1.0) |
| **Inputs** | δ₀ (material), Λ (nm), f, cosθ map |
| **Outputs** | SE1 yield map |
| **Algorithm** | δ = δ₀ · (cosθ)**(−f) · exp(Λ·(1 − cosθ)), vectorized |
| **Complexity** | O(M×N) |
| **Stability** | cosθ clamped ≥ 1e-6; Λ·(1−cosθ) ≤ ~Λ bounded → no overflow |
| **Validation** | Flat Si (δ₀=0.15, Λ=2.5): δ = 0.15 exactly. 45° slope: δ = 0.15·(0.7071)^(−1)·exp(2.5·0.2929) ≈ 0.15·1.414·2.08 ≈ 0.44. Match within 1e-9 analytic |

---

## 4. Algorithm P3: BSE Yield (Everhart)

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 2.2: Everhart model η(Z) = 0.0254 + 0.016·Z − 1.86e−4·Z² + 8.3e−7·Z³ |
| **Inputs** | Material Z (atomic number) |
| **Outputs** | η (BSE yield) |
| **Algorithm** | Polynomial evaluation per material ID (precomputed at material load; no per-pixel cost) |
| **Complexity** | O(1) per material (precomputed) |
| **Stability** | Z ≤ 92; polynomial monotonic for Z ∈ [1, 79]; guard negative → clamp 0 |
| **Validation** | Si (Z=14): η = 0.0254 + 0.224 − 0.0365 + 0.0023 ≈ 0.215. Published Si η(1 keV) ≈ 0.19–0.22 ✅ |

---

## 5. Algorithm P4: SE2 Contribution (BSE-Induced SE)

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 2.3: total SE = SE1 + SE2 where SE2 = BSEs re-entering the bulk generate additional SEs |
| **Inputs** | η_map, SE-bulk efficiency g_bulk (configurable, default 0.5), SE1 map |
| **Outputs** | SE_total = SE1 + η·g_bulk·SE1_scale |
| **Algorithm** | SE2 = η_map · g_bulk · SE1; SE_total = SE1 + SE2 |
| **Complexity** | O(M×N) |
| **Stability** | Non-negative by construction |
| **Validation** | Flat Cu (η=0.31, g_bulk=0.5): SE2 = 0.155·SE1; ratio SE2/SE1 = 0.155 ± 1e-9 |

---

## 6. Algorithm P5: Edge Brightening

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 2.3: enhanced SE emission at steep edges (factor 1.5–3.0 vs flat) |
| **Inputs** | SE1 map, cosθ map, edge_mask (cosθ < cos_threshold, e.g. 0.7), factor ∈ [1.5, 3.0] |
| **Outputs** | Enhanced SE map |
| **Algorithm** | SE_enh = SE · (1 + (factor−1)·edge_weight), where edge_weight = smooth ramp of (1−cosθ) in the edge band |
| **Complexity** | O(M×N) |
| **Stability** | Smooth ramp (no discontinuity); factor = 1.0 → identity |
| **Validation** | Edge pixel: ratio to flat = factor ± 0.5%; flat: ratio = 1.0; factor 1.0 → bitwise identity |

---

## 7. Algorithm P6: Charging Modulation

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 2.4: surface-charging potential modulates yield; **valid for isolated structures only** (certified caveat) |
| **Inputs** | Yield map, charging_config (enabled, potential_model, isolated_mask), material |
| **Outputs** | Modulated yield |
| **Algorithm** | Compute charging potential V_surf from accumulated charge (simplified: V_surf = α·(signal − bleed)), modulated yield = yield·(1 + β·V_surf/E_b); apply only inside isolated_mask; if charging enabled on non-isolated geometry → emit warning + skip |
| **Complexity** | O(M×N) |
| **Stability** | Modulation bounded to ±50%; isolated-only guard documented |
| **Validation** | Disabled → identity; isolated structure → bounded modulation; dense → warning + identity (documented limitation) |

---

## 8. Algorithm P7: PSF Generation & Convolution

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 2.4: Gaussian beam profile; probe_diameter_nm = FWHM; **normalization sum = 1** (Phase 4.5 verification decision) |
| **Inputs** | probe_diameter_nm, pixel_size_nm, kernel_radius_multiplier (default 4σ) |
| **Outputs** | PSF kernel (K×K float64, sum = 1) |
| **Algorithm** | σ = FWHM/2.3548; grid over ±radius_mult·σ; G = exp(−(x²+y²)/(2σ²)); G /= ΣG |
| **Convolution** | `scipy.signal.fftconvolve(map, kernel, mode='same')`; if K < 15 use `scipy.ndimage.convolve` (spatial cross-over, implementation decision) |
| **Complexity** | O(M·N·log(M·N)) FFT; O(M·N·K²) spatial |
| **Stability** | Sum-1 exact (1e-12); FFT boundary wrap avoided by zero-padding to next FFT-friendly size |
| **Validation** | Sum = 1 ± 1e-12; FWHM of kernel = probe_diameter ± 1%; delta input (probe = 0.5 px) → identity; conserved mean ± 1e-9 |

**Future Optimization:** Separable Gaussian (2×1D passes) — deferred; 2D FFT adequate.

---

## 9. Algorithm P8: Shot Noise (Poisson)

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 2.4: shot noise = Poisson counting statistics |
| **Inputs** | Yield map, counts_per_electron (electrons per yield unit), seed |
| **Outputs** | Noisy yield map |
| **Algorithm** | n = round(Y·cpe); n' ~ Poisson(n) via `Generator.poisson(n)`; Y' = n'/cpe |
| **Complexity** | O(M×N), vectorized |
| **Stability** | Poisson requires n ≥ 0; cpe > 0; deterministic given seed |
| **Validation** | mean(Y') = mean(Y) ± 1%; var(Y'·cpe) ≈ mean(Y·cpe) ± 5% (Poisson); same seed → identical; different seed → different |

**Implementation decision:** Apply on the SE map primarily (BSE typically lower-noise detection channel); both configurable.

---

## 10. Algorithm P9: Detector Read Noise (Gaussian)

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 2.4: additive Gaussian detector noise |
| **Inputs** | Yield map, σ_read (yield units), seed |
| **Outputs** | Noisy yield map |
| **Algorithm** | Y' = Y + N(0, σ_read²) via `Generator.normal(0, σ_read, size)` |
| **Complexity** | O(M×N) |
| **Stability** | σ_read ≥ 0; σ_read = 0 → identity (skip call) |
| **Validation** | mean shift ≈ 0 ± 1e-3; measured σ = σ_read ± 2%; seeded reproducibility |

---

## 11. Algorithm P10: Digitization

| Aspect | Specification |
|---|---|
| **Frozen Spec** | Phase 2.5: I = clip(gain·Y + offset, 0, 2^bits − 1); bit_depth ∈ {8, 16} |
| **Inputs** | Yield map, gain, offset, bit_depth, saturate_enabled |
| **Outputs** | SEMImage (uint8/uint16), FormationRecord (saturation fraction) |
| **Algorithm** | V = np.round(gain·Y + offset) (round-half-even, deterministic); np.clip(V, 0, max); astype(uint) |
| **Complexity** | O(M×N) |
| **Stability** | gain > 0; overflow guarded by clip; round-half-even documented |
| **Validation** | Known Y → known DN; clip bounds; saturation fraction = count(V == max)/N · 100%; uint dtype correct |

---

## 12. Algorithm Summary Table

| # | Algorithm | Frozen Spec | Complexity | Key Numerical Care | Validation |
|---|---|---|---|---|---|
| P1 | Surface normals | Phase 2.3 | O(M·N) | cosθ clamp ≥ 1e-6 | Flat/45° analytic |
| P2 | Universal SE yield | Phase 2.2 | O(M·N) | exponent bounds | δ₀ flat exact; 45° analytic |
| P3 | BSE yield (Everhart) | Phase 2.2 | O(1) precomp | Z guard, clamp | Si η ≈ 0.19–0.22 |
| P4 | SE2 contribution | Phase 2.3 | O(M·N) | non-negative | Ratio check |
| P5 | Edge brightening | Phase 2.3 | O(M·N) | smooth ramp | factor 1.5–3.0 |
| P6 | Charging modulation | Phase 2.4 | O(M·N) | isolated-only guard | disabled → identity |
| P7 | PSF gen + convolution | Phase 2.4 | O(MN log MN) | sum-1; FFT padding | FWHM ± 1%; mean conserved |
| P8 | Shot noise | Phase 2.4 | O(M·N) | Poisson n ≥ 0 | mean ± 1%; var ≈ mean |
| P9 | Detector noise | Phase 2.4 | O(M·N) | σ ≥ 0; zero → skip | measured σ ± 2% |
| P10 | Digitization | Phase 2.5 | O(M·N) | round-half-even; clip | DN bounds; saturation |

---

## Sources

- Phase 2.2 — Electron–sample interaction (SE/BSE yield models).
- Phase 2.3 — Contrast formation (topographic, material, edge brightening).
- Phase 2.4 — Degradation physics (PSF, shot noise, detector noise, charging).
- Phase 2.5 — Canonical SEM specification (digitization).
- Phase 4.2 — Interfaces I4, I5, I6.
- [P1] H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- [P2] T. E. Everhart, R. F. M. Thornley, "Wide-band detector...," *J. Sci. Instrum.*, vol. 37, 1960.
- [P7] A. Papoulis, S. U. Pillai, *Probability, Random Variables, and Stochastic Processes*, 4th ed. McGraw-Hill, 2002.
