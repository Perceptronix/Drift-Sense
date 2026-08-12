# DS5 — Final-Training Dataset

**Status:** READY TO POPULATE (post-implementation)

| Aspect | Value |
|---|---|
| Purpose | Primary deliverable — ML/CD-SEM benchmarking dataset |
| Size | 100,000 samples @1024×1024 |
| Image | 1024×1024, 16-bit, 1.0 nm/px |
| Master seed | 5005 |
| Expected volume | ~400 GB |
| Generation config | `generation_configs/ds5_final_training.yml` |
| Validation gates | L1, L2, L3, L4 (sampling), L5 |
| Release criteria | All gates pass; benchmark-readiness review; **stakeholder sign-off on structure weighting** |

## Structure Weighting (pending stakeholder review)

| Structure | Weight | Count |
|---|---|---|
| dense_ls | 20.0% | 20,000 |
| contact | 15.0% | 15,000 |
| via | 10.0% | 10,000 |
| iso_line | 15.0% | 15,000 |
| fin | 10.0% | 10,000 |
| gate | 10.0% | 10,000 |
| trench | 8.0% | 8,000 |
| sti | 5.0% | 5,000 |
| bimaterial | 4.0% | 4,000 |
| pitch_std | 3.0% | 3,000 |

## Splits (frozen, deterministic)

| Split | Count | Fraction |
|---|---|---|
| Train | 70,000 | 70% |
| Validation | 15,000 | 15% |
| Test | 15,000 | 15% |

Stratified by structure type; disjoint sample sets (no leakage).

## Contents (populated by generator)

```
ds5_final_training/
├── dataset_index.json
├── dataset_schema.txt
├── LICENSE                  (CC BY 4.0)
├── README.md
├── images/*.tiff
├── ground_truth/*.json
├── metadata/*_config.json, *_metadata.json
├── splits/train.txt, val.txt, test.txt
└── logs/
```

## Generation Command (post-implementation)

```
semicon-sim batch --config ../generation_configs/ds5_final_training.yml
semicon-sim --validate ds5_final_training --level L5
```

No images exist yet — this directory is specified, not populated.
