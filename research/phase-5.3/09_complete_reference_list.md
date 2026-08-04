# Complete Reference List — Phase 5.3

**Research Phase:** 5.3
**Document:** 09_complete_reference_list.md
**Date:** 2026-07-30

---

## A. Electron Microscopy Physics

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [P1] | H. Seiler | "Secondary electron emission in the scanning electron microscope" | *J. Appl. Phys.*, vol. 54, R1–R18 | 1983 | 01, 04, 05, 07 |
| [P2] | T. E. Everhart, R. F. M. Thornley | "Wide-band detector for micro-microampere low-energy electron currents" | *J. Sci. Instrum.*, vol. 37, 246–248 | 1960 | 01, 04 |
| [P8] | L. Reimer | *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. | Springer | 1998 | 05, 07 |

---

## B. Numerical Computing

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [P3] | C. R. Harris, K. J. Millman, S. J. van der Walt et al. | "Array programming with NumPy" | *Nature*, vol. 585, 357–362 | 2020 | 03 |
| [P4] | P. Virtanen, R. Gommers, T. E. Oliphant et al. | "SciPy 1.0: fundamental algorithms for scientific computing in Python" | *Nature Methods*, vol. 17, 261–272 | 2020 | 03 |

---

## C. Random Number Generation

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [P5] | M. Matsumoto, T. Nishimura | "Mersenne Twister: A 623-dimensionally equidistributed uniform pseudo-random number generator" | *ACM Trans. Model. Comput. Simul.*, vol. 8 | 1998 | 03 |
| [P6] | M. E. O'Neill | "PCG: A Family of Simple Fast Space-Efficient Statistically Good Algorithms for Random Number Generation" | HMC-CS-2014-0905 | 2014 | 03 |

---

## D. Stochastic Processes

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [P7] | A. Papoulis, S. U. Pillai | *Probability, Random Variables, and Stochastic Processes*, 4th ed. | McGraw-Hill | 2002 | 04 |

---

## E. Software Engineering (reused conventions)

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [G8] | S. McConnell | *Code Complete*, 2nd ed. | Microsoft Press | 2004 | 06 |
| [G9] | J. B. Rainsberger | *JUnit Recipes* | Manning | 2004 | 07 |
| [G10] | D. MacIver | *Property-Based Testing with PropEr, Erlang, and Hypothesis* | leanpub | 2019 | 07 |
| [G11] | B. Boehm | "A Spiral Model of Software Development and Enhancement" | *IEEE Computer*, vol. 21 | 1988 | 07 |

---

## F. Cross-Phase References

| Ref | Phase | Documents | Title | Cited In |
|---|---|---|---|---|
| [P2.1] | 2.1 | All | SEM Fundamentals | 05 |
| [P2.2] | 2.2 | All | Electron–Sample Interaction | 01, 04, 05 |
| [P2.3] | 2.3 | All | Contrast Formation | 01, 02, 04 |
| [P2.4] | 2.4 | All | Degradation Physics | 01, 02, 04 |
| [P2.5] | 2.5 | All | Canonical SEM Specification | 01, 02, 04 |
| [P2.6] | 2.6 | All | SEM Physics Engine Certification | 01, 03, 05 |
| [P4.2] | 4.2 | 03, 04 | Canonical Data Objects, API Contracts | 01, 02, 04, 06 |
| [P4.3] | 4.3 | 05 | Reproducibility (seed chain) | 03 |
| [P5.1] | 5.1 | 05, 06 | Validation Gates, Environment | 03, 06, 07 |
| [P5.2] | 5.2 | All | Geometry Engine Blueprint | 01, 02, 06 |

---

## G. Key Reference Summary

### Physics Models
- [P1] Seiler (1983) — SE yield universal model. Basis for Algorithm P2.
- [P2] Everhart & Thornley (1960) — BSE yield / detector. Basis for Algorithm P3.
- [P8] Reimer (1998) — SEM image formation. Reference values for material properties.

### Numerical
- [P3] Harris et al. (2020) — NumPy. Array core + PCG64 RNG.
- [P4] Virtanen et al. (2020) — SciPy. fftconvolve, ndimage.
- [P6] O'Neill (2014) — PCG. Generator choice justification.

---

*End of Reference List — Phase 5.3*
