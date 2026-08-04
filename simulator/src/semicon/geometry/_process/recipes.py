"""Structure process recipes (Phase 3.2; frozen structure semantics).

Each recipe drives a :class:`ProcessSimulator` from the per-layer masks of
the structure, producing height field + material map for that structure type.
Parameters: cd_nm, height_nm (feature height), pitch_nm.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from semicon.foundation.datatypes import STRUCTURE_TYPES
from semicon.geometry._process.process_simulator import ProcessSimulator
from semicon.geometry._raster.mask_builder import MaskSet

# material IDs
_SI, _SIO2, _SIN, _CU, _W, _PR = 1, 2, 3, 4, 5, 6


def _opts(masks: MaskSet) -> Optional[np.ndarray]:
    """Default pattern = union mask (primary features)."""
    return masks.union.astype(bool)


def recipe_iso_line(sim: ProcessSimulator, masks: MaskSet, cd_nm, height_nm, pitch_nm) -> None:
    """Raised Si line on Si substrate -> topographic step."""
    sim.deposit(_SI, height_nm, pattern=_opts(masks))
    sim.corner_round(min(4.0, height_nm * 0.05))


def recipe_dense_ls(sim: ProcessSimulator, masks: MaskSet, cd_nm, height_nm, pitch_nm) -> None:
    """Array of raised Si lines/spaces."""
    sim.deposit(_SI, height_nm, pattern=_opts(masks))
    sim.corner_round(min(3.0, height_nm * 0.05))


def recipe_contact(sim: ProcessSimulator, masks: MaskSet, cd_nm, height_nm, pitch_nm) -> None:
    """SiO2 field with Cu contact squares (fill + CMP)."""
    oxide = max(height_nm, 40.0)
    sim.deposit(_SIO2, oxide, pattern=None)
    sim.etch(oxide, pattern=_opts(masks), sidewall_angle_deg=86.0)
    sim.deposit(_CU, oxide, pattern=_opts(masks))
    sim.planarize(sim.substrate_top_nm + oxide)


def recipe_via(sim: ProcessSimulator, masks: MaskSet, cd_nm, height_nm, pitch_nm) -> None:
    """SiO2 field with round W vias (fill + CMP)."""
    oxide = max(height_nm, 40.0)
    sim.deposit(_SIO2, oxide, pattern=None)
    sim.etch(oxide, pattern=_opts(masks), sidewall_angle_deg=85.0)
    sim.deposit(_W, oxide, pattern=_opts(masks))
    sim.planarize(sim.substrate_top_nm + oxide)


def recipe_trench(sim: ProcessSimulator, masks: MaskSet, cd_nm, height_nm, pitch_nm) -> None:
    """Recessed trench in Si (dark lines)."""
    sim.etch(height_nm, pattern=_opts(masks), sidewall_angle_deg=87.0)
    sim.corner_round(min(3.0, height_nm * 0.05))


def recipe_fin(sim: ProcessSimulator, masks: MaskSet, cd_nm, height_nm, pitch_nm) -> None:
    """Raised SiN fins on Si substrate."""
    sim.deposit(_SIN, height_nm, pattern=_opts(masks))
    sim.corner_round(min(3.0, height_nm * 0.05))


def recipe_gate(sim: ProcessSimulator, masks: MaskSet, cd_nm, height_nm, pitch_nm) -> None:
    """SiN fins with a W gate bar crossing on top (layer 1)."""
    fin_mask = masks.layer_masks[0].astype(bool)
    gate_mask = masks.layer_masks.get(1, np.zeros_like(fin_mask)).astype(bool)
    sim.deposit(_SIN, height_nm, pattern=fin_mask)
    sim.deposit(_W, max(12.0, height_nm * 0.5), pattern=gate_mask)
    sim.corner_round(min(3.0, height_nm * 0.05))


def recipe_sti(sim: ProcessSimulator, masks: MaskSet, cd_nm, height_nm, pitch_nm) -> None:
    """Shallow-trench isolation: SiO2-filled trenches in Si, planarized."""
    depth = max(height_nm, 40.0)
    sim.etch(depth, pattern=_opts(masks), sidewall_angle_deg=86.0)
    sim.deposit(_SIO2, depth, pattern=_opts(masks))
    sim.planarize(sim.substrate_top_nm)


def recipe_bimaterial(sim: ProcessSimulator, masks: MaskSet, cd_nm, height_nm, pitch_nm) -> None:
    """Cu and W blocks side-by-side for material contrast."""
    left = masks.layer_masks[0].astype(bool)
    right = masks.layer_masks.get(1, np.zeros_like(left)).astype(bool)
    sim.deposit(_CU, height_nm, pattern=left)
    sim.deposit(_W, height_nm, pattern=right)


def recipe_pitch_std(sim: ProcessSimulator, masks: MaskSet, cd_nm, height_nm, pitch_nm) -> None:
    """Si lines at three different pitches (2x/3x/4x)."""
    sim.deposit(_SI, height_nm, pattern=_opts(masks))
    sim.corner_round(min(3.0, height_nm * 0.05))


_RECIPES = {
    "iso_line": recipe_iso_line,
    "dense_ls": recipe_dense_ls,
    "contact": recipe_contact,
    "via": recipe_via,
    "trench": recipe_trench,
    "fin": recipe_fin,
    "gate": recipe_gate,
    "sti": recipe_sti,
    "bimaterial": recipe_bimaterial,
    "pitch_std": recipe_pitch_std,
}


def apply_recipe(sim: ProcessSimulator, masks: MaskSet, structure_type: str, cd_nm: float, height_nm: float, pitch_nm: Optional[float]) -> None:
    if structure_type not in _RECIPES:
        raise KeyError(f"no recipe for structure {structure_type!r}; valid: {list(_RECIPES)}")
    _RECIPES[structure_type](sim, masks, cd_nm, height_nm, pitch_nm)


def valid_structure_types() -> tuple:
    return STRUCTURE_TYPES
