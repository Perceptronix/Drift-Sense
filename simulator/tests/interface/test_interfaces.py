"""Interface tests I1-I8 (Phase 4.2; Phase 5.4 T1).

Each interface is exercised with real producer output -> real consumer
input, checking the frozen postconditions.
"""
from __future__ import annotations

import numpy as np
import pytest

from semicon.foundation.datatypes import (
    GroundTruth,
    HeightField,
    MaterialMap,
    PixelMask,
    SEMImage,
    YieldMaps,
)
from semicon.geometry import process, raster
from semicon.physics import degrade, formation, signal


def test_i1_raster_pixelmask(context):
    mask_set = raster.rasterize(context.library, "iso_line", 128.0, 128.0, 1.0, ss=2)
    pm = raster.to_pixel_mask_obj(mask_set, 1.0)
    assert isinstance(pm, PixelMask)
    assert pm.data.shape == (128, 128)
    assert set(np.unique(pm.data)) <= {0, 1}
    assert 0 < pm.data.sum()


def test_i2_geometry(context):
    masks = raster.rasterize(context.library, "dense_ls", 128.0, 128.0, 1.0, ss=2)
    H, M = process.build_geometry(masks, "dense_ls", 16.0, 40.0, 32.0, 1.0)
    assert isinstance(H, HeightField) and isinstance(M, MaterialMap)
    assert H.data.shape == M.data.shape == (128, 128)
    assert np.isfinite(H.data).all()
    assert set(np.unique(M.data)) <= set(range(7))


def test_i3_variability_feeds_i4(context):
    from semicon.geometry.variability import apply_variability

    masks = raster.rasterize(context.library, "iso_line", 128.0, 128.0, 1.0, ss=2)
    H, M = process.build_geometry(masks, "iso_line", 16.0, 40.0, None, 1.0)
    var_cfg = {"enabled": True, "ler_3sigma_nm": 1.0, "ler_xi_nm": 20.0, "overlay_dx_nm": 0.5, "overlay_dy_nm": 0.0, "cdu_sigma_nm": 0.0}
    Hv, Mv, _ = apply_variability(H, M, var_cfg, 5)
    assert Hv.data.shape == (128, 128)
    assert np.isfinite(Hv.data).all()
    y, _ = signal.compute_yields(Hv, Mv, context.materials, {})
    assert y.se_yield.shape == (128, 128)


def test_i4_yield_maps(context):
    masks = raster.rasterize(context.library, "iso_line", 128.0, 128.0, 1.0, ss=2)
    H, M = process.build_geometry(masks, "iso_line", 16.0, 40.0, None, 1.0)
    y, rec = signal.compute_yields(H, M, context.materials, {"edge_factor": 2.0})
    assert isinstance(y, YieldMaps)
    assert y.se_yield.min() >= 0.0 and y.se_yield.max() <= 10.0
    assert y.bse_yield.min() >= 0.0 and y.bse_yield.max() <= 1.0


def test_i5_degrade(context):
    masks = raster.rasterize(context.library, "iso_line", 128.0, 128.0, 1.0, ss=2)
    H, M = process.build_geometry(masks, "iso_line", 16.0, 40.0, None, 1.0)
    y, _ = signal.compute_yields(H, M, context.materials, {})
    d, rec = degrade.degrade_yields(y, {"probe_diameter_nm": 2.0, "noise_enabled": True, "counts_per_electron": 100.0}, 3)
    assert d.shape == (128, 128)
    assert np.isfinite(d).all()
    assert d.min() >= 0.0


def test_i6_formation(context):
    masks = raster.rasterize(context.library, "iso_line", 128.0, 128.0, 1.0, ss=2)
    H, M = process.build_geometry(masks, "iso_line", 16.0, 40.0, None, 1.0)
    y, _ = signal.compute_yields(H, M, context.materials, {})
    d, _ = degrade.degrade_yields(y, {"probe_diameter_nm": 2.0, "noise_enabled": False}, 3)
    img, fr = formation.form_image(d, 1.0, {"gain": 4000.0, "bit_depth": 16, "saturate": True})
    assert isinstance(img, SEMImage)
    assert img.data.dtype == np.uint16
    assert img.data.shape == (128, 128)
    assert img.data.min() >= 0 and img.data.max() <= 65535


def test_i7_ground_truth(context):
    from semicon.dataset.groundtruth import build_ground_truth

    masks = raster.rasterize(context.library, "iso_line", 128.0, 128.0, 1.0, ss=2)
    H, M = process.build_geometry(masks, "iso_line", 16.0, 40.0, None, 1.0)
    gt = build_ground_truth(H, M, "iso_line", 16.0, None)
    assert isinstance(gt, GroundTruth)
    assert gt.segmentation.shape == (128, 128)
    assert len(gt.cd_measurements) > 0


def test_i8_writer(context, tmp_path):
    from semicon.dataset.groundtruth import build_ground_truth
    from semicon.dataset.writer import finalize_dataset, write_sample

    masks = raster.rasterize(context.library, "iso_line", 128.0, 128.0, 1.0, ss=2)
    H, M = process.build_geometry(masks, "iso_line", 16.0, 40.0, None, 1.0)
    y, _ = signal.compute_yields(H, M, context.materials, {})
    d, _ = degrade.degrade_yields(y, {"probe_diameter_nm": 2.0, "noise_enabled": False}, 3)
    img, _ = formation.form_image(d, 1.0, {"gain": 4000.0, "bit_depth": 16, "saturate": True})
    gt = build_ground_truth(H, M, "iso_line", 16.0, None)
    arts = write_sample(tmp_path, 0, img, gt, H, M, {"structure": {}}, {"x": 1}, {}, write_aux=True)
    assert any(str(k).endswith("images/000000.tiff") for k in arts)
    idx = finalize_dataset(tmp_path, "demo", "0.1.0", [{"status": "OK"}], 42, "0.1.0", "dev")
    assert idx.exists()
    assert (tmp_path / "SHA256SUMS").exists()
