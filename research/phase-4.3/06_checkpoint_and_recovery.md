# Checkpoint and Recovery

**Research Phase:** 4.3
**Document:** 06_checkpoint_and_recovery.md
**Date:** 2026-07-30

---

## 1. Checkpoint Philosophy

| Principle | Description |
|---|---|
| **Per-structure granularity** | Checkpoints are written after each complete structure/image, not within a pipeline |
| **Recovery = restart from last completed job** | Failed batch resumes from the last successfully written output |
| **No intra-pipeline checkpoints** | A single pipeline run (∼2 s) does not justify the overhead of intermediate checkpointing |
| **Checkpoint is the output itself** | A successfully written image file IS a checkpoint — no separate checkpoint file needed |

**Engineering Decision:** Checkpoint granularity = one completed image. If a pipeline run fails, the failure is recorded and the next job begins. The completed set is all images with successful output files.

---

## 2. Checkpoint Model

```
Before execution:
    job_manifest.json  ← all jobs to run

During execution:
    output_dir/images/image_0000.tiff  ← written atomically
    output_dir/images/image_0001.tiff
    output_dir/images/image_0002.tiff  ← (incomplete — if worker crashes)

After execution:
    dataset_index.json  ← aggregated from all output metadata
    failed_jobs.json    ← any jobs that did not complete
```

**The checkpoint set = files present in the output directory.**

---

## 3. Restart Strategy

### 3.1 Normal Restart (From Manifest)

```
1. Check for existing job_manifest.json
2. If found:
   a. Scan output directory for existing image files
   b. Compare completed set against manifest
   c. Subtract completed jobs from work queue
   d. Run only pending jobs
3. If not found:
   a. Start fresh (generate new manifest)
```

### 3.2 Resume After Failure

```
1. Read failed_jobs.json (or scan for missing files)
2. List all jobs with status != COMPLETED
3. Re-attempt up to max_retries times
4. Report final counts: total, completed, failed
```

### 3.3 Crash Recovery

```
System crash during execution:
1. On restart, check for job_manifest.json
2. Files written before crash → preserved
3. Files being written during crash → incomplete (corrupted)
4. Incomplete files detected by:
   a. Missing EoF marker in image file
   b. File size smaller than expected
5. Remove incomplete files and re-run those jobs
```

---

## 4. Failure Classification

| Failure Type | Examples | Recovery |
|---|---|---|
| **Transient** | Temporary disk full, I/O error, network timeout | Retry (up to 3×) |
| **Persistent** | Config error, missing library entry, invalid parameters | Abort that job; continue batch |
| **Fatal** | No disk space, config file corrupt, missing dependency | Abort entire run |
| **Unknown** | Worker crash without error | Detect missing output → retry |

---

## 5. Failure Handling in Workers

```
worker_pipeline(structure, seed):
    try:
        config = build_config(structure, seed)
        height_field = process_model(config.pixel_mask, config.layer_stack)
        height_field_var = variability_engine(height_field, config.variability)
        yield_maps = signal_generator(height_field_var, config.physics)
        yield_degraded = degradation_model(yield_maps, config.degradation)
        image = image_former(yield_degraded, config.detector)
        metadata = build_metadata(config, seed)
        writer.write(image, metadata)
        return SUCCESS
    except ImageWriter.WriterError as e:
        logger.warning(f"Write failed for {structure}: {e}")
        if e.transient:
            return RETRY
        return FAILED
    except Config.ConfigError as e:
        logger.error(f"Config error for {structure}: {e}")
        return FAILED (no retry — persistent)
    except Exception as e:
        logger.error(f"Unexpected error for {structure}: {e}")
        return FAILED
```

---

## 6. Checkpoint File Structure

```
output_dir/
├── job_manifest.json          ← Complete job description (written before execution)
├── config_snapshot.json       ← Resolved configuration
├── failed_jobs.json           ← Jobs that failed (updated during execution)
├── images/
│   ├── image_0000.tiff        ← Per-image output
│   ├── image_0000_metadata.json
│   ├── image_0001.tiff
│   ├── image_0001_metadata.json
│   └── ...
├── ground_truth/
│   ├── gt_0000.json           ← Ground truth (if enabled)
│   └── ...
├── logs/
│   ├── run_2026-07-30_143000.log
│   ├── worker_0.log
│   ├── worker_1.log
│   └── ...
└── dataset_index.json          ← Final index (written at completion)
```

---

## 7. Storage Requirements for Checkpoint Data

| Component | Per Image | 10,000 Images |
|---|---|---|
| Image (TIFF, 16-bit, 1024×1024) | 2 MB | 20 GB |
| Metadata (JSON) | 4 KB | 40 MB |
| Ground truth (JSON) | 10–50 KB | 100–500 MB |
| Worker logs | 1 KB | 10 MB |
| Job manifest | — | < 1 MB |
| Dataset index | — | < 1 MB |

**Inference:** A 10,000-image dataset requires approximately 20–25 GB of storage for images + metadata. Ground truth adds 0.1–0.5 GB.

---

## Sources

- [R1] I. Foster, *Designing and Building Parallel Programs*, Addison-Wesley, 1995.
- [R10] W. Gropp et al., *Using MPI*, 3rd ed. MIT Press, 2014.
- [R11] P. Brinch Hansen, "Distributed Processes: A Concurrent Programming Concept," *CACM*, 1978.
- Phase 4.1, Document 03 — Module decomposition.
- Phase 4.2, Document 03 — Data objects (Metadata specification).
