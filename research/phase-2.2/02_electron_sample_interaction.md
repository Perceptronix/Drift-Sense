# Electron–Sample Interaction

**Research Phase:** 2.2
**Document:** 02_electron_sample_interaction.md
**Date:** 2026-07-30

---

## 1. Overview

When a focused electron beam with energy $E_0$ (typically 300 eV–30 keV) strikes a solid sample, the incident electrons penetrate the surface and undergo a cascade of scattering events. These events fall into two fundamental categories:

- **Elastic scattering:** The electron's direction changes but it loses negligible energy (<1 eV).
- **Inelastic scattering:** The electron transfers significant energy to the sample, creating secondary signals.

The balance between these two scattering types determines the shape and extent of the **interaction volume**, the three-dimensional region within the sample where the primary beam energy is deposited and from which signals emerge.

---

## 2. Elastic Scattering

### 2.1 Physical Mechanism

Elastic scattering occurs when a primary electron passes near an atomic nucleus and is deflected by the Coulomb field of the positively charged nucleus (partially screened by the surrounding electron cloud). Because the nucleus is much heavier than the electron ($m_{\text{nucleus}} / m_e \approx 10^4$–$10^5$), the electron transfers negligible kinetic energy — typically <1 eV even for large-angle deflections.

**Fact:** Elastic scattering is the dominant mechanism at large scattering angles and is responsible for redirecting electrons back toward the sample surface, producing backscattered electrons.

### 2.2 Rutherford Scattering Model

The differential cross-section for elastic scattering of an electron by a screened nucleus is described by the screened Rutherford cross-section:

$$\frac{d\sigma_{\text{el}}}{d\Omega} = \frac{Z^2 e^4}{16 E^2} \cdot \frac{1}{(\sin^2(\theta/2) + \alpha^2)^2}$$

where:
- $Z$ = atomic number
- $e$ = electron charge
- $E$ = electron energy
- $\theta$ = scattering angle
- $\alpha$ = screening parameter (accounts for electron cloud shielding)

**Inference:** The $Z^2$ dependence means high-Z materials (W, Au) scatter electrons much more strongly than low-Z materials (Si, C). This is the physical origin of BSE compositional contrast.

### 2.3 Mott Cross-Sections

The screened Rutherford model is accurate for high-energy electrons and light elements but becomes increasingly inaccurate for:
- Low energies (<5 keV)
- High-Z elements

Under these conditions, the **Mott cross-section** — which accounts for spin-orbit coupling and relativistic effects — provides a more accurate description. Most modern Monte Carlo simulations use Mott cross-sections for elastic scattering.

### 2.4 Mean Free Path for Elastic Scattering

The elastic mean free path $\lambda_{\text{el}}$ is the average distance an electron travels between elastic scattering events:

$$\lambda_{\text{el}} = \frac{1}{N \sigma_{\text{el}}}$$

where $N$ is the atomic number density and $\sigma_{\text{el}}$ is the total elastic cross-section.

**Typical values (approximate, for 10 keV primary beam):**

| Material | Elastic MFP (nm) |
|---|---|
| Si | ~40 |
| Cu | ~10 |
| W | ~3 |

**Fact:** At lower energies (<1 keV), the elastic mean free path decreases significantly because the scattering cross-section increases as approximately $1/E$.

---

## 3. Inelastic Scattering

### 3.1 Physical Mechanism

Inelastic scattering occurs when a primary electron interacts with electrons bound to sample atoms. The primary electron loses energy, and this energy is transferred to the atom, causing one of several possible outcomes:

1. **Ionization:** An inner-shell or outer-shell electron is ejected (produces SE, Auger, X-rays).
2. **Plasmon excitation:** Collective oscillations of valence electrons (dominant energy loss mechanism in metals).
3. **Phonon excitation:** Lattice vibrations (very small energy loss, ~0.01 eV).
4. **Bremsstrahlung:** Deceleration in the nuclear field (produces continuum X-rays).
5. **Cathodoluminescence:** Valence band → conduction band transitions in insulators/semiconductors (produces photons).

