# Engineering Conclusions

**Research Phase:** 4.3
**Document:** 08_engineering_conclusions.md
**Date:** 2026-07-30

---

## 1. Frozen Runtime Decisions

| # | Decision | Value | Justification |
|---|---|---|---|
| RD1 | **Execution model** | Single-process sequential per image; multiprocessing worker pool for batch | Embarrassingly parallel workload |
| RD2 | **Pipeline lifecycle** | 10 phases (Startup → Config → Resources → Job Expansion → Pipeline → Validation → Finalize → Export → Shutdown) | Complete, ordered lifecycle |
| RD3 | **Scheduling** | Static pool for uniform batch; dynamic pool for sweeps | Matches workload characteristics |
| RD4 | **Worker parallelism** | Independent samples only; one structure per worker | No shared state → no synchronization |
| RD5 | **Within-pipeline parallelism** | M4 and M7 are independent consumers of M3 output → can run concurrently | Only safe intra-pipeline parallelism |
| RD6 | **GPU acceleration** | Not required for initial implementation | Per-stage CPU overhead is acceptable |
| RD7 | **Reproducibility model** | Hierarchical seed manager; version-pinned dependencies; config snapshot per run | Bitwise reproducibility on same platform |
| RD8 | **Checkpoint granularity** | Per-image (output file itself is the checkpoint) | No overhead for image-level checkpointing |
| RD9 | **Recovery** | Resume from last completed image; retry transient failures (max 3×) | Simple, reliable |
| RD10 | **Logging** | Structured JSON logging; three channels (progress, logs, telemetry) | Machine-parseable + human-readable |
| RD11 | **Progress reporting** | Three levels (minimal, normal, verbose) | Adapts to user need |
| RD12 | **Caching** | Deterministic height fields only; cache key = hash(input_params) | Meaningful speedup for repeated structures with different seeds |
| RD13 | **Self-check mode** | Minimal pipeline with fixed seed; output hash compared to reference | Quick (<5 s) system integrity test |

---

## 2. Frozen Configuration Additions

| Parameter | Section | Default | Description |
|---|---|---|---|
| `worker_count` | execution | `min(4, cpu_count())` | Parallel workers |
| `max_retries` | execution | 0 | Retries per failed job |
| `fail_fast` | execution | false | Abort on first failure |
| `enable_cache` | execution | true | Enable height field cache |
| `progress_level` | execution | "normal" | "minimal", "normal", "verbose" |
| `self_check` | execution | false | Run self-check before batch |

---

## 3. Frozen Reproducibility Chain

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       REPRODUCIBILITY CHAIN                                  │
│                                                                             │
│  Config Snapshot (resolved JSON)                                            │
│  ├── Contains: all parameters, expanded defaults, resolved references      │
│  └── Hash: SHA-256(config_snapshot)                                         │
│                                                                             │
│  Master Seed (uint32 from config)                                           │
│  └── Hierarchical derivation:                                               │
│       seed_structure = hash(master_seed, structure_index, structure_params) │
│       seed_image  = hash(seed_structure, repetition)                       │
│       seed_ler    = hash(seed_image, "ler")                                │
│       seed_noise  = hash(seed_image, "noise")                              │
│       seed_overlay= hash(seed_image, "overlay")                            │
│                                                                             │
│  Version Pinning (all dependencies recorded)                                │
│  ├── Application: git commit hash                                           │
│  ├── Python: major.minor.patch                                              │
│  └── Libraries: pip freeze output                                          │
│                                                                             │
│  Output Metadata (per image)                                                │
│  ├── Full image seed chain                                                  │
│  ├── Applied parameters (sub-sampled from config snapshot)                  │
│  └── Version information                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Frozen Monitoring Model

| Channel | Format | Medium | Content |
|---|---|---|---|
| Progress | Single line, updated in place | Console (stdout) | Counters, ETA, rate |
| Logging | Structured JSON | File | All lifecycle events, debug data |
| Telemetry | JSON summary | File | Performance metrics, resource usage |

---

## 5. Frozen Execution Guarantees

| Guarantee | How Achieved |
|---|---|
| **Deterministic** | Same config + seed → identical output (same platform) |
| **Isolated** | Jobs do not share state, files, or RNG |
| **Resumable** | Failed batch can restart from last completed image |
| **Verifiable** | Self-check mode validates all pipeline stages |
| **Traceable** | Every output maps back to exact config, seed, and version |

---

## Sources

- Phase 4.1 — System architecture.
- Phase 4.2 — Interface contracts, data objects.
- [R1] I. Foster, *Designing and Building Parallel Programs*, Addison-Wesley, 1995.
- [R5] J. K. Ousterhout, *A Philosophy of Software Design*, Yaknyam Press, 2018.
