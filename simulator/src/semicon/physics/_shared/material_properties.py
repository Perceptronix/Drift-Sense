"""Material property library (Phase 5.3 doc 05; Phase 2.6 certification).

Values are v1 calibration references within the certified Phase 2 ranges,
pinned to satisfy the L4 scientific targets:
  Si SE yield at 1 keV flat  delta0(Si) in [0.4, 0.8]
  material contrast:  Cu SE < Si SE  (delta0_Cu < delta0_Si)
  BSE ordering:        W eta > Cu eta > Si eta   (Everhart polynomial)

BSE yield eta is computed from the Everhart polynomial on Z (Algorithm P3).
Material IDs 0-6 are immutable; extensions must use IDs >= 7.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from semicon.foundation.datatypes import MATERIAL_NAMES, VALID_MATERIAL_IDS


def everhart_eta(z: float) -> float:
    """Everhart polynomial: eta(Z) = 0.0254 + 0.016Z - 1.86e-4 Z^2 + 8.3e-7 Z^3."""
    return 0.0254 + 0.016 * z - 1.86e-4 * z**2 + 8.3e-7 * z**3


@dataclass(frozen=True)
class MaterialRecord:
    id: int
    name: str
    z: float  # effective atomic number
    delta0: float  # SE yield at normal incidence (1 keV calibration)
    lambda_nm: float  # SE escape depth (nm)
    tilt_exp: float  # cos(theta) exponent f
    g_bulk: float  # SE2 backscatter efficiency factor
    eta: float  # BSE yield (Everhart)

    @classmethod
    def build(cls, mid: int, name: str, z: float, delta0: float, lambda_nm: float,
              tilt_exp: float = 1.0, g_bulk: float = 0.5) -> "MaterialRecord":
        eta = everhart_eta(z) if mid != 0 else 0.0
        return cls(id=mid, name=name, z=z, delta0=delta0, lambda_nm=lambda_nm,
                   tilt_exp=tilt_exp, g_bulk=g_bulk, eta=eta)


class MaterialLibrary:
    """Frozen lookup table. Material IDs 0-6 immutable."""

    def __init__(self, records: Optional[Dict[int, MaterialRecord]] = None) -> None:
        if records is None:
            records = default_records()
        self.records: Dict[int, MaterialRecord] = dict(records)
        missing = VALID_MATERIAL_IDS - set(self.records.keys())
        if missing:
            raise ValueError(f"material library missing IDs {sorted(missing)}")
        for mid in self.records:
            if mid not in VALID_MATERIAL_IDS:
                raise ValueError(f"material library uses reserved/out-of-range ID {mid}")

    def get(self, mid: int) -> MaterialRecord:
        return self.records[int(mid)]

    # --- vectorized lookup arrays (for np.take) ---
    def delta0_array(self) -> np.ndarray:
        ids = sorted(self.records)
        return np.array([self.records[i].delta0 for i in ids], dtype=np.float64)

    def lambda_array(self) -> np.ndarray:
        ids = sorted(self.records)
        return np.array([self.records[i].lambda_nm for i in ids], dtype=np.float64)

    def tilt_array(self) -> np.ndarray:
        ids = sorted(self.records)
        return np.array([self.records[i].tilt_exp for i in ids], dtype=np.float64)

    def eta_array(self) -> np.ndarray:
        ids = sorted(self.records)
        return np.array([self.records[i].eta for i in ids], dtype=np.float64)

    def g_bulk_array(self) -> np.ndarray:
        ids = sorted(self.records)
        return np.array([self.records[i].g_bulk for i in ids], dtype=np.float64)


def default_records() -> Dict[int, MaterialRecord]:
    """v1 pinned material records (Phase 5.3 doc 05 calibration values)."""
    rows = [
        # id, name,    Z,    delta0, lambda, tilt, g_bulk
        (1, "Si",      14.0, 0.50, 2.5, 1.0, 0.5),
        (2, "SiO2",    10.8, 0.60, 2.8, 1.0, 0.5),
        (3, "SiN",     10.4, 0.52, 2.6, 1.0, 0.5),
        (4, "Cu",      29.0, 0.40, 1.8, 1.0, 0.5),
        (5, "W",       74.0, 0.35, 1.5, 1.0, 0.5),
        (6, "PR",      5.0,  0.80, 4.0, 1.0, 0.5),
    ]
    recs: Dict[int, MaterialRecord] = {0: MaterialRecord.build(0, "vacuum", 0.0, 0.0, 0.0)}
    for (mid, name, z, d0, lam, tilt, g) in rows:
        recs[mid] = MaterialRecord.build(mid, name, z, d0, lam, tilt, g)
    return recs


def load_material_library(path: Optional[str] = None) -> MaterialLibrary:
    """Load from YAML if provided, else the pinned defaults.

    YAML layout (per material):
        - id: 1
          name: Si
          z: 14.0
          delta0: 0.50
          lambda_nm: 2.5
          tilt_exp: 1.0
          g_bulk: 0.5
    """
    if path is None:
        return MaterialLibrary(default_records())
    import yaml

    from pathlib import Path

    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    recs: Dict[int, MaterialRecord] = {}
    for row in data["materials"]:
        mid = int(row["id"])
        recs[mid] = MaterialRecord.build(
            mid,
            row["name"],
            float(row["z"]),
            float(row["delta0"]),
            float(row["lambda_nm"]),
            float(row.get("tilt_exp", 1.0)),
            float(row.get("g_bulk", 0.5)),
        )
    return MaterialLibrary(recs)


def library_checksum() -> str:
    """SHA-256 over the canonical default records (for metadata provenance)."""
    import hashlib
    import json

    recs = default_records()
    payload = json.dumps(
        {mid: rec.__dict__ for mid, rec in sorted(recs.items())}, sort_keys=True
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
