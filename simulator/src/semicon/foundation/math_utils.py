"""Small shared numerical helpers (foundation).

Deterministic, vectorized, float64-preserving. No allocations of global state.
"""
from __future__ import annotations

import numpy as np

EPS = 1e-6


def clamp_cos(theta_cos: np.ndarray) -> np.ndarray:
    """Clamp cos(theta) into [EPS, 1] to avoid division-by-zero (Phase 5.3 P1)."""
    return np.clip(theta_cos, EPS, 1.0)


def central_difference(field: np.ndarray, pixel_size_nm: float):
    """Central-difference gradient of a 2D field with reflect padding.

    Returns (gy, gx) with gx = dH/dx (nm/nm), gy = dH/dy. Row=Y.
    """
    from scipy import ndimage

    pad = 1
    f = np.pad(field, pad, mode="reflect")
    gx = (f[1:-1, 2:] - f[1:-1, :-2]) / (2.0 * pixel_size_nm)
    gy = (f[2:, 1:-1] - f[:-2, 1:-1]) / (2.0 * pixel_size_nm)
    return gy, gx


def surface_normals(height: np.ndarray, pixel_size_nm: float, cos_theta_min: float = 0.7):
    """Surface normals + cos(theta) from a height field (Phase 5.3 P1).

    cosθ = nz = 1 / sqrt(1 + gx^2 + gy^2), clamped to [cos_theta_min, 1].

    cos_theta_min is a DG1 calibration decision: the universal SE yield
    model (P2) diverges as cosθ -> 0 on the near-vertical walls produced by
    discrete rasterization. Clamping the *effective* tilt to ~45.6 deg
    (cos 0.7) bounds all yields within the frozen [0, 10] postcondition
    while preserving monotonic topographic enhancement and edge contrast.
    Returns (nx, ny, nz, cos_theta).
    """
    gy, gx = central_difference(height, pixel_size_nm)
    denom = np.sqrt(1.0 + gx**2 + gy**2)
    nz = np.clip(1.0 / denom, cos_theta_min, 1.0)
    nx = -gx / denom
    ny = -gy / denom
    return nx, ny, nz, nz


def kernel_fwhm_px(kernel: np.ndarray) -> float:
    """Interpolated FWHM (in pixels) of a symmetric Gaussian kernel from its
    centre row, using linear crossings of the half-maximum level."""
    row = kernel[kernel.shape[0] // 2, :]
    peak = row.max()
    if peak <= 0:
        return 0.0
    half = peak / 2.0
    above = row >= half
    idx = np.where(above)[0]
    if len(idx) < 2:
        return float(len(idx))
    lo, hi = idx[0], idx[-1]
    # linear interpolation at the crossing points
    def cross_lo():
        if lo == 0:
            return 0.0
        f = (row[lo - 1] - half) / (row[lo - 1] - row[lo] + 1e-12)
        return lo - 1 + f

    def cross_hi():
        if hi == len(row) - 1:
            return float(len(row) - 1)
        f = (row[hi] - half) / (row[hi] - row[hi + 1] + 1e-12)
        return hi + f

    return float(cross_hi() - cross_lo())


def gaussian_kernel_2d(fwhm_nm: float, pixel_size_nm: float, radius_mult: float = 4.0) -> np.ndarray:
    """2D Gaussian PSF kernel, sum-normalised to exactly 1 (Phase 5.3 P7).

    sigma = fwhm / (2 * sqrt(2*ln2)) = fwhm / 2.35482
    Kernel size is the smallest odd size covering +/-radius_mult*sigma.
    """
    if fwhm_nm <= 0.0:
        raise ValueError(f"fwhm must be > 0, got {fwhm_nm}")
    if pixel_size_nm <= 0.0:
        raise ValueError("pixel_size_nm must be > 0")
    sigma = fwhm_nm / (2.0 * np.sqrt(2.0 * np.log(2.0)))
    sigma_px = sigma / pixel_size_nm
    radius_px = max(1, int(np.ceil(radius_mult * sigma_px)))
    size = 2 * radius_px + 1
    yy, xx = np.mgrid[-radius_px : radius_px + 1, -radius_px : radius_px + 1]
    k = np.exp(-(xx**2 + yy**2) / (2.0 * sigma_px**2))
    k = k / k.sum()
    return k


def distance_transform_binary(binary: np.ndarray, pixel_size_nm: float) -> np.ndarray:
    """Exact Euclidean distance transform scaled to nm (Phase 5.2 A10).

    Positive distance to the nearest background pixel; 0 on the object.
    """
    from scipy import ndimage

    dt = ndimage.distance_transform_edt(binary).astype(np.float64) * pixel_size_nm
    return dt
