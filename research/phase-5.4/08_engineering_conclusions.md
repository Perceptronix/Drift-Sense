# Engineering Conclusions

**Research Phase:** 5.4
**Document:** 08_engineering_conclusions.md
**Date:** 2026-07-30

---

## 1. Frozen Integration Decisions

| ID | Decision | Value | Justification |
|---|---|---|---|
| **IN1** | Pipeline stages | 10-stage sequential pipeline (Doc 02) | Matches frozen architecture AD1 |
| **IN2** | Data handoff | Immutable D-objects through master controller | Phase 4.1 AD4/AD5 |
| **IN3** | Module communication | Direct function calls via controller; no module-to-module | Strict pipeline (AD4) |
| **IN4** | GT parallelism | Stage 7 parallel with stages 4–6 (thread pool) | Phase 4.3 RD5 |
| **IN5** | Seed chain | master → structure → image → stage (hash-derived) | Phase 4.3 RD7 |
| **IN6** | Config snapshot | Full resolved config per sample | Phase 4.3 |
| **IN7** | Error taxonomy | OK/RETRY/FAILED/ABORT; 3× backoff retry | Operational policy |
| **IN8** | Checkpoint | Per-image checkpoint + manifest journal + atomic writes | Phase 4.3 RD10 |
| **IN9** | Logging | Structured JSON-lines per stage | Operational policy |
| **IN10** | Generation modes | Single / Batch (grid) / Sweep (sampled) | Phase 5.1 |
| **IN11** | Determinism | Bitwise on same platform; SHA-256 verified | Phase 4.3 RD2 |
| **IN12** | Memory budget | < 500 MB RSS/worker; < 2 GB @ 4W | Doc 06 |
| **IN13** | Runtime budget | < 3.0 s/image @1024² sequential | Doc 06 |
| **IN14** | Parallel target | ≥ 3.5× @ 4 workers | Doc 06 |
| **IN15** | Cache target | ≥ 50% hit rate; ≥ 1.5× speedup | Doc 06 |
| **IN16** | Integration tests | 6 layers T1–T6 | Doc 05 |
| **IN17** | Datasets | DS1–DS5 portfolio | Doc 07 |
| **IN18** | Splits | 70/15/15 deterministic, stratified | Doc 07 |
| **IN19** | Dataset versioning | Semver + dataset_id in metadata | Phase 4.4 |
| **IN20** | Performance profiling gates | Geometry < 350 ms; physics < 500 ms; batch < 15 min @ 4W | Doc 06 |

---

## 2. Frozen Integration Architecture

```
CLI → Job Manager (orch_job)
        → Worker pool (processes, n_workers)
            → Master Pipeline (orch_pipeline)
                → Stage 0 Config
                → Stage 1 Structure (I1)
                → Stage 2 Process (I2)
                → Stage 3 Variability (I3)
                → Stage 4 Signal (I4)      ┐
                → Stage 5 Degrade (I5)      ├ parallel with
                → Stage 6 Image (I6)        ┘ Stage 7 GT (I7)
                → Stage 8 Metadata
                → Stage 9 Packaging (I8)
        → Dataset finalization (index, stats, splits, hashes, validation)
```

---

## 3. Frozen Runtime Orchestration

| Component | Frozen Behavior |
|---|---|
| orch_pipeline | 10-stage execution; timing capture; per-stage validation; error classification |
| orch_job | Manifest-driven batch; process pool; checkpoint; resume; progress; aggregation |
| Cache | geometry-level (pre-variability); LRU; config-keyed |
| Logging | JSON-lines; levels DEBUG→CRITICAL; per-stage |
| Recovery | Per-image checkpoint; atomic writes; resume; 3× retry |

---

## 4. Frozen Dataset Generation Process

```
Dataset definition → Sample plan (seeded) → Batch execution → Finalization → Validation → Packaging
```

Key properties: deterministic, reproducible, versioned, FAIR-compliant, canonical layout.

---

## 5. Frozen Production Dataset Plan

| ID | Dataset | Size | Purpose | Gate |
|---|---|---|---|---|
| DS1 | Development | 50 | Smoke/dev | M3 |
| DS2 | Unit-test | 100 | CI regression | M4/M5 |
| DS3 | Validation | 1,000 | L1–L5 gates | M5 |
| DS4 | Scientific-benchmark | 200 | L4 scientific | M5 |
| DS5 | Final-training | 100,000 | Release | M7 |

---

## 6. Frozen Acceptance Criteria

| Criterion | Target |
|---|---|
| Per-image p95 | < 3.0 s @ 1024² |
| Memory | < 500 MB RSS/worker |
| Speedup | ≥ 3.5× @ 4 workers |
| Cache | ≥ 50% hit; ≥ 1.5× speedup |
| Validation L1–L5 | 100% pass on DS3 |
| Scientific (L4) | All targets (Doc 05 §6) |
| Determinism | SHA-256 identical on same platform |
| Failure recovery | Resume test passes; retry works |
| Storage | < 4 MB/sample core |

---

## 7. Certification Statement

The **system integration architecture is frozen and complete**. The simulator is fully specified:

- 10-stage pipeline with 8 certified interfaces
- Runtime orchestration with checkpoint, retry, logging, progress
- Deterministic dataset pipeline with canonical Phase 4.4 output
- 6-layer integration testing strategy
- Measured performance budget with acceptance criteria
- 5-dataset production plan

An engineering team can build the complete integrated simulator from Phases 5.1–5.4 without revisiting research.

---

## Sources

- Phase 4.1 — Architecture decisions.
- Phase 4.3 — Runtime decisions.
- Phase 4.4 — Dataset specification.
- Phase 5.1 — Roadmap milestones.
- Phase 5.2/5.3 — Engine blueprints.
- Documents 01–07 of this phase.
