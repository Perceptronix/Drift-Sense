# Module Decomposition

**Research Phase:** 4.1
**Document:** 03_module_decomposition.md
**Date:** 2026-07-30

---

## 1. Module Inventory

The system decomposes into **10 primary modules** across **5 subsystems**:

| Subsystem | Module | Abbreviation | Priority |
|---|---|---|---|
| **Geometry** | GDSII Rasterizer | `geo_raster` | Phase A |
| **Geometry** | Process Model | `geo_process` | Phase A |
| **Geometry** | Variability Engine | `geo_variability` | Phase A |
| **Physics** | Signal Generation | `phys_signal` | Phase A |
| **Physics** | Degradation Model | `phys_degrade` | Phase A |
| **Physics** | Image Formation | `phys_formation` | Phase A |
| **Dataset** | Dataset Writer | `data_writer` | Phase A |
| **Dataset** | Ground Truth Generator | `data_groundtruth` | Phase B |
| **Orchestration** | Pipeline Controller | `orch_pipeline` | Phase A |
| **Orchestration** | Job Manager | `orch_job` | Phase B |

---

## 2. Module Specifications

### 2.1 Module: GDSII Rasterizer (geo_raster)

| Aspect | Specification |
|---|---|
| **Purpose** | Read GDSII layout files and rasterize polygons to a pixel grid |
| **Inputs** | GDSII file path; layer number; image dimensions (M, N); pixel size (Δx) |
| **Outputs** | Binary pixel mask (M × N): 1 = feature present, 0 = no feature |
| **Responsibilities** | 1) Parse GDSII stream format 2) Transform polygons to pixel coordinates 3) Anti-alias edges for sub-pixel accuracy 4) Handle multiple GDSII layers 5) Validate GDSII against layer stack spec |
| **Dependencies** | GDSII file format library |
| **Internal state** | None (stateless) |
| **Shared with** | geo_process (provides pixel mask for lithography step) |

### 2.2 Module: Process Model (geo_process)

| Aspect | Specification |
|---|---|
| **Purpose** | Apply semiconductor process steps to generate deterministic 2.5D geometry |
| **Inputs** | Pixel mask from geo_raster; layer stack spec; process parameters (sidewall angle, CD bias, corner radii, thicknesses, material IDs) |
| **Outputs** | Deterministic height field (M × N, float — nm); deterministic material map (M × N, uint8) |
| **Responsibilities** | 1) Apply conformal/bottom-up deposition 2) Apply resist coating and lithography pattern 3) Apply anisotropic/isotropic etch 4) Apply resist strip 5) Apply CMP planarization 6) Sequentially process all layers in stack |
| **Dependencies** | Height field manipulation library; material map management |
| **Internal state** | Current height field and material map (updated per layer) |
| **Shared with** | geo_variability (I2 interface); geo_raster (receives mask) |

### 2.3 Module: Variability Engine (geo_variability)

| Aspect | Specification |
|---|---|
| **Purpose** | Apply manufacturing variability to deterministic geometry |
| **Inputs** | Deterministic height field + material map; variability parameters (LER 3σ, ξ, ρ, CDU σ, overlay σ, sidewall angle σ, etc.); random seed |
| **Outputs** | Variable height field (M × N, float — nm); variable material map (M × N, uint8) |
| **Responsibilities** | 1) Generate LER on all feature edges (correlated Gaussian random process) 2) Compute LWR from left/right LER 3) Apply overlay translation shifts per layer 4) Apply sidewall angle variation per feature 5) Apply thickness and corner radius variation 6) Apply CMP dishing/erosion variation |
| **Dependencies** | Random number generator; LER generation library |
| **Internal state** | Random number generator (seeded per realization) |
| **Shared with** | geo_process (I2 input); phys_signal (I3/I4 output) |

### 2.4 Module: Signal Generation (phys_signal)

| Aspect | Specification |
|---|---|
| **Purpose** | Compute SEM signal (SE/BSE yield) for each pixel based on geometry and material |
| **Inputs** | Height field + material map (I4); physics parameters (beam energy, probe current, material properties table — δ₀, η, Λ, etc.) |
| **Outputs** | Per-pixel SE yield map (M × N, float); per-pixel BSE yield map (M × N, float) |
| **Responsibilities** | 1) Compute surface normals from height field 2) Look up material properties (δ₀, η, Λ) from material library 3) Compute topographic contrast (secθ or Lambertian model) 4) Compute material contrast 5) Apply edge brightening 6) Compute charging modulation 7) Scale yields by probe current |
| **Dependencies** | Material property library; surface normal computation |
| **Internal state** | None (stateless) |
| **Shared with** | phys_degrade (provides yield maps) |

### 2.5 Module: Degradation Model (phys_degrade)

| Aspect | Specification |
|---|---|
| **Purpose** | Apply physical degradation effects to the ideal SEM signal |
| **Inputs** | SE/BSE yield maps; PSF parameters (probe diameter, beam energy); noise model parameters; charging parameters |
| **Outputs** | Degraded yield maps (M × N, float) |
| **Responsibilities** | 1) Compute and apply PSF convolution (Gaussian beam profile) 2) Add Poisson (shot) noise 3) Add detector noise 4) Apply SE escape depth effects 5) Apply charging-induced signal modulation |
| **Dependencies** | Convolution library; noise generation library |
| **Internal state** | Random number generator (for noise) |
| **Shared with** | phys_signal (receives yield); phys_formation (provides degraded signal) |

### 2.6 Module: Image Formation (phys_formation)

