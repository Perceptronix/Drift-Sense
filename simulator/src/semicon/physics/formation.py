"""phys_formation — PUBLIC module, interface I6 (Phase 4.2).

Responsibility: degraded SE map -> SEMImage (digitized).
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np

from semicon.foundation.datatypes import FormationRecord, SEMImage
from semicon.physics._formation.image_former import form_image as _form_image


def form_image(
    se_degraded: np.ndarray,
    pixel_size_nm: float,
    config: Dict[str, Any],
) -> Tuple[SEMImage, FormationRecord]:
    """I6 output: SEMImage + FormationRecord."""
    return _form_image(se_degraded, pixel_size_nm, config)
