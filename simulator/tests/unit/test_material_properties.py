"""Unit tests: material property library (Phase 5.3 doc 05)."""
from __future__ import annotations

import numpy as np
import pytest

from semicon.physics._shared.material_properties import (
    MaterialLibrary,
    default_records,
    everhart_eta,
    library_checksum,
)


def test_default_library_complete():
    lib = MaterialLibrary()
    assert set(lib.records) == {0, 1, 2, 3, 4, 5, 6}


def test_bse_ordering():
    """W eta > Cu eta > Si eta (L4 material-contrast constraint)."""
    lib = MaterialLibrary()
    assert lib.get(5).eta > lib.get(4).eta > lib.get(1).eta


def test_bse_ranges():
    lib = MaterialLibrary()
    assert 0.15 <= lib.get(1).eta <= 0.25  # Si in [0.15, 0.25]
    assert 0.0 <= lib.get(0).eta <= 1e-9  # vacuum


def test_se_ordering():
    """Cu SE < Si SE (L4 material-contrast constraint)."""
    lib = MaterialLibrary()
    assert lib.get(4).delta0 < lib.get(1).delta0


def test_se_si_in_certified_range():
    lib = MaterialLibrary()
    assert 0.4 <= lib.get(1).delta0 <= 0.8  # L4 target


def test_everhart_polynomial():
    assert everhart_eta(14.0) == pytest.approx(0.215, abs=0.01)
    assert everhart_eta(0.0) == pytest.approx(0.0254, abs=1e-6)


def test_checksum_stable():
    a = library_checksum()
    b = library_checksum()
    assert a == b
    assert len(a) == 64


def test_load_from_yaml():
    from pathlib import Path

    from semicon.physics._shared.material_properties import load_material_library

    path = Path(__file__).resolve().parents[2] / "configs" / "materials.yml"
    lib = load_material_library(str(path))
    assert lib.get(1).name == "Si"
    assert lib.get(5).eta > lib.get(4).eta
