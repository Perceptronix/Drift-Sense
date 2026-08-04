"""Dataset writer (Phase 4.4; interface I8).

Writes the canonical per-sample layout and finalizes the dataset index,
splits, and SHA-256 registry. Writes are atomic (temp file + rename) so a
crash never leaves a half-written sample.

CHUNKED LAYOUT (Hugging Face compatible):
  images/chunk_NNN/
  ground_truth/chunk_NNN/
  metadata/chunk_NNN/

Each chunk contains CHUNK_SIZE samples (default 1000).
No directory exceeds 5000 files.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from semicon.foundation.datatypes import GroundTruth, HeightField, MaterialMap, SEMImage
from semicon.foundation.image_io import save_png, save_tiff

# Chunk configuration
CHUNK_SIZE = 1000  # samples per chunk directory


def _get_chunk(sample_index: int) -> str:
    """Deterministic chunk name from sample index."""
    return f"chunk_{sample_index // CHUNK_SIZE:03d}"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(str(tmp), str(path))


def write_sample(
    out_dir: Path,
    sample_index: int,
    sem_image: SEMImage,
    ground_truth: GroundTruth,
    height_field: HeightField,
    material_map: MaterialMap,
    config_dict: Dict[str, Any],
    metadata_dict: Dict[str, Any],
    timing_dict: Dict[str, Any],
    write_aux: bool = True,
) -> Dict[str, Any]:
    """Persist one sample. Returns {artifact: sha256} dict.

    Writes to chunked directories: images/chunk_NNN/, ground_truth/chunk_NNN/, metadata/chunk_NNN/
    """
    out_dir = Path(out_dir)
    name = f"{sample_index:06d}"
    chunk = _get_chunk(sample_index)

    paths = {
        "image": out_dir / "images" / chunk / f"{name}.tiff",
        "gt": out_dir / "ground_truth" / chunk / f"{name}_gt.json",
        "height": out_dir / "ground_truth" / chunk / f"{name}_height.npy",
        "material": out_dir / "ground_truth" / chunk / f"{name}_material.png",
        "config": out_dir / "metadata" / chunk / f"{name}_config.json",
        "metadata": out_dir / "metadata" / chunk / f"{name}_metadata.json",
        "timing": out_dir / "metadata" / chunk / f"{name}_timing.json",
    }

    save_tiff(sem_image.data, paths["image"])
    gt_json = {
        "sample": name,
        "structure_type": config_dict.get("structure", {}).get("structure_type", ""),
        "pixel_size_nm": sem_image.pixel_size_nm,
        "cd_measurements": ground_truth.cd_measurements,
        "contours": [c.tolist() for c in ground_truth.contours],
        "edge_map_summary": {
            "min": float(ground_truth.edge_map.min()),
            "max": float(ground_truth.edge_map.max()),
        },
    }
    _atomic_write_text(paths["gt"], json.dumps(gt_json, indent=2))

    if write_aux:
        paths["height"].parent.mkdir(parents=True, exist_ok=True)
        np.save(paths["height"], height_field.data)
        rgb = material_map.as_rgb()
        save_png(rgb, paths["material"])

    _atomic_write_text(paths["config"], json.dumps(config_dict, indent=2))
    _atomic_write_text(paths["metadata"], json.dumps(metadata_dict, indent=2))
    _atomic_write_text(paths["timing"], json.dumps(timing_dict, indent=2))

    artifacts = {v.relative_to(out_dir).as_posix(): _sha256(v) for k, v in paths.items() if v.exists()}
    return artifacts


def finalize_dataset(
    out_dir: Path,
    dataset_name: str,
    dataset_version: str,
    samples: List[Dict[str, Any]],
    master_seed: int,
    app_version: str,
    git_hash: str,
    config_snapshot: Optional[Dict[str, Any]] = None,
    splits: Optional[Dict[str, List[int]]] = None,
) -> Path:
    """Write dataset_index.json, splits/, and SHA256SUMS."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    index = {
        "dataset": dataset_name,
        "dataset_version": dataset_version,
        "schema_version": "1.0",
        "n_samples": len(samples),
        "n_success": sum(1 for s in samples if s["status"] == "OK"),
        "n_failed": sum(1 for s in samples if s["status"] != "OK"),
        "rng_master_seed": master_seed,
        "provenance": {
            "app_version": app_version,
            "git_hash": git_hash,
            "generation_config": config_snapshot or {},
        },
        "license": "CC BY 4.0",
        "samples": samples,
    }
    if splits:
        index["splits"] = {k: v for k, v in splits.items()}
    _atomic_write_text(out_dir / "dataset_index.json", json.dumps(index, indent=2))

    if splits:
        sp = out_dir / "splits"
        sp.mkdir(parents=True, exist_ok=True)
        for part, ids in splits.items():
            _atomic_write_text(sp / f"{part}.txt", "\n".join(f"{i:06d}" for i in ids) + "\n")

    # SHA-256 registry over all files
    sums = []
    for root, _dirs, files in os.walk(out_dir):
        for fn in sorted(files):
            p = Path(root) / fn
            if p.name == "SHA256SUMS":
                continue
            rel = p.relative_to(out_dir).as_posix()
            sums.append(f"{_sha256(p)}  {rel}")
    sums.sort()
    _atomic_write_text(out_dir / "SHA256SUMS", "\n".join(sums) + "\n")
    return out_dir / "dataset_index.json"
