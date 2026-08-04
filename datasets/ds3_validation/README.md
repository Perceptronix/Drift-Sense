# DS3 — Validation Dataset

**Status:** READY TO POPULATE (post-implementation)

| Aspect | Value |
|---|---|
| Purpose | Milestone gates L1–L5, cross-module consistency |
| Size | 1,000 samples (100 × 10 structure types) |
| Image | 1024×1024, 16-bit, 1.0 nm/px |
| Master seed | 3003 |
| Expected volume | ~4 GB |
| Generation config | `generation_configs/ds3_validation.yml` |
| Validation gates | L1, L2, L3, L5 |
| Release criteria | L1–L5 pass; statistics report produced; cross-module invariants verified |

## Contents (populated by generator)

```
ds3_validation/
├── dataset_index.json
├── dataset_schema.txt
├── LICENSE                  (CC BY 4.0)
├── README.md
├── images/*.tiff
├── ground_truth/*.json, *_height.npy
├── metadata/*_config.json, *_metadata.json, *_timing.json
├── splits/train.txt, val.txt, test.txt
└── logs/
```

## Parameter Coverage (frozen)

| Parameter | Range | Sampling |
|---|---|---|
| CD | 10–500 nm | Stratified log |
| Height | 20–200 nm | Stratified |
| Pitch | 20–1000 nm | Stratified |
| LER 3σ | 0–5 nm | Stratified |
| LER ξ | 5–100 nm | Stratified |

## Generation Command (post-implementation)

```
semicon-sim batch --config ../generation_configs/ds3_validation.yml
semicon-sim --validate ds3_validation --level L5
```

No images exist yet — this directory is specified, not populated.
