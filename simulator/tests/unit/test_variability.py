"""Unit tests: variability engine (I3; Phase 3.3 A7-A9)."""
from __future__ import annotations

import numpy as np

from semicon.foundation.datatypes import HeightField, MaterialMap
from semicon.geometry.variability import apply_variability


def _flat():
    H = HeightField(data=np.full((64, 64), 100.0), pixel_size_nm=1.0)
    M = MaterialMap(data=np.full((64, 64), 1, dtype=np.uint8), pixel_size_nm=1.0)
    return H, M


def test_disabled_identity():
    H, M = _flat()
    cfg = {"enabled": False, "overlay_dx_nm": 3.0}
    H2, M2, rec = apply_variability(H, M, cfg, 1)
    assert np.array_equal(H2.data, H.data)
    assert np.array_equal(M2.data, M.data)


def test_overlay_shifts():
    H, M = _flat()
    cfg = {"enabled": True, "overlay_dx_nm": 5.0, "overlay_dy_nm": 0.0,
           "ler_3sigma_nm": 0.0, "cdu_sigma_nm": 0.0}
    H2, M2, rec = apply_variability(H, M, cfg, 1)
    # uniform field is invariant under translation
    assert np.allclose(H2.data, H.data)


def test_deterministic():
    H = HeightField(data=np.pad(np.zeros((32, 64)) + 150.0, ((16, 16), (0, 0))), pixel_size_nm=1.0)
    M = MaterialMap(data=np.full((64, 64), 1, dtype=np.uint8), pixel_size_nm=1.0)
    cfg = {"enabled": True, "ler_3sigma_nm": 2.0, "ler_xi_nm": 20.0, "overlay_dx_nm": 0.5}
    H1, M1, _ = apply_variability(H, M, cfg, 7)
    H2, M2, _ = apply_variability(H, M, cfg, 7)
    assert np.array_equal(H1.data, H2.data)
    assert np.array_equal(M1.data, M2.data)


def test_seed_changes_output():
    # LER warps edges; a flat field has no edges, so use a stepped field
    H = HeightField(data=np.pad(np.zeros((32, 64)) + 150.0, ((16, 16), (0, 0))), pixel_size_nm=1.0)
    M = MaterialMap(data=np.full((64, 64), 1, dtype=np.uint8), pixel_size_nm=1.0)
    cfg = {"enabled": True, "ler_3sigma_nm": 2.0, "ler_xi_nm": 20.0}
    H1, _, _ = apply_variability(H, M, cfg, 1)
    H2, _, _ = apply_variability(H, M, cfg, 2)
    assert not np.array_equal(H1.data, H2.data)


def test_record_contents():
    H, M = _flat()
    cfg = {"enabled": True, "ler_3sigma_nm": 1.5, "ler_xi_nm": 20.0,
           "overlay_dx_nm": 1.0, "overlay_dy_nm": -1.0}
    _, _, rec = apply_variability(H, M, cfg, 3)
    d = rec.to_dict()
    assert d["ler_3sigma_nm"] == 1.5
    assert d["overlay_dx_nm"] == 1.0
    assert d["overlay_dy_nm"] == -1.0
