"""Unit tests: physics engine (I4-I6; Phase 5.3 P1-P10)."""
from __future__ import annotations

import numpy as np
import pytest

from semicon.foundation.datatypes import HeightField, MaterialMap, YieldMaps
from semicon.physics._degrade.psf_generator import make_psf
from semicon.physics._signal.signal_assembler import assemble_signal
from semicon.physics._shared.material_properties import MaterialLibrary


def _flat_si(shape=(64, 64)):
    H = HeightField(data=np.full(shape, 100.0), pixel_size_nm=1.0)
    M = MaterialMap(data=np.full(shape, 1, dtype=np.uint8), pixel_size_nm=1.0)
    return H, M


def test_flat_si_yield_is_delta0():
    H, M = _flat_si()
    lib = MaterialLibrary()
    se, bse, rec = assemble_signal(H.data, M.data, 1.0, lib, {})
    expected = lib.get(1).delta0 * (1.0 + lib.get(1).g_bulk * lib.get(1).eta)
    assert se.mean() == pytest.approx(expected, rel=0.02)


def test_se2_boost():
    """Flat Si total SE = delta0 + g_bulk*eta*delta0."""
    H, M = _flat_si()
    lib = MaterialLibrary()
    se, bse, _ = assemble_signal(H.data, M.data, 1.0, lib, {})
    expected = lib.get(1).delta0 * (1.0 + lib.get(1).g_bulk * lib.get(1).eta)
    assert se.mean() == pytest.approx(expected, rel=0.02)


def test_bse_material_contrast():
    H, M = _flat_si()
    lib = MaterialLibrary()
    M2 = MaterialMap(data=np.full((64, 64), 5, dtype=np.uint8), pixel_size_nm=1.0)
    _, bse_w, _ = assemble_signal(H.data, M2.data, 1.0, lib, {})
    _, bse_si, _ = assemble_signal(H.data, M.data, 1.0, lib, {})
    assert bse_w.mean() > bse_si.mean()


def test_se_material_ordering():
    H, M = _flat_si()
    lib = MaterialLibrary()
    se_cu, _, _ = assemble_signal(H.data, MaterialMap(data=np.full((64, 64), 4, np.uint8), pixel_size_nm=1.0).data, 1.0, lib, {})
    se_si, _, _ = assemble_signal(H.data, M.data, 1.0, lib, {})
    assert se_cu.mean() < se_si.mean()


def test_topographic_boost():
    """A 45 deg slope boosts SE vs flat."""
    H = HeightField(data=np.tile(np.arange(64, dtype=np.float64), (64, 1)) * 1.0 + 100.0, pixel_size_nm=1.0)
    M = MaterialMap(data=np.full((64, 64), 1, np.uint8), pixel_size_nm=1.0)
    lib = MaterialLibrary()
    se_slope, _, _ = assemble_signal(H.data, M.data, 1.0, lib, {"edge_factor": 1.0})
    se_flat, _, _ = assemble_signal(np.full((64, 64), 100.0), M.data, 1.0, lib, {"edge_factor": 1.0})
    assert se_slope.mean() > se_flat.mean()


def test_edge_effects_increase_edges():
    H = HeightField(data=np.pad(np.zeros((32, 64)) + 150.0, ((16, 16), (0, 0))), pixel_size_nm=1.0)
    M = MaterialMap(data=np.full((64, 64), 1, np.uint8), pixel_size_nm=1.0)
    lib = MaterialLibrary()
    se_flat, _, _ = assemble_signal(H.data, M.data, 1.0, lib, {"edge_factor": 1.0})
    se_edge, _, _ = assemble_signal(H.data, M.data, 1.0, lib, {"edge_factor": 2.0})
    # the step adds strong extra signal at edges
    assert se_edge.max() > se_flat.max() * 1.3


