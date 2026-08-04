"""Deterministic dataset splitting (Phase 4.4; Phase 5.4 IN18).

Stratified 70/15/15 by structure type, derived from the master seed so the
split is stable across regenerations and leakage-free (each sample belongs
to exactly one split).
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np


def stratify_split(
    sample_types: List[str],
    master_seed: int,
    train: float = 0.70,
    val: float = 0.15,
    test: float = 0.15,
) -> Dict[str, List[int]]:
    rng = np.random.default_rng(master_seed)
    train_ids, val_ids, test_ids = [], [], []
    by_type: Dict[str, List[int]] = {}
    for i, t in enumerate(sample_types):
        by_type.setdefault(t, []).append(i)
    for t, ids in sorted(by_type.items()):
        perm = rng.permutation(ids)
        n = len(perm)
        n_tr = int(round(n * train))
        n_va = int(round(n * val))
        train_ids.extend(perm[:n_tr].tolist())
        val_ids.extend(perm[n_tr : n_tr + n_va].tolist())
        test_ids.extend(perm[n_tr + n_va :].tolist())
    return {"train": sorted(train_ids), "val": sorted(val_ids), "test": sorted(test_ids)}