| Aspect | Specification |
|---|---|
| **Purpose** | Convert physical signal to digitized SEM image |
| **Inputs** | Degraded yield maps; detector parameters (gain, offset, saturation level); bit depth |
| **Outputs** | Digitized SEM image (M × N, uint16 or uint8) |
| **Responsibilities** | 1) Scale yield signal to digital counts 2) Apply detector gain and offset 3) Apply saturation/clipping 4) Digitize to specified bit depth 5) Apply detector efficiency map (optional shading correction) |
| **Dependencies** | None (pure arithmetic) |
| **Internal state** | None (stateless) |
| **Shared with** | phys_degrade (receives degraded signal); data_writer (outputs image) |

### 2.7 Module: Dataset Writer (data_writer)

| Aspect | Specification |
|---|---|
| **Purpose** | Save generated images and metadata to disk in organized structure |
| **Inputs** | Digitized SEM image; metadata (parameters, seed, timestamps, version info) |
| **Outputs** | Image files on disk (TIFF/PNG); metadata files (JSON/YAML); dataset index |
| **Responsibilities** | 1) Write image files in specified format 2) Write metadata as sidecar JSON files 3) Organize output directory structure 4) Generate dataset index for batch jobs 5) Validate writes (verify files exist and are readable) |
| **Dependencies** | Image I/O library (TIFF, PNG); filesystem |
| **Internal state** | Output directory path; dataset index accumulator |
| **Shared with** | phys_formation (receives image); data_groundtruth (receives metadata context) |

### 2.8 Module: Ground Truth Generator (data_groundtruth)

| Aspect | Specification |
|---|---|
| **Purpose** | Generate ground-truth labels for training/evaluating metrology algorithms |
| **Inputs** | Height field, material map (from geo_variability); structure parameters; image metadata |
| **Outputs** | Ground truth labels: edge position maps, CD values, material segmentation maps |
| **Responsibilities** | 1) Extract true edge positions from height field (at specified threshold height) 2) Compute true CD values per feature 3) Generate material segmentation mask 4) Generate topographic contour maps 5) Annotate structure types per region 6) Save labels alongside images |
| **Dependencies** | Image I/O library; geometry utilities |
| **Internal state** | None (stateless) |
| **Shared with** | data_writer (ground-truth files); geo_variability (provides source geometry) |

### 2.9 Module: Pipeline Controller (orch_pipeline)

| Aspect | Specification |
|---|---|
| **Purpose** | Orchestrate the execution of the complete pipeline for a single structure |
| **Inputs** | Complete configuration (parsed config object) |
| **Outputs** | Completed dataset entry (image + ground truth + metadata) |
| **Responsibilities** | 1) Validate configuration at startup 2) Resolve structure type and parameters from library 3) Call geo_raster → geo_process → geo_variability → phys_signal → phys_degrade → phys_formation → data_groundtruth → data_writer in sequence 4) Pass immutable data between stages 5) Handle errors at each stage with clear messages 6) Record timing and resource usage 7) Return success/failure with diagnostics |
| **Dependencies** | All pipeline modules |
| **Internal state** | Pipeline configuration; stage registry |
| **Shared with** | All modules (orchestrates); orch_job (receives pipeline instances) |

### 2.10 Module: Job Manager (orch_job)

| Aspect | Specification |
|---|---|
| **Purpose** | Manage batch execution of multiple pipeline runs for dataset generation |
| **Inputs** | Batch configuration (list of structures, parameter sweeps, repetition count, output directory) |
| **Outputs** | Completed dataset (multi-image) |
| **Responsibilities** | 1) Expand batch config into individual pipeline jobs 2) Execute pipeline runs (sequentially or in parallel) 3) Manage random seeds per realization 4) Aggregate results into dataset index 5) Handle partial failures (continue on error) 6) Report progress and statistics |
| **Dependencies** | orch_pipeline; parallel execution library |
| **Internal state** | Job queue; progress tracker; result accumulator |
| **Shared with** | orch_pipeline (submits jobs); data_writer (output aggregation) |

---

## 3. Module Dependency Graph

```
                    ┌──────────────────┐
                    │   orch_job      │
                    └────────┬─────────┘
                             │ creates & manages
                             ▼
                    ┌──────────────────┐
                    │  orch_pipeline   │
                    └────────┬─────────┘
                             │ orchestrates
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   geo_raster    │ │  geo_process    │ │ geo_variability  │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   phys_signal   │ │  phys_degrade   │ │ phys_formation   │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
┌──────────────────┐ ┌──────────────────┐
│   data_writer   │ │ data_groundtruth │
└──────────────────┘ └──────────────────┘
```

---

## 4. Module Boundaries

| Rule | Description |
|---|---|
| **No circular dependencies** | The module graph is a directed acyclic graph (DAG) |
| **Single direction of dependency** | Geometry → Physics → Dataset → Orchestration |
| **No shared mutable state** | Each module receives data and returns new data |
| **Modules do not call each other directly** | The orchestrator invokes modules in order |
| **Module A cannot depend on module B's internal data** | Only public interfaces are visible |

---

## Sources

- [S1] L. Bass et al., *Software Architecture in Practice*, Addison-Wesley, 2021.
- [S2] E. Gamma et al., *Design Patterns*, Addison-Wesley, 1994.
- [S5] J. K. Ousterhout, *A Philosophy of Software Design*, Yaknyam Press, 2018.
- [S8] R. C. Martin, *Clean Architecture*, Prentice Hall, 2017.
- Phase 3.4 — Geometry Engine specification.
- Phase 2.6 — SEM Physics Engine specification.
