# Data Flow Architecture

**Research Phase:** 4.1
**Document:** 04_data_flow_architecture.md
**Date:** 2026-07-30

---

## 1. Data Flow Principles

| Principle | Description | Rationale |
|---|---|---|
| **Immutability** | Data objects are never modified once created | Enables caching, debugging, and parallel execution |
| **Explicit interfaces** | Each stage has one well-defined input and one well-defined output | No hidden state; clear contracts |
| **No side effects** | Modules do not modify global state, files (except the dataset writer), or each other's data | Deterministic execution; testability |
| **Fail fast** | Invalid data is detected at module boundaries before processing | Clear error messages; no silent corruption |
| **Type-safe** | Data types carry physical units and dimensions | Prevents unit errors (nm vs μm, int vs float) |

---

## 2. Data Types

The system uses five core data types that flow through the pipeline:

| Data Type | Abbreviation | Description | Physical Units |
|---|---|---|---|
| **HeightField** | `H` | 2D array of heights per pixel | nm (float) |
| **MaterialMap** | `M` | 2D array of material IDs per pixel | — (uint8) |
| **YieldMap** | `Y` | 2D array of SE/BSE yield values | e⁻/incident e⁻ (float) |
| **SEMImage** | `I` | 2D array of digitized pixel intensities | Digital counts (uint) |
| **GroundTruth** | `G` | Structured collection of labels | Mixed |

Additional supporting types:

| Type | Description | Used By |
|---|---|---|
| **Config** | Complete system configuration (parsed from file) | orch_pipeline |
| **StructureSpec** | Structure type definition and parameters | geo_raster → geo_process |
| **PixelMask** | Binary rasterized GDSII layer | geo_raster → geo_process |
| **LayerStack** | Ordered list of layers with materials and thicknesses | geo_process |
| **Metadata** | Parameters, seed, timestamps, version | data_writer |
| **Seed** | Random seed for reproducibility | All |

---

## 3. Data Flow Through Pipeline

### 3.1 Complete Flow

```
Stage 1: Configuration Parsing
  Input:  Config file (YAML/TOML)
  Output: Config (parsed)
  Transformer: orch_pipeline

Stage 2: Structure Resolution
  Input:  Config.structure
  Output: StructureSpec
  Transformer: orch_pipeline (uses library)

Stage 3: GDSII Rasterization
  Input:  GDSII file, layer_number, image_dims
  Output: PixelMask[M][N]
  Transformer: geo_raster

Stage 4: Process Model
  Input:  PixelMask, StructureSpec (process params)
  Output: HeightField_det[M][N], MaterialMap_det[M][N]
  Transformer: geo_process
  ─── Interface I2 ───

Stage 5: Variability
  Input:  HeightField_det, MaterialMap_det, StructureSpec (variability params), Seed
  Output: HeightField_var[M][N], MaterialMap_var[M][N]
  Transformer: geo_variability
  ─── Interface I3 / I4 ───

Stage 6: Signal Generation
  Input:  HeightField_var, MaterialMap_var, Config.physics
  Output: YieldMap_SE[M][N], YieldMap_BSE[M][N]
  Transformer: phys_signal

Stage 7: Degradation
  Input:  YieldMap_SE, YieldMap_BSE, Config.physics (degradation params), Seed
  Output: YieldMap_SE_degraded[M][N], YieldMap_BSE_degraded[M][N]
  Transformer: phys_degrade

Stage 8: Image Formation
  Input:  YieldMap_SE_degraded, Config.physics (detector params)
  Output: SEMImage[M][N] (uint)
  Transformer: phys_formation

Stage 9: Ground Truth
  Input:  HeightField_var, MaterialMap_var, Config.dataset
  Output: GroundTruth (edge_maps, CD_values, segmentation)
  Transformer: data_groundtruth

Stage 10: Dataset Writing
  Input:  SEMImage, GroundTruth, Metadata
  Output: Directory with files on disk
  Transformer: data_writer
```

