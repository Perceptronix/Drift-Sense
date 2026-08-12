"""Unit tests: GDSII round-trip and polygon rasterization (A1)."""
from __future__ import annotations

import numpy as np
import pytest

from semicon.geometry._raster.gdsii import (
    GdsElement,
    GdsLibrary,
    GdsStructure,
    read_gds,
    write_gds,
)
from semicon.geometry._raster.polygon_rasterizer import rasterize_polygon, rasterize_polygons
from semicon.geometry.structures import build_structure_library


def test_write_read_roundtrip(tmp_path):
    lib = GdsLibrary(name="T")
    s = GdsStructure(name="A", elements=[GdsElement(etype="boundary", layer=0, xy=[(0, 0), (10, 0), (10, 10), (0, 10)])])
    lib.structures.append(s)
    p = tmp_path / "x.gds"
    write_gds(lib, p)
    lib2 = read_gds(p)
    assert lib2.name == "T"
    assert lib2.get("A") is not None
    poly = lib2.polygons("A")
    assert len(poly) == 1
    assert poly[0][0] == 0
    assert len(poly[0][1]) == 4


def test_structure_library_all_types():
    lib = build_structure_library(fov_nm=300.0)
    names = {s.name for s in lib.structures}
    assert names == {
        "iso_line", "dense_ls", "contact", "via", "trench", "fin",
        "gate", "sti", "bimaterial", "pitch_std",
    }


def test_structure_library_polygons_present():
    lib = build_structure_library(fov_nm=300.0)
    for s in lib.structures:
        polys = lib.polygons(s.name)
        assert len(polys) > 0, s.name


def test_rasterize_rect_area():
    # 10x10 nm square at 1 nm/px -> ~100 px
    m = rasterize_polygon([(0, 0), (10, 0), (10, 10), (0, 10)], (20, 20), 1.0, ss=4)
    assert 90 <= m.sum() <= 110


def test_rasterize_supersampled_edge():
    # supersampling vs single-sample: values must be binary and near-equal
    poly = [(5.0, 5.0), (15.0, 5.0), (15.0, 15.0), (5.0, 15.0)]
    m1 = rasterize_polygon(poly, (20, 20), 1.0, ss=1)
    m4 = rasterize_polygon(poly, (20, 20), 1.0, ss=4)
    assert set(np.unique(m4)) <= {0, 1}
    assert abs(int(m1.sum()) - int(m4.sum())) <= 2


def test_rasterize_union():
    polys = [[(0, 0), (5, 0), (5, 5), (0, 5)], [(10, 0), (15, 0), (15, 5), (10, 5)]]
    m = rasterize_polygons(polys, (10, 20), 1.0, ss=2)
    assert m.sum() == pytest.approx(50, abs=4)