### 3.2 Bethe Energy Loss (Stopping Power)

The average energy loss per unit path length is given by the **Bethe stopping power formula** (for non-relativistic electrons):

$$\frac{dE}{ds} = -\left(\frac{2\pi e^4 N_A Z \rho}{E A}\right) \ln\left(\frac{1.166 E}{J}\right)$$

where:
- $dE/ds$ = stopping power (keV/cm)
- $N_A$ = Avogadro's number
- $Z$ = atomic number
- $\rho$ = density (g/cm³)
- $E$ = electron energy (keV)
- $A$ = atomic weight (g/mol)
- $J$ = mean ionization potential (eV)

**Fact:** The stopping power scales approximately as $1/E$. Low-energy electrons lose energy faster per unit path length than high-energy electrons. This is why low-voltage SEM (<1 keV) deposits energy in a much shallower region.

### 3.3 Mean Ionization Potential

The mean ionization potential $J$ is a material-dependent parameter that determines the effective "cost" of inelastic scattering:

$$J \approx (9.76 Z + 58.8 Z^{-0.19}) \times 10^{-3} \text{ keV}$$

For silicon ($Z = 14$): $J \approx 0.172$ keV.
For copper ($Z = 29$): $J \approx 0.322$ keV.
For tungsten ($Z = 74$): $J \approx 0.527$ keV.

### 3.4 Continuous Slowing Down Approximation (CSDA)

The CSDA treats energy loss as a continuous process along the electron trajectory, ignoring the stochastic nature of individual scattering events. The **Bethe range** $R_B$ is the total path length traveled before the electron comes to rest:

$$R_B = \int_{0}^{E_0} \frac{dE}{-(dE/ds)}$$

**Fact:** The Bethe range is the maximum distance an electron of energy $E_0$ can travel in a solid. The actual penetration depth (straight-line distance from surface to stopping point) is typically 2–5× smaller than the Bethe range because elastic scattering causes the trajectory to zigzag.

### 3.5 Discrete Energy Loss Model

For Monte Carlo simulation, inelastic scattering is modeled as discrete events rather than continuous loss:

- The electron travels a distance $\lambda_{\text{inel}}$ (inelastic mean free path).
- At each inelastic event, a specific energy loss $\Delta E$ is sampled from an energy loss distribution (e.g., the Bethe differential cross-section or a dielectric function model).
- The electron direction may change slightly (small-angle inelastic scattering).

---

## 4. The Interaction Volume

### 4.1 Definition

The interaction volume is the three-dimensional region within the sample where the primary electron beam deposits energy and from which detectable signals emerge.

### 4.2 Dependence on Beam Energy

**Fact:** The interaction volume size scales approximately as $E_0^{1.7}$ for energies in the 1–30 keV range. This rapid scaling means changing the accelerating voltage is the most effective way to control the sampling depth.

| Energy (keV) | Penetration in Si (μm) |
|---|---|
| 0.5 | ~0.01 |
| 1.0 | ~0.03 |
| 2.0 | ~0.1 |
| 5.0 | ~0.5 |
| 10.0 | ~1.5 |
| 20.0 | ~4.0 |
| 30.0 | ~7.0 |

### 4.3 Dependence on Material (Atomic Number)

| Material | Penetration at 10 keV (μm) | Penetration at 1 keV (nm) |
|---|---|---|
| Si (Z=14, ρ=2.33 g/cm³) | ~1.5 | ~30 |
| Cu (Z=29, ρ=8.96 g/cm³) | ~0.5 | ~15 |
| W (Z=74, ρ=19.3 g/cm³) | ~0.15 | ~5 |
| Photoresist (Z~5, ρ~1.1 g/cm³) | ~5 | ~100 |

**Inference:** Higher density and higher atomic number both reduce the interaction volume because:
1. Higher density → more atoms per unit volume → more frequent scattering.
2. Higher Z → larger scattering cross-section → stronger deflection.

### 4.4 Shape of the Interaction Volume

The shape depends on the balance between elastic and inelastic scattering:

