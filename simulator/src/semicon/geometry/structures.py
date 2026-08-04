"""Structure library: programmatic GDSII polygons for the 10 frozen structure types.

Each builder returns a ``GdsStructure`` with polygons in nanometres. The
coordinate origin is the FOV centre; y increases downward (row-major).
Layer 0 is the primary pattern; additional layers are used by multi-material
structures (gate, bimaterial).
"""
from __future__ import annotations

from typing import Optional, Tuple

import math

from semicon.geometry._raster.gdsii import GdsElement, GdsLibrary, GdsStructure

# ---------------------------------------------------------------------------
# polygon helpers
# ---------------------------------------------------------------------------
def rect(cx: float, cy: float, w: float, h: float) -> list:
    """Rectangle centred at (cx,cy) with width w (x) and height h (y), nm."""
    return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]


def polygon(cx: float, cy: float, r: float, n: int = 16) -> list:
    """Regular n-gon (circle approx) centred at (cx,cy), radius r nm."""
    pts = []
    for k in range(n):
        a = 2.0 * math.pi * k / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def vertical_lines(widths: list, pitch: float, half_h: float, layer: int = 0) -> list:
    """Vertical lines centred around x=0, each of the given widths, spaced by pitch."""
    els = []
    x = -(len(widths) - 1) * pitch / 2.0
    for w in widths:
        els.append(GdsElement(etype="boundary", layer=layer, xy=rect(x, 0.0, w, 2 * half_h)))
        x += pitch
    return els


def grid_of(cx0: float, cy0: float, w: float, h: float, nx: int, ny: int, sx: float, sy: float, layer: int = 0) -> list:
    els = []
    for i in range(nx):
        for j in range(ny):
            els.append(GdsElement(etype="boundary", layer=layer, xy=rect(cx0 + i * sx, cy0 + j * sy, w, h)))
    return els


# ---------------------------------------------------------------------------
# structure builders (frozen parameter semantics)
# ---------------------------------------------------------------------------
def _fov(pitch_nm, fov_nm, cd_nm, height_nm):
    """Common FOV resolution: at least 6x pitch, capped to requested fov."""
    f = max(fov_nm, 8.0 * (pitch_nm or fov_nm))
    return min(f, 2048.0)


def iso_line(cd_nm: float, height_nm: float, pitch_nm: Optional[float], fov_nm: float) -> GdsStructure:
    s = GdsStructure(name="iso_line")
    half_h = fov_nm / 2
    s.elements = vertical_lines([cd_nm], pitch_nm or cd_nm * 6, half_h, layer=0)
    return s


