"""Topography engine (Phase 5.3 P1): surface normals + cos(theta)."""
from __future__ import annotations

from typing import Tuple

import numpy as np

from semicon.foundation.math_utils import surface_normals


def compute_cos_theta(height_field: np.ndarray, pixel_size_nm: float) -> np.ndarray:
    """cos(theta) of the surface normal w.r.t. the beam, clamped to [eps, 1]."""
    _, _, _, cos_theta = surface_normals(height_field, pixel_size_nm)
    return cos_theta


def compute_gradient_magnitude(height_field: np.ndarray, pixel_size_nm: float) -> np.ndarray:
    """|grad H| in nm/nm (used for edge detection)."""
    from semicon.foundation.math_utils import central_difference

    gy, gx = central_difference(height_field, pixel_size_nm)
    return np.sqrt(gx**2 + gy**2)