**Low-Z materials (Si, C, photoresist):**
- Primary electrons undergo relatively few elastic scattering events.
- Electrons travel deeper before being significantly deflected.
- Interaction volume is **teardrop-shaped**: narrow neck near the surface, widest at ~0.5× the total penetration depth.

**High-Z materials (W, Au):**
- Frequent elastic scattering events deflect electrons quickly.
- Electrons spread laterally very close to the surface.
- Interaction volume is **hemispherical**: maximum width near the surface.

### 4.5 Signal Origin Regions

Different signals originate from different depths within the interaction volume:

```
Surface
  │
  ├─ [0–2 nm]     SE-I (primary SE)            → Highest resolution
  ├─ [0.5–3 nm]   Auger electrons               → Surface composition
  ├─ [0–20 nm]    SE-II (from exiting BSE)     → Lower resolution SE
  ├─ [0.1–1 μm]   BSE (elastically scattered)   → Compositional contrast
  ├─ [0.1–5 μm]   Characteristic X-rays         → Elemental identification
  └─ [0.1–5 μm]   Bremsstrahlung (continuous)   → X-ray background
```

**Fact:** The spatial resolution of each signal is determined by the volume from which it can escape. SE resolution ≈ probe diameter. BSE resolution ≈ 0.1–0.5× interaction diameter. X-ray resolution ≈ interaction diameter.

---

## 5. Energy Loss Mechanisms

### 5.1 Regimes of Energy Loss

For electrons in the energy range relevant to SEM (0.3–30 keV), the dominant energy loss mechanisms are:

| Mechanism | Energy Loss per Event | Typical Energy Loss (eV) | Spatial Scale |
|---|---|---|---|
| Plasmon excitation | $E_p$ (bulk plasmon) | 5–30 eV | ~10 nm |
| Inner-shell ionization | Binding energy of shell | 50–20,000 eV | ~0.1–1 nm |
| Valence electron ionization | Valence/conduction band | 2–20 eV | ~0.1–1 nm |
| Phonon excitation | ~0.01 eV | ~0.01 eV | ~0.1–1 nm |
| Bremsstrahlung | 0–$E_0$ (continuous) | Variable | Nuclear scale |

### 5.2 Plasmon Losses

In metals and doped semiconductors, the valence electron gas can undergo collective oscillations — **plasmons** — when excited by a fast electron. The energy loss is quantized in units of the plasmon energy $E_p$:

For Si: $E_p \approx 16.7$ eV
For Al: $E_p \approx 15.0$ eV
For Cu: $E_p \approx 7.5$ eV

**Fact:** Plasmon excitation is the dominant energy loss mechanism for medium-energy electrons (200 eV–10 keV) in materials with free or weakly bound electrons.

### 5.3 Inner-Shell Ionization

When a primary electron has energy exceeding the binding energy of a core electron, it can eject that electron, leaving the atom in an excited state. This is followed by relaxation:

- **X-ray fluorescence:** An electron from a higher shell fills the vacancy, emitting an X-ray with energy equal to the difference in binding energies.
- **Auger emission:** The energy released by the electron transition ejects a second (Auger) electron.

The probability of each relaxation path is given by the **fluorescence yield** $\omega$, which increases with Z.

### 5.4 Surface and Near-Surface Behavior

At very low energies (<100 eV), the Bethe stopping power model breaks down because:
- The mean free path becomes comparable to atomic spacing.
- The dielectric response of the material becomes important.
- Surface excitations (surface plasmons, surface phonons) contribute significantly.

---

## 6. Monte Carlo Interpretation of Electron Trajectories

### 6.1 Principle

Monte Carlo simulation treats the electron trajectory as a random walk through the solid. Each electron undergoes a sequence of scattering events:

1. An electron starts at the surface with initial energy $E_0$ and direction normal to the surface.
2. Travel a distance $\Delta s$ sampled from an exponential distribution with mean $\lambda_{\text{mfp}}$ (total mean free path).
3. At each scattering event:
   - Determine if the event is elastic or inelastic (by random number vs. $\sigma_{\text{el}}/\sigma_{\text{total}}$).
   - If elastic: sample scattering angle $\theta$ from the elastic cross-section.
   - If inelastic: sample energy loss $\Delta E$ and small angular change.
