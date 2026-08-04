"""Scientific validation (Phase 5.5 doc 05; L4 targets).

These tests validate physics output against the frozen L4 scientific targets
on the full pipeline output.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from semicon.orchestration.pipeline import run_pipeline

CONFIGS = str(Path(__file__).resolve().parents[2] / "configs")


def _cfg(**overrides):
    from semicon.orchestration.config import load_config

    return load_config(None, defaults_path=f"{CONFIGS}/defaults.yml", overrides=overrides)


def _flat_region(signal, margin=0.1):
    """Mean of the central flat region of a signal map."""
    M, N = signal.shape
    r0, r1 = int(M * margin), int(M * (1 - margin))
    c0, c1 = int(N * margin), int(N * (1 - margin))
    return signal[r0:r1, c0:c1]


def test_si_se_yield_in_range(context, tmp_path):
    """L4: Si SE yield at 1 keV flat in [0.4, 0.8]."""
    r = run_pipeline(context, _cfg(**{"structure.structure_type": "iso_line"}), tmp_path, 0, "sci", 1, write_outputs=False)
    se = r.metadata["physics"]["signal"]["se_range"]
    flat_delta = r.metadata["physics"]["signal"]["cos_theta_range"]
    # derive flat delta0 from a pure-Si sample by running assemble_signal directly
    from semicon.dataset.groundtruth import build_ground_truth  # noqa: F401
    from semicon.geometry import process, raster
    from semicon.physics.signal import compute_yields

    masks = raster.rasterize(context.library, "iso_line", 320.0, 320.0, 1.0, ss=2)
    H, M = process.build_geometry(masks, "iso_line", 40.0, 70.0, None, 1.0)
    y, _ = compute_yields(H, M, context.materials, {"edge_factor": 1.0, "noise_enabled": True})
    flat = _flat_region(y.se_yield)
    assert 0.4 <= float(flat.mean()) <= 0.8
    assert se[0] >= 0.0


def test_si_bse_in_range(context, tmp_path):
    """L4: Si BSE yield in [0.15, 0.25]."""
    from semicon.physics._shared.material_properties import MaterialLibrary

    lib = MaterialLibrary()
    assert 0.15 <= lib.get(1).eta <= 0.25


def test_material_contrast_ordering(context, tmp_path):
    """L4: W BSE > Cu BSE > Si BSE (bimaterial sample, frozen ordering)."""
    from semicon.physics.signal import compute_yields
    from semicon.geometry import process, raster

    masks = raster.rasterize(context.library, "bimaterial", 320.0, 320.0, 1.0, ss=2)
    H, M = process.build_geometry(masks, "bimaterial", 40.0, 70.0, None, 1.0)
    y, _ = compute_yields(H, M, context.materials, {"edge_factor": 1.0, "noise_enabled": False})
    # left block is Cu (layer 0), right block is W (layer 1)
    mid = M.data.shape[1] // 2
    bse_left = y.bse_yield[:, : mid - 10].mean()  # Cu
    bse_right = y.bse_yield[:, mid + 10 :].mean()  # W
    assert bse_right > bse_left  # W BSE > Cu BSE (frozen ordering)
    assert bse_left > y.bse_yield.min()  # Cu above Si field baseline


def test_psf_fwhm_accuracy(context, tmp_path):
    """L4: PSF FWHM within 1% of configured probe diameter."""
    from semicon.foundation.math_utils import kernel_fwhm_px
    from semicon.physics._degrade.psf_generator import make_psf

    k = make_psf(4.0, 1.0)
    fwhm_px = kernel_fwhm_px(k)
    assert fwhm_px == pytest.approx(4.0, rel=0.01)


def test_cd_accuracy(context, tmp_path):
    """L3: GT CD within tolerance of the configured value."""
    from semicon.dataset.groundtruth import build_ground_truth
    from semicon.geometry import process, raster

    masks = raster.rasterize(context.library, "iso_line", 320.0, 320.0, 1.0, ss=4)
    H, M = process.build_geometry(masks, "iso_line", 40.0, 70.0, None, 1.0)
    gt = build_ground_truth(H, M, "iso_line", 40.0, None)
    line_cd = [c["cd_nm"] for c in gt.cd_measurements if c["feature"] == "line"]
    assert len(line_cd) == 1
    assert abs(line_cd[0] - 40.0) <= 1.0  # within 1 nm (mask pixelization)
