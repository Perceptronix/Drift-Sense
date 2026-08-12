# Open Questions (Phase 2.1)

**Research Phase:** 2.1
**Document:** 08_open_questions.md
**Date:** 2026-07-30

---

## Instructions

This document captures questions that arose during Phase 2.1 research that were outside the scope of this phase. They are categorized by:

- **Answered:** Questions resolved within this phase.
- **Deferred:** Questions that naturally lead into Phase 2.2.
- **Future:** Questions that are beyond Phase 2.2 but will become relevant in later phases.
- **Unresolved:** Questions where the literature is ambiguous or where credible numerical values could not be found.

---

## 1. Answered Within Phase 2.1

| Question | Answer | Document |
|---|---|---|
| Who invented the SEM? | Manfred von Ardenne (1937–1938), with critical advances by Oatley's Cambridge group | 02_sem_fundamentals.md |
| Why can't optical microscopes achieve sub-100 nm resolution? | Abbe diffraction limit (~λ/2 ≈ 200 nm for visible light) | 02_sem_fundamentals.md |
| What is the maximum resolution of a modern SEM? | <0.5 nm with aberration-corrected FEG-SEM | 02_sem_fundamentals.md |
| Which electron source is best for semiconductor metrology? | Schottky FEG | 04_electron_sources.md |
| Why is low voltage (<1 kV) preferred for semiconductor inspection? | Reduced beam damage, reduced charging, surface sensitivity | 07_semiconductor_inspection_configuration.md |
| How is magnification determined in an SEM? | By the scan area (not by lens zoom) | 05_beam_formation.md |
| What vacuum level is required for Schottky FEG operation? | 10⁻⁹ torr (gun chamber) | 04_electron_sources.md |
| What is the typical probe diameter in a CD-SEM? | 0.5–2 nm | 05_beam_formation.md |

---

## 2. Questions Deferred to Phase 2.2

These questions are the **essential knowledge gap** between understanding the SEM instrument and understanding how it produces images of semiconductor structures.

### 2.1 Electron-Sample Interaction

| # | Question |
|---|---|
| Q1 | What is the full range of signals generated when a primary electron beam strikes a solid sample? |
| Q2 | How is the interaction volume defined and how does its size depend on beam energy and sample composition? |
| Q3 | What are the generation mechanisms and energy distributions of secondary electrons (SE) and backscattered electrons (BSE)? |
| Q4 | What are the characteristic escape depths for SE and BSE from typical semiconductor materials? |
| Q5 | How does the Bethe energy loss model describe electron slowing in solids? |

### 2.2 Contrast Formation

| # | Question |
|---|---|
| Q6 | How does surface topography modulate SE and BSE emission to create image contrast? |
| Q7 | What is the physical origin of edge brightening (SE signal enhancement at pattern edges)? |
| Q8 | How does material composition (atomic number Z) create contrast in BSE images? |
| Q9 | What is voltage contrast and how does it enable electrical defect detection? |
| Q10 | How do the SE and BSE signals differ in their information content and spatial resolution? |

### 2.3 Image Pixel Formation

| # | Question |
|---|---|
| Q11 | How is pixel intensity determined from the detected electron flux at each scan position? |
| Q12 | What is the relationship between the number of detected electrons and the pixel grayscale value? |
| Q13 | How does the detector transfer function affect the mapping from electron count to pixel intensity? |

### 2.4 Noise

| # | Question |
|---|---|
| Q14 | What are the fundamental noise sources in SEM imaging? |
| Q15 | How does Poisson (shot) noise arise from the discrete nature of electron detection? |
| Q16 | How does detector noise (Johnson-Nyquist, PMT excess noise) contribute to total image noise? |
| Q17 | How does frame averaging reduce noise, and what are its limitations? |
| Q18 | What is the relationship between beam current, dwell time, and SNR? |

### 2.5 Blur and Resolution Degradation

| # | Question |
|---|---|
| Q19 | What mechanisms degrade spatial resolution beyond the probe diameter? |
| Q20 | How does electron diffusion within the sample contribute to signal delocalization (SE and BSE blur)? |
| Q21 | How do mechanical vibrations, magnetic interference, and thermal drift contribute to image blur? |
| Q22 | How is the effective resolution in an SEM image determined from the signal profile? |

### 2.6 Summary of Phase 2.2 Requirements

The following topics must be addressed to connect the instrument understanding from Phase 2.1 to the contrast formation and image quality modeling needed for later phases:

- **Electron-solid interactions:** Bethe stopping power, interaction volume, SE/BSE generation, escape depth.
- **Contrast mechanisms:** Topographic (SE), compositional (BSE), voltage contrast.
- **Signal formation:** Detector response model, pixel intensity model.
- **Noise sources:** Shot noise, detector noise, SNR scaling.
- **Resolution and blur:** Signal delocalization, instrumental blur sources, effective resolution.

---

## 3. Questions for Later Phases (Beyond Phase 2.2)

| # | Question | Likely Phase |
|---|---|---|
| Q23 | How is the SEM signal profile at a pattern edge related to the true edge position? | Phase 3 (CD Metrology) |
| Q24 | What is the line profile model used for CD extraction? | Phase 3 |
| Q25 | How does the instrument transfer function affect CD measurement accuracy? | Phase 3 |
| Q26 | How should the SEM image formation process be modeled for simulation? | Phase 3 or Phase 4 |
| Q27 | What parameters should a physics-based SEM renderer accept and output? | Phase 4 (Renderer) |
| Q28 | How do SEM operating conditions affect measurement uncertainty? | Phase 3 |

---

## 4. Unresolved Questions

The following questions could not be fully answered with the literature available during Phase 2.1:

| # | Question | Nature of Uncertainty |
|---|---|---|
| U1 | What is the exact numerical brightness of the ZrO/W Schottky emitter in A/cm²·sr for a specific CD-SEM product? | Proprietary — manufacturers (Applied Materials, Hitachi) do not publish exact brightness figures for their tools. Published values (10⁷–10⁸ A/cm²·sr) are inferred from academic literature and general Schottky emitter data. |
| U2 | What is the exact probe diameter for a given CD-SEM operating at a specific current and voltage? | Probe diameter depends on the specific lens design, aberration correction, and alignment state — all tool-specific. Estimates of 0.5–2 nm are engineering best-practice values. |
| U3 | What are the exact multi-frame averaging limits for CD-SEM in high-volume manufacturing? | The trade-off between frame averaging and throughput is specific to each tool and recipe. General principle (SNR ∝ √N) is well understood. |
| U4 | What is the precise energy-dependent charging behavior for each semiconductor material stack? | Charging depends on the exact film stack, surface condition, and accumulated dose. Material-specific yield curves are available in the literature but exact in-situ behavior is sample-dependent. |

**Recommendation:** Where exact numerical values are needed for modeling or simulation, use the representative values provided in this phase's documents as default parameters, with the understanding that they may need to be tuned to match a specific tool configuration.

---

## 5. Process for Resolving Open Questions

1. **Phase 2.2** will answer Q1–Q22 (electron interactions, contrast, noise, blur).
2. **Phase 3+** will address the modeling and rendering questions (Q23–Q28).
3. **Unresolved questions (U1–U4)** should be addressed through:
   - Collaboration with tool manufacturers (Applied Materials, Hitachi, JEOL).
   - Literature review of published tool characterization papers.
   - Direct measurement or characterization of specific tools if available.
   - Where exact values are not available, sensitivity analysis should be used to determine whether the uncertainty affects the conclusions of later phases.
