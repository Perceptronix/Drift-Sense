"""Shared test fixtures (DG1).

The structure library is generated once per session into a temp GDSII file
and loaded through the same path the CLI uses (I1 boundary exercised in
tests, not bypassed).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture(scope="session")
def structure_gds(tmp_path_factory):
    from semicon.geometry.raster import save_library
    from semicon.geometry.structures import build_structure_library

    lib = build_structure_library(fov_nm=320.0, cd_nm=40.0, height_nm=70.0)
    path = tmp_path_factory.mktemp("lib") / "semicon.gds"
    save_library(lib, path)
    return str(path)


@pytest.fixture(scope="session")
def context(structure_gds):
    from semicon.orchestration.pipeline import build_context

    return build_context(structure_gds)


@pytest.fixture(scope="session")
def materials():
    from semicon.physics._shared.material_properties import MaterialLibrary

    return MaterialLibrary()


@pytest.fixture()
def default_config():
    from semicon.orchestration.config import load_config

    return load_config(None, defaults_path=str(ROOT / "configs" / "defaults.yml"))