4. Update position, energy, and direction.
5. Repeat until the electron energy falls below a threshold (typically 50 eV) or it exits the sample.
6. If the electron exits the surface, record it as a backscattered electron (if energy >50 eV) or a secondary electron (if energy <50 eV).

### 6.2 Single vs. Plural vs. Multiple Scattering

| Regime | Condition | Characteristics | Validity for SEM |
|---|---|---|---|
| Single scattering | Thickness << $\lambda_{\text{mfp}}$ | No scattering events | Not applicable (sample is thick) |
| Plural scattering | Thickness ≈ $\lambda_{\text{mfp}}$ | 2–20 events | Low-kV, thin films |
| Multiple scattering | Thickness >> $\lambda_{\text{mfp}}$ | Many events, Gaussian angular distribution | Most SEM conditions |
| Diffusion | Thickness >> $\lambda_{\text{tr}}$ | Isotropic angular distribution | High-kV, bulk samples |

**Fact:** For semiconductor CD-SEM operating at 500 eV–1.5 keV, the scattering regime is **plural to multiple scattering** — electrons undergo tens to hundreds of scattering events before stopping or exiting.

### 6.3 The CASINO Monte Carlo Code

The widely-used **CASINO** (monte CArlo SImulation of electroN trajectory in sOlids) code, developed at the Université de Sherbrooke, is specifically designed for SEM electron trajectory simulation. Key features:

- Uses Mott cross-sections for elastic scattering.
- Uses the Bethe continuous slowing down approximation or discrete energy loss.
- Models SE generation using the Joy and Luo or Kanaya-Okayama models.
- Outputs: electron trajectories, BSE yield, SE yield, energy distributions, spatial distributions.

### 6.4 What Monte Carlo Physics Reveals

For a 1 keV beam on silicon:
- Mean number of elastic scattering events per electron: ~100
- Mean number of inelastic scattering events per electron: ~500
- Total path length (Bethe range): ~45 nm
- Maximum penetration depth: ~30 nm
- BSE yield: ~0.2
- SE yield: ~1.0

**Inference:** Each primary electron generates multiple secondary electrons during its trajectory. Most SEs are generated deep within the interaction volume and cannot escape — only those generated within ~1–5 nm of the surface contribute to the detected signal.

---

## 7. Summary of Scattering Processes

```
Primary Electron (E₀ = 0.3–30 keV) enters sample
    │
    ├── Elastic scattering (Rutherford / Mott) ──→ Direction change, no energy loss
    │   │
    │   └── Backscattered electron (θ > 90°) ──→ Exits as BSE
    │
    └── Inelastic scattering (Bethe / dielectric)
        │
        ├── Ionization (inner shell) ──→ Characteristic X-ray OR Auger electron
        ├── Ionization (valence) ──→ Secondary electron (<50 eV)
        ├── Plasmon excitation ──→ Energy loss in multiples of E_p
        ├── Bremsstrahlung ──→ Continuum X-ray
        └── Phonon excitation ──→ Heat (negligible for imaging)
```

Each primary electron can undergo hundreds of scattering events, generating dozens of secondary electrons, and potentially producing X-rays or backscattered electrons before coming to rest within the sample or exiting.

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- P. Hovington, D. Drouin, and R. Gauvin, "CASINO: A new Monte Carlo code in C language for electron beam interactions," *Scanning*, vol. 19, 1997.
- D. Drouin, A. R. Couture, D. Joly, et al., "CASINO V2.42 — A fast and easy-to-use modeling tool for scanning electron microscopy," *Scanning*, vol. 29, 2007.
- NIST, "Electron Inelastic Mean Free Path Database" (SRD 71).
- Wikipedia, "Interaction Volume," accessed July 2026.
- Nanoscience Instruments, "Scanning Electron Microscopy," technical resource.
- H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
