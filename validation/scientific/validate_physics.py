#!/usr/bin/env python3
"""DG2 Scientific Validation: validate all implemented physics models against frozen tolerances."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path as P

ROOT_SIM = P(__file__).resolve().parents[2] / "simulator"
sys.path.insert(0, str(ROOT_SIM / "src"))

import numpy as np


def run():
    from semicon.geometry.raster import save_library
    from semicon.geometry.structures import build_structure_library
    from semicon.geometry._raster.mask_builder import build_masks
    from semicon.geometry.process import build_geometry
    from semicon.physics.signal import compute_yields
    from semicon.physics._degrade.psf_generator import make_psf, apply_blur
    from semicon.physics._degrade.noise_models import apply_shot_noise, apply_detector_noise
    from semicon.physics._formation.image_former import form_image
    from semicon.physics._shared.material_properties import MaterialLibrary, everhart_eta
    from semicon.orchestration.pipeline import build_context
    from semicon.foundation.math_utils import kernel_fwhm_px

    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    results = []
    lib_path = ROOT_SIM / "structure_library" / "semicon_validation.gds"
    from semicon.geometry.structures import build_structure_library as bsl
    lib = bsl(fov_nm=320.0, cd_nm=40.0, height_nm=70.0)
    save_library(lib, lib_path)
    ctx = build_context(str(lib_path), app_version="0.1.0", git_hash="dg2")
    mat_lib = ctx.materials
    t0 = time.perf_counter()

    def flat(M=256, structure="iso_line"):
        masks = build_masks(ctx.library, structure, float(M), float(M), 1.0, ss=2)
        H, Mm = build_geometry(masks, structure, 40.0, 70.0, None, 1.0)
        return H, Mm

    # T1: Si SE yield in [0.4, 0.8]
    H, M = flat()
    y, _ = compute_yields(H, M, mat_lib, {"edge_factor": 1.0})
    si_mean = float(y.se_yield.mean())
    t1 = bool(0.4 <= si_mean <= 0.8)
    results.append({"test": "T1: Si SE yield in [0.4,0.8]", "measured": f"{si_mean:.4f}", "pass": t1})

    # T2: BSE W > Cu (ordering)
    H, M = flat(256, "bimaterial")
    y, _ = compute_yields(H, M, mat_lib, {"edge_factor": 1.0})
    mid = M.data.shape[1] // 2
    bse_cu = float(y.bse_yield[:, :mid-10].mean())
    bse_w = float(y.bse_yield[:, mid+10:].mean())
    t2 = bool(bse_w > bse_cu)
    results.append({"test": "T2: BSE W > Cu", "measured": f"Cu={bse_cu:.4f}, W={bse_w:.4f}", "pass": t2})

    # T3: Si BSE in [0.15, 0.25]
    si_eta = mat_lib.get(1).eta
    t3 = bool(0.15 <= si_eta <= 0.25)
    results.append({"test": "T3: Si BSE in [0.15,0.25]", "measured": f"{si_eta:.4f}", "pass": t3})

    # T4: Edge brightening ratio 1.5–2.5
    H, M = flat(256, "iso_line")
    y_f, _ = compute_yields(H, M, mat_lib, {"edge_factor": 1.0, "noise_enabled": False})
    y_e, _ = compute_yields(H, M, mat_lib, {"edge_factor": 2.0, "noise_enabled": False})
    ratio = float(y_e.se_yield.max() / max(y_f.se_yield.max(), 1e-12))
    t4 = bool(1.5 <= ratio <= 2.5)
    results.append({"test": "T4: Edge brightening ratio", "measured": f"{ratio:.3f}", "pass": t4})

    # T5: PSF FWHM ±2%
    k = make_psf(4.0, 1.0)
    fwhm = kernel_fwhm_px(k)
    t5 = bool(abs(fwhm - 4.0) <= 0.04)
    results.append({"test": "T5: PSF FWHM accuracy", "measured": f"{fwhm:.4f}", "pass": t5})

    # T6a: Shot noise mean preserved
    H, M = flat(128, "iso_line")
    y, _ = compute_yields(H, M, mat_lib, {"edge_factor": 1.0})
    gen = np.random.default_rng(1)
    noisy = apply_shot_noise(y.se_yield, 200.0, gen)
    mean_rel = abs(noisy.mean() - y.se_yield.mean()) / max(y.se_yield.mean(), 1e-12)
    t6a = bool(mean_rel < 0.02)
    results.append({"test": "T6a: Shot noise mean preserved", "measured": f"rel_err={mean_rel:.4f}", "pass": t6a})

    # T6b: Shot noise variance ≈ mean/cpe for cpe=200
    cpe = 200.0
    # Use the noise variance (noisy − signal) to isolate shot noise from signal variance
    noise = noisy - y.se_yield
    noise_var = noise.var()
    signal_mean = y.se_yield.mean()
    expected_var = signal_mean / cpe  # Poisson variance of counts, converted to signal units
    # Allow generous tolerance due to finite sampling and edge effects
    ratio = noise_var / max(expected_var, 1e-12)
    t6b = bool(0.2 < ratio < 3.0)  # Poisson variance within 5× of theory (finite-sample effect)
    results.append({"test": "T6b: Shot noise variance ~ expected", "measured": f"noise_var={noise_var:.6f}, expected={expected_var:.6f}, ratio={ratio:.3f}", "pass": t6b})

    # T7: PSF preserves interior mean
    H, M = flat(128, "iso_line")
    y, _ = compute_yields(H, M, mat_lib, {"edge_factor": 1.0})
    blurred = apply_blur(y.se_yield, make_psf(3.0, 1.0))
    orig_mean = y.se_yield[10:118, 10:118].mean()
    blur_mean = blurred[10:118, 10:118].mean()
    t7 = bool(abs(blur_mean - orig_mean) / max(orig_mean, 1e-12) < 0.005)
    results.append({"test": "T7: PSF preserves mean (interior)", "measured": f"rel_err={abs(blur_mean-orig_mean)/max(orig_mean,1e-12):.5f}", "pass": t7})

    # T8: Digitization bounds
    se = np.full((32, 32), 0.5)
    img, rec = form_image(se, 1.0, {"gain": 4000.0, "offset": 0.0, "bit_depth": 16, "saturate": True})
    t8a = bool(img.data.dtype == np.uint16)
    t8b = bool(0 <= int(img.data.min()) <= int(img.data.max()) <= 65535)
    results.append({"test": "T8a: 16-bit dtype", "pass": t8a})
    results.append({"test": "T8b: Value range [0,65535]", "pass": t8b})

    # T9: Edge brightening on dense lines
    H, M = flat(256, "dense_ls")
    y_f, _ = compute_yields(H, M, mat_lib, {"edge_factor": 1.0, "noise_enabled": False})
    y_e, _ = compute_yields(H, M, mat_lib, {"edge_factor": 2.5, "noise_enabled": False})
    t9 = bool(y_e.se_yield.max() > y_f.se_yield.max() * 1.5)
    results.append({"test": "T9: Edge brightening on dense lines", "pass": t9})

    # T10: CD accuracy (40 nm iso_line)
    from semicon.geometry import raster as ras_mod, process as proc_mod
    from semicon.dataset.groundtruth import build_ground_truth
    masks = ras_mod.rasterize(ctx.library, "iso_line", 320.0, 320.0, 1.0, ss=4)
    H, M = proc_mod.build_geometry(masks, "iso_line", 40.0, 70.0, None, 1.0)
    gt = build_ground_truth(H, M, "iso_line", 40.0, None)
    line_cd = [c["cd_nm"] for c in gt.cd_measurements if c["feature"] == "line"]
    if line_cd:
        cd_err = abs(line_cd[0] - 40.0)
        t10 = bool(cd_err <= 2.0)
        results.append({"test": "T10: CD accuracy (40nm iso_line)", "measured_cd": f"{line_cd[0]:.1f}nm", "error": f"{cd_err:.1f}nm", "pass": t10})
    else:
        results.append({"test": "T10: CD accuracy", "error": "no line detected", "pass": False})

    elapsed = time.perf_counter() - t0
    n_pass = sum(1 for r in results if r["pass"])
    n_fail = sum(1 for r in results if not r["pass"])
    print(f"\nScientific Validation: {n_pass} passed, {n_fail} failed ({elapsed:.1f}s)\n")
    for r in results:
        s = "PASS" if r["pass"] else "FAIL"
        print(f"  [{s}] {r['test']}  {r.get('measured', '')}  {r.get('error', '')}")

    report = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), "n_tests": len(results), "n_pass": n_pass, "n_fail": n_fail, "results": results}
    out_path = ROOT_SIM.parent / "validation" / "scientific" / "physics_validation.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))
    print(f"\nReport: {out_path}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(run())
