"""Edge brightening (Phase 5.3 P5).

Multiplies the SE signal near topographic edges by a smooth ramp from 1.0
(at the edge-band boundary) to edge_factor (at the edge crest). The band
half-width is edge_width_nm; the ramp is the square of a cosine window so
that no discontinuities are introduced and mean signal far from edges is
unchanged.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

from semicon.physics._signal.topography_engine import compute_gradient_magnitude


def edge_band(
    height_field: np.ndarray,
    pixel_size_nm: float,
    edge_threshold: float = 0.05,
) -> np.ndarray:
    """Binary mask of topographic edges (|grad H| > threshold)."""
    grad = compute_gradient_magnitude(height_field, pixel_size_nm)
    return (grad > edge_threshold).astype(np.uint8)


def apply_edge_effects(
    se_map: np.ndarray,
    height_field: np.ndarray,
    pixel_size_nm: float,
    edge_factor: float = 2.0,
    edge_width_nm: float = 8.0,
    edge_threshold: float = 0.05,
) -> np.ndarray:
    """Return SE map with edge brightening applied (P5)."""
    if edge_factor <= 1.0:
        return se_map
    grad = compute_gradient_magnitude(height_field, pixel_size_nm)
    edges = (grad > edge_threshold).astype(np.uint8)
    if not edges.any():
        return se_map
    w_px = max(1, int(round(edge_width_nm / pixel_size_nm)))
    dist = ndimage.distance_transform_edt(1 - edges) * pixel_size_nm  # nm from edge
    # ramp: factor at the edge crest (dist=0), decays to 1.0 over edge_width
    t = np.clip(dist / max(edge_width_nm, 1e-6), 0.0, 1.0)
    ramp = 1.0 + (edge_factor - 1.0) * (1.0 - t) ** 2
    return se_map * ramp