### 3.2 Immutable Data Crossing

```
    ┌──────────┐   Config    ┌──────────┐   StructSpec    ┌──────────┐
    │  Config  │ ──────────▶ │ Resolve  │ ──────────────▶ │  Raster  │
    │  Parser  │             │ Structure│                  │          │
    └──────────┘             └──────────┘                  └──────────┘
                                                                    │
                                                         PixelMask  │
                                                                    ▼
┌──────────┐   H_var+M_var  ┌──────────┐   H_det+M_det  ┌──────────┐
│ Variabil │ ◀───────────── │ Process  │ ◀───────────── │  Raster  │
│   -ity   │   (I3)         │  Model   │   (I2)         │          │
└──────────┘                └──────────┘                └──────────┘
    │
    │  H_var+M_var (I4)
    ▼
┌──────────┐    Y_SE+Y_BSE  ┌──────────┐   Y_degraded   ┌──────────┐
│  Signal  │ ──────────────▶ │ Degrade  │ ──────────────▶ │  Forma-  │
│  Gen     │                 │          │                 │  tion    │
└──────────┘                 └──────────┘                 └──────────┘
                                                                    │
                                                          SEMImage  │
                                                                    ▼
┌──────────┐   GroundTruth   ┌──────────┐   SEMImage   ┌──────────┐
│  Ground  │ ◀────────────── │  Writer  │ ◀────────────│  Forma-  │
│  Truth   │   (from H+M)   │          │              │  tion    │
└──────────┘                 └──────────┘              └──────────┘
```

**Inference:** At every arrow, the data is a **new immutable object**. The producing module creates it and never touches it again. The consuming module receives a read-only reference. This enables safe parallel execution, caching, and debugging.

---

## 4. Data Immutability Rules

| Stage | Rule | Rationale |
|---|---|---|
| Config | Parsed once; never modified | Single source of truth |
| PixelMask | Read-only after creation | Used by process model as reference only |
| HeightField_det | Read-only after creation | Variability reads but does not modify |
| HeightField_var | Read-only after creation | Physics engine reads but does not modify |
| YieldMap | Read-only after creation | Processed in sequence |
| SEMImage | Read-only after creation | Written to disk as-is |

**Engineering Decision:** Immutable data passing is enforced by architectural convention (not the type system). Each module creates output data and returns it. No module modifies data received from another module.

---

## 5. Metadata Propagation

Metadata accumulates as data flows through the pipeline:

| Stage | Metadata Added | Accumulated |
|---|---|---|
| Config parse | Config version, timestamp | Config |
| Structure resolve | Structure type, parameters | + StructureSpec |
| Process model | Layer stack, process params | + Process params |
| Variability | LER, CDU, overlay values | + Variability params |
| Physics | Beam params, signal params | + Physics params |
| Image formation | Detector params, bit depth | + Detector params |
| Dataset | Generation timestamp, version | Completed metadata record |

---

## 6. Data Flow Properties

| Property | Value | Benefit |
|---|---|---|
| **Acyclic** | Data flows in one direction only | No cycles → simple debugging |
| **Synchronous** | Each stage waits for its input | Predictable execution |
| **Deterministic** | Same input + seed → same output | Reproducibility |
| **Parallelizable** | Multiple pipeline instances can run concurrently | Batch performance |
| **Cacheable** | Output of each stage can be cached | Fast re-generation with tweaks |

---

## Sources

- [S1] L. Bass et al., *Software Architecture in Practice*, Addison-Wesley, 2021.
- [S4] I. Gorton, *Essential Software Architecture*, Springer, 2011.
- [S5] J. K. Ousterhout, *A Philosophy of Software Design*, Yaknyam Press, 2018.
- [S9] M. Fowler and K. Beck, *Refactoring*, 2nd ed. Addison-Wesley, 2018.
- Phase 2.6 — SEM Physics Engine interface.
- Phase 3.4 — Geometry Engine interface.
