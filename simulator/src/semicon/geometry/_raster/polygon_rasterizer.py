"""Edge-function / point-in-polygon rasterization (Phase 5.2, A1).

A polygon (vertices in nm) is rasterized onto an MxN grid with a given
pixel size. Default sampling is the pixel centre (SS=1). Supersampling
(SS>1) subdivides each pixel for anti-aliased edges, thresholded at 0.5.

Convention: vertex (x, y) nm maps to (col = x / ps, row = y / ps). Row is
the first array axis.

DG1 implementation decision: fast-path for axis-aligned rectangles (direct
numpy slicing), general path via ray-casting with optional supersampling.
"""
from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np


def point_in_polygon(col: np.ndarray, row: np.ndarray, poly: np.ndarray) -> np.ndarray:
    """Even-odd ray cast. poly is (P,2) with columns [x,y] nm, first point NOT closed."""
    inside = np.zeros(col.shape, dtype=bool)
    p = np.asarray(poly, dtype=np.float64)
    n = len(p)
    for i in range(n):
        x1, y1 = p[i - 1]
        x2, y2 = p[i]
        cond1 = (y1 > row) != (y2 > row)
        denom = y2 - y1
        with np.errstate(divide="ignore", invalid="ignore"):
            x_cross = (x2 - x1) * (row - y1) / denom + x1 if denom != 0 else np.full_like(row, np.inf)
        cond2 = col < x_cross
        inside ^= cond1 & cond2
    return inside


def _is_axis_aligned_rect(poly: np.ndarray) -> bool:
    """Check if polygon is an axis-aligned rectangle (4 vertices, opposite edges parallel)."""
    if len(poly) != 4:
        return False
    xs, ys = poly[:, 0], poly[:, 1]
    return (
        xs[0] == xs[3] and xs[1] == xs[2] and
        ys[0] == ys[1] and ys[2] == ys[3]
    )


def rasterize_polygon(
    vertices_nm: Sequence[Tuple[float, float]],
    shape: Tuple[int, int],
    pixel_size_nm: float,
    ss: int = 1,
) -> np.ndarray:
    """Return uint8 mask (M,N) in {0,1} with 1 = inside polygon."""
    poly = np.asarray(vertices_nm, dtype=np.float64)
    if len(poly) < 3:
        raise ValueError("polygon needs >= 3 vertices")
    M, N = shape
    ps = float(pixel_size_nm)

    # Fast path for axis-aligned rectangles (most structure polygons)
    # A pixel at column i is "inside" if its center ((i+0.5)*ps) lies within the rect.
    if _is_axis_aligned_rect(poly):
        xs, ys = poly[:, 0], poly[:, 1]
        col_min = max(0, int(np.floor(xs.min() / ps)))
        col_max = min(N, int(np.floor((xs.max() - 1e-9) / ps)) + 1)
        row_min = max(0, int(np.floor(ys.min() / ps)))
        row_max = min(M, int(np.floor((ys.max() - 1e-9) / ps)) + 1)
        mask = np.zeros((M, N), dtype=np.uint8)
        if col_min < col_max and row_min < row_max:
            mask[row_min:row_max, col_min:col_max] = 1
        return mask

    # General polygon path
    row_c = (np.arange(M, dtype=np.float64) + 0.5) * ps
    col_c = (np.arange(N, dtype=np.float64) + 0.5) * ps

    if ss == 1:
        cols, rows = np.meshgrid(col_c, row_c)
        inside = point_in_polygon(cols.ravel(), rows.ravel(), poly)
        return inside.reshape(M, N).astype(np.uint8)

    # Supersampled: average sub-samples per pixel
    out = np.zeros((M, N), dtype=np.float32)
    for si in range(ss):
        for sj in range(ss):
            r_off = ((si + 0.5) / ss - 0.5) * ps
            c_off = ((sj + 0.5) / ss - 0.5) * ps
            cols = col_c[None, :] + c_off
            rows = row_c[:, None] + r_off
            cols, rows = np.broadcast_arrays(cols, rows)
            inside = point_in_polygon(cols.ravel(), rows.ravel(), poly)
            out += inside.reshape(M, N).astype(np.float32)
    out /= ss * ss
    return (out >= 0.5).astype(np.uint8)


def rasterize_polygons(
    polygons: Sequence[Sequence[Tuple[float, float]]],
    shape: Tuple[int, int],
    pixel_size_nm: float,
    ss: int = 1,
) -> np.ndarray:
    """Union of several polygons -> single uint8 mask."""
    mask = np.zeros(shape, dtype=np.uint8)
    for poly in polygons:
        mask |= rasterize_polygon(poly, shape, pixel_size_nm, ss=ss)
    return mask
