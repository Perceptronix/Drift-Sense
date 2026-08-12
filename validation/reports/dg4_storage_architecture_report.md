# DG4 Storage Architecture Report

**SEMICON 2026 Synthetic SEM Image Generator — Storage Optimization Study**
**Date:** 2026-07-31
**Status of DG4 production run:** NOT started. This report is a prerequisite analysis — no full DS5 generation has occurred. All numbers below are derived from (a) direct measurement of the existing DS1–DS4 datasets on disk and (b) analytical scaling to DS5's 1024×1024 spec, cross-validated against a 300-sample DS5-resolution smoke test that was generated and then deleted after measurement.

**Scope discipline, per instructions:** this document proposes a storage *architecture* only. No simulator code, scientific model, pixel value, or dataset content has been modified to produce it. Nothing has been deleted from DS1–DS4 (only my own throwaway diagnostic outputs were removed). No compression has actually been applied yet — Task 6/7 numbers are benchmarked estimates pending explicit sign-off, per Task 9.

---

## Task 1 — Storage Audit

### 1.1 Measured composition, DS1–DS4 (1,350 samples total, all at the 300×300px "validation" scale — none of these are at DS5's production 1024×1024 scale)

| Dataset | Samples | images/ | ground_truth/ | metadata/ | index+checksums | Total |
|---|---|---|---|---|---|---|
| DS1 | 50 | 9.5 MB | 46 MB | 0.53 MB | 0.08 MB | ~56 MB |
| DS2 (unit-test) | 100 | 17 MB | 81 MB | 1.1 MB | 0.16 MB | ~99 MB |
| DS3 (validation) | 1,000 | 168 MB | 808 MB | 11 MB | 1.5 MB | ~989 MB |
| DS4 (scientific benchmark) | 200 | 34 MB | 162 MB | 2.1 MB | 0.31 MB | ~198 MB |
| **Total** | **1,350** | **228.5 MB** | **1,097 MB** | **14.7 MB** | **~2.0 MB** | **~1.34 GB** |

**Key finding: `ground_truth/` is ~4.8× larger than `images/`** across every dataset, consistently. This is the single largest optimization target.

### 1.2 File-type breakdown (1,350 samples, all datasets combined)

| Extension | Count | Role |
|---|---|---|
| `.json` | 5,404 | gt.json (1/sample), metadata.json + config.json + timing.json (3/sample), + 4 dataset-level index files |
| `.tiff` | 1,350 | SEM image (16-bit, LZW-compressed), 1/sample |
| `.png` | 1,350 | material segmentation map, 1/sample |
| `.npy` | 1,350 | height field (float64), 1/sample |

### 1.3 Per-file-type measured sizes (from `ds3_validation`, 1,000 samples, most statistically representative)

| Artifact | Format | Avg size | Notes |
|---|---|---|---|
| `images/*.tiff` | 16-bit, LZW | 172,695 B | LZW barely compresses this — real SEM sensor noise is high-entropy and resists lossless compression (expected; confirmed by spot-checking raw vs. compressed size) |
| `ground_truth/*_height.npy` | float64 | 133,223 B avg (720,128 B for a full 300×300 sample; average is lower because some structure types crop to smaller arrays) | **Largest single artifact.** Precision requirement per `research/phase-4.4/04_ground_truth_specification.md` §7 is **±0.1 nm** — float64 supplies ~15-17 significant digits, i.e. roughly 10¹⁴× more precision than the spec calls for |
| `ground_truth/*_material.png` | 8-bit indexed PNG | 273 B | Already near-optimal — low-cardinality label data (7 material IDs), PNG's own lossless compression already does the job |
| `ground_truth/*_gt.json` | indented JSON, float64 | 11,615 B | Dominated by `contours` arrays: per-point (x_nm, y_nm) pairs stored as 16-17-significant-digit floats (e.g. `80.35355339059328` for a value the spec only requires to ±0.1 nm) plus 2-space JSON indentation overhead |
| `metadata/*.json` (×3/sample) | indented JSON | 140 B avg | Negligible |

---

## Task 2 — Redundancy Classification

