# Reproducibility Strategy

**Research Phase:** 4.3
**Document:** 05_reproducibility_strategy.md
**Date:** 2026-07-30

---

## 1. Reproducibility Requirements

| Level | Requirement | Method |
|---|---|---|
| **Bitwise identical** | Same config + same seed → same output every time | Deterministic pipeline, seeded RNG, no floating-point non-determinism |
| **Cross-platform** | Same result on different OS/hardware | IEEE 754 compliance, deterministic reduction order |
| **Long-term** | Same result 1 year later | Version-pinned dependencies, config snapshot |
| **Traceable** | Every output identifies its generating config | Config snapshots embedded in metadata |

---

## 2. Seed Management

### 2.1 Hierarchical Seed Derivation

The seed manager uses a deterministic hierarchical scheme:

```
Master Seed (uint32, from config)
    │
    ├── hash(master, "geometry", geometry_config)
    │   └── Geometry Engine seed
    │
    ├── hash(master, "physics", physics_config)
    │   └── Physics Engine seed
    │
    └── hash(master, "variability", variability_config)
        └── Variability seed
            │
            ├── LER seed  = hash(variability_seed, "ler")
            ├── overlay seed = hash(variability_seed, "overlay")
            └── noise seed = hash(variability_seed, "noise")
```

For batch jobs, the structure-level seed is derived from the master seed and structure index:

```
master_seed = config.global.seed
for each structure s with parameters p_s, repetitions R_s:
    structure_seed = hash(master_seed, s, p_s)
    for r in 0..R_s-1:
        image_seed = hash(structure_seed, r)
```

**Inference:** The hierarchical scheme ensures that:
- Each image has a unique, deterministic seed
- Changing any parameter (config, structure, repetition) changes all downstream seeds
- Seeds are reproducible without storing them (only the master seed + config is needed)
- Adding a new structure to the beginning of a batch shifts all subsequent seeds (by design — avoids collisions)

### 2.2 Seed Storage

Each image's metadata records:

| Seed Field | Source |
|---|---|
| `master_seed` | Global config |
| `structure_seed` | Derived from master + structure params |
| `image_seed` | Derived from structure_seed + repetition |
| `ler_seed` | Derived from image_seed + "ler" |
| `overlay_seed` | Derived from image_seed + "overlay" |
| `noise_seed` | Derived from image_seed + "noise" |

---

## 3. Version Tracking

### 3.1 What Must Be Recorded

| Component | Recorded As | Precision |
|---|---|---|
| **Application version** | Git commit hash + tag | Exact commit |
| **Configuration** | Full config snapshot (resolved) | All parameters |
| **Structure library** | Library file hash | SHA-256 |
| **Material library** | Library file hash | SHA-256 |
| **Dependencies** | `pip freeze` or equivalent | Exact versions |
| **Platform** | OS, Python version, CPU | High-level |

### 3.2 How It Is Recorded

```
metadata.json (per image):
{
    "structure_name": "iso_line_cd30nm",
    "parameters": { ... full resolved config ... },
    "seed": { master_seed, structure_seed, image_seed, ... },
    "versions": {
        "application": "v0.2.0-rc1 (git: a1b2c3d)",
        "config_schema": "1.0.0",
        "library_version": "2026-07-30",
        "material_library_hash": "sha256:abc...",
        "python": "3.11.4",
        "dependencies": {
            "numpy": "1.25.2",
            "scipy": "1.11.1",
            ...
        },
        "platform": "Windows-11-10.0.26200-SP0"
    }
}
```

---

## 4. Configuration Snapshot

| When | What | Where |
|---|---|---|
| Before pipeline execution | Full resolved Config (not raw YAML) saved to file | `output_dir/config_snapshot.json` |
| After each image | Per-image metadata with parameters | `metadata.json` per image |
| At completion | Run summary with all parameters | `dataset_index.json` |

**Engineering Decision:** The config is snapshotted in its **resolved** form (all defaults applied, all references resolved) — not the raw user input. This eliminates ambiguity from default resolution.

---

## 5. Environment Recording

Environment recording captures the execution context without making reproducibility dependent on exact environment matching:

```
dataset_index.json:
{
    "run": {
        "timestamp": "2026-07-30T14:30:00Z",
        "duration_s": 142.3,
        "n_images_total": 1000,
        "n_images_success": 997,
        "n_images_failed": 3
    },
    "version": { ... application, dependencies, platform ... },
    "seed": { ... master seed structure ... },
    "config_snapshot_path": "config_snapshot.json"
}
```

---

## 6. Repeatability Verification

| Test | What It Checks | Frequency |
|---|---|---|
| **Self-test mode** | Pipeline runs with known config + fixed seed; output hash matches reference | Before each batch run (optional) |
| **Determinism test** | Run same config twice; outputs bit-identical | CI / nightly |
| **Regression test** | Run config from previous version; output hash matches or differences are documented | On version change |

---

## 7. Non-Reproducibility Risk Factors

| Factor | Risk | Mitigation |
|---|---|---|
| Floating-point associative non-determinism (parallel reduction) | Low | Fixed reduction order (serial summation, not parallel) |
| Hash randomization (Python 3.3+) | Low | PYTHONHASHSEED=0 for reproducibility mode |
| System RNG used instead of seeded RNG | Low | Config validation warns if seed = 0 |
| File system timestamps | None | Timestamps not used in computation |
| GPU non-determinism | None | GPU not used in initial implementation |

**Inference:** With the hierarchical seed manager, deterministic pipeline, and no GPU, the system achieves **bitwise reproducibility** across runs on the same platform and **numerical reproducibility** across platforms (IEEE 754 differences in the last ulp may occur).

---

## Sources

- [R5] J. K. Ousterhout, *A Philosophy of Software Design*, Yaknyam Press, 2018.
- [R7] D. E. Knuth, *The Art of Computer Programming, Vol. 2: Seminumerical Algorithms*, 3rd ed. Addison-Wesley, 1997.
- [R8] G. Marsaglia, "Xorshift RNGs," *J. Stat. Softw.*, vol. 8, 2003.
- [R9] D. Lemire, "Fast Random Integer Generation," *Software: Practice and Experience*, vol. 49, 2019.
- Phase 4.2, Document 05 — Configuration model.
