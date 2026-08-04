# Engineering Conclusions

**Research Phase:** 4.4
**Document:** 07_engineering_conclusions.md
**Date:** 2026-07-30

---

## 1. Frozen Dataset Decisions

| # | Decision | Value | Justification |
|---|---|---|---|
| DD1 | **Directory hierarchy** | `images/`, `ground_truth/`, `metadata/`, `splits/`, `logs/`, `cache/` | Standard ML dataset layout |
| DD2 | **Naming convention** | `{type}_{param_hash}_{seed_hash}.ext` | Deterministic, self-describing |
| DD3 | **Dataset versioning** | Semver (major.minor.patch) | Industry standard for data |
| DD4 | **Splits** | Train/Validation/Test .txt files | Flexible, no file duplication |
| DD5 | **Manifest** | `dataset_index.json` with summary + per-sample entries | Single source of truth |
| DD6 | **Primary artifact** | SEM image (16-bit TIFF, LZW) | Standard microscopy format |
| DD7 | **Ground truth format** | JSON | Human-readable, universally parseable |
| DD8 | **GT edge maps** | Signed distance to nearest edge (nm) | Direct — enables any downstream metrology |
| DD9 | **GT CD values** | Top CD, bottom CD, height per feature | Complete metrology ground truth |
| DD10 | **GT contours** | Ordered point sequences in physical units | No pixel quantization artifacts |
| DD11 | **Seed metadata** | Full hierarchical chain (master → structure → image → stage) | Enables exact reproduction |
| DD12 | **Config snapshot** | Full resolved config per sample | Eliminates ambiguity |
| DD13 | **Version recording** | App version, git hash, schema version, library hashes | Complete provenance |
| DD14 | **Distribution** | `.tar.gz` archive of canonical directory tree | Universal access |
| DD15 | **License** | CC BY 4.0 | Permissive, requires attribution |
| DD16 | **Integrity** | SHA256SUMS per dataset | Verification |

---

## 2. Frozen Dataset Validation

| # | Check | Level | Method |
|---|---|---|---|
| V1 | File completeness | L1 | Scan files vs manifest |
| V2 | Metadata consistency | L2 | Cross-reference config ↔ metadata |
| V3 | Ground truth accuracy | L3 | GT edges match height field |
| V4 | Version compatibility | L4 | Schema version uniform |
| V5 | Reproducibility | L5 | Config + seed → same hash |

---

## 3. Frozen Artifact Priorities

| Priority | Artifact | Status |
|---|---|---|
| **P0** | SEM Image (.tiff) | ✅ Required |
| **P1** | Ground Truth (.json) | ✅ Required |
| **P1** | Configuration Snapshot (.json) | ✅ Required |
| **P1** | Metadata Record (.json) | ✅ Required |
| **P2** | Height Field (.npy) | ⚠️ Recommended |
| **P2** | Material Map (.png) | ⚠️ Recommended |
| **P3** | Yield Maps (.npz) | ❌ Optional |

---

## 4. Frozen Metadata Categories

| Category | Status | Key Fields |
|---|---|---|
| Structure | ✅ Required | type, cd_nm, height_nm, material, substrate |
| Geometry Process | ✅ Required | sidewall_angle, cd_bias, process_model |
| Variability | ✅ Required | ler_3sigma, ler_xi, ler_rho, overlay_xy |
| Physics | ✅ Required | beam_energy_keV, probe_current_pA, models |
| Seeds | ✅ Required | master → structure → image → stage chain |
| Version | ✅ Required | app version, git hash, schema version |
| Provenance | ✅ Required | timestamp, duration, warnings |

---

## 5. Frozen Dataset Organization

```
{dataset_name}/
├── dataset_index.json              ✅ Required (manifest)
├── dataset_schema.txt              ✅ Required (schema version)
├── LICENSE                         ✅ Required (CC BY 4.0)
├── README.md                       ✅ Required (documentation)
├── images/*.tiff                   ✅ Required (SEM images)
├── ground_truth/*.json             ✅ Required (labels)
├── metadata/*_config.json          ✅ Required (config snapshot)
├── metadata/*_metadata.json        ✅ Required (metadata record)
├── metadata/*_timing.json          ❌ Optional (timing)
├── ground_truth/*_height.npy       ⚠️ Recommended (height field)
├── ground_truth/*_material.png     ⚠️ Recommended (material map)
├── ground_truth/*_yields.npz       ❌ Optional (yield maps)
├── splits/train.txt                ✅ Required (train list)
├── splits/val.txt                  ✅ Required (validation list)
├── splits/test.txt                 ✅ Required (test list)
├── logs/                           ❌ Optional (generation logs)
└── SHA256SUMS                      ✅ Required (integrity checksums)
```

---

## Sources

- Phase 4.2, Document 03 — Canonical data objects.
- Phase 4.3, Document 06 — Checkpoint and recovery.
- Phase 4.1, Document 06 — Repository organization.
- [D1] Creek et al., "Best Practices for Scientific Computing," *Nature Physics*, 2016.
- [D3] Lamprecht et al., "Towards FAIR Principles," *Data Science*, 2020.
