# Complete Reference List — Phase 5.2

**Research Phase:** 5.2
**Document:** 09_complete_reference_list.md
**Date:** 2026-07-30

---

## A. GDSII and Layout

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [G1] | H. Koppelaar | *gdspy: A Python Library for GDSII Layout* | gdspy.readthedocs.io | 2015 | 01, 03 |
| [G2] | J. D. Foley, A. van Dam, S. K. Feiner, J. F. Hughes | *Computer Graphics: Principles and Practice*, 3rd ed. | Addison-Wesley | 1995 | 01, 03, 04 |

---

## B. Numerical and Image Computing

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [G3] | S. van der Walt, J. L. Schönberger, J. Nunez-Iglesias et al. | "scikit-image: image processing in Python" | *PeerJ*, vol. 2 | 2014 | 03 |
| [G4] | C. R. Harris, K. J. Millman, S. J. van der Walt et al. | "Array programming with NumPy" | *Nature*, vol. 585 | 2020 | 03 |
| [G5] | P. Virtanen, R. Gommers, T. E. Oliphant et al. | "SciPy 1.0: fundamental algorithms for scientific computing in Python" | *Nature Methods*, vol. 17 | 2020 | 03 |

---

## C. Stochastic Processes

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [G6] | A. Papoulis, S. U. Pillai | *Probability, Random Variables, and Stochastic Processes*, 4th ed. | McGraw-Hill | 2002 | 04 |
| [G7] | D. J. Higham | *An Introduction to Financial Option Valuation* (numerical methods) | Cambridge Univ. Press | 2004 | 04 |

---

## D. Software Engineering

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [G8] | S. McConnell | *Code Complete*, 2nd ed. | Microsoft Press | 2004 | 05, 06 |
| [G9] | J. B. Rainsberger | *JUnit Recipes: Practical Methods for Programmer Testing* | Manning | 2004 | 07 |
| [G10] | D. MacIver | *Property-Based Testing with PropEr, Erlang, and Hypothesis* | leanpub | 2019 | 07 |
| [G11] | B. Boehm | "A Spiral Model of Software Development and Enhancement" | *IEEE Computer*, vol. 21 | 1988 | 06 |

---

## E. Cross-Phase References

| Ref | Phase | Documents | Title | Cited In |
|---|---|---|---|---|
| [P3.1] | 3.1 | All | Geometry Representation | 01, 02, 04 |
| [P3.2] | 3.2 | All | Process Model | 01, 02, 04 |
| [P3.3] | 3.3 | All | Manufacturing Variability | 01, 02, 04 |
| [P3.4] | 3.4 | All | Geometry Engine Certification | 01, 02, 04, 07 |
| [P4.2] | 4.2 | 03, 04 | Canonical Data Objects, API Contracts | 01, 02, 04, 05 |
| [P5.1] | 5.1 | 02, 05, 06 | WBS, Validation Gates, Environment | 01, 03, 05, 06, 07 |

---

## F. Key Reference Summary

### Geometry Engine
- [G1] gdspy (2015) — GDSII parsing library. Primary selection for geo_raster.
- [G2] Foley et al. (1995) — Computer graphics rasterization. Basis for edge-function supersampling.

### Numerical Core
- [G4] Harris et al. (2020) — NumPy. Foundation for all array operations.
- [G5] Virtanen et al. (2020) — SciPy 1.0. ndimage/fft for process and variability algorithms.
- [G3] van der Walt et al. (2014) — scikit-image. Distance transforms, contours.

### Stochastic Processes
- [G6] Papoulis & Pillai (2002) — Exponential ACF / PSD. Basis for LER spectral synthesis (A7).

### Software Engineering
- [G8] McConnell (2004) — Code Complete. File organization, public/private discipline.
- [G10] MacIver (2019) — Hypothesis. Property-based testing framework.

---

*End of Reference List — Phase 5.2*
