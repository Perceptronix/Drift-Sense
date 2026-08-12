# SEMICON 2026 Synthetic SEM Dataset Repository

**Applied Materials — Synthetic SEM Image Generator**
**Dataset Release Package — v1.0.0 (Specification)**

> **STATUS: RELEASE SPECIFICATION.** This directory contains the complete specification for generating the five production datasets. Images are generated **after implementation** using the certified simulator. No synthetic SEM images are present until then.

---

## Overview

Five datasets constitute the production portfolio (frozen in Phase 5.5, Document 05):

| Dataset | Purpose | Size | Master Seed | Expected Volume |
|---|---|---|---|---|
| **DS1** Development | Dev smoke tests, module debugging | 50 | 1001 | ~200 MB |
| **DS2** Unit-test | CI regression, golden hashes | 100 @512² | 2002 | ~100 MB |
| **DS3** Validation | Milestone gates L1–L5 | 1,000 | 3003 | ~4 GB |
| **DS4** Scientific-benchmark | L4 physics accuracy | 200 | 4004 | ~1 GB |
| **DS5** Final-training | ML/CD-SEM benchmark release | 100,000 | 5005 | ~400 GB |

---

## Generation Workflow

```
1. Implement simulator (Phases 5.1–5.4 blueprints)
2. Verify self-check + determinism (L5)
3. Load generation config: generation_configs/dsN_*.yml
4. Generate: semicon-sim batch --config dsN_*.yml
5. Validate: semicon-sim --validate <dataset>  (L1–L5)
6. Record checksums: checksums/SHA256SUMS
7. Release: tag version, archive, publish
```

---

## Dataset Layout (Canonical, per sample)

```
{dataset_name}/
├── dataset_index.json
├── dataset_schema.txt
├── LICENSE                    (CC BY 4.0)
├── README.md
├── images/*.tiff
├── ground_truth/*.json, *_height.npy, *_material.png, *_yields.npz
├── metadata/*_config.json, *_metadata.json, *_timing.json
├── splits/train.txt, val.txt, test.txt
└── logs/
```

---

## Licensing

All datasets are licensed under **CC BY 4.0** (Attribution). Please cite the SEMICON 2026 simulator when publishing.

---

## Directory Contents

| Path | Contents |
|---|---|
| `generation_configs/` | Frozen YAML generation templates (DS1–DS5) |
| `ds1_development/` … `ds5_final_training/` | Dataset output directories (populated after implementation) |
| `manifests/` | Sample-plan manifest schema + per-dataset manifest templates |
| `metadata/` | Metadata schemas + dataset-level metadata records |
| `checksums/` | SHA-256 registry template + verification script |
| `documentation/` | Dataset readme, ground-truth format, schema, validation spec, release notes |

---

## Reproducibility Guarantee

Same `generation_configs/dsN_*.yml` + pinned software versions + same platform → **bitwise identical dataset** (SHA-256 verified). Cross-platform bitwise equality is not guaranteed (documented tolerance).

---

*Generated 2026-07-30. Specification frozen by Phase 5.5 certification.*
