"""geo_variability — PUBLIC module, interface I3 (Phase 4.2).

Responsibility: deterministic geometry -> variability-applied geometry
(height field + material map) that feeds physics (I4) and ground truth (I7).
"""
from __future__ import annotations

from typing import Dict, Tuple

from semicon.foundation.datatypes import HeightField, MaterialMap
from semicon.geometry._variability.variability_applier import (
    VariabilityRecord,
    apply_variability as _apply,
)


def apply_variability(
    height_field: HeightField,
    material_map: MaterialMap,
    config: Dict,
    seed: int,
) -> Tuple[HeightField, MaterialMap, VariabilityRecord]:
    """Apply overlay/LER/CDU per config, driven by a deterministic seed."""
    import numpy as np

    gen = np.random.default_rng(seed)
    return _apply(height_field, material_map, config, gen)
