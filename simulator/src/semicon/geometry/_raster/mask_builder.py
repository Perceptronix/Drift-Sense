"""Mask builder (Phase 5.2 A1): GDSII structure -> per-layer binary masks.

Produces a ``MaskSet`` of per-layer uint8 masks in pixel space, plus the I1
``PixelMask`` union. Supersampling defaults to SS=4 for edge quality.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from semicon.foundation.datatypes import PixelMask
from semicon.geometry._raster.gdsii import GdsLibrary
from semicon.geometry._raster.polygon_rasterizer import rasterize_polygon


@dataclass(frozen=True)
class MaskSet:
    layer_masks: Dict[int, np.ndarray]  # layer id -> (M,N) uint8 {0,1}
    union: np.ndarray  # (M,N) uint8 {0,1}

    @property
    def layers(self) -> List[int]:
        return sorted(self.layer_masks)


def build_masks(
    library: GdsLibrary,
    struct_name: str,
    width_nm: float,
    height_nm: float,
    pixel_size_nm: float,
    ss: int = 4,
) -> MaskSet:
    """Rasterize the named structure onto a width x height nm FOV.

    Polygons are unioned per GDS layer. A polygon that falls fully outside
    the FOV is skipped.
    """
    if pixel_size_nm <= 0:
        raise ValueError("pixel_size_nm must be > 0")
    M = int(round(height_nm / pixel_size_nm))
    N = int(round(width_nm / pixel_size_nm))
    shape = (M, N)
    half_w, half_h = width_nm / 2, height_nm / 2

    polys = library.polygons(struct_name)
    layer_masks: Dict[int, np.ndarray] = {}
    for layer, verts in polys:
        verts_arr = np.asarray(verts, dtype=np.float64)
        if len(verts_arr) < 3:
            continue
        # translate to pixel coordinates: x=-half_w -> col 0, y=-half_h -> row 0
        cols = (verts_arr[:, 0] + half_w) / pixel_size_nm
        rows = (verts_arr[:, 1] + half_h) / pixel_size_nm
        # skip polygons wholly outside the FOV
        if cols.max() < 0 or cols.min() > N or rows.max() < 0 or rows.min() > M:
            continue
        # clip vertices to the FOV boundary for robustness
        cols = np.clip(cols, 0, N)
        rows = np.clip(rows, 0, M)
        px = np.stack([cols, rows], axis=1)
        if layer not in layer_masks:
            layer_masks[layer] = np.zeros(shape, dtype=np.uint8)
        layer_masks[layer] |= rasterize_polygon(px.tolist(), shape, 1.0, ss=ss)

    union = np.zeros(shape, dtype=np.uint8)
    for m in layer_masks.values():
        union |= m
    return MaskSet(layer_masks=layer_masks, union=union)


def to_pixel_mask(mask_set: MaskSet, pixel_size_nm: float) -> PixelMask:
    return PixelMask(data=mask_set.union, pixel_size_nm=pixel_size_nm)
