"""Yield computation (Phase 5.3 P2-P4).

P2  universal SE1:  delta = delta0 * cos(theta)^(-f) * exp(Lambda*(1-cos(theta)))
P3  BSE:            eta = Everhart polynomial on Z (precomputed per material)
P4  SE2:            delta2 = g_bulk * eta * delta1
"""
from __future__ import annotations

import numpy as np

from semicon.physics._shared.material_properties import MaterialLibrary


def compute_yields(
    cos_theta: np.ndarray,
    material_map: np.ndarray,
    library: MaterialLibrary,
) -> tuple:
    """Return (se1, bse, se2) maps as float64 (M,N)."""
    mat = material_map.astype(np.int64)
    delta0 = library.delta0_array()
    lam = library.lambda_array()
    tilt = library.tilt_array()
    eta_arr = library.eta_array()
    g = library.g_bulk_array()

    d0 = np.take(delta0, mat)
    Lambda = np.take(lam, mat)
    f = np.take(tilt, mat)
    eta = np.take(eta_arr, mat)
    gb = np.take(g, mat)

    c = cos_theta  # already clamped
    se1 = d0 * np.power(c, -f) * np.exp(Lambda * (1.0 - c))
    se2 = gb * eta * se1
    return se1, eta, se2
