# Complete Reference List — Phase 4.3

**Research Phase:** 4.3
**Document:** 09_complete_reference_list.md
**Date:** 2026-07-30

---

## A. Parallel and Distributed Computing

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [R1] | I. Foster | *Designing and Building Parallel Programs: Concepts and Tools for Parallel Software Engineering* | Addison-Wesley | 1995 | 01, 02, 03, 04, 06, 08 |
| [R2] | M. Snir, S. Otto, S. Huss-Lederman, D. Walker, J. Dongarra | *MPI: The Complete Reference* | MIT Press | 1998 | 01 |
| [R3] | B. Wilkinson, M. Allen | *Parallel Programming: Techniques and Applications Using Networked Workstations and Parallel Computers*, 2nd ed. | Prentice Hall | 2005 | 01, 03, 04 |
| [R4] | M. J. Quinn | *Parallel Programming in C with MPI and OpenMP* | McGraw-Hill | 2003 | 03, 04 |

---

## B. Software Design and Reproducibility

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [R5] | J. K. Ousterhout | *A Philosophy of Software Design* | Yaknyam Press | 2018 | 01, 02, 05, 07, 08 |
| [R6] | J. L. Hennessy, D. A. Patterson | *Computer Architecture: A Quantitative Approach*, 6th ed. | Morgan Kaufmann | 2017 | 04 |
| [R7] | D. E. Knuth | *The Art of Computer Programming, Vol. 2: Seminumerical Algorithms*, 3rd ed. | Addison-Wesley | 1997 | 05 |
| [R8] | G. Marsaglia | "Xorshift RNGs" | *J. Stat. Softw.*, vol. 8 | 2003 | 05 |
| [R9] | D. Lemire | "Fast Random Integer Generation" | *Software: Practice and Experience*, vol. 49 | 2019 | 05 |

---

## C. Systems Programming and Reliability

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [R10] | W. Gropp, E. Lusk, A. Skjellum | *Using MPI: Portable Parallel Programming with the Message-Passing Interface*, 3rd ed. | MIT Press | 2014 | 06 |
| [R11] | P. Brinch Hansen | "Distributed Processes: A Concurrent Programming Concept" | *CACM*, vol. 21 | 1978 | 06 |
| [R12] | P. J. Plauger | *The Standard C Library* | Prentice Hall | 1992 | 07 |
| [R13] | C. Evans | *Software Engineering for Science* | CRC Press | 2017 | 07 |
| [R14] | A. S. Tanenbaum, H. Bos | *Modern Operating Systems*, 4th ed. | Pearson | 2015 | — |

---

## D. Cross-Phase References

| Ref | Phase | Document(s) | Title | Cited In |
|---|---|---|---|---|
| [P4.1] | 4.1 | 03, 05 | Module decomposition, Layered architecture | 02, 04, 07 |
| [P4.2] | 4.2 | 03, 05, 10 | Canonical data objects, Config model, Final report | 01, 03, 05, 06, 08 |

---

## E. Key Reference Summary

### Parallel Computing (Primary)
- [R1] Foster (1995) — Design of parallel programs. Embarrassingly parallel patterns, worker pools, scalability analysis.
- [R3] Wilkinson, Allen (2005) — Practical parallel programming. Process pools, shared vs. distributed memory, performance modeling.

### Reproducibility
- [R7] Knuth (1997) — Random number generation, the foundational reference. The basis for the hierarchical seed manager.
- [R8] Marsaglia (2003) — Xorshift RNG. Fast, deterministic, reliable.

### Software Design
- [R5] Ousterhout (2018) — Module decomposition, complexity reduction, design philosophy.

---

*End of Reference List — Phase 4.3*
