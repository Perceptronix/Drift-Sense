# Output Artifacts

**Research Phase:** 4.4
**Document:** 03_output_artifacts.md
**Date:** 2026-07-30

---

## 1. Artifact Overview

Each generated sample produces up to **7 artifacts**, organized by priority:

| Priority | Artifact | Always Produced? | Essential for ML? |
|---|---|---|---|
| **P0** | SEM Image | ✅ Required | ✅ Yes |
| **P1** | Ground Truth (JSON) | ✅ Required | ✅ Yes |
| **P1** | Configuration Snapshot (JSON) | ✅ Required | ✅ Yes |
| **P1** | Metadata Record (JSON) | ✅ Required | ✅ Yes |
| **P2** | Height Field (NumPy) | ⚠️ Recommended | No (useful for research) |
| **P2** | Material Map (PNG) | ⚠️ Recommended | No (redundant with GT material seg.) |
| **P3** | Yield Maps (NumPy) | ❌ Optional | No (debugging/research) |

---

## 2. Artifact Specifications

### 2.1 P0: SEM Image

| Aspect | Specification |
|---|---|
| **File** | `images/{name}.tiff` |
| **Format** | 16-bit grayscale TIFF |
| **Content** | Digitized SEM image — intensity per pixel |
| **Dimensions** | M × N (configurable, default 1024 × 1024) |
| **Bit depth** | 16 (configurable to 8) |
| **Compression** | LZW (lossless) |
| **Color space** | Grayscale (single channel) |
| **Pixel meaning** | 0 = black (minimum signal), 65535 = white (saturation) |
| **Coordinate system** | Row = Y (slow scan), Column = X (fast scan); origin at top-left |
| **Relationship to other artifacts** | The image is the primary output. All other artifacts describe or annotate this image. |

### 2.2 P1: Ground Truth (JSON)

| Aspect | Specification |
|---|---|
| **File** | `ground_truth/{name}.json` |
| **Format** | JSON |
| **Content** | Structured labels: edge maps, CD values, segmentation, contours |
| **Required when** | `dataset.include_ground_truth = true` |
| **See** | Document 04 (Ground Truth Specification) for full field list |

### 2.3 P1: Configuration Snapshot

| Aspect | Specification |
|---|---|
| **File** | `metadata/{name}_config.json` |
| **Format** | JSON |
| **Content** | Full resolved configuration used to generate this sample |
| **Purpose** | Enables exact reproduction of any sample |
| **Required when** | Always |
| **Size** | Typically 2–10 KB |

### 2.4 P1: Metadata Record

| Aspect | Specification |
|---|---|
| **File** | `metadata/{name}_metadata.json` |
| **Format** | JSON |
| **Content** | Seed chain, version info, timestamps, warnings |
| **Purpose** | Provenance tracking, filtering, quality assessment |
| **Required when** | Always |
| **See** | Document 05 (Metadata Specification) for full field list |

### 2.5 P2: Height Field

| Aspect | Specification |
|---|---|
| **File** | `ground_truth/{name}_height.npy` |
| **Format** | NumPy .npy (float64, M × N) |
| **Content** | Z = height at each pixel (nm). Same as the HeightField_var data from the pipeline. |
| **Purpose** | Enables 3D visualization, custom analysis, alternative ground truth extraction |
| **Required when** | `dataset.include_height_field = true` (default: false) |
| **Unit** | nm (substrate Z = 0) |
| **Dimensions** | M × N, must match the SEM image dimensions exactly |

### 2.6 P2: Material Map

| Aspect | Specification |
|---|---|
| **File** | `ground_truth/{name}_material.png` |
| **Format** | 16-bit grayscale PNG (lossless) |
| **Content** | Material ID per pixel: 0 = vacuum, 1 = Si, 2 = SiO₂, 3 = SiN, 4 = Cu, 5 = W, 6 = PR |
| **Purpose** | Material segmentation ground truth |
| **Required when** | `dataset.include_material_map = true` (default: false) |
| **Relation to GT** | Redundant with material_segmentation in the JSON GT file. This is a convenience copy in image format. |

### 2.7 P3: Yield Maps

| Aspect | Specification |
|---|---|
| **File** | `ground_truth/{name}_yields.npz` |
| **Format** | NumPy .npz (compressed archive with `se_yield` and `bse_yield` arrays) |
| **Content** | Pre-degradation SE and BSE yield maps (float64) |
| **Purpose** | Research: studying signal formation, debugging physics model |
| **Required when** | `dataset.include_yield_maps = true` (default: false) |
| **Size** | ~16 MB per map (1024×1024 × float64) |

---

## 3. Artifact Relationships

```
                  ┌─────────────────┐
                  │  SEM Image      │  ← Primary output
                  │  (P0, .tiff)    │
                  └────────┬────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
│  Ground Truth   │ │  Config      │ │  Metadata    │
│  (P1, .json)    │ │  Snapshot    │ │  (P1, .json) │
│                 │ │  (P1, .json) │ │              │
├─────────────────┤ ├──────────────┤ ├──────────────┤
│• Edge maps      │ │• Full config │ │• Seed chain  │
│• CD values      │ │• Structure   │ │• Version     │
│• Segmentation   │ │• Geometry    │ │• Timestamp   │
│• Contours       │ │• Physics     │ │• Warnings    │
│• Edge types     │ │• Dataset     │ │• Duration    │
└─────────────────┘ └──────────────┘ └──────────────┘
         │
         ├─────────────────────────────────────────┐
         ▼                                         ▼
┌─────────────────┐                         ┌──────────────┐
│  Height Field   │                         │  Material    │
│  (P2, .npy)     │                         │  Map         │
│                 │                         │  (P2, .png)  │
│ Redundant with  │                         │ Redundant    │
│ GT edge logic   │                         │ with GT seg  │
└─────────────────┘                         └──────────────┘
         │
         ▼
┌─────────────────┐
│  Yield Maps     │
│  (P3, .npz)     │
│                 │
│ Research-only   │
└─────────────────┘
```

---

## 4. File Format Selection Rationale

| Format | Used For | Why |
|---|---|---|
| **TIFF** (16-bit) | SEM image | Standard in microscopy; supports 16-bit, metadata, compression, multi-page |
| **JSON** | Ground truth, config, metadata | Human-readable; universally parseable; self-describing |
| **NumPy .npy** | Height field, yield maps | Fast I/O; no precision loss; Python-native |
| **PNG** (16-bit) | Material map | Lossless; browser-viewable; indexed color support |
| **NumPy .npz** | Yield map pairs | Compressed archive for two correlated arrays |

---

## 5. Artifact Consistency Rules

| Rule | Description |
|---|---|
| Same dimensions | SEM image, height field, material map, ground truth edge maps all share the same M × N dimensions |
| Same naming | All artifacts for one sample share the same base filename stem (`{name}`) |
| Same coordinate system | Row = Y, Column = X, origin at top-left — consistent across all artifacts |
| No orphan files | Every file in the dataset must be referenced in `dataset_index.json` |
| No missing references | Every entry in `dataset_index.json` must have an existing file on disk |

---

## Sources

- Phase 4.2, Document 03 — Canonical data objects (HeightField, MaterialMap, SEMImage, GroundTruth, Metadata).
- [D4] Kaggle, "Dataset Specification Best Practices," 2023.
- [D5] Open Microscopy Environment (OME), "TIFF specification for microscopy," 2010.
- [D6] NumPy, "NumPy file format specification," 2023.
