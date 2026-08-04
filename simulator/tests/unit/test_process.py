"""Unit tests: process simulator + recipes (I2)."""
from __future__ import annotations

import numpy as np
import pytest

from semicon.geometry._process.process_simulator import ProcessSimulator
from semicon.geometry._raster.mask_builder import MaskSet
from semicon.geometry.process import build_geometry


def _sim():
    return ProcessSimulator((64, 64), 1.0, substrate_material=1, substrate_top_nm=100.0)


def _center_mask(w: int = 10) -> np.ndarray:
    m = np.zeros((64, 64), dtype=np.uint8)
    m[:, 32 - w // 2 : 32 + w // 2] = 1
    return m


def test_deposit_increases_height():
    sim = _sim()
    mask = _center_mask()
    sim.deposit(6, 50.0, pattern=mask)
    assert np.allclose(sim.H[mask.astype(bool)], 150.0)
    assert np.all(sim.mat[mask.astype(bool)] == 6)
    assert np.all(sim.H[~mask.astype(bool)] == 100.0)


def test_etch_creates_trench():
    sim = _sim()
    mask = _center_mask()
    sim.etch(40.0, pattern=mask, sidewall_angle_deg=90.0)
    assert np.allclose(sim.H[mask.astype(bool)], 60.0)


def test_etch_sidewall_slope():
    sim = _sim()
    # a 56 px wide mask centred on a 64 px field
    mask = np.zeros((64, 64), dtype=np.uint8)
    mask[:, 4:60] = 1
    sim.etch(20.0, pattern=mask, sidewall_angle_deg=45.0)
    # centre is 28 nm from the boundary >= depth/tan(45)=20 -> full depth (80 nm);
    # the boundary column (ds=0) is not etched at all
    assert sim.H[32, 32] == pytest.approx(80.0, abs=1.0)
    assert sim.H[32, 4] == pytest.approx(100.0, abs=1.0)
    # a mid column is partially etched (slope)
    assert 80.0 < sim.H[32, 4 + 10] < 100.0


def test_planarize_clips():
    sim = _sim()
    sim.deposit(4, 80.0, pattern=None)
    sim.planarize(120.0)
    assert sim.H.max() == pytest.approx(120.0)


def test_build_geometry_all_types():
    from semicon.geometry.structures import build_structure_library
    from semicon.geometry._raster.mask_builder import build_masks

    lib = build_structure_library(fov_nm=128.0, cd_nm=16.0, height_nm=40.0)
    for s in lib.structures:
        masks = build_masks(lib, s.name, 128.0, 128.0, 1.0, ss=2)
        H, M = build_geometry(masks, s.name, 16.0, 40.0, 32.0, 1.0)
        assert H.data.shape == (128, 128)
        assert M.data.shape == (128, 128)
        assert np.isfinite(H.data).all()


def test_build_geometry_unknown_type():
    masks = MaskSet(layer_masks={0: np.ones((8, 8), np.uint8)}, union=np.ones((8, 8), np.uint8))
    with pytest.raises(KeyError):
        build_geometry(masks, "nope", 16.0, 40.0, None, 1.0)
