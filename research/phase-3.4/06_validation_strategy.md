# Geometry Validation Strategy

**Research Phase:** 3.4
**Document:** 06_validation_strategy.md
**Date:** 2026-07-30

---

## 1. Validation Domains

Geometry validation is organized into 5 domains:

| Domain | What We Validate | How |
|---|---|---|
| **Geometric correctness** | Does the geometry match the specified parameters? | Automated measurements |
| **Manufacturing realism** | Does the geometry look like a real fabricated structure? | Cross-section comparison |
| **Physical consistency** | Are heights, materials, and profiles physically possible? | Constraint checks |
| **Statistical validity** | Do the variability distributions match specification? | Statistical tests |
| **Interface compliance** | Does the output match the Phase 2.6 geometry interface? | Schema validation |

---

## 2. Unit Tests

### 2.1 Geometric Correctness Tests

| # | Test | Structure | Input | Expected Output | Tolerance |
|---|---|---|---|---|---|
| GT1 | Flat surface | Si substrate | h = 0, m = 1 | Height map = 0 everywhere | ±0.1 nm |
| GT2 | Straight line | Isolated line CD=50, H=100, θ=90° | Parameters | CD = 50 ± 0.5 nm | ±0.5 nm |
| GT3 | Tapered line | Isolated line θ=87°, H=100, CD_top=20 | Parameters | CD_bot = CD_top + 2H/tan(3°) ≈ 22.9 nm | ±0.5 nm |
| GT4 | Corner rounding | Line with R=5 nm | Parameters | Corner radius = 5 ± 1 nm | ±1 nm |
| GT5 | CMP clipping | Topography > H_CMP | Post-CMP | All heights ≤ H_CMP | ±0.1 nm |
| GT6 | Material assignment | Line (resist m=6) on Si (m=1) | Layer stack | Line pixels = 6, substrate = 1 | Exact |
| GT7 | Multiple layers | Gate over fin | Layer stack | Correct materials at each height | Exact |

### 2.2 Interface Compliance Tests

| # | Test | Check | Tolerance |
|---|---|---|---|
| IT1 | Height map format | 16-bit PNG, not palette-based | Must pass |
| IT2 | Material map format | 16-bit PNG, grayscale | Must pass |
| IT3 | Dimension match | M, N identical for both maps | Must match |
| IT4 | Material ID range | All values ≤ 6 | Must pass |
| IT5 | Height range | All height_DN ≤ 65535 | Must pass |
| IT6 | Metadata present | pixel_size_nm, pixel_to_nm_scale, structure_name | Must exist |

---

## 3. Manufacturing Realism Tests

### 3.1 Cross-Section Verification

| # | Structure | Characteristic | Acceptable Range | Method |
|---|---|---|---|---|
| MR1 | Isolated line | Trapezoidal profile | Top CD < Bottom CD | Cross-section |
| MR2 | Isolated line | Corner rounding | R = 2–20 nm | Corner measurement |
| MR3 | Contact hole | Tapered profile | Top > Bottom | Cross-section |
| MR4 | Fin | Rounded top | R = 1–5 nm | Top profile |
| MR5 | Gate stack | Sidewall spacer | Width = 5–10 nm | Material map |
| MR6 | CMP surface | Planarized | Height variation < 1 nm | Height flatness |

### 3.2 Visual Verification

| # | Check | Method | Pass Condition |
|---|---|---|---|
| VV1 | Lines look like real semiconductor lines | Expert review | "Convincing" |
| VV2 | Edges have roughness (LER) | Visual inspection | Edges are not perfectly straight |
| VV3 | Sidewalls are tapered (not perfectly vertical) | Cross-section | Visible 85–89° angle |

---

## 4. Statistical Validation Tests

| # | Test | Parameter | Method | Acceptance |
|---|---|---|---|---|
| SV1 | LER amplitude | σ_LER | Measure edge position std. dev. over 10 μm line | σ_measured = σ_specified ± 10% |
| SV2 | LER correlation | ξ | Fit ACF of edge positions to exponential | ξ_fit = ξ_specified ± 20% |
| SV3 | LWR amplitude | σ_LWR | Measure CD std. dev. along line | σ_LWR = √(2(1-ρ)) × LER ± 10% |
| SV4 | CDU | σ_CDU | Measure CD across 9 fields | σ_CD = σ_CDU_specified ± 15% |
| SV5 | Overlay | σ_ovl | Measure layer shift | σ_ovl × 2 = ± 20% |
| SV6 | Sidewall angle distribution | σ_θ | Measure angle on 100 features | σ_θ = specified ± 0.2° |
| SV7 | Normality test | CDU, overlay | Shapiro-Wilk on 1000 samples | p > 0.05 |

---

## 5. Acceptance Thresholds

| Phase | Minimum | Target | Excellent |
|---|---|---|---|
| **Phase A (deterministic)** | All GT tests pass. Interface compliance. | GT + MR1–4 pass | All unit tests + expert review |
| **Phase B (with LER/LWR)** | All GT + SV1–3 pass. LER visible. | LER amplitude within 10% of spec. | LER ACF matches spec within 20% |
| **Phase C (+process variation)** | All SV tests pass. Overlay visible. | All statistical tests pass. | Expert review: "convincing" |
| **Phase D (+CMP variation)** | All MR tests pass. | All tests pass. | Complete validation report. |

---

## 6. Validation Tools

| Tool | Used For | Reference |
|---|---|---|
| Cross-section viewer | Geometry inspection | Custom |
| CD measurement tool | Automated CD extraction | Custom |
| LER analysis tool | LER PSD and ACF computation | Custom |
| Material map checker | Material ID validation | Custom |
| Normality test suite | Statistical distribution checks | SciPy or equivalent |

---

## 7. Test Data Generation

| Test Data Set | Size | Contents | Used For |
|---|---|---|---|
| Minimal test set | 10 structures | Flat surface, 1 line, 1 trench, 1 contact, 1 fin, 1 gate, bi-materials | Phase A validation |
| Full test set | 50 structures | All 10 library types × 5 parameter variations each | Phase B+ validation |
| Statistical test set | 1000 structures | Same structure × 1000 random seeds | Statistical validation |
| Edge case set | 10 structures | Extreme parameters (min CD, max aspect ratio) | Robustness testing |

---

## Sources

- [M1] Habermas et al., "LER and LWR metrology," *Proc. SPIE*, vol. 10583, 2018.
- [M4] B. D. Bunday et al., "CD-SEM metrology," *Proc. SPIE*, vol. 5038, 2003.
- Phase 2.6, Document 05 — Validation strategy.
- Phase 2.6, Document 06 — Geometry interface.
