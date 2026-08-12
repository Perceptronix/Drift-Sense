"""geo_raster — PUBLIC module, interface I1 (Phase 4.2).

Responsibility: GDSII -> per-layer masks + PixelMask union.
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

from semicon.foundation.datatypes import PixelMask
from semicon.geometry._raster.gdsii import GdsLibrary, read_gds, write_gds
from semicon.geometry._raster.mask_builder import MaskSet, build_masks, to_pixel_mask


def load_library(path) -> GdsLibrary:
    """Load a GDSII library from disk."""
    return read_gds(path)


def save_library(library: GdsLibrary, path) -> None:
    """Persist a library to a GDSII file (used by the structure library)."""
    write_gds(library, path)


def rasterize(
    library: GdsLibrary,
    struct_name: str,
    width_nm: float,
    height_nm: float,
    pixel_size_nm: float,
    ss: int = 4,
) -> MaskSet:
    """Rasterize structure struct_name onto a width x height nm FOV."""
    return build_masks(library, struct_name, width_nm, height_nm, pixel_size_nm, ss=ss)


def to_pixel_mask_obj(mask_set: MaskSet, pixel_size_nm: float) -> PixelMask:
    """I1 output: union mask as a PixelMask."""
    return to_pixel_mask(mask_set, pixel_size_nm)
