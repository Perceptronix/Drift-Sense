# Reusable Geometry Library

**Research Phase:** 3.4
**Document:** 04_reusable_geometry_library.md
**Date:** 2026-07-30

---

## 1. Library Overview

The reusable geometry library contains 10 structure types that cover all standard CD-SEM measurement targets. Each structure is defined by a parameter set that the geometry engine uses to generate the 2.5D height field and material map.

---

## 2. Structure Catalog

### 2.1 Isolated Line

| Aspect | Detail |
|---|---|
| **Purpose** | Basic CD-SEM target — edge profile characterization |
| **Structure** | Single line on substrate |
| **Parameters** | CD, height, sidewall angle, corner radii, material (line), material (substrate) |
| **Variability** | LER on both edges, LWR, sidewall angle variation |
| **GDSII** | Single rectangle of width = CD, length = L |
| **Phases** | Front-end (resist on Si) or BEOL (metal in dielectric) |

### 2.2 Dense Line/Space Array

| Aspect | Detail |
|---|---|
| **Purpose** | Pitch measurement, dense vs. isolated CD comparison |
| **Structure** | Periodic array of lines and spaces |
| **Parameters** | Line CD, space CD, pitch, height, sidewall angle, material (line), material (space) |
| **Variability** | LER/LWR on all edges, pitch walk (systematic), CDU across array |
| **GDSII** | Repeated rectangles. Center-to-center spacing = pitch |
| **Configurations** | 1:1 (dense), 1:2, 1:3 (semi-dense) |

### 2.3 Contact Hole

| Aspect | Detail |
|---|---|
| **Purpose** | Hole edge profile, annular ring SEM characterization |
| **Structure** | Circular opening in dielectric, filled with conductor |
| **Parameters** | Top diameter, bottom diameter (taper), depth, material (fill), material (dielectric) |
| **Variability** | Radial LER on hole perimeter, diameter variation, taper variation |
| **GDSII** | Single circle or octagon of diameter = CD |
| **Constraint** | Aspect ratio can be high (5:1–15:1 at N5) |

### 2.4 Via

| Aspect | Detail |
|---|---|
| **Purpose** | BEOL interconnect metrology |
| **Structure** | Vertical interconnect between two metal layers |
| **Parameters** | Top CD, bottom CD, depth, barrier thickness, material (fill), material (barrier), material (ILD) |
| **Variability** | Same as contact hole + overlay shift relative to M1/M2 |
| **GDSII** | Circle or octagon in via layer |
| **Note** | Structurally similar to contact but shallower (AR 1:1–3:1) |

### 2.5 Trench

| Aspect | Detail |
|---|---|
| **Purpose** | Trench metrology (e.g., STI, damascene) |
| **Structure** | Elongated rectangular depression in material |
| **Parameters** | Top CD, bottom CD, depth, sidewall angle, corner radii (top, bottom), material (fill), material (substrate) |
| **Variability** | LER on both edges, bottom roughness, taper variation |
| **GDSII** | Rectangle (the absence of material defines the trench) |

### 2.6 FinFET Fin

| Aspect | Detail |
|---|---|
| **Purpose** | Fin metrology — the most challenging CD-SEM target at N5 |
| **Structure** | Narrow vertical Si fin surrounded by STI oxide |
| **Parameters** | Fin top CD, fin bottom CD, fin height, STI recess, sidewall angle, corner radius (top) |
| **Variability** | Fin CD variation, fin height variation, LER on fin edges |
| **GDSII** | Narrow rectangle (width = fin bottom CD) |
| **Constraint** | Fin width (5–8 nm) approaches SEM resolution limit |

### 2.7 Gate Structure (Over Fin)

| Aspect | Detail |
|---|---|
| **Purpose** | Gate metrology — multi-material stack over fin topography |
| **Structure** | Gate electrode crossing fins, with spacers, work-function metals |
| **Parameters** | Gate length, gate height, spacer width, WF metal thickness, gate material, spacer material, substrate |
| **Variability** | Gate CDV, spacer width variation, overlay relative to fin |
| **GDSII** | Rectangle crossing fin array |
| **Complexity** | 3–5 materials in a vertical stack; most complex structure |

### 2.8 STI Array

| Aspect | Detail |
|---|---|
| **Purpose** | Isolation metrology, corner rounding characterization |
| **Structure** | Periodic oxide-filled trenches in Si |
| **Parameters** | STI depth, top CD, bottom CD, corner radius (top), material (oxide), material (substrate Si) |
| **Variability** | Trench CD variation, corner rounding variation, depth variation |
| **GDSII** | Repeated rectangles or grid |

### 2.9 Bi-Material Boundary

