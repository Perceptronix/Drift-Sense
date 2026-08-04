"""Configuration system (Phase 4.3 / 5.4 IN6; module M9).

Layering: built-in defaults -> defaults.yml -> user YAML -> CLI overrides.
Validation applies the frozen ranges:
  cd_nm       [10, 500]
  height_nm   [20, 200]
  pitch_nm    [20, 1000] or None
  pixel_size  (0, 100]
  beam_energy [0.3, 30] keV
  probe_cur   [1, 1000] pA
  probe_dia   [0.5, 10] nm
  bit_depth   {8, 16}
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from semicon.foundation.datatypes import STRUCTURE_TYPES, Config

_RANGES = {
    "cd_nm": (10.0, 500.0),
    "height_nm": (20.0, 200.0),
    "pitch_nm": (20.0, 1000.0),
    "pixel_size_nm": (1e-6, 100.0),
    "beam_energy_keV": (0.3, 30.0),
    "probe_current_pA": (1.0, 1000.0),
    "probe_diameter_nm": (0.5, 10.0),
}


def _deep_merge(base: Dict, over: Dict) -> Dict:
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _check_range(name: str, value: Any) -> None:
    if name not in _RANGES:
        return
    lo, hi = _RANGES[name]
    if value is None:
        return
    if not (lo <= float(value) <= hi):
        raise ValueError(f"{name}={value} outside certified range [{lo}, {hi}]")


def validate(config: Config) -> Config:
    st = config.structure
    stype = st.get("structure_type")
    if stype not in STRUCTURE_TYPES:
        raise ValueError(f"structure_type {stype!r} not in {STRUCTURE_TYPES}")
    for k in ("cd_nm", "height_nm"):
        _check_range(k, st.get(k))
    _check_range("pitch_nm", st.get("pitch_nm"))
    _check_range("pixel_size_nm", st.get("pixel_size_nm"))
    if st.get("width_nm") is None:
        st["width_nm"] = float(st.get("cd_nm", 30.0)) * 8.0
    if st.get("height_nm_fov") is None:
        st["height_nm_fov"] = st.get("width_nm")
    ph = config.physics
    _check_range("beam_energy_keV", ph.get("beam_energy_keV"))
    _check_range("probe_current_pA", ph.get("probe_current_pA"))
    _check_range("probe_diameter_nm", ph.get("probe_diameter_nm"))
    bd = int(config.detector.get("bit_depth", 16))
    if bd not in (8, 16):
        raise ValueError(f"detector.bit_depth must be 8 or 16, got {bd}")
    return config


def _to_config(d: Dict[str, Any]) -> Config:
    cfg = Config(
        general=dict(d.get("general", {})),
        structure=dict(d.get("structure", {})),
        process=dict(d.get("process", {})),
        variability=dict(d.get("variability", {})),
        physics=dict(d.get("physics", {})),
        detector=dict(d.get("detector", {})),
        ground_truth=dict(d.get("ground_truth", {})),
        dataset=dict(d.get("dataset", {})),
    )
    return validate(cfg)


def load_config(
    user_path: Optional[str] = None,
    defaults_path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None,
) -> Config:
    """Load, merge, validate. Overrides use dotted keys: 'structure.cd_nm'."""
    base: Dict[str, Any] = {}
    if defaults_path:
        with open(defaults_path, "r", encoding="utf-8") as fh:
            base = yaml.safe_load(fh) or {}
    merged = _deep_merge(base, {})
    if user_path:
        with open(user_path, "r", encoding="utf-8") as fh:
            user = yaml.safe_load(fh) or {}
        merged = _deep_merge(merged, user)
    if overrides:
        merged = _apply_overrides(merged, overrides)
    return _to_config(merged)


def _apply_overrides(cfg: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(cfg)
    for key, value in overrides.items():
        parts = key.split(".")
        node = out
        for p in parts[:-1]:
            nxt = node.get(p)
            if not isinstance(nxt, dict):
                nxt = {}
                node[p] = nxt
            node = nxt
        if isinstance(node, dict):
            node[parts[-1]] = value
    return out


def config_snapshot(config: Config) -> Dict[str, Any]:
    return config.merged()
