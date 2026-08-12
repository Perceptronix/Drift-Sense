"""phys_signal — PUBLIC module, interface I4 (Phase 4.2).

Responsibility: variability-applied geometry -> YieldMaps (SE + BSE).
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

from semicon.foundation.datatypes import HeightField, MaterialMap, YieldMaps
from semicon.physics._shared.material_properties import MaterialLibrary
from semicon.physics._signal.signal_assembler import SignalRecord, assemble_signal


def compute_yields(
    height_field: HeightField,
    material_map: MaterialMap,
    library: MaterialLibrary,
    config: Dict[str, Any],
) -> Tuple[YieldMaps, SignalRecord]:
    """I4 output. Returns YieldMaps + SignalRecord (ranges, warnings)."""
    se, bse, record = assemble_signal(
        height_field.data,
        material_map.data,
        height_field.pixel_size_nm,
        library,
        config,
    )
    yields = YieldMaps(se_yield=se, bse_yield=bse, pixel_size_nm=height_field.pixel_size_nm)
    return yields, record