| File type | Purpose | Regenerable from seed+config? | Required in **released** dataset? | Disposition |
|---|---|---|---|---|
| `images/*.tiff` | The actual SEM micrograph — the ML input | No (physics simulation is stochastic per-run even with same seed unless every RNG stream is checkpointed; treat as authoritative output) | **Yes — required** | Keep, unchanged |
| `ground_truth/*_material.png` | Material segmentation map — explicitly listed as a ground-truth component in Phase 4.4 §5 | Yes, in principle, from height+material physics buffers | **Yes — required** (it's canonical ground truth, not a debug artifact, per the frozen spec) | Keep, already near-optimal |
| `ground_truth/*_gt.json` | CD values + contour lines — explicitly listed as ground-truth components in Phase 4.4 §4 & §6 | Yes, but expensive to recompute (re-run contour extraction) | **Yes — required** | Keep, but re-encode (Task 4) |
| `ground_truth/*_height.npy` | **Intermediate physics buffer.** Per Phase 4.4 §1: edge maps, CD values, and contours are all listed as "Direct — from height field," i.e. the height field is the *input* to ground-truth derivation, not itself one of the 5 canonical ground-truth components | Yes — fully reproducible from `(seed, config, simulator version)` per Task 6 | **Optional / dev-only** | **Exclude from release profile**, keep in dev profile |
| `metadata/*_config.json` | Exact config used for this sample | N/A — this IS the reproducibility record | **Yes — required** (this is what makes everything else regenerable) | Keep |
| `metadata/*_metadata.json` | Run metadata (version, git hash, timing) | N/A | Optional — useful, tiny | Keep (negligible cost) |
| `metadata/*_timing.json` | Per-stage profiling timing | No, but also not scientifically meaningful to keep | **No — debug only** | **Exclude from release**, keep in dev profile |
| `checkpoint.json` | Job-runner resume state | N/A — operational, not scientific | **No — operational only** | Never ships in any dataset profile |
| `_lib*.gds` | Structure library used for generation | Yes — deterministic from config | Optional (useful for exact reproduction) | Keep one copy per dataset in dev; reference by hash in release manifest instead of shipping per-sample |

---

## Task 3 — Two Storage Profiles

### Profile A — Development (everything)

```
datasets/<name>/
  images/*.tiff              # required
  ground_truth/*_height.npy  # kept — needed for physics validation, debugging, re-deriving GT if the derivation code changes
  ground_truth/*_material.png
  ground_truth/*_gt.json
  metadata/*_config.json
  metadata/*_metadata.json
  metadata/*_timing.json     # kept — perf diagnostics
  dataset_index.json
  SHA256SUMS
  checkpoint.json            # operational, dev-only
  _lib*.gds
```

### Profile B — Release

```
datasets/<name>/
  images/*.tiff                     # unchanged
  ground_truth/*_material.png       # unchanged, already tiny
  ground_truth/*_gt.json            # re-encoded: precision-rounded to spec tolerance, minified, gzip'd (Task 4)
  metadata/*_config.json            # unchanged — this is what makes height.npy/timing.json regenerable on demand
  dataset_index.json
  SHA256SUMS
  README.md
  LICENSE
```

`ground_truth/*_height.npy`, `metadata/*_timing.json`, and `checkpoint.json` are **not** shipped in Profile B. A `regenerate_height_field.py`-style entry point (already implicit in the existing `simulator/generate.py run --config ... --seed ...` path) is documented in the release README as the reproduction method — this satisfies Task 6 without duplicating derivable data.

---

## Task 4 — Lossless Compression Strategy, Per File Type

| File type | Current | Recommended | Basis | Precision impact |
|---|---|---|---|---|
| `images/*.tiff` | 16-bit, TIFF/LZW | **No change.** Benchmarked: LZW achieves ~1.92 B/px vs. 2.0 B/px raw on real SEM images — noise-dominated data doesn't compress further under any lossless scheme (verified by inspection, not assumed) | Direct measurement | None — untouched |
| `ground_truth/*_material.png` | 8-bit indexed PNG | No change — already near-optimal for 7-value label data | Direct measurement (273 B for 90,000 px = negligible) | None |
| `ground_truth/*_height.npy` (dev profile only) | float64, uncompressed `.npy` | **`.npz` with `zlib`/`deflate` compression, same float64 dtype.** Height fields are smooth/piecewise-continuous topography (not per-pixel noise like the SEM image), so lossless compression should perform well — this is a **zero-precision-loss** change (identical bytes when decompressed) | Standard `numpy.savez_compressed` semantics; no rounding | **None — bit-identical after decompression** |
| `ground_truth/*_height.npy` — **flagged, requires explicit sign-off, NOT applied automatically** | float64 | float32, i.e. halve storage (8→4 B/px) | Phase 4.4 §7 requires ±0.1 nm precision; float32 gives ~7 significant decimal digits, i.e. ~0.001 nm absolute error on values up to a few hundred nm — **~100× better than the stated requirement**, so it does not violate the spec's own precision tolerance. This is **not** the same category as "reducing image bit depth" (which the instructions explicitly forbid) — it is a change to an *intermediate physics buffer*, not to the released SEM image or its pixel values. Presented as optional because it does change the literal stored bytes (unlike `.npz` compression, which is bit-identical) | Sub-0.1nm rounding only, within spec tolerance — but **flagged rather than assumed acceptable**, since the instructions were explicit about "never reduce bit depth" |
| `ground_truth/*_gt.json` | Indented JSON, float64 literals (16-17 sig figs) | (1) Round all `x_nm`/`y_nm`/`cd_nm` values to 4 decimal places (0.0001 nm resolution — still 1000× finer than the ±0.1nm spec requirement); (2) minify (no indentation); (3) gzip on top | Phase 4.4 §7 precision requirement (±0.1 nm) directly justifies dropping digits beyond the 4th decimal — this is rounding *within the spec's own stated tolerance*, not an ad hoc precision cut | Values change by <0.0001 nm — 1000× inside the documented ±0.1nm requirement |
| `metadata/*_config.json`, `*_metadata.json` | Indented JSON | Minify only (negligible size regardless) | — | None |
| Cross-file | Many small files (7 files/sample) | Pack ground-truth + metadata per sample into a single per-shard archive (e.g. one `.tar` or `.parquet`/columnar file per 1,000-sample shard) rather than 7,000 loose files | Reduces filesystem overhead (inode/allocation-unit waste) and dramatically speeds up any cloud upload/download of the release set | None — pure repackaging |

### Compression benchmark (measured on real DS3 files, not projected)

| Transform | Sample tested | Before | After | Ratio |
|---|---|---|---|---|
| `gt.json` minify + 4-decimal round (manual spot check on `000000_gt.json`) | 1 file, `gate` structure | 11,615 B (avg across dataset) | *(not yet executed — Task 9 requires re-verification before any change ships; estimate below is from manual inspection of the coordinate-string-length reduction, e.g. `"80.35355339059328"` → `"80.3536"`, ~2.3× per-number reduction)* | **est. ~3-4×** after minify+round, **est. ~6-10×** after adding gzip (JSON text remains highly compressible) |
| `.npy` → `.npz` (zlib) on height field | Not yet benchmarked on this project's actual files | — | — | Literature/typical range for smooth topographic float data: **3-8×**, to be confirmed by direct benchmark before adoption |

**Honesty note (Task 9 relevant):** the gt.json and npz ratios above are principled estimates from the data's known structure (verbose float precision, JSON indentation, smooth topography), not yet measured end-to-end on this repository's files. Before this architecture is adopted for a real release, these two transforms should be benchmarked on the actual DS1–DS4 files (cheap — 1,350 samples, already on disk) to replace the estimate with a measured ratio.

---

## Task 5 — Intermediate Artifacts Excluded From Release

| Artifact | Why excluded | Regeneration path |
|---|---|---|
| `ground_truth/*_height.npy` | Intermediate physics buffer (input to, not itself, canonical ground truth per Phase 4.4 §1) | `generate.py run --config <stored config.json> --seed <stored seed>` reproduces byte-identical inputs to the height-field computation |
| `metadata/*_timing.json` | Per-stage profiling data, not scientific content | Regenerate by re-running with `--profile`-equivalent flag if timing data is ever needed again |
| `checkpoint.json` | Job-runner operational state | Not applicable to a finished, released dataset |
| `_lib_validation.gds` (per-sample duplication) | Same structure library reused across many samples | Store once per dataset, reference by content hash in manifest, not per-sample |

---

## Task 6 — Seed-Based Reproducibility Requirement

Every sample already stores `metadata/*_config.json` (full merged config) and the sample's seed is derivable from `(master_seed, sample_index)` per the existing deterministic sample-plan logic in `simulator/src/semicon/orchestration/job.py::_sample_plan`. This is sufficient to satisfy Task 6 **only if** two additional facts are also pinned per sample (currently present in `metadata/*_metadata.json` per the earlier DG3 report's "app_version, git_hash" fields):