def test_yield_map_postconditions():
    from semicon.geometry.structures import build_structure_library
    from semicon.geometry._raster.mask_builder import build_masks
    from semicon.geometry.process import build_geometry
    from semicon.physics.signal import compute_yields

    lib = build_structure_library(fov_nm=128.0)
    masks = build_masks(lib, "dense_ls", 128.0, 128.0, 1.0, ss=2)
    H, M = build_geometry(masks, "dense_ls", 16.0, 40.0, 32.0, 1.0)
    y, _ = compute_yields(H, M, MaterialLibrary(), {"edge_factor": 2.0, "noise_enabled": True})
    assert y.se_yield.min() >= 0.0
    assert y.se_yield.max() <= 10.0
    assert y.bse_yield.min() >= 0.0
    assert y.bse_yield.max() <= 1.0


def test_psf_sum_one():
    k = make_psf(3.0, 1.0)
    assert k.sum() == pytest.approx(1.0, abs=1e-12)


def test_blur_preserves_mean():
    from semicon.physics._degrade.psf_generator import apply_blur

    sig = np.random.default_rng(0).random((64, 64)).astype(np.float64) + 1.0
    k = make_psf(2.0, 1.0)
    blurred = apply_blur(sig, k)
    # reflect padding conserves the mean to ~0.03% (no systematic DC shift)
    assert blurred.mean() == pytest.approx(sig.mean(), rel=2e-3)


def test_shot_noise_mean_and_variance():
    from semicon.physics._degrade.noise_models import apply_shot_noise

    gen = np.random.default_rng(1)
    cpe = 100.0
    sig = np.full((256, 256), 0.5)
    noisy = apply_shot_noise(sig, cpe, gen)
    assert noisy.mean() == pytest.approx(0.5, rel=0.01)
    # Poisson: variance of counts ~ mean count -> var(signal) ~ mean/cpe
    var = noisy.var()
    assert var == pytest.approx(0.5 / cpe, rel=0.15)


def test_detector_noise_sigma():
    from semicon.physics._degrade.noise_models import apply_detector_noise

    gen = np.random.default_rng(2)
    sig = np.zeros((256, 256))
    noisy = apply_detector_noise(sig, 0.05, gen)
    assert noisy.std() == pytest.approx(0.05, rel=0.05)


def test_degrade_deterministic():
    from semicon.physics.degrade import degrade_yields

    y = YieldMaps(se_yield=np.full((32, 32), 0.5), bse_yield=np.zeros((32, 32)), pixel_size_nm=1.0)
    cfg = {"probe_diameter_nm": 2.0, "noise_enabled": True, "counts_per_electron": 100.0}
    a, _ = degrade_yields(y, cfg, 5)
    b, _ = degrade_yields(y, cfg, 5)
    assert np.array_equal(a, b)


def test_digitization_bounds():
    from semicon.physics.formation import form_image

    sig = np.array([[0.1, 0.5, 1.0, 2.0, 5.0]])
    img, rec = form_image(sig, 1.0, {"gain": 1000.0, "offset": 0.0, "bit_depth": 8, "saturate": True})
    assert img.data.dtype == np.uint8
    assert img.data.max() <= 255
    assert img.data.min() >= 0
    # values 500,1000,2000,5000 clip to 255 -> 4 of 5 pixels saturate
    assert rec.saturation_fraction == pytest.approx(4 / 5, abs=1e-9)


def test_digitization_round_half_even():
    from semicon.physics.formation import form_image

    # 2.5 * gain -> round half even
    sig = np.array([[0.0025]])
    img, _ = form_image(sig, 1.0, {"gain": 1000.0, "offset": 0.0, "bit_depth": 8, "saturate": True})
    assert img.data[0, 0] == 2  # round-half-even


def test_noise_disabled_identity_signal():
    from semicon.physics.degrade import degrade_yields

    y = YieldMaps(se_yield=np.full((32, 32), 0.5), bse_yield=np.zeros((32, 32)), pixel_size_nm=1.0)
    cfg = {"probe_diameter_nm": 1e-6, "noise_enabled": False}
    a, _ = degrade_yields(y, cfg, 1)
    assert np.allclose(a, 0.5, atol=1e-9)
