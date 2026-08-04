# Phase 2.1 Final Report: How a Scanning Electron Microscope Works

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 2.1)

---

## Executive Summary

This phase has established a comprehensive understanding of how a Scanning Electron Microscope (SEM) is built and operated, specifically in the context of semiconductor wafer inspection and critical dimension (CD) metrology.

The SEM is an instrument that generates a focused beam of electrons, scans it across a sample surface in a raster pattern, and collects emitted signals to form an image. Its dominance in semiconductor inspection is explained by three fundamental advantages: sub-nanometer resolution (exceeding the Abbe diffraction limit of optical microscopy by ~200×), orders-of-magnitude greater depth of field, and multiple simultaneous signal channels providing topographic, compositional, and electrical information.

---

## 1. Key Findings by Document

### 1.1 SEM Fundamentals (Document 02)

**History:**
- Manfred von Ardenne invented the SEM in 1937–1938.
- Charles Oatley's Cambridge group advanced the design in the 1950s.
- Cambridge Scientific Instruments delivered the first commercial SEM (Stereoscan) in 1965.
- Field emission guns became commercially viable in the 1980s–1990s.
- Modern aberration-corrected SEMs achieve <0.5 nm resolution.

**Why SEM dominates semiconductor inspection:**
- Resolution below the Abbe diffraction limit (~200 nm for optical).
- Depth of field ~1,000× greater than optical at equivalent magnification.
- Multiple imaging modes: SE (topography), BSE (composition), EDS (elemental).
- Quantitative metrology with sub-0.2 nm (3σ) precision in CD-SEMs.

### 1.2 SEM System Architecture (Document 03)

The SEM is a vertical instrument composed of eight major subsystems:

| Subsystem | Core Function | Critical Parameter |
|---|---|---|
| **Electron source** | Generate free electrons | Brightness, stability |
| **Electron column** | Guide beam under vacuum | Vacuum integrity (10⁻⁷–10⁻¹⁰ torr) |
| **Condenser lenses** | Demagnify beam to fine probe | Demagnification factor (50–2,000×) |
| **Objective lens** | Final focus onto sample | Aberration coefficients (Cs, Cc) |
| **Apertures** | Control convergence angle and current | Diameter (10–200 μm) |
| **Scan coils** | Raster beam in X/Y | Double-deflection for on-axis entry |
| **Specimen stage** | Position sample precisely | 5-axis, laser-interferometric feedback |
| **Vacuum chamber** | Enable electron travel | Multi-stage differential pumping |
| **Electron detectors** | Convert emitted e⁻ to electrical signal | TTL SE, E-T, solid-state BSE |
| **Control electronics** | Synchronize all subsystems | Scan gen, ADC, HV stability |

**Architecture recommendation:** A Schottky FEG source with two-stage condenser lenses, semi-in-lens objective, beam-defining aperture of 20–40 μm, double-deflection scanning, TTL SE detector, and laser-interferometric stage.

### 1.3 Electron Sources (Document 04)

Three electron source technologies were compared. The comprehensive comparison established:

| Parameter | Tungsten | LaB₆ | Schottky FEG | Cold FEG |
|---|---|---|---|---|
| Brightness (A/cm²·sr) | 10⁴–10⁵ | 10⁵–10⁶ | 10⁷–10⁸ | 10⁸–10⁹ |
| Source size (nm) | ~50,000 | ~10,000 | ~15–30 | ~3–5 |
| Energy spread (eV) | 2–3 | 1–2 | 0.3–1.0 | 0.2–0.5 |
| Vacuum (torr) | 10⁻⁵ | 10⁻⁷ | 10⁻⁹ | 10⁻¹⁰ |
| Lifetime (hours) | ~100 | ~500–1,000 | >10,000 | >10,000 |
| Current stability | Moderate | Good | Excellent | Fair |

**Recommendation:** The Schottky FEG is the preferred source for semiconductor metrology because it offers the best balance of high brightness (10⁷–10⁸ A/cm²·sr), excellent emission stability (<0.5%/hour drift), long lifetime (>10,000 hours), and moderate vacuum requirements (10⁻⁹ torr). Cold FEG offers marginally better resolution but its emission instability and periodic flashing requirement preclude its use in high-throughput, high-precision manufacturing metrology.

### 1.4 Beam Formation (Document 05)

The beam formation process transforms a raw electron emission into a focused probe through five sequential stages:

1. **Generation:** Electrons extracted from the Schottky tip by field-assisted thermionic emission.
2. **Acceleration:** Electrons accelerated to 0.3–30 kV; CD-SEM uses multi-stage acceleration with beam booster and retarding field.
3. **Demagnification:** C1 lens (10×–100×) and C2 lens (5×–20×) reduce the beam crossover.
4. **Aperture limitation:** Beam-defining aperture sets convergence angle (5–15 mrad) and probe current (10–50 pA for CD).
5. **Final focusing:** Objective lens focuses to probe of 0.5–2 nm at the sample.

The final probe diameter is given by:

$$d_p^2 = d_g^2 + \left(\frac{1}{2}C_s\alpha^3\right)^2 + \left(C_c\frac{\Delta E}{E}\alpha\right)^2 + (0.61\lambda/\alpha)^2$$

Probe current is fundamentally limited by source brightness:

$$I_p = \beta \cdot (\pi \alpha^2) \cdot \frac{\pi d_p^2}{4}$$

### 1.5 Image Acquisition Workflow (Document 06)

The complete acquisition pipeline is:

```
Electron Generation → Beam Acceleration → Beam Conditioning →
Beam Scanning → Sample Irradiation → Signal Collection → Image Formation
```

