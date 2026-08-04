"""2.5D column-model process simulator (Phase 3.2 / Phase 5.2 A2-A6).

The substrate is an MxN array of vertical columns. Each column has a top
surface height (nm above the substrate backside) and a top-surface material.
Operations (deposit / etch / planarize) are vectorized and deterministic.

Height convention: H = height of the top surface above the substrate
backside; a bare substrate has H = substrate_top_nm everywhere.
"""
from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from semicon.foundation.datatypes import HeightField, MaterialMap, PixelMask
from semicon.foundation.math_utils import distance_transform_binary


class ProcessSimulator:
    def __init__(
        self,
        shape: Tuple[int, int],
        pixel_size_nm: float,
        substrate_material: int = 1,
        substrate_top_nm: float = 100.0,
    ) -> None:
        self.shape = tuple(shape)
        self.pixel_size_nm = float(pixel_size_nm)
        self.substrate_material = int(substrate_material)
        self.substrate_top_nm = float(substrate_top_nm)
        self.H = np.full(shape, self.substrate_top_nm, dtype=np.float64)
        self.mat = np.full(shape, self.substrate_material, dtype=np.uint8)

    # ------------------------------------------------------------------
    # primitive operations
    # ------------------------------------------------------------------
    def _mask(self, pattern: Optional[np.ndarray]) -> np.ndarray:
        if pattern is None:
            return np.ones(self.shape, dtype=bool)
        p = np.asarray(pattern)
        if p.dtype != bool:
            p = p.astype(bool)
        if p.shape != self.shape:
            raise ValueError(f"pattern shape {p.shape} != {self.shape}")
        return p

    def deposit(self, material: int, thickness_nm: float, pattern: Optional[np.ndarray] = None) -> None:
        """Uniform conformal deposition of thickness_nm within the pattern."""
        if thickness_nm < 0:
            raise ValueError("deposition thickness must be >= 0")
        mask = self._mask(pattern)
        self.H[mask] += thickness_nm
        self.mat[mask] = material

    def etch(self, depth_nm: float, pattern: Optional[np.ndarray] = None, sidewall_angle_deg: float = 90.0) -> None:
        """Etch depth_nm inside the pattern with trapezoidal sidewalls (A3).

        sidewall_angle_deg is measured from the horizontal; 90.0 is vertical.
        Near the pattern boundary the cut depth is reduced to
        min(depth, dist_to_boundary * tan(angle)), forming the slope.
        The etched surface becomes the substrate material (exposed layer).
        """
        if depth_nm <= 0:
            return
        mask = self._mask(pattern)
        top = self.H.copy()
        angle = float(sidewall_angle_deg)
        if angle >= 89.5:
            new_h = top - depth_nm
        else:
            slope = np.tan(np.deg2rad(angle))
            ds = distance_transform_binary(mask, self.pixel_size_nm)
            cut = np.minimum(depth_nm, ds * slope)
            new_h = top - cut
        new_h = np.minimum(new_h, top - 1e-12)
        self.H[mask] = new_h[mask]
        # exposed etch bottom/sidewall -> substrate material (simplified column model)
        self.mat[mask] = self.substrate_material

    def planarize(self, target_height_nm: float, pattern: Optional[np.ndarray] = None) -> None:
        """CMP-like planarization: clip height to target within pattern (A6)."""
        mask = self._mask(pattern)
        np.minimum(self.H, target_height_nm, out=self.H, where=mask)

    def corner_round(self, radius_nm: float, pattern: Optional[np.ndarray] = None) -> None:
        """Isotropic corner rounding (A4): median-smooth heights in the
        pattern's boundary band. radius <= 0 is a no-op."""
        if radius_nm <= 0:
            return
        from scipy import ndimage

        mask = self._mask(pattern)
        r = max(1, int(round(radius_nm / self.pixel_size_nm)))
        # boundary band = 1 within r px inside and outside the mask edge
        inner = ndimage.binary_dilation(mask, iterations=r).astype(bool)
        outer = ndimage.binary_dilation(~mask, iterations=r).astype(bool)
        band = (inner & outer) | mask
        smoothed = ndimage.median_filter(self.H, size=2 * r + 1)
        blend = band & (mask | inner)  # only on / near the feature
        self.H[blend] = smoothed[blend]

    # ------------------------------------------------------------------
    # outputs (Phase 3.2 / I2)
    # ------------------------------------------------------------------
    def height_field(self) -> HeightField:
        return HeightField(data=self.H.copy(), pixel_size_nm=self.pixel_size_nm)

    def material_map(self) -> MaterialMap:
        return MaterialMap(data=self.mat.copy(), pixel_size_nm=self.pixel_size_nm)
