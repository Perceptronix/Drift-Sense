# Ground Truth Format Specification

**Frozen:** Phase 4.4 doc 04 (data_groundtruth). **Precision:** 0.1 nm.

---

## Per-Sample Ground Truth Artifacts

| Artifact | File | Format |
|---|---|---|
| Edge maps | `ground_truth/<sample>_edges.json` | JSON |
| CD measurements | `ground_truth/<sample>_cd.json` | JSON |
| Segmentation | `ground_truth/<sample>_segmentation.json` | JSON (RLE or polygon) |
| Contours | `ground_truth/<sample>_contours.json` | JSON (polygon vertex lists, nm) |
| Edge types | `ground_truth/<sample>_edgetypes.json` | JSON |
| Height field (optional) | `ground_truth/<sample>_height.npy` | float64 M×N, nm |
| Material map (optional) | `ground_truth/<sample>_material.png` | uint8 palette PNG |

---

## Edge Map JSON

```json
{
  "sample": "ds3_validation_000123",
  "structure_type": "iso_line",
  "pixel_size_nm": 1.0,
  "edges": [
    {
      "edge_id": 0,
      "edge_type": "top_left",
      "points_nm": [[30.0, 10.0], [30.0, 500.0]],
      "cd_target": 30.0
    }
  ]
}
```

## CD JSON

```json
{
  "sample": "ds3_validation_000123",
  "cd_measurements": [
    { "feature": "line_top", "cd_nm": 30.1 },
    { "feature": "line_bottom", "cd_nm": 32.4 },
    { "feature": "space", "cd_nm": 60.2 }
  ],
  "accuracy_nm": 0.1
}
```

---

## Coordinate System (Frozen)

- Row = Y, Col = X
- Top-left origin (0,0)
- Units: nm (vertex coordinates) / pixels (indices)
- Conversion: `nm = index * pixel_size_nm`

---

## Segmentation JSON

```json
{
  "classes": {
    "0": "vacuum", "1": "Si", "2": "SiO2", "3": "SiN",
    "4": "Cu", "5": "W", "6": "PR"
  },
  "encoding": "rle",
  "data": { "1": "RLE run-length string", "2": "..." }
}
```

---

## Validation Requirements

| Check | Tolerance |
|---|---|
| CD accuracy | ± 0.1 nm |
| Edge position | ± 1 px |
| Contour continuity | no gaps |
| Material assignment | matches MaterialMap |
| Coordinate consistency | all nm values = index × pixel_size |

---

*Frozen in Phase 5.5; derived from Phase 4.4 doc 04.*