Key characteristics:
- Each pixel corresponds to one beam position with known dwell time.
- Magnification = Display size / Scan area (not optical zoom).
- ADC converts analog detector signal to digital grayscale values (8–16 bit).
- Synchronization between scan coils and pixel acquisition is critical.
- Frame averaging improves SNR as √N.

### 1.6 Semiconductor Inspection Configuration (Document 07)

The optimized CD-SEM configuration is:

| Parameter | Value | Rationale |
|---|---|---|
| **Landing energy** | 300–1,500 eV | Low damage, reduced charging, surface sensitivity |
| **Probe current** | 10–30 pA (CD), 50–200 pA (defect review) | Small probe for resolution vs. speed |
| **Working distance** | 4–6 mm (CD), 6–10 mm (defect review) | Resolution vs. depth of field |
| **Magnification** | 100,000×–300,000× (CD) | Adequate pixel sampling for sub-10 nm features |
| **Detector** | TTL SE (primary), BSE (secondary) | Highest resolution topographic signal |
| **Frame averaging** | 16–32 frames | Noise reduction for quantitative measurement |
| **Stage** | Laser-interferometric, 300 mm wafer | Sub-50 nm positioning precision |

---

## 2. Critical Unresolved Questions

The following questions could not be definitively answered from the available literature:

1. **Exact brightness of Schottky emitters in specific CD-SEM products:** Published values (10⁷–10⁸ A/cm²·sr) are from general Schottky emitter literature; exact values for specific tools are proprietary.

2. **Exact probe diameter for a specific tool at given operating conditions:** Probe size depends on the detailed lens design, aberration state, and alignment — all tool-specific. Estimates of 0.5–2 nm are based on general principles.

3. **Exact charging behavior for specific material stacks:** Charging depends on the film stack, surface condition, and accumulated dose. General principles are known; exact in-situ behavior is sample-dependent.

---

## 3. Knowledge Required for Phase 2.2

This phase has explained how the SEM instrument works. The natural next question — and the essential requirement for Phase 2.2 — is:

**How does the sample create the grayscale image?**

Phase 2.2 must answer every question in the list below. These questions are the complete handoff from Phase 2.1 to Phase 2.2.

### 3.1 Electron-Sample Interactions

1. What signals are generated when the primary electron beam strikes the sample? (SE, BSE, X-rays, Auger, CL)
2. How is the interaction volume defined and how does it depend on:
   - Beam energy (accelerating voltage)?
   - Sample composition (Z)?
   - Sample density?
3. What are the generation mechanisms and energy distributions of:
   - Secondary electrons (SE-I, SE-II, SE-III)?
   - Backscattered electrons (single-scattered, multiple-scattered)?
4. What are the characteristic escape depths of SE and BSE from:
   - Silicon?
   - Silicon dioxide?
   - Copper?
   - Photoresist?
5. How does the Bethe stopping power model describe electron energy loss in solids?
6. What is the Monte Carlo method for simulating electron trajectories in solids?

### 3.2 Contrast Formation

7. How does surface topography modulate SE emission? (the tilt and edge effects)
8. What is the physical origin of edge brightening in SE images?
9. How does atomic number Z create contrast in BSE images?
10. What is voltage contrast and how does it enable electrical defect detection without probe contact?
11. What is the information content difference between SE and BSE images?
12. What other contrast mechanisms are relevant for semiconductor structures? (shadowing, channeling, magnetic)

### 3.3 Pixel Intensity and Signal Model

13. How is pixel intensity determined from the detected electron flux?
14. What is the functional relationship between detected electron count and pixel grayscale value?
15. How does the detector transfer function affect the signal-to-pixel mapping?

### 3.4 Noise Sources

16. What is shot noise and how does Poisson statistics govern the detected signal?
17. What are the detector noise contributions? (Johnson-Nyquist, PMT excess noise, amplifier noise)
18. How does frame averaging (integration) reduce noise, and what are its limits?
19. What is the relationship between beam current, pixel dwell time, and signal-to-noise ratio?
20. What noise sources are dominant in low-voltage, low-current CD-SEM imaging?

### 3.5 Blur and Resolution

21. What is SE and BSE signal delocalization and how does it limit effective resolution beyond the probe diameter?
22. How do instrumental factors contribute to image blur? (vibration, magnetic interference, thermal drift, charging-induced beam deflection)
23. How is the effective resolution of an SEM image determined from the signal profile?
24. What is the modulation transfer function (MTF) for SEM imaging and how does it characterize resolution?

### 3.6 Scope of Phase 2.2

Phase 2.2 should produce a comprehensive understanding of:
- The physics of e-beam interaction with semiconductor materials
- How signals are generated, escape from the sample, and are detected
- How contrast arises in SE and BSE images
- Why noise and blur limit the precision and accuracy of SEM measurements
- **Everything between "the beam hits the sample" and "the pixel value appears"**

This knowledge completes the bridge between the instrument (Phase 2.1) and the methods for simulating and measuring semiconductor structures (subsequent phases).

---

## 4. Phase 2.1 Success Criteria Checklist

| Criterion | Status | Evidence |
|---|---|---|
| ✓ How an SEM is built | Achieved | Documents 03, 05 |
| ✓ How electrons are generated | Achieved | Document 04 |
| ✓ How the beam is formed | Achieved | Document 05 |
| ✓ How the microscope acquires an image | Achieved | Document 06 |
| ✓ Why SEM dominates semiconductor inspection | Achieved | Documents 02, 07 |
| ✓ Which source is best for semiconductor metrology | Achieved | Document 04 |
| ✓ Typical operating conditions for CD-SEM | Achieved | Document 07 |
| ✓ Without explaining how the sample creates the grayscale image | Maintained | Deferred to Phase 2.2 |

---

*End of Phase 2.1 Final Report*
