"""Canonical data objects (Phase 4.2, D1-D10).

Every object is frozen-immutable after construction and validates its own
invariants (dimensions, dtype, value ranges) in ``__post_init__``.
All arrays are MxN with Row=Y, Col=X, top-left origin, in the units stated.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

# ---------------------------------------------------------------------------
# Frozen constants (Phase 1 / Phase 3.1 / Phase 4.4)
# ---------------------------------------------------------------------------
MATERIAL_NAMES: Dict[int, str] = {
    0: "vacuum",
    1: "Si",
    2: "SiO2",
    3: "SiN",
    4: "Cu",
    5: "W",
    6: "PR",
}
VALID_MATERIAL_IDS = frozenset(MATERIAL_NAMES)

STRUCTURE_TYPES = (
    "iso_line",
    "dense_ls",
    "contact",
    "via",
    "trench",
    "fin",
    "gate",
    "sti",
    "bimaterial",
    "pitch_std",
)

# Postcondition bounds (Phase 2.2 / 2.5)
YIELD_MAX = 10.0
SE_YIELD_MAX = 10.0
BSE_YIELD_MAX = 1.0


def _check_dims(name: str, a: np.ndarray, ref: Optional[np.ndarray] = None) -> None:
    if a.ndim != 2:
        raise ValueError(f"{name} must be 2D, got ndim={a.ndim}")
    if ref is not None and a.shape != ref.shape:
        raise ValueError(f"{name} shape {a.shape} != reference {ref.shape}")


def _check_finite(name: str, a: np.ndarray) -> None:
    if not np.all(np.isfinite(a)):
        raise ValueError(f"{name} contains NaN/Inf")


def _check_pixel_size(name: str, v: float) -> None:
    if not (0.0 < v <= 100.0):
        raise ValueError(f"{name} pixel_size_nm={v} out of (0, 100]")


# ---------------------------------------------------------------------------
# D3 - PixelMask
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PixelMask:
    data: np.ndarray  # (M,N) uint8 in {0,1}
    pixel_size_nm: float

    def __post_init__(self) -> None:
        d = self.data
        if d.dtype != np.uint8:
            object.__setattr__(self, "data", np.ascontiguousarray(d, dtype=np.uint8))
        _check_dims("PixelMask", self.data)
        _check_pixel_size("PixelMask", self.pixel_size_nm)
        vals = np.unique(self.data)
        if not np.all(np.isin(vals, (0, 1))):
            raise ValueError(f"PixelMask values must be in {{0,1}}, got {vals}")

    @property
    def shape(self) -> tuple:
        return self.data.shape

    def area_px(self) -> int:
        return int(self.data.sum())


# ---------------------------------------------------------------------------
# D5 - HeightField
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class HeightField:
    data: np.ndarray  # (M,N) float64, height in nm above substrate backside
    pixel_size_nm: float

    def __post_init__(self) -> None:
        d = self.data
        if d.dtype != np.float64:
            object.__setattr__(self, "data", np.ascontiguousarray(d, dtype=np.float64))
        _check_dims("HeightField", self.data)
        _check_finite("HeightField", self.data)
        _check_pixel_size("HeightField", self.pixel_size_nm)

    @property
    def shape(self) -> tuple:
        return self.data.shape


# ---------------------------------------------------------------------------
# D6 - MaterialMap
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class MaterialMap:
    data: np.ndarray  # (M,N) uint8, IDs in {0..6}
    pixel_size_nm: float

    def __post_init__(self) -> None:
        d = self.data
        if d.dtype != np.uint8:
            object.__setattr__(self, "data", np.ascontiguousarray(d, dtype=np.uint8))
        _check_dims("MaterialMap", self.data)
        _check_pixel_size("MaterialMap", self.pixel_size_nm)
        ids = np.unique(self.data)
        if not np.all(np.isin(ids, list(VALID_MATERIAL_IDS))):
            raise ValueError(f"MaterialMap has invalid IDs {ids}")

    @property
    def shape(self) -> tuple:
        return self.data.shape

    def as_rgb(self) -> np.ndarray:
        """Deterministic false-colour RGB image for debugging (uint8, MxNx3)."""
        palette = {
            0: (0, 0, 0),       # vacuum
            1: (90, 130, 180),  # Si
            2: (150, 90, 200),  # SiO2
            3: (120, 200, 140), # SiN
            4: (210, 140, 60),  # Cu
            5: (140, 140, 160), # W
            6: (220, 60, 60),   # PR
        }
        out = np.zeros(self.data.shape + (3,), dtype=np.uint8)
        for mid, rgb in palette.items():
            out[self.data == mid] = rgb
        return out


# ---------------------------------------------------------------------------
# D7 - YieldMaps
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class YieldMaps:
    se_yield: np.ndarray  # (M,N) float64
    bse_yield: np.ndarray  # (M,N) float64
    pixel_size_nm: float

    def __post_init__(self) -> None:
        for n in ("se_yield", "bse_yield"):
            a = getattr(self, n)
            if a.dtype != np.float64:
                object.__setattr__(self, n, np.ascontiguousarray(a, dtype=np.float64))
        _check_dims("YieldMaps.se", self.se_yield)
        _check_dims("YieldMaps.bse", self.bse_yield, ref=self.se_yield)
        _check_finite("YieldMaps", self.se_yield)
        _check_finite("YieldMaps", self.bse_yield)
        _check_pixel_size("YieldMaps", self.pixel_size_nm)
        if self.se_yield.min() < 0.0 or self.se_yield.max() > SE_YIELD_MAX:
            raise ValueError(
                f"se_yield out of [0, {SE_YIELD_MAX}]: [{self.se_yield.min()}, {self.se_yield.max()}]"
            )
        if self.bse_yield.min() < 0.0 or self.bse_yield.max() > BSE_YIELD_MAX:
            raise ValueError(
                f"bse_yield out of [0, {BSE_YIELD_MAX}]: [{self.bse_yield.min()}, {self.bse_yield.max()}]"
            )

    @property
    def shape(self) -> tuple:
        return self.se_yield.shape


# ---------------------------------------------------------------------------
# D8 - SEMImage + FormationRecord
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FormationRecord:
    gain: float
    offset: float
    bit_depth: int
    saturate_enabled: bool
    saturation_fraction: float  # fraction of pixels clipped at max value
    signal_min: float
    signal_max: float


@dataclass(frozen=True)
class SEMImage:
    data: np.ndarray  # (M,N) uint8 or uint16
    bit_depth: int
    pixel_size_nm: float
    formation_record: FormationRecord

    def __post_init__(self) -> None:
        _check_dims("SEMImage", self.data)
        _check_pixel_size("SEMImage", self.pixel_size_nm)
        if self.bit_depth not in (8, 16):
            raise ValueError(f"bit_depth must be 8 or 16, got {self.bit_depth}")
        expected_dtype = np.uint8 if self.bit_depth == 8 else np.uint16
        if self.data.dtype != expected_dtype:
            raise ValueError(
                f"SEMImage dtype {self.data.dtype} inconsistent with bit_depth {self.bit_depth}"
            )
        maxval = (1 << self.bit_depth) - 1
        if self.data.min() < 0 or self.data.max() > maxval:
            raise ValueError(f"SEMImage values out of [0,{maxval}]")

    @property
    def shape(self) -> tuple:
        return self.data.shape


# ---------------------------------------------------------------------------
# D9 - GroundTruth (demo scope: edges, cd, segmentation, contours, height/mat)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class GroundTruth:
    segmentation: np.ndarray  # (M,N) uint8 material IDs (== MaterialMap)
    edge_map: np.ndarray  # (M,N) float64: |gradient of height| (nm/px)
    edge_mask: np.ndarray  # (M,N) bool: binary edge locations
    cd_measurements: List[Dict[str, Any]]  # feature CD values in nm
    contours: List[np.ndarray]  # polygon vertex lists (nm, one per feature)
    pixel_size_nm: float

    def __post_init__(self) -> None:
        _check_dims("GroundTruth.segmentation", self.segmentation)
        _check_dims("GroundTruth.edge_map", self.edge_map, ref=self.segmentation)
        _check_dims("GroundTruth.edge_mask", self.edge_mask, ref=self.segmentation)
        _check_finite("GroundTruth.edge_map", self.edge_map)
        _check_pixel_size("GroundTruth", self.pixel_size_nm)


# ---------------------------------------------------------------------------
# D1 - Config (thin structured container; validation lives in orchestration.config)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    general: Dict[str, Any]
    structure: Dict[str, Any]
    process: Dict[str, Any]
    variability: Dict[str, Any]
    physics: Dict[str, Any]
    detector: Dict[str, Any]
    ground_truth: Dict[str, Any] = field(default_factory=dict)
    dataset: Dict[str, Any] = field(default_factory=dict)

    def merged(self) -> Dict[str, Any]:
        """Full dict form (config snapshot for metadata)."""
        return {
            "general": dict(self.general),
            "structure": dict(self.structure),
            "process": dict(self.process),
            "variability": dict(self.variability),
            "physics": dict(self.physics),
            "detector": dict(self.detector),
            "ground_truth": dict(self.ground_truth),
            "dataset": dict(self.dataset),
        }


# ---------------------------------------------------------------------------
# D10 - Metadata (assembled by orchestration.pipeline)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Metadata:
    structure: Dict[str, Any]
    process: Dict[str, Any]
    variability: Dict[str, Any]
    physics: Dict[str, Any]
    seeds: Dict[str, Any]
    version: Dict[str, Any]
    provenance: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "structure": dict(self.structure),
            "process": dict(self.process),
            "variability": dict(self.variability),
            "physics": dict(self.physics),
            "seeds": dict(self.seeds),
            "version": dict(self.version),
            "provenance": dict(self.provenance),
        }
