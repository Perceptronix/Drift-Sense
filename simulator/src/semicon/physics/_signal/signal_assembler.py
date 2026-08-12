"""Signal assembler: combines P1-P6 into the I4 YieldMaps."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from semicon.foundation.datatypes import SE_YIELD_MAX
from semicon.physics._signal.charging_engine import apply_charging
from semicon.physics._signal.edge_effects import apply_edge_effects
from semicon.physics._signal.topography_engine import compute_cos_theta
from semicon.physics._signal.yield_computer import compute_yields


@dataclass(frozen=True)
class SignalRecord:
    cos_theta_range: tuple
    se_range: tuple
    bse_range: tuple
    edge_factor: float
    charging_enabled: bool
    charging_skipped: bool
    warnings: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.warnings is None:
            object.__setattr__(self, "warnings", [])
        if self.se_range[1] > SE_YIELD_MAX:
            object.__setattr__(self, "se_range", (self.se_range[0], SE_YIELD_MAX))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cos_theta_range": list(self.cos_theta_range),
            "se_range": list(self.se_range),
            "bse_range": list(self.bse_range),
            "edge_factor": self.edge_factor,
            "charging_enabled": self.charging_enabled,
            "charging_skipped": self.charging_skipped,
            "warnings": list(self.warnings),
        }


def assemble_signal(
    height_field: np.ndarray,
    material_map: np.ndarray,
    pixel_size_nm: float,
    library,
    config: Dict[str, Any],
) -> tuple:
    """Return (se_map, bse_map, SignalRecord)."""
    cos_theta = compute_cos_theta(height_field, pixel_size_nm)
    se1, eta, se2 = compute_yields(cos_theta, material_map, library)

    se = se1 + se2

    # P5 edge effects
    edge_factor = float(config.get("edge_factor", 2.0))
    edge_width_nm = float(config.get("edge_width_nm", 8.0))
    if edge_factor > 1.0:
        se = apply_edge_effects(
            se, height_field, pixel_size_nm,
            edge_factor=edge_factor, edge_width_nm=edge_width_nm,
        )

    # P6 charging (isolated-only guard)
    charging_enabled = bool(config.get("charging_enabled", False))
    charge_factor = float(config.get("charge_factor", 0.15))
    diff_len = float(config.get("charging_diffusion_nm", 50.0))
    se, charge_warning = apply_charging(
        se, material_map, pixel_size_nm,
        enabled=charging_enabled, charge_factor=charge_factor,
        diffusion_length_nm=diff_len,
    )
    charging_skipped = charging_enabled and charge_warning

    # yield saturation guard: enforce the frozen YieldMaps postcondition [0, 10]
    se = np.clip(se, 0.0, SE_YIELD_MAX)

    warnings: List[str] = []
    if charging_skipped:
        warnings.append("charging requested on dense pattern; charging approximation skipped (isolated-only guard)")

    record = SignalRecord(
        cos_theta_range=(float(cos_theta.min()), float(cos_theta.max())),
        se_range=(float(se.min()), float(se.max())),
        bse_range=(float(eta.min()), float(eta.max())),
        edge_factor=edge_factor,
        charging_enabled=charging_enabled,
        charging_skipped=charging_skipped,
        warnings=warnings,
    )
    return se, eta, record
