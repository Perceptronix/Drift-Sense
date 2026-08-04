"""Minimal, self-contained GDSII reader/writer (DG1 implementation decision).

The frozen blueprint (Phase 5.2, doc 03) selects ``gdspy`` as the primary
GDSII library. gdspy is not installed in the DG1 environment, so a compact,
pure-Python GDSII implementation covering the subset needed by the simulator
(BOUNDARY polygons, STRUCTURE/SREF references) is provided instead. It is
strictly drop-in for the geometry reader's responsibilities and is replaced
by gdspy without interface change if it becomes available.

Supported records:
  HEADER, BGNLIB, LIBNAME, UNITS, ENDLIB, BGNSTR, STRNAME, ENDSTR,
  BOUNDARY, PATH, SREF, AREF, LAYER, DATATYPE, XY, ENDEL, SNAME,
  COLROW, STRANS, MAG, ANGLE, TEXT, TEXTTYPE.

Coordinates are stored as (x, y) float nanometres with **y increasing
downward** (row-major array convention, top-left origin) -- see foundation
datatypes. This is a documented DG1 convention; GDSII has no intrinsic
orientation, so the generator writes in this space directly.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

# --- GDSII record types (subset) ---
R_HEADER = 0x00
R_BGNLIB = 0x01
R_LIBNAME = 0x02
R_UNITS = 0x03
R_ENDLIB = 0x04
R_BGNSTR = 0x05
R_STRNAME = 0x06
R_ENDSTR = 0x07
R_BOUNDARY = 0x08
R_PATH = 0x09
R_SREF = 0x0A
R_AREF = 0x0B
R_TEXT = 0x0C
R_LAYER = 0x0D
R_DATATYPE = 0x0E
R_WIDTH = 0x0F
R_XY = 0x10
R_ENDEL = 0x11
R_SNAME = 0x12
R_COLROW = 0x13
R_TEXTTYPE = 0x16
R_STRING = 0x19
R_STRANS = 0x1A
R_MAG = 0x1B
R_ANGLE = 0x1C

# data types
D_NONE = 0x00
D_BIT = 0x01
D_INT2 = 0x02
D_INT4 = 0x03
D_REAL4 = 0x04
D_REAL8 = 0x05
D_STR = 0x06

# GDS II version byte for HEADER
GDS_VERSION = 6


@dataclass
class GdsElement:
    etype: str  # 'boundary' | 'path' | 'sref' | 'aref' | 'text'
    layer: int = 0
    datatype: int = 0
    xy: List[Tuple[float, float]] = field(default_factory=list)  # nm
    width: Optional[float] = None  # nm
    sname: str = ""
    colrow: Tuple[int, int] = (1, 1)
    strans: int = 0
    mag: float = 1.0
    angle: float = 0.0


@dataclass
class GdsStructure:
    name: str
    elements: List[GdsElement] = field(default_factory=list)


@dataclass
class GdsLibrary:
    name: str = "SEMICON"
    unit_nm: float = 1.0  # nanometres per database unit
    structures: List[GdsStructure] = field(default_factory=list)

    def get(self, name: str) -> Optional[GdsStructure]:
        for s in self.structures:
            if s.name == name:
                return s
        return None

    def polygons(self, struct_name: str) -> List[Tuple[int, List[Tuple[float, float]]]]:
        """Flatten SREF/AREF into (layer, vertices_nm) polygons."""
        out: List[Tuple[int, List[Tuple[float, float]]]] = []
        s = self.get(struct_name)
        if s is None:
            raise ValueError(f"structure {struct_name!r} not found")
        for el in s.elements:
            if el.etype == "boundary":
                out.append((el.layer, el.xy))
            elif el.etype in ("sref", "aref"):
                sub = self.get(el.sname)
                if sub is None:
                    continue
                for subel in sub.elements:
                    if subel.etype == "boundary":
                        out.append((subel.layer, _transform(subel.xy, el)))
        return out


def _transform(xy: List[Tuple[float, float]], ref: GdsElement) -> List[Tuple[float, float]]:
    import math

    angle = math.radians(ref.angle)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    mirror = bool(ref.strans & 0x8000)
    out = []
    for (x, y) in xy:
        if mirror:
            x = -x
        x2 = x * cos_a - y * sin_a
        y2 = x * sin_a + y * cos_a
        out.append((x2 * ref.mag, y2 * ref.mag))
    return out


# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------
def _record(rec_type: int, data_type: int, payload: bytes) -> bytes:
    n = 4 + len(payload)
    return struct.pack(">HBB", n, rec_type, data_type) + payload


def _real8(value: float) -> bytes:
    return struct.pack(">d", value)


def _int2(value: int) -> bytes:
    return struct.pack(">h", value)


def _int4(value: int) -> bytes:
    return struct.pack(">i", value)


def _string(value: str) -> bytes:
    return value.encode("ascii")


def _xy_record(xy: List[Tuple[float, float]], scale: float) -> bytes:
    coords = []
    for (x, y) in xy:
        coords.append(int(round(x / scale)))
        coords.append(int(round(y / scale)))
    return _record(R_XY, D_INT4, struct.pack(">%di" % len(coords), *coords))


def write_gds(library: GdsLibrary, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    scale = library.unit_nm  # nm per db unit
    buf = bytearray()
    buf += _record(R_HEADER, D_INT2, _int2(GDS_VERSION))
    buf += _record(R_BGNLIB, D_NONE, b"")
    buf += _record(R_LIBNAME, D_STR, _string(library.name))
    buf += _record(R_UNITS, D_REAL8, _real8(scale * 1e-9) + _real8(scale * 1e-9 * 1000.0))
    for s in library.structures:
        buf += _record(R_BGNSTR, D_NONE, b"")
        buf += _record(R_STRNAME, D_STR, _string(s.name))
        for el in s.elements:
            buf += _element_records(el, scale)
        buf += _record(R_ENDSTR, D_NONE, b"")
    buf += _record(R_ENDLIB, D_NONE, b"")
    path.write_bytes(bytes(buf))


def _element_records(el: GdsElement, scale: float) -> bytes:
    buf = bytearray()
    if el.etype == "boundary":
        buf += _record(R_BOUNDARY, D_NONE, b"")
    elif el.etype == "path":
        buf += _record(R_PATH, D_NONE, b"")
    elif el.etype == "sref":
        buf += _record(R_SREF, D_NONE, b"")
    elif el.etype == "aref":
        buf += _record(R_AREF, D_NONE, b"")
    elif el.etype == "text":
        buf += _record(R_TEXT, D_NONE, b"")
    else:
        raise ValueError(f"unknown element type {el.etype}")
    buf += _record(R_LAYER, D_INT2, _int2(el.layer))
    buf += _record(R_DATATYPE, D_INT2, _int2(el.datatype))
    if el.etype == "path" and el.width is not None:
        buf += _record(R_WIDTH, D_INT4, _int4(int(round(el.width / scale))))
    if el.etype == "sref" or el.etype == "aref":
        buf += _record(R_SNAME, D_STR, _string(el.sname))
        if el.etype == "aref":
            c, r = el.colrow
            buf += _record(R_COLROW, D_INT2, _int2(c) + _int2(r))
        if el.strans:
            buf += _record(R_STRANS, D_BIT, struct.pack(">H", el.strans))
        if el.mag != 1.0:
            buf += _record(R_MAG, D_REAL8, _real8(el.mag))
        if el.angle != 0.0:
            buf += _record(R_ANGLE, D_REAL8, _real8(el.angle))
    if el.etype == "text":
        buf += _record(R_TEXTTYPE, D_INT2, _int2(el.datatype))
    buf += _xy_record(el.xy, scale)
    buf += _record(R_ENDEL, D_NONE, b"")
    return bytes(buf)


# ---------------------------------------------------------------------------
# Reader
# ---------------------------------------------------------------------------
def read_gds(path) -> GdsLibrary:
    path = Path(path)
    data = path.read_bytes()
    lib = GdsLibrary()
    pos = 0
    cur_struct: Optional[GdsStructure] = None
    cur_el: Optional[GdsElement] = None
    scale = 1.0  # db units per nm (unit_nm = nm per db unit)

    def nm(v: int) -> float:
        return v * scale

    while pos < len(data):
        if pos + 4 > len(data):
            raise ValueError("truncated GDSII file")
        (n, rec_type, data_type) = struct.unpack_from(">HBB", data, pos)
        payload = data[pos + 4 : pos + n]
        pos += n
        if rec_type == R_HEADER:
            pass
        elif rec_type == R_BGNLIB:
            pass
        elif rec_type == R_LIBNAME:
            lib.name = payload.rstrip(b"\x00").decode("ascii", "replace")
        elif rec_type == R_UNITS and data_type == D_REAL8 and len(payload) >= 8:
            u = struct.unpack_from(">d", payload, 0)[0]  # metres per db unit
            scale = u * 1e9  # nm per db unit
            lib.unit_nm = scale
        elif rec_type == R_BGNSTR:
            cur_struct = GdsStructure(name="")
            lib.structures.append(cur_struct)
            cur_el = None
        elif rec_type == R_STRNAME and cur_struct is not None:
            cur_struct.name = payload.rstrip(b"\x00").decode("ascii", "replace")
        elif rec_type == R_BOUNDARY:
            cur_el = GdsElement(etype="boundary")
        elif rec_type == R_PATH:
            cur_el = GdsElement(etype="path")
        elif rec_type == R_SREF:
            cur_el = GdsElement(etype="sref")
        elif rec_type == R_AREF:
            cur_el = GdsElement(etype="aref")
        elif rec_type == R_TEXT:
            cur_el = GdsElement(etype="text")
        elif rec_type == R_LAYER and cur_el is not None:
            cur_el.layer = struct.unpack_from(">h", payload, 0)[0]
        elif rec_type == R_DATATYPE and cur_el is not None:
            cur_el.datatype = struct.unpack_from(">h", payload, 0)[0]
        elif rec_type == R_WIDTH and cur_el is not None:
            cur_el.width = nm(struct.unpack_from(">i", payload, 0)[0])
        elif rec_type == R_XY and cur_el is not None:
            vals = struct.unpack(">%di" % (len(payload) // 4), payload)
            cur_el.xy = [(nm(vals[i]), nm(vals[i + 1])) for i in range(0, len(vals), 2)]
        elif rec_type == R_SNAME and cur_el is not None:
            cur_el.sname = payload.rstrip(b"\x00").decode("ascii", "replace")
        elif rec_type == R_COLROW and cur_el is not None:
            c, r = struct.unpack_from(">hh", payload, 0)
            cur_el.colrow = (c, r)
        elif rec_type == R_STRANS and cur_el is not None:
            cur_el.strans = struct.unpack_from(">H", payload, 0)[0]
        elif rec_type == R_MAG and cur_el is not None and data_type == D_REAL8:
            cur_el.mag = struct.unpack_from(">d", payload, 0)[0]
        elif rec_type == R_ANGLE and cur_el is not None and data_type == D_REAL8:
            cur_el.angle = struct.unpack_from(">d", payload, 0)[0]
        elif rec_type == R_ENDEL and cur_el is not None and cur_struct is not None:
            cur_struct.elements.append(cur_el)
            cur_el = None
        elif rec_type == R_ENDSTR:
            cur_struct = None
        elif rec_type == R_ENDLIB:
            break
        # other record types are safely ignored
    return lib
