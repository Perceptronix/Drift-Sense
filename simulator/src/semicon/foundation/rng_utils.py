"""Deterministic random-number management (Phase 4.3 RD7).

Seed hierarchy:
    master_seed
      -> structure_seed  = derive(master, dataset_name, structure_key)
      -> image_seed      = derive(master, dataset_name, sample_index)
           -> stage seeds = derive(image_seed, stage_name)

All generation uses ``numpy.random.Generator`` (PCG64) for portability and
reproducibility. Derivation uses SHA-256 in a fixed, documented way.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional

import numpy as np


def derive(seed: int, *parts: Any) -> int:
    """Deterministically derive a child seed from a parent seed + labels."""
    payload = json.dumps([seed] + [str(p) for p in parts], sort_keys=True).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big")  # 64-bit sub-seed


class SeedManager:
    """Tracks and derives the full seed chain for one run."""

    def __init__(self, master_seed: int) -> None:
        if master_seed <= 0:
            raise ValueError(f"master_seed must be positive, got {master_seed}")
        self.master_seed = int(master_seed)
        self._image_seed: Optional[int] = None
        self._dataset_name: str = "default"
        self._sample_index: int = 0

    def set_image(self, dataset_name: str, sample_index: int) -> None:
        self._dataset_name = str(dataset_name)
        self._sample_index = int(sample_index)
        self._image_seed = derive(self.master_seed, dataset_name, sample_index)

    @property
    def image_seed(self) -> int:
        if self._image_seed is None:
            self.set_image("default", 0)
        return int(self._image_seed)  # type: ignore[return-value]

    def stage_seed(self, stage: str) -> int:
        return derive(self.image_seed, stage)

    def stage_generator(self, stage: str) -> np.random.Generator:
        return np.random.default_rng(self.stage_seed(stage))

    def snapshot(self) -> Dict[str, Any]:
        return {
            "master_seed": self.master_seed,
            "dataset_name": self._dataset_name,
            "sample_index": self._sample_index,
            "image_seed": self.image_seed,
        }
