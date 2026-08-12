# DS2 — Unit-Test Dataset

**Status:** READY TO POPULATE (post-implementation)

| Aspect | Value |
|---|---|
| Purpose | CI regression, golden-reference pinning |
| Size | 100 samples (10 × 10 structure types) |
| Image | 512×512, 16-bit, 1.0 nm/px |
| Master seed | 2002 |
| Expected volume | ~100 MB |
| Generation config | `generation_configs/ds2_unit_test.yml` |
| Validation gates | L1, L2, L5 |
| Release criteria | Golden hashes match committed reference; CI green |

## Contents (populated by generator)

```
ds2_unit_test/
├── dataset_index.json
├── dataset_schema.txt
├── LICENSE                  (CC BY 4.0)
├── README.md
├── images/*.tiff
├── ground_truth/*.json
├── metadata/*_config.json, *_metadata.json
├── splits/
└── logs/
```

## Golden Hashes

Per-file SHA-256 hashes committed to `tests/data/reference_hashes.json` in the implementation repo. Regeneration must reproduce them bitwise (same platform).

## Generation Command (post-implementation)

```
semicon-sim batch --config ../generation_configs/ds2_unit_test.yml
```

No images exist yet — this directory is specified, not populated.
