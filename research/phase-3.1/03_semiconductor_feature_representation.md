# Semiconductor Feature Representation

**Research Phase:** 3.1
**Document:** 03_semiconductor_feature_representation.md
**Date:** 2026-07-30

---

## 1. Feature Catalog

This document catalogs every semiconductor feature type relevant to CD-SEM metrology and defines its geometric representation in the 2.5D height field format.

---

## 2. Interconnect Features (BEOL)

### 2.1 Metal Line

| Property | Specification |
|---|---|
| **Description** | A rectangular metal conductor running horizontally in a dielectric matrix |
| **Key parameters** | CD (critical dimension), pitch, height, sidewall angle, liner thickness |
| **2.5D representation** | Rectangular region in material map (metal ID) elevated by line height |
| **SE contrast** | High: edge brightening at both line edges |
| **Typical dimensions (N5)** | CD = 15–30 nm, pitch = 30–60 nm, height = 30–50 nm |

**Cross-section (2.5D height field):**
```
Height map (x-axis cross-section):
         ▄▄▄▄▄▄▄▄▄▄▄▄
         █            █          ← Metal line (height = H)
         █            █
▀▀▀▀▀▀▀▀▀            ▀▀▀▀▀▀▀▀  ← Dielectric (height = 0)

Material map:
111111111222222222221111111111  ← 1=dielectric (SiO₂), 2=metal (Cu)
```

### 2.2 Line/Space Array (Dense Pattern)

| Property | Specification |
|---|---|
| **Description** | Periodic array of alternating lines and spaces |
| **Key parameters** | Line CD, space CD, pitch = line + space, height, sidewall angle |
| **2.5D representation** | Repeated rectangle regions in material map |
| **SE contrast** | Periodic bright peaks at each edge |
| **Typical dimensions (N5)** | Pitch = 30–50 nm, line:space ratio 1:1 or 1:3 |

### 2.3 Contact Hole

| Property | Specification |
|---|---|
| **Description** | Vertical cylindrical hole through dielectric, filled with conductor |
| **Key parameters** | Diameter, depth, taper angle, bottom CD |
| **2.5D representation** | Circular region in material map with cylindrical depression |
| **SE contrast** | Annular bright ring at hole edge; dark interior |
| **Typical dimensions (N5)** | Diameter = 20–40 nm, depth = 50–200 nm, aspect ratio 2:1 to 10:1 |

**Cross-section (2.5D height field):**
```
Height map (plan view):
   ▄▄▄▄▄▄▄▄▄
  ▄          ▄
 █            █     ← Annular bright ring at hole edge
 █   Dark     █
  ▄  interior ▄
   ▄▄▄▄▄▄▄▄▄

Height map (cross-section):
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀  ← Top surface (height H)
           ↓
        ▄▄▄▄▄         ← Contact hole (depth H, diameter D)
```

### 2.4 Via

| Property | Specification |
|---|---|
| **Description** | Vertical interconnect between two metal layers |
| **Key parameters** | Diameter, depth, taper angle, barrier thickness |
| **2.5D representation** | Circular depression in upper metal layer, filled with via metal |
| **SE contrast** | Edge brightening at via perimeter |
| **Typical dimensions (N5)** | Diameter = 15–30 nm, depth = 20–50 nm |

**Fact:** Vias differ from contacts primarily in their position (between metal layers vs. contact to substrate) and aspect ratio (vias are shallower).

---

## 3. Front-End-of-Line (FEOL) Features

### 3.1 FinFET Fin

| Property | Specification |
|---|---|
| **Description** | Vertical semiconductor fin serving as the transistor channel |
| **Key parameters** | Fin width, fin height, fin pitch, sidewall angle |
| **2.5D representation** | Narrow elevated rectangular strip in Si |
| **SE contrast** | Very narrow edge brightening; top surface may be visible |
| **Typical dimensions (N5)** | Width = 5–8 nm, height = 30–50 nm, pitch = 25–40 nm |

**Cross-section (2.5D height field):**
```
          ▄▄▄▄▄▄▄▄▄▄
          █          █          ← Fin (Si, height = H)
          █          █
▀▀▀▀▀▀▀▀▀█          █▀▀▀▀▀▀▀▀▀  ← STI oxide (height = 0)
          █          █
          █  (bulk)  █
```

**Inference:** Fins are the most challenging CD-SEM target at advanced nodes. The fin width (5–8 nm) approaches the SEM resolution limit. Edge brightening peaks may merge into a single broad peak if the fin is narrower than ~2× the probe diameter.

### 3.2 Gate Structure

