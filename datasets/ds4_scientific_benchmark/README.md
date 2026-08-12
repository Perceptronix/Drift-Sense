# DS4 — Scientific-Benchmark Dataset

**Status:** READY TO POPULATE (post-implementation)

| Aspect | Value |
|---|---|
| Purpose | L4 scientific validation, physics accuracy vs published values |
| Size | 200 samples (20 × 10 structure types) |
| Image | 1024×1024, 16-bit, 1.0 nm/px |
| Master seed | 4004 |
| Expected volume | ~1 GB (includes yield maps) |
| Generation config | `generation_configs/ds4_scientific_benchmark.yml` |
| Validation gates | L1, L2, L3, L4 |
| Release criteria | L4 scientific targets met (see table) |

## Contents (populated by generator)

```
ds4_scientific_benchmark/
├── dataset_index.json
├── dataset_schema.txt
├── LICENSE                  (CC BY 4.0)
├── README.md
├── images/*.tiff
├── ground_truth/*.json
├── yields/*.npz             ← SE/BSE yield maps (extra artifact)
├── metadata/*_config.json, *_metadata.json
├── splits/
└── logs/
```

## L4 Scientific Targets

| Metric | Target |
|---|---|
| Si SE yield (1 keV) | δ ∈ [0.4, 0.8] |
| Si BSE yield (1 keV) | η ∈ [0.15, 0.25] |
| Material contrast | Cu SE < Si SE; W BSE > Cu BSE > Si BSE |
| CD accuracy | ± 0.1 nm |
| LER 3σ | ± 0.3 nm |
| PSF FWHM | ± 1% |
| Edge brightening | ± 0.5% |

## Material Stacks (frozen)

Si-only; Si–SiO₂–SiN; Si–Cu; Si–W; PR-on-Si.

## Generation Command (post-implementation)

```
semicon-sim batch --config ../generation_configs/ds4_scientific_benchmark.yml
semicon-sim --validate ds4_scientific_benchmark --level L4
```

No images exist yet — this directory is specified, not populated.
