# Metadata Schema Documentation

**Frozen:** Phase 4.4 doc 05; schemas in `datasets/metadata/*_schema.json`.

---

## Schema Files

| File | Scope |
|---|---|
| `sample_metadata_schema.json` | Per-sample metadata (7 categories) |
| `dataset_index_schema.json` | Dataset-level index + aggregate stats |
| `manifests/manifest_schema.json` | Sample-plan manifest |

---

## Per-Sample Metadata Categories

| Category | Purpose | Mandatory |
|---|---|---|
| **structure** | structure_type, cd_nm, pitch_nm, height_nm | ✅ |
| **process** | layer_stack, process_steps | ✅ |
| **variability** | ler_3sigma_nm, ler_xi_nm, overlay_dx/dy_nm, cdu_sigma_nm | ✅ |
| **physics** | beam_energy_keV, probe_current_pA, probe_diameter_nm, detector_config | ✅ |
| **seeds** | master_seed, sample_seed, stage_seeds | ✅ |
| **version** | app_version, git_hash, schema_version, material_library_hash | ✅ |
| **provenance** | generation_date, dataset_name, dataset_version, warnings | ✅ |

---

## Dataset-Level Index Fields

| Field | Content |
|---|---|
| dataset / version / schema_version | Identity |
| n_samples / n_success / n_failed | Counts |
| structure_distribution | Counts per type |
| parameter_ranges | Sampled coverage |
| rng_master_seed | Reproducibility anchor |
| splits | train/val/test sample lists |
| provenance | app version, git hash, config path |
| license | CC BY 4.0 |
| samples[] | per-sample status + file hashes |

---

## Provenance Requirements

- Same dataset + seed + platform → bitwise identical
- Cross-platform: documented tolerance, not enforced
- All hashes: SHA-256 hex (64 chars)

---

*Frozen in Phase 5.5; derived from Phase 4.4 doc 05.*
