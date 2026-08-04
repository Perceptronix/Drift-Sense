"""Variability engine (Phase 3.3 / Phase 5.2 A7-A9): overlay, LER, CDU.

Applies variability to the *deterministic* height field + material map
(I3 boundary). All operations are deterministic under the stage generator.

Mechanisms
----------
- Overlay: constant sub-pixel translation of H and material map (A8).
- LER: lateral warp of the height field along the surface normal by a
  random field with exponential autocorrelation (3-sigma = ler_3sigma_nm,
  correlation length = ler_xi_nm). The material map is warped by the same
  displacement so material and topographic edges stay aligned (A7).
- CDU: low-frequency warp (gaussian ACF, 3-sigma = cdu_sigma_nm,
  correlation cdu_xi_nm) modulating feature widths across the field (A9).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np
from scipy import ndimage

from semicon.foundation.datatypes import HeightField, MaterialMap
from semicon.foundation.math_utils import surface_normals
from semicon.geometry._variability.random_fields import exponential_random_field, gaussian_random_field


@dataclass(frozen=True)
class VariabilityRecord:
    ler_3sigma_nm: float
    ler_xi_nm: float
    cdu_sigma_nm: float
    cdu_xi_nm: float
    overlay_dx_nm: float
    overlay_dy_nm: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ler_3sigma_nm": self.ler_3sigma_nm,
            "ler_xi_nm": self.ler_xi_nm,
            "cdu_sigma_nm": self.cdu_sigma_nm,
            "cdu_xi_nm": self.cdu_xi_nm,
            "overlay_dx_nm": self.overlay_dx_nm,
            "overlay_dy_nm": self.overlay_dy_nm,
        }


def _warp_displacement(height: np.ndarray, pixel_size_nm: float, dx_field: np.ndarray, dy_field: np.ndarray) -> tuple:
    """Resample H (order 1) and material (order 0) by displacement fields."""
    M, N = height.shape
    ps = float(pixel_size_nm)
    rows = np.arange(M, dtype=np.float64) + 0.5
    cols = np.arange(N, dtype=np.float64) + 0.5
    # map_coordinates uses (row, col) = (y, x) index space
    coord_r = rows[:, None] - dy_field / ps
    coord_c = cols[None, :] - dx_field / ps
    return coord_r, coord_c


def apply_variability(
    height_field: HeightField,
    material_map: MaterialMap,
    config: Dict[str, Any],
    generator: np.random.Generator,
) -> tuple:
    """Return (HeightField, MaterialMap, VariabilityRecord)."""
    H = height_field.data.copy()
    M = material_map.data.copy()
    ps = height_field.pixel_size_nm
    shape = H.shape

    enabled = bool(config.get("enabled", True))
    dx = float(config.get("overlay_dx_nm", 0.0))
    dy = float(config.get("overlay_dy_nm", 0.0))
    ler_sigma = float(config.get("ler_3sigma_nm", 0.0))
    ler_xi = float(config.get("ler_xi_nm", 20.0))
    cdu_sigma = float(config.get("cdu_sigma_nm", 0.0))
    cdu_xi = float(config.get("cdu_xi_nm", 100.0))

    disp_x = np.zeros(shape, dtype=np.float64)
    disp_y = np.zeros(shape, dtype=np.float64)

    if enabled:
        # --- overlay: constant translation ---
        if abs(dx) > 1e-9 or abs(dy) > 1e-9:
            disp_x += dx
            disp_y += dy

        # --- LER: displacement along surface normal ---
        if ler_sigma > 0:
            nfield = exponential_random_field(shape, ler_xi, ps, generator, sigma=ler_sigma)
            _, _, nz, _ = surface_normals(H, ps)
            gx = np.gradient(H, ps, axis=1)
            gy = np.gradient(H, ps, axis=0)
            denom = np.sqrt(1.0 + gx**2 + gy**2)
            nx = -gx / denom
            ny = -gy / denom
            disp_x = disp_x + nx * nfield
            disp_y = disp_y + ny * nfield

        # --- CDU: low-frequency width modulation ---
        if cdu_sigma > 0:
            cfield = gaussian_random_field(shape, cdu_xi, ps, generator, sigma=cdu_sigma)
            gx = np.gradient(H, ps, axis=1)
            gy = np.gradient(H, ps, axis=0)
            denom = np.sqrt(1.0 + gx**2 + gy**2)
            nx = -gx / denom
            ny = -gy / denom
            disp_x = disp_x + nx * cfield
            disp_y = disp_y + ny * cfield

    # --- warp both arrays with the total displacement ---
    if np.any(np.abs(disp_x) > 1e-9) or np.any(np.abs(disp_y) > 1e-9):
        coord_r, coord_c = _warp_displacement(H, ps, disp_x, disp_y)
        H = ndimage.map_coordinates(H, np.stack([coord_r, coord_c]), order=1, mode="nearest")
        M = ndimage.map_coordinates(M, np.stack([coord_r, coord_c]), order=0, mode="nearest").astype(np.uint8)

    record = VariabilityRecord(
        ler_3sigma_nm=ler_sigma,
        ler_xi_nm=ler_xi,
        cdu_sigma_nm=cdu_sigma,
        cdu_xi_nm=cdu_xi,
        overlay_dx_nm=dx,
        overlay_dy_nm=dy,
    )
    return HeightField(data=H, pixel_size_nm=ps), MaterialMap(data=M, pixel_size_nm=ps), record
