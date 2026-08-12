# Dataset Organization

**Research Phase:** 4.4
**Document:** 02_dataset_organization.md
**Date:** 2026-07-30

---

## 1. Dataset Directory Hierarchy

Every generated dataset follows this canonical structure:

```
{dataset_name}/
│
├── dataset_index.json                    ← Complete dataset manifest (required)
├── dataset_schema.txt                    ← Schema version of this dataset (required)
├── LICENSE                               ← License file (required)
├── README.md                             ← Dataset description (required)
│
├── images/                               ← SEM images
│   ├── iso_line_cd30_7a3b_9c1f.tiff
│   ├── iso_line_cd30_7a3b_d4e8.tiff
│   └── ...
│
├── ground_truth/                         ← Ground-truth labels
│   ├── iso_line_cd30_7a3b_9c1f.json
│   ├── iso_line_cd30_7a3b_9c1f_height.npy
│   ├── iso_line_cd30_7a3b_9c1f_material.png
│   └── ...
│
├── metadata/                             ← Per-sample metadata
│   ├── iso_line_cd30_7a3b_9c1f_config.json
│   ├── iso_line_cd30_7a3b_9c1f_metadata.json
│   └── ...
│
├── splits/                               ← Train/validation/test splits
│   ├── train.txt                         ← List of sample IDs in training set
│   ├── val.txt                           ← List of sample IDs in validation set
│   └── test.txt                          ← List of sample IDs in test set
│
├── logs/                                 ← Generation logs (optional)
│   └── generation_run.log
│
├── cache/                                ← Deterministic geometry cache (optional, git-ignored)
│   └── ...
│
└── dataset_statistics.json               ← Aggregate statistics (generated at finalization)
```

---

## 2. Naming Convention

### 2.1 File Naming

```
{structure_type}_{parameter_hash}_{seed_hash}.{extension}
```

| Component | Description | Example |
|---|---|---|
| `structure_type` | Short name from library | `iso_line`, `dense_ls`, `contact`, `fin` |
| `parameter_hash` | 4-char hex hash of structure parameters | `7a3b` |
| `seed_hash` | 4-char hex hash of image seed | `9c1f` |
| `extension` | File type | `tiff`, `json`, `npy`, `png` |

**Inference:** The naming convention is deterministic — same parameters + same seed → same filename. This prevents accidental overwrites and makes filenames self-describing.

### 2.2 Collision Prevention

Collisions occur when two different configurations produce the same filename. This is prevented by:

| Mechanism | Implementation |
|---|---|
| **Parameter hash** | SHA-256 first 4 hex chars of sorted parameter string |
| **Seed hash** | SHA-256 first 4 hex chars of image seed value |
| **Duplicate detection** | If filename collision detected, append `_v2`, `_v3` etc. |

**Engineering Decision:** Filename collision probability for 4-char hex is 1/65536 per pair — acceptable for datasets up to 10⁵ images. Detection and renaming provides a safety net.

---

## 3. Dataset Versioning

### 3.1 Version Scheme

Datasets are versioned with semantic versioning:

```
v{major}.{minor}.{patch}+{short_hash}

Examples:
  v1.0.0          ← First release
  v1.1.0          ← Added structures, new physics features
  v2.0.0          ← Breaking schema change
  v1.0.0+7a3b9c   ← Specific generation
```

| Level | Bump When | Example |
|---|---|---|
| **Major** | Breaking changes to schema, semantics, or format | v1.0.0 → v2.0.0 |
| **Minor** | New features, backward-compatible additions | v1.0.0 → v1.1.0 |
| **Patch** | Bug fixes, regenerations, no schema change | v1.0.0 → v1.0.1 |

### 3.2 Dataset Identity

Dataset identity is a tuple:

```
dataset_id = (dataset_name, version, generation_date)
```

This tuple is recorded in every `dataset_index.json` and in every per-sample metadata file.

---

## 4. Train/Validation/Test Splits

| Split | Fraction | Purpose |
|---|---|---|
| **Train** | 60–80% | Model training |
| **Validation** | 10–20% | Hyperparameter tuning, early stopping |
| **Test** | 10–20% | Final evaluation, held out |

### 4.1 Split Strategy

```
Single dataset:
  Entire dataset → random stratified split → train.txt / val.txt / test.txt

Multiple datasets (recommended for ML):
  Dataset A (train)  →  no split needed (all train)
  Dataset B (val)    →  no split needed (all val)
  Dataset C (test)   →  no split needed (all test)
```

**Engineering Decision:** Split lists (`.txt` files) are preferred over separate directories. This enables multiple split strategies without duplicating files.

### 4.2 Split Criteria

| Criterion | Application |
|---|---|
| **Random** | General purpose |
| **By structure type** | Train on lines, test on contacts (domain shift evaluation) |
| **By parameter range** | Train on low noise, test on high noise (robustness) |
| **By seed** | Train on even seeds, test on odd seeds (determinism check) |

---

## 5. Dataset Manifest (dataset_index.json)

```
{
    "dataset": {
        "name": "semicon-synth-v1",
        "version": "1.0.0",
        "generation_date": "2026-07-30",
        "schema_version": "1.0"
    },
    "summary": {
        "n_samples_total": 10000,
        "n_success": 9997,
        "n_failed": 3,
        "image_format": "tiff",
        "image_bit_depth": 16,
        "image_dimensions_pixels": [1024, 1024],
        "pixel_size_nm": 1.0,
        "total_storage_mb": 25500,
        "structure_types": ["iso_line", "dense_ls", "contact"],
        "parameter_space": {
            "cd_nm": [20, 30, 50, 100],
            "height_nm": [50, 100],
            "ler_3sigma_nm": [0, 1.5, 2.4]
        }
    },
    "files": [
        {
            "sample_id": "iso_line_cd30_7a3b_9c1f",
            "image": "images/iso_line_cd30_7a3b_9c1f.tiff",
            "ground_truth": "ground_truth/iso_line_cd30_7a3b_9c1f.json",
            "metadata": "metadata/iso_line_cd30_7a3b_9c1f_metadata.json",
            "config": "metadata/iso_line_cd30_7a3b_9c1f_config.json",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb924..."
        }
    ],
    "splits": {
        "train": ["iso_line_cd30_7a3b_9c1f", ...],
        "val": ["iso_line_cd30_7a3b_d4e8", ...],
        "test": ["iso_line_cd30_7a3b_f6a2", ...]
    }
}
```

---

## 6. Comparison with Alternatives

| Organization Model | Pros | Cons | Verdict |
|---|---|---|---|
| **Flat (all samples in one directory)** | Simple | Unmanageable at scale | Rejected |
| **By structure type** | Clear grouping | Hard to maintain splits | Acceptable |
| **By structure type + seed** | Self-describing | Deep nesting | Acceptable |
| **Flat + index file (selected)** | Index is single source of truth; any grouping is possible | Requires index lookup | **Recommended** |

---

## Sources

- [D1] M. G. Creek et al., "Best Practices for Scientific Computing," *Nature Physics*, vol. 12, 2016.
- [D3] J. Lamprecht et al., "Towards FAIR Principles for Research Software," *Data Science*, vol. 3, 2020.
- [D4] Kaggle, "Dataset Specification Best Practices," 2023.
- Phase 4.2, Document 03 — Canonical data objects.
- Phase 4.3, Document 06 — Checkpoint and recovery.
