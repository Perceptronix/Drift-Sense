"""Charging model (Phase 5.3 P6).

Scope-limited by design: charging is only applied when explicitly enabled
and to *isolated* structures (pattern fill fraction below a threshold).
It modulates the SE signal over insulator regions (SiO2, SiN, PR) with a
smooth field whose amplitude grows with accumulated dose (proportional to
the local insulator coverage blurred over the charge-diffusion length).

A warning flag is recorded when charging is requested on dense patterns
(fill > fill_threshold), per the frozen "isolated-only guard".
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage


def charging_field(
    material_map: np.ndarray,
    pixel_size_nm: float,
    diffusion_length_nm: float = 50.0,
) -> np.ndarray:
    """Smooth insulator-coverage field in [0,1]."""
    insulator = np.isin(material_map, (2, 3, 6)).astype(np.float64)
    sigma_px = max(1.0, diffusion_length_nm / pixel_size_nm)
    return ndimage.gaussian_filter(insulator, sigma=sigma_px, mode="nearest")


def apply_charging(
    se_map: np.ndarray,
    material_map: np.ndarray,
    pixel_size_nm: float,
    enabled: bool = False,
    charge_factor: float = 0.15,
    diffusion_length_nm: float = 50.0,
    fill_threshold: float = 0.35,
) -> tuple:
    """Return (se_map_charged, warning: bool)."""
    warning = False
    if not enabled:
        return se_map, warning
    fill = float((material_map != 0).mean())
    if fill > fill_threshold:
        warning = True  # dense pattern: charging approximation not applicable
        return se_map, warning
    field = charging_field(material_map, pixel_size_nm, diffusion_length_nm)
    se_out = se_map * (1.0 + charge_factor * field)
    return se_out, warning
