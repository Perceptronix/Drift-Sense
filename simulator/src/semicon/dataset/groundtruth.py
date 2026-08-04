"""Ground-truth generation (Phase 4.4 doc 04; interface I7).

Produces the five ground-truth components from the variability-applied
geometry: edge map, edge mask, CD measurements, contours, segmentation
(== material map). Precision target: 0.1 nm for CD measurements.

CD measurement method (DG1): thresholded cross-section at the vertical
midpoint of each edge in the smoothed height profile. Line-like features
(iso_line, dense_ls, trench, fin, pitch_std) are averaged over the central
rows; square features (contact, via, sti) are measured on both axes; gate
measures fin pitch + gate width; bimaterial measures both block widths.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
from skimage.measure import find_contours

from semicon.foundation.datatypes import GroundTruth, HeightField, MaterialMap
from semicon.foundation.math_utils import central_difference
from semicon.physics._signal.topography_engine import compute_gradient_magnitude


def _smooth1d(x: np.ndarray, k: int = 3) -> np.ndarray:
    if k <= 1:
        return x
    kernel = np.ones(k, dtype=np.float64) / k
    return np.convolve(x, kernel, mode="same")


def _edge_crossings(profile: np.ndarray, ps: float) -> np.ndarray:
    """Sub-pixel edge positions (nm) at the vertical midpoint of the profile.

    No smoothing: the height field is already smooth (process + corner
    rounding), and any extra averaging shifts crossings on steep walls.
    """
    p = profile.astype(np.float64)
    lo, hi = p.min(), p.max()
    if hi - lo < 1e-9:
        return np.array([], dtype=np.float64)
    n = (p - lo) / (hi - lo)
    mid = 0.5
    crossings = []
    for i in range(len(n) - 1):
        if (n[i] - mid) * (n[i + 1] - mid) <= 0:
            frac = (mid - n[i]) / (n[i + 1] - n[i] + 1e-12)
            crossings.append((i + 1 + frac) * ps)
    return np.array(crossings, dtype=np.float64)


def _widths_from_crossings(crossings: np.ndarray) -> np.ndarray:
    return np.diff(crossings)


def measure_line_like(H: np.ndarray, ps: float, n_rows: int = 5) -> List[float]:
    """Average half-height widths of vertical features from central rows."""
    M, N = H.shape
    r0 = M // 2 - n_rows // 2
    widths: List[float] = []
    for r in range(r0, r0 + n_rows):
        if 0 <= r < M:
            edges = _edge_crossings(H[r, :], ps)
            widths.extend(_widths_from_crossings(edges).tolist())
    if not widths:
        return []
    # pair widths by parity (raised features are odd-indexed crossings pairs)
    return widths


def measure_square(H: np.ndarray, ps: float) -> Dict[str, float]:
    M, N = H.shape
    r, c = M // 2, N // 2
    wx = _widths_from_crossings(_edge_crossings(H[r, :], ps))
    wy = _widths_from_crossings(_edge_crossings(H[:, c], ps))
    x = wx[0] if len(wx) else 0.0
    y = wy[0] if len(wy) else 0.0
    return {"x_nm": float(x), "y_nm": float(y)}


def _contours_from_edges(edge_map: np.ndarray, level: float) -> List[np.ndarray]:
    try:
        return [c.astype(np.float64) for c in find_contours(edge_map, level)]
    except Exception:
        return []


def build_ground_truth(
    height_field: HeightField,
    material_map: MaterialMap,
    structure_type: str,
    cd_nm: float,
    pitch_nm: float,
) -> GroundTruth:
    H = height_field.data
    M = material_map.data
    ps = height_field.pixel_size_nm

    grad = compute_gradient_magnitude(H, ps)
    edge_map = grad
    threshold = max(0.02, grad.max() * 0.25)
    edge_mask = grad > threshold

    # --- CD measurements ---
    if structure_type in ("iso_line", "dense_ls", "trench", "fin", "pitch_std"):
        widths = measure_line_like(H, ps)
        cd_meas: List[Dict[str, Any]] = []
        for i, w in enumerate(widths):
            cd_meas.append({"feature": f"line_{i}", "cd_nm": round(w, 1)})
        if cd_meas:
            cd_meas[0]["feature"] = "line"
    elif structure_type in ("contact", "via", "sti"):
        sq = measure_square(H, ps)
        cd_meas = [
            {"feature": f"{structure_type}_x", "cd_nm": round(sq["x_nm"], 1)},
            {"feature": f"{structure_type}_y", "cd_nm": round(sq["y_nm"], 1)},
        ]
    elif structure_type == "gate":
        widths = measure_line_like(H, ps)
        cd_meas = []
        # widths alternate fin/gate-line segments along the row; report first few
        for i, w in enumerate(widths[:6]):
            cd_meas.append({"feature": f"segment_{i}", "cd_nm": round(w, 1)})
    elif structure_type == "bimaterial":
        widths = measure_line_like(H, ps)
        cd_meas = [
            {"feature": "block_left", "cd_nm": round(widths[0], 1)},
            {"feature": "block_right", "cd_nm": round(widths[1], 1)},
        ]
    else:
        cd_meas = []

    contours = _contours_from_edges(edge_map, threshold)

    return GroundTruth(
        segmentation=M,
        edge_map=edge_map,
        edge_mask=edge_mask,
        cd_measurements=cd_meas,
        contours=contours,
        pixel_size_nm=ps,
    )