| Aspect | Detail |
|---|---|
| **Purpose** | Material contrast calibration — reference for SEM intensity ratios |
| **Structure** | Two materials meeting at a step edge |
| **Parameters** | Height difference, material A, material B, step transition width |
| **Variability** | Step edge roughness, boundary width variation |
| **GDSII** | Two adjacent polygons without gap |

### 2.10 Calibration Structure (Pitch Standard)

| Aspect | Detail |
|---|---|
| **Purpose** | SEM calibration — known pitch reference |
| **Structure** | Array of lines with precisely known pitch |
| **Parameters** | Pitch, line CD, number of lines, material |
| **Variability** | Minimal LER, minimal CDU (calibration quality) |
| **GDSII** | Repeated rectangles with exact pitch |

---

## 3. Structure Parameter Summary

| # | Structure | Parameters (Essential) | Parameters (Variation) | Materials | Complexity |
|---|---|---|---|---|---|
| 1 | Isolated line | CD, H, θ, R | LER, LWR, θ_σ | 2 | Low |
| 2 | Dense L/S | CD, pitch, H, θ | LER, LWR, CDU, θ_σ | 2–3 | Moderate |
| 3 | Contact hole | D_top, D_bot, depth | Radial LER, CDU, taper | 2–3 | Moderate |
| 4 | Via | D_top, D_bot, depth, barrier | Radial LER, overlay | 3–4 | Moderate |
| 5 | Trench | CD_top, CD_bot, depth, θ | LER, θ_σ, bottom R | 2 | Low |
| 6 | FinFET fin | CD_top, CD_bot, H, recess | Fin CDU, LER, H_σ | 2 | High |
| 7 | Gate stack | L_gate, H_gate, spacer | CDV, spacer_σ, overlay | 3–5 | High |
| 8 | STI array | D, CD, R_corner | CDU, R_σ, D_σ | 2 | Moderate |
| 9 | Bi-material | ΔH, mat A, mat B | Edge rough, ΔH_σ | 2 | Low |
| 10 | Pitch standard | Pitch, CD, N | Minimal LER | 1–2 | Low |

---

## 4. Library Schema

### 4.1 Structure Definition Format

Each library entry is defined as:

```
Structure {
    name: string;                       // e.g., "iso_line_50nm"
    type: "line" | "trench" | "contact" | "via" | "fin" | "gate" | "sti" | "bimaterial" | "pitch_std" | "ls_array";
    description: string;                // Free text
    parameters: Parameter[];            // See below
    material_stack: MaterialLayer[];    // Layer order with materials
    variability: VariabilityConfig;     // LER, CDU, overlay defaults
    constraints: Constraint[];          // e.g., "CD >= 5 nm"
    metadata: {                         // author, version, date, etc.
        version: string;
        author: string;
        date: string;
        technology_node: string;        // e.g., "N5"
    };
};
```

### 4.2 Parameter Definition

```
Parameter {
    name: string;                       // e.g., "cd_nm"
    symbol: string;                     // e.g., "CD"
    description: string;                // "Critical dimension (top CD)"
    units: string;                      // "nm"
    default: float;                     // 50.0
    min: float;                         // 5.0
    max: float;                         // 1000.0
    distribution: "fixed" | "gaussian" | "truncated_gaussian";
    sigma: float;                       // 1.0 (if applicable)
};
```

---

## 5. Library Organization

```
geometry_library/
├── lines/
│   ├── iso_line_50nm.yml
│   ├── iso_line_20nm.yml
│   ├── dense_ls_1to1_30nm.yml
│   └── dense_ls_1to3_40nm.yml
├── contacts/
│   ├── contact_30nm.yml
│   └── contact_20nm_ar10.yml
├── vias/
│   ├── via_20nm.yml
│   └── chain_via_30nm.yml
├── fins/
│   ├── fin_width6nm.yml
│   └── fin_array_30nm_pitch.yml
├── gates/
│   ├── gate_length16nm.yml
│   └── gate_over_fin.yml
├── trenches/
│   ├── sti_trench.yml
│   └── deep_trench_ar20.yml
├── calibration/
│   ├── pitch_standard_100nm.yml
│   └── bimaterial_si_sio2.yml
└── library_index.yml                  ← Master index of all structures
```

---

## Sources

- [F1] J. D. Plummer, *Silicon VLSI Technology*, Prentice Hall, 2000.
- [F2] S. Wolf, *Silicon Processing for the VLSI Era*, Lattice Press, 2002.
- [E1] S. M. Sze, *Semiconductor Devices*, Wiley, 2012.
- [E7] J. W. Smith et al., *Proc. SPIE*, vol. 10145, 2017.
- Phase 3.2, Document 04 — Feature cross-section models.
- Phase 3.3, Document 02 — LER/LWR models.
