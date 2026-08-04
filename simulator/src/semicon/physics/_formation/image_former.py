"""Image formation / digitization (Phase 5.3 P10; Phase 2.5).

DN = round_half_even(clip(se * gain + offset, 0, 2^bits-1))

The rounding is banker's (round-half-even) so that a constant input maps to
a deterministic constant output. Saturation fraction is recorded.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np

from semicon.foundation.datatypes import FormationRecord, SEMImage


def form_image(
    se_degraded: np.ndarray,
    pixel_size_nm: float,
    config: Dict[str, Any],
) -> Tuple[SEMImage, FormationRecord]:
    gain = float(config.get("gain", 4000.0))
    offset = float(config.get("offset", 0.0))
    bit_depth = int(config.get("bit_depth", 16))
    saturate = bool(config.get("saturate", True))
    if bit_depth not in (8, 16):
        raise ValueError(f"bit_depth must be 8 or 16, got {bit_depth}")
    maxval = (1 << bit_depth) - 1

    signal = se_degraded * gain + offset
    lo = 0.0 if saturate else float(signal.min())
    hi = float(maxval) if saturate else float(signal.max())
    clipped = np.clip(signal, lo, hi)
    dn = np.rint(clipped).astype(np.float64)  # numpy uses round-half-even
    if not saturate:
        dn = np.clip(dn, 0, maxval)
    dn = dn.astype(np.uint8 if bit_depth == 8 else np.uint16)

    sat_frac = float((dn >= maxval).mean()) if maxval > 0 else 0.0
    record = FormationRecord(
        gain=gain,
        offset=offset,
        bit_depth=bit_depth,
        saturate_enabled=saturate,
        saturation_fraction=sat_frac,
        signal_min=float(se_degraded.min()),
        signal_max=float(se_degraded.max()),
    )
    img = SEMImage(data=dn, bit_depth=bit_depth, pixel_size_nm=pixel_size_nm, formation_record=record)
    return img, record