| Property | Specification |
|---|---|
| **Description** | Transistor gate electrode over the channel region |
| **Key parameters** | Gate length, gate height, spacer width, work function metal thickness |
| **2.5D representation** | Elevated strip crossing the fin structure (complex 2.5D topology) |
| **SE contrast** | Multi-peak structure from gate edge + spacer edges + fin edges |
| **Typical dimensions (N5)** | Gate length = 12–20 nm, height = 40–60 nm, spacer = 5–10 nm |

**Fact:** The gate structure involves multiple materials (polysilicon or metal gate + SiN/SiO₂ spacers + work-function metals), creating a complex multi-peak SEM profile.

### 3.3 Shallow Trench Isolation (STI)

| Property | Specification |
|---|---|
| **Description** | Oxide-filled trench isolating adjacent transistors |
| **Key parameters** | Trench depth, top CD, bottom CD, corner rounding radius |
| **2.5D representation** | Depressed region in Si, filled with oxide (different material ID) |
| **SE contrast** | Edge peaks at STI boundary; material contrast between Si and oxide |
| **Typical dimensions (N5)** | Depth = 200–400 nm, width = 30–50 nm, corner radius = 3–10 nm |

---

## 4. Memory Array Features (DRAM)

### 4.1 DRAM Capacitor

| Property | Specification |
|---|---|
| **Description** | Deep cylindrical capacitor in DRAM array |
| **Key parameters** | Diameter, depth (aspect ratio 20:1–50:1), bottom CD |
| **2.5D representation** | Circular depression with very high aspect ratio |
| **SE contrast** | Strong edge brightening; bottom may be invisible due to aspect ratio |
| **Typical dimensions** | Diameter = 30–50 nm, depth = 1–2 μm |

**Fact:** DRAM capacitors have the highest aspect ratios in semiconductor manufacturing. The deep trench creates significant charging and beam deflection artifacts in SEM imaging.

### 4.2 DRAM Buried Wordline

| Property | Specification |
|---|---|
| **Description** | Wordline buried in the Si substrate |
| **Key parameters** | Line CD, pitch, depth, dielectric thickness |
| **2.5D representation** | Narrow trench with oxide fill and conductor |
| **SE contrast** | Subtle topographic contrast at wordline edges |

---

## 5. Feature Representation Summary

| Feature | 2.5D OK? | Material Count | Key Dimension Min | Key to SEM Contrast |
|---|---|---|---|---|
| Metal line | ✓ Yes | 2 | CD = 15 nm | Edge brightening at foot/top |
| Line/space array | ✓ Yes | 2 | Pitch = 30 nm | Periodic edge peaks |
| Contact hole | ⚠ Circular (approximated) | 2–3 | CD = 20 nm | Annular edge ring |
| Via | ✓ Yes | 2–3 | CD = 15 nm | Perimeter edge |
| FinFET fin | ✓ Yes | 1–2 | Width = 5 nm | Very narrow double peak |
| Gate (over fin) | ✓ Yes | 3–5 | Length = 12 nm | Multi-peak from stacked materials |
| STI | ✓ Yes | 2 | Width = 30 nm | Material + topographic contrast |
| DRAM capacitor | ✓ Yes | 2–3 | CD = 30 nm | Edge ring, charging artifacts |
| DRAM wordline | ✓ Yes | 2–3 | CD = 15 nm | Subtle T contrast |

---

## 6. Minimum Geometric Information Required

For each feature type, the minimum information needed to generate a 2.5D height field for SEM simulation:

| Feature | Required Parameters | Optional Parameters |
|---|---|---|
| Metal line | CD, height, pitch, material | Sidewall angle (default 88°), liner thickness |
| Trench | Top CD, depth, material | Bottom CD (taper), corner rounding |
| Contact hole | Top diameter, depth, material | Taper angle, bottom diameter |
| Fin | Width, height, material | Sidewall angle, STI recess |
| Gate | Length, height, spacer width, work function metals | Sidewall profile, recess |
| STI | Depth, top CD, oxide material | Corner rounding, bottom CD |

**Engineering Decision:** The geometry engine must accept at minimum these parameters per feature. Default values (sidewall angles, corner radii) are defined for cases where the user provides minimal input.

---

## Sources

- [E1] S. M. Sze, *Semiconductor Devices: Physics and Technology*, 3rd ed. Wiley, 2012.
- [E4] M. Quirk and J. Serda, *Semiconductor Manufacturing Technology*, Prentice Hall, 2001.
- [E10] ITRS (International Technology Roadmap for Semiconductors), 2022 edition.
- [E11] Y. Taur and T. H. Ning, *Fundamentals of Modern VLSI Devices*, 3rd ed. Cambridge, 2021.
- [E12] S. K. Saha, "Scaling considerations for sub-10 nm FinFET technology," *IEEE TED*, 2018.
- [E13] G. S. May and S. M. Sze, *Fundamentals of Semiconductor Fabrication*, Wiley, 2004.
