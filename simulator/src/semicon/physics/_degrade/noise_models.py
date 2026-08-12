"""Noise models (Phase 5.3 P8-P9).

P8 shot noise: the SE signal is interpreted as a mean electron count per
pixel via ``counts_per_electron`` (electrons per unit yield); a Poisson
sample is drawn and converted back to signal units, so variance = mean/N.
P9 detector noise: additive zero-mean Gaussian with standard deviation
``detector_noise_sigma`` in the same signal units.

Both are deterministic under the passed Generator.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np


def apply_shot_noise(signal: np.ndarray, counts_per_electron: float, generator: np.random.Generator) -> np.ndarray:
    if counts_per_electron <= 0:
        raise ValueError("counts_per_electron must be > 0")
    means = np.maximum(signal * counts_per_electron, 0.0)
    counts = generator.poisson(means)
    return (counts / counts_per_electron).astype(np.float64)


def apply_detector_noise(signal: np.ndarray, sigma: float, generator: np.random.Generator) -> np.ndarray:
    if sigma <= 0:
        return signal
    return signal + generator.normal(0.0, sigma, size=signal.shape)


def degrade_signal(
    se_map: np.ndarray,
    config: Dict[str, Any],
    generator: np.random.Generator,
    kernel: np.ndarray,
) -> tuple:
    """Full I5 chain: PSF blur -> shot noise -> detector noise.

    Returns (degraded, DegradeRecord-dict).
    """
    from semicon.physics._degrade.psf_generator import apply_blur

    cpe = float(config.get("counts_per_electron", 200.0))
    dn_sigma = float(config.get("detector_noise_sigma", 0.02))
    noise_enabled = bool(config.get("noise_enabled", True))

    blurred = apply_blur(se_map, kernel)
    if noise_enabled:
        blurred = apply_shot_noise(blurred, cpe, generator)
        blurred = apply_detector_noise(blurred, dn_sigma, generator)
    blurred = np.clip(blurred, 0.0, None)
    from semicon.foundation.math_utils import kernel_fwhm_px

    record = {
        "counts_per_electron": cpe,
        "detector_noise_sigma": dn_sigma,
        "noise_enabled": noise_enabled,
        "psf_fwhm_px": kernel_fwhm_px(kernel),
    }
    return blurred, record
