"""geo_process — PUBLIC module, interface I2 (Phase 4.2).

Responsibility: mask set -> deterministic height field + material map via
the 2.5D process recipes.
"""
from __future__ import annotations

from typing import Optional, Tuple

from semicon.foundation.datatypes import HeightField, MaterialMap
from semicon.geometry._process.process_simulator import ProcessSimulator
from semicon.geometry._process.recipes import apply_recipe, valid_structure_types
from semicon.geometry._raster.mask_builder import MaskSet


def build_geometry(
    masks: MaskSet,
    structure_type: str,
    cd_nm: float,
    height_nm: float,
    pitch_nm: Optional[float],
    pixel_size_nm: float,
    substrate_top_nm: float = 100.0,
) -> Tuple[HeightField, MaterialMap]:
    """Deterministic geometry (I2). Raises KeyError on unknown structure type."""
    if structure_type not in valid_structure_types():
        raise KeyError(f"unknown structure type {structure_type!r}")
    shape = masks.union.shape
    sim = ProcessSimulator(shape, pixel_size_nm, substrate_material=1, substrate_top_nm=substrate_top_nm)
    apply_recipe(sim, masks, structure_type, cd_nm, height_nm, pitch_nm)
    return sim.height_field(), sim.material_map()