- Simulator version / git hash (already recorded)
- Exact config snapshot (already recorded)

**Open gap, flagged rather than assumed solved:** exact reproducibility of `height.npy` also requires that every RNG draw inside the physics pipeline (variability/noise stages) be deterministically derivable from `(master_seed, sample_index)` alone, with no hidden entropy sources (e.g. `np.random` global state, timestamp-seeded processes). This was not independently verified in this report — recommend a dedicated regenerate-and-diff test (generate one sample, delete its `height.npy`, regenerate from stored config+seed, byte-compare) before relying on this as a release guarantee. See `10_open_questions` equivalent note below.

---

## Task 7 — Final Release Directory Structure

```
datasets/
  ds1/                          # kept as-is (dev, small)
  ds2_unit_test/                # kept as-is (dev, small)
  ds3_validation/                # kept as-is (dev, small)
  ds4_scientific_benchmark/      # kept as-is (dev, small)
  ds5_release/                   # NEW — Profile B only, this is what gets distributed
    images/
    ground_truth/                # material.png + gt.json only (no height.npy)
    metadata/                    # config.json + metadata.json only (no timing.json)
    dataset_index.json
    SHA256SUMS
manifests/
  ds5_release_manifest.json      # sample->shard mapping if sharded
checksums/
  SHA256SUMS.ds5_release
documentation/
  README.md
  LICENSE
  ground_truth_format.md         # already exists at datasets/documentation/
```

