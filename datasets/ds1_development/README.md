# DS1 — Development Dataset

**Status:** READY TO POPULATE (post-implementation)

| Aspect | Value |
|---|---|
| Purpose | Development smoke tests, module debugging |
| Size | 50 samples (5 × 10 structure types) |
| Image | 1024×1024, 16-bit, 1.0 nm/px |
| Master seed | 1001 |
| Expected volume | ~200 MB |
| Generation config | `generation_configs/ds1_development.yml` |
| Validation gates | L1, L2 |
| Release criteria | All 50 valid; index consistent; determinism spot-check |

## Contents (populated by generator)

```
ds1_development/
├── dataset_index.json
├── dataset_schema.txt
├── LICENSE                  (CC BY 4.0)
├── README.md                (from documentation/dataset_readme_template.md)
├── images/*.tiff
├── ground_truth/*.json
├── metadata/*_config.json, *_metadata.json
├── splits/
└── logs/
```

## Generation Command (post-implementation)

```
semicon-sim batch --config ../generation_configs/ds1_development.yml
```

No images exist yet — this directory is specified, not populated.