def dense_ls(cd_nm: float, height_nm: float, pitch_nm: Optional[float], fov_nm: float) -> GdsStructure:
    p = pitch_nm or cd_nm * 2
    n = max(2, int(fov_nm // p))
    widths = [cd_nm] * n
    s = GdsStructure(name="dense_ls")
    s.elements = vertical_lines(widths, p, fov_nm / 2, layer=0)
    return s


def contact(cd_nm: float, height_nm: float, pitch_nm: Optional[float], fov_nm: float) -> GdsStructure:
    s = GdsStructure(name="contact")
    p = pitch_nm or cd_nm * 3
    nx = max(2, int(fov_nm // (p * 1.6)))
    ny = max(2, int(fov_nm // (p * 1.6)))
    nx, ny = min(nx, 6), min(ny, 6)
    x0 = -(nx - 1) * p / 2
    y0 = -(ny - 1) * p / 2
    s.elements = grid_of(x0, y0, cd_nm, cd_nm, nx, ny, p, p, layer=0)
    return s


def via(cd_nm: float, height_nm: float, pitch_nm: Optional[float], fov_nm: float) -> GdsStructure:
    s = GdsStructure(name="via")
    p = pitch_nm or cd_nm * 3
    nx = max(2, int(fov_nm // (p * 1.6)))
    ny = max(2, int(fov_nm // (p * 1.6)))
    nx, ny = min(nx, 6), min(ny, 6)
    x0 = -(nx - 1) * p / 2
    y0 = -(ny - 1) * p / 2
    for i in range(nx):
        for j in range(ny):
            s.elements.append(GdsElement(etype="boundary", layer=0, xy=polygon(x0 + i * p, y0 + j * p, cd_nm / 2, 16)))
    return s


def trench(cd_nm: float, height_nm: float, pitch_nm: Optional[float], fov_nm: float) -> GdsStructure:
    s = GdsStructure(name="trench")
    p = pitch_nm or cd_nm * 3
    n = max(1, int(fov_nm // (p * 1.5)))
    widths = [cd_nm] * n
    s.elements = vertical_lines(widths, p, fov_nm / 2, layer=0)
    return s


def fin(cd_nm: float, height_nm: float, pitch_nm: Optional[float], fov_nm: float) -> GdsStructure:
    s = GdsStructure(name="fin")
    p = pitch_nm or cd_nm * 3
    n = max(2, int(fov_nm // (p * 1.5)))
    widths = [cd_nm] * n
    s.elements = vertical_lines(widths, p, fov_nm / 2, layer=0)
    return s


def gate(cd_nm: float, height_nm: float, pitch_nm: Optional[float], fov_nm: float) -> GdsStructure:
    s = GdsStructure(name="gate")
    fin_pitch = pitch_nm or cd_nm * 3
    n = max(2, int(fov_nm // (fin_pitch * 1.5)))
    widths = [max(6.0, cd_nm / 3)] * n
    s.elements = vertical_lines(widths, fin_pitch, fov_nm / 2, layer=0)
    # gate: horizontal bar crossing the fins (layer 1)
    s.elements.append(GdsElement(etype="boundary", layer=1, xy=rect(0.0, 0.0, fov_nm * 0.8, cd_nm)))
    return s


def sti(cd_nm: float, height_nm: float, pitch_nm: Optional[float], fov_nm: float) -> GdsStructure:
    s = GdsStructure(name="sti")
    p = pitch_nm or cd_nm * 2.5
    nx = max(2, int(fov_nm // (p * 1.6)))
    ny = max(2, int(fov_nm // (p * 1.6)))
    nx, ny = min(nx, 6), min(ny, 6)
    x0 = -(nx - 1) * p / 2
    y0 = -(ny - 1) * p / 2
    s.elements = grid_of(x0, y0, cd_nm, cd_nm, nx, ny, p, p, layer=0)
    return s


def bimaterial(cd_nm: float, height_nm: float, pitch_nm: Optional[float], fov_nm: float) -> GdsStructure:
    s = GdsStructure(name="bimaterial")
    w = max(cd_nm, fov_nm * 0.2)
    s.elements.append(GdsElement(etype="boundary", layer=0, xy=rect(-w / 2, 0.0, w, fov_nm)))
    s.elements.append(GdsElement(etype="boundary", layer=1, xy=rect(w / 2, 0.0, w, fov_nm)))
    return s


def pitch_std(cd_nm: float, height_nm: float, pitch_nm: Optional[float], fov_nm: float) -> GdsStructure:
    s = GdsStructure(name="pitch_std")
    # three pitches: 2x, 3x, 4x the nominal, two lines each
    els = []
    x = -fov_nm * 0.42
    for mult in (2, 3, 4):
        p = (pitch_nm or cd_nm * 2) * mult
        for i in range(2):
            els.append(GdsElement(etype="boundary", layer=0, xy=rect(x, 0.0, cd_nm, fov_nm)))
            x += p
    s.elements = els
    return s


_BUILDERS = {
    "iso_line": iso_line,
    "dense_ls": dense_ls,
    "contact": contact,
    "via": via,
    "trench": trench,
    "fin": fin,
    "gate": gate,
    "sti": sti,
    "bimaterial": bimaterial,
    "pitch_std": pitch_std,
}


def build_structure_library(
    fov_nm: float,
    cd_nm: float = 30.0,
    height_nm: float = 60.0,
    pitch_nm: Optional[float] = None,
) -> GdsLibrary:
    """Generate a GdsLibrary containing all 10 structure types."""
    lib = GdsLibrary(name="SEMICON_STRUCTURES")
    for name, fn in _BUILDERS.items():
        lib.structures.append(fn(cd_nm, height_nm, pitch_nm, fov_nm))
    return lib


def get_builder(name: str):
    if name not in _BUILDERS:
        raise KeyError(f"unknown structure type {name!r}; valid: {list(_BUILDERS)}")
    return _BUILDERS[name]
