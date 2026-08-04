"""Unit tests: shared math utilities."""
from __future__ import annotations

import numpy as np
import pytest

from semicon.foundation.math_utils import (
    central_difference,
    clamp_cos,
    gaussian_kernel_2d,
    surface_normals,
)


def test_gaussian_kernel_sums_to_one():
    k = gaussian_kernel_2d(3.0, 1.0)
    assert k.sum() == pytest.approx(1.0, abs=1e-12)


def test_gaussian_kernel_fwhm():
    """Kernel FWHM (in nm) should match the input probe diameter ~2%."""
    from semicon.foundation.math_utils import kernel_fwhm_px

    k = gaussian_kernel_2d(4.0, 1.0)
    fwhm = kernel_fwhm_px(k)
    assert fwhm == pytest.approx(4.0, rel=0.02)


def test_gaussian_kernel_odd_symmetric():
    k = gaussian_kernel_2d(3.0, 1.0)
    assert k.shape[0] == k.shape[1]
    assert k.shape[0] % 2 == 1
    assert np.allclose(k, k.T, atol=1e-12)


def test_surface_normals_flat():
    H = np.full((64, 64), 100.0)
    nx, ny, nz, cos = surface_normals(H, 1.0)
    assert np.allclose(cos, 1.0, atol=1e-9)
    assert np.allclose(nx, 0.0, atol=1e-9)


def test_surface_normals_45deg():
    """A 45-degree slope has cos(theta) = cos(45 deg)."""
    H = np.arange(64, dtype=np.float64).reshape(-1, 1) + np.zeros((64, 64))
    _, _, _, cos = surface_normals(H, 1.0)
    assert cos[32, 32] == pytest.approx(np.cos(np.pi / 4), rel=0.01)


def test_clamp_cos():
    x = np.array([-0.5, 0.0, 0.5, 1.5])
    c = clamp_cos(x)
    assert c.min() >= 1e-6
    assert c.max() <= 1.0


def test_central_difference_linear():
    H = np.arange(64, dtype=np.float64).reshape(-1, 1) + np.zeros((64, 64))
    gy, gx = central_difference(H, 1.0)
    assert np.allclose(gx, 0.0, atol=1e-9)
    assert np.allclose(gy[32], 1.0, atol=1e-9)
