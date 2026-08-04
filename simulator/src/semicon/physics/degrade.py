"""phys_degrade — PUBLIC module, interface I5 (Phase 4.2).

Responsibility: YieldMaps -> degraded yield map (PSF + noise).
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np

from semicon.foundation.datatypes import YieldMaps
from semicon.physics._degrade.noise_models import degrade_signal
from semicon.physics._degrade.psf_generator import make_psf


def degrade_yields(
    yields: YieldMaps,
    config: Dict[str, Any],
    seed: int,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """I5 output: degraded SE map (primary imaging channel) + record dict."""
    probe_nm = float(config.get("probe_diameter_nm", 3.0))
    kernel = make_psf(probe_nm, yields.pixel_size_nm)
    generator = np.random.default_rng(seed)
    se_degraded, record = degrade_signal(yields.se_yield, config, generator, kernel)
    record["probe_diameter_nm"] = probe_nm
    return se_degraded, record
