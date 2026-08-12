"""PSF generation + blur application (Phase 5.3 P7).

The beam PSF is a Gaussian whose FWHM equals the probe diameter. The kernel
is sum-normalised to exactly 1 (mean-preserving). Blur is applied with FFT
convolution, 'same' output shape.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import fftconvolve

from semicon.foundation.math_utils import gaussian_kernel_2d, kernel_fwhm_px


def make_psf(probe_diameter_nm: float, pixel_size_nm: float, radius_mult: float = 4.0) -> np.ndarray:
    return gaussian_kernel_2d(probe_diameter_nm, pixel_size_nm, radius_mult=radius_mult)


def apply_blur(field: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """FFT convolution, same shape, float64 preserved.

    The field is reflect-padded by the kernel half-size before the FFT so the
    mean is conserved (no DC shift) even at the image borders (frozen
    requirement: 'no systematic DC shift').
    """
    kh, kw = kernel.shape
    ph, pw = kh // 2, kw // 2
    if ph == 0 and pw == 0:
        return field
    padded = np.pad(field, ((ph, ph), (pw, pw)), mode="reflect")
    conv = fftconvolve(padded, kernel, mode="same")
    return conv[ph : ph + field.shape[0], pw : pw + field.shape[1]]