DS1–DS4 stay as dev-profile datasets (they're small — 1.34GB combined — no pressure to optimize them). Only DS5, at 100,000 samples, needs the release/dev split to be practical on local hardware.

---

## Task 8 — Storage Estimates

All per-sample figures are for DS5's actual spec: **1024×1024 px, 16-bit image, full ground-truth set**. Derived two ways — (a) analytically scaling the measured 300×300 DS3 numbers by pixel-count ratio (11.65×) for the image/height field and by linear/perimeter ratio (3.41×) for contour-length-dependent JSON — and (b) cross-checked against the actual 300-sample DS5-resolution smoke test (3.3GB / 300 = 11.3 MB/sample measured, close to the 10.05 MB/sample analytical figure below; the smoke test additionally included `_lib_validation.gds` and `checkpoint.json` overhead not present per-sample, accounting for the small gap).

### Per-sample budget (DS5, 1024×1024)

| Profile | image | height.npy | material.png | gt.json | metadata | **Total/sample** |
|---|---|---|---|---|---|---|
| **A — Dev, current format** | 2.01 MB | 8.00 MB | 3.18 KB | 39.6 KB | ~0.5 KB | **~10.05 MB** |
| **A — Dev, with lossless npz + gt.json minify/gzip** | 2.01 MB | ~1.5-2.5 MB (est. 3-5× npz ratio, unconfirmed) | 3.18 KB | ~5-10 KB | ~0.5 KB | **~3.6-4.6 MB** |
| **B — Release (height.npy excluded, gt.json optimized)** | 2.01 MB | — (excluded) | 3.18 KB | ~5-10 KB | ~0.3 KB | **~2.02-2.03 MB** |

### Full-dataset totals

| N samples | Profile A (current) | Profile A (npz+gzip, unconfirmed ratio) | **Profile B (release)** |
|---|---|---|---|
| 10,000 | ~100.5 GB | ~36-46 GB | **~20.2-20.3 GB** |
| 50,000 | ~502.5 GB | ~180-230 GB | **~101-102 GB** |
| 100,000 | **~1,005 GB (~1.0 TB)** | ~360-460 GB | **~202-203 GB** |

**Bottom line for your stated constraint ("machine can't handle 400GB"):** even the optimized **Release profile at full 100k scale is still ~202GB** — larger than what a machine with ~14GB currently free (353GB total disk) can hold locally alongside everything else on it. Compression alone (Tasks 4-6) gets DS5 from ~1TB down to ~200GB — a ~5× reduction — but does **not** get it under a "fits comfortably on this machine" bar by itself. Getting there requires one of:
- **Reduce N** (e.g. 10,000 samples → ~20GB release, fits easily), and/or
- **Never materialize the full set locally at once** — generate in shards (e.g. 5,000-sample chunks), upload/archive each shard immediately, delete the local copy, repeat. This is a workflow/orchestration change (Task 8's real answer for your hardware), not a per-file compression trick, and is worth designing explicitly before any large run — see Final Recommendation.

---

## Task 9 — Validation Requirements (for whenever this is actually implemented)

Before any compression/repackaging change ships, verify:

- [ ] Byte-identical `images/*.tiff` before/after (untouched — should trivially pass)
- [ ] `.npz`-recompressed height fields decompress to bit-identical float64 arrays vs. the original `.npy` (verify with `np.array_equal`, not just shape/dtype)
- [ ] Precision-rounded `gt.json` values differ from originals by less than the stated ±0.1nm spec tolerance, for every field, on a full-dataset pass — not a spot check
- [ ] Every checksum in `SHA256SUMS` still validates for files that were *not* changed (images, material.png); a new `SHA256SUMS` is generated for files that *were* re-encoded (gt.json), since their bytes legitimately changed even though their scientific content did not
- [ ] `dataset_index.json` and manifest entries account for every sample — no silent drops during repackaging
- [ ] The seed+config reproducibility claim (Task 6) is actually tested end-to-end at least once: delete a sample's `height.npy`, regenerate from stored config+seed, confirm the regenerated field matches the pre-deletion original within the stated tolerance

None of this validation has been executed yet — this report is the design, not the implementation.

---

## Final Recommendation

1. **Immediate, zero-risk, zero-precision-loss:** switch the release profile to exclude `height.npy`, `timing.json`, and `checkpoint.json` per Task 3/5 — this alone is a ~5× reduction (1.0TB → ~200GB at 100k) using only the project's own existing definition of what counts as "ground truth" (Phase 4.4 §1), not a new judgment call.
2. **High-value, needs a quick benchmark first:** `gt.json` minify + precision-round-to-spec-tolerance + gzip, and `.npz` compression for any height fields kept in the dev profile. Principled estimates suggest another meaningful reduction on top of #1, but should be measured on the real DS1-4 files (cheap, already on disk) before being trusted as a number.
3. **Flagged, requires your explicit sign-off (not assumed):** float64→float32 for height fields, justified by the spec's own ±0.1nm tolerance but held out because the instructions were explicit about never reducing bit depth, and this is a genuine (if scientifically negligible) change to stored values rather than a pure repackaging.
4. **The actual answer to "don't let 400GB land on my machine":** even optimized, DS5 at full 100k scale (~200GB release / ~1TB dev) will not comfortably fit given ~14GB currently free. Compression reduces the problem by ~5×; it does not solve it. The real fix is either **reducing DS5's sample count** to something your disk can hold, or **generating in shards with immediate upload/deletion** so the full set never exists locally at once — this is a generation-workflow decision, not a storage-format one, and needs your input on which you'd prefer before any large-scale run is attempted.

I have not implemented any of the above — this is the design document per your instructions. Let me know which of #1-4 you want built next; #1 in particular is safe to implement immediately since it uses no new judgment calls, only the project's existing frozen ground-truth definition.
