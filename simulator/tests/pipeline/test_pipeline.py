"""End-to-end pipeline tests (Phase 5.4 T2)."""
from __future__ import annotations

import json
from pathlib import Path

from semicon.orchestration.config import load_config
from semicon.orchestration.pipeline import run_pipeline

CONFIGS = str(Path(__file__).resolve().parents[2] / "configs")


def _cfg(**overrides):
    return load_config(None, defaults_path=f"{CONFIGS}/defaults.yml", overrides=overrides)


def test_pipeline_full(context, tmp_path):
    result = run_pipeline(context, _cfg(), tmp_path, 0, "test", 42, write_outputs=False)
    assert result.status == "OK", result.error
    assert result.timing["total_s"] > 0
    assert "se_range" in result.metadata["physics"]["signal"]
    assert "degrade" in result.metadata["physics"]
    assert result.metadata["seeds"]["master_seed"] == 42


def test_pipeline_determinism(context, tmp_path):
    """Same seed -> identical outputs (SHA-256 of image files)."""
    d1 = tmp_path / "d1"
    d2 = tmp_path / "d2"
    r1 = run_pipeline(context, _cfg(), d1, 0, "test", 42, write_outputs=True)
    r2 = run_pipeline(context, _cfg(), d2, 0, "test", 42, write_outputs=True)
    assert r1.status == r2.status == "OK"
    assert r1.metadata == r2.metadata
    h1 = d1 / "images" / "000000.tiff"
    h2 = d2 / "images" / "000000.tiff"
    assert h1.read_bytes() == h2.read_bytes()


def test_pipeline_writes_artifacts(context, tmp_path):
    result = run_pipeline(context, _cfg(), tmp_path, 3, "test", 42, write_outputs=True)
    assert result.status == "OK"
    assert (tmp_path / "images" / "000003.tiff").exists()
    assert (tmp_path / "ground_truth" / "000003_gt.json").exists()
    assert (tmp_path / "ground_truth" / "000003_height.npy").exists()
    assert (tmp_path / "metadata" / "000003_metadata.json").exists()


def test_pipeline_all_structure_types(context, tmp_path):
    for stype in ["iso_line", "dense_ls", "contact", "via", "trench", "fin", "gate", "sti", "bimaterial", "pitch_std"]:
        result = run_pipeline(context, _cfg(**{"structure.structure_type": stype}), tmp_path, 0, f"test_{stype}", 1, write_outputs=False)
        assert result.status == "OK", f"{stype}: {result.error}"


def test_job_batch(context, tmp_path):
    from semicon.orchestration.job import run_job

    dist = {s: 1 for s in ["iso_line", "dense_ls", "contact", "via", "trench", "fin", "gate", "sti", "bimaterial", "pitch_std"]}
    cfg = _cfg(**{"dataset.structure_distribution": dist})
    out = tmp_path / "batch"
    job = run_job(context, cfg, out, n_samples=10, master_seed=7, write_outputs=True)
    assert job.n_ok == 10, job.failures
    assert (out / "dataset_index.json").exists()
    idx = json.loads((out / "dataset_index.json").read_text())
    assert idx["n_samples"] == 10
    assert (out / "SHA256SUMS").exists()
    assert (out / "splits" / "train.txt").exists()
