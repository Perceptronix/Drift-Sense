"""orch_job (Phase 5.4): batch sample-plan execution + dataset finalization.

A job derives a deterministic sample plan (config + master seed) and
executes each sample through the pipeline. Runs sequentially for DG1;
parallel execution is a DG2+ optimization. Statuses are tracked and the
dataset is finalized with index, splits, and checksums.
"""
from __future__ import annotations

import json
import logging
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from semicon.dataset.splitter import stratify_split
from semicon.foundation.datatypes import STRUCTURE_TYPES, Config
from semicon.orchestration.pipeline import RuntimeContext, run_pipeline

log = logging.getLogger("semicon.job")


@dataclass
class JobResult:
    n_total: int = 0
    n_ok: int = 0
    n_failed: int = 0
    failures: List[str] = None  # type: ignore[assignment]
    index_path: Optional[str] = None

    def __post_init__(self) -> None:
        if self.failures is None:
            self.failures = []


def _sample_plan(config: Config, n_samples: int, master_seed: int) -> List[Dict[str, Any]]:
    """Deterministic plan: sample index -> (structure_type, overrides)."""
    rng = random.Random(master_seed)
    dist = config.dataset.get("structure_distribution")
    stype = config.structure.get("structure_type")
    types: List[str] = []
    if dist:
        total = sum(float(v) for v in dist.values())
        for t, w in dist.items():
            types.extend([t] * int(round(n_samples * float(w) / total)))
        while len(types) < n_samples:
            types.append(stype or "iso_line")
        types = types[:n_samples]
    else:
        types = [stype] * n_samples
    # deterministic shuffle
    rng.shuffle(types)
    plan = []
    for i, t in enumerate(types):
        overrides: Dict[str, Any] = {"structure.structure_type": t}
        if config.dataset.get("random_parameters"):
            overrides.update(_random_params(config, rng))
        plan.append({"sample_index": i, "structure_type": t, "overrides": overrides})
    return plan


def _random_params(config: Config, rng: random.Random) -> Dict[str, Any]:
    lo, hi = config.dataset.get("cd_range", [30, 60])
    hlo, hhi = config.dataset.get("height_range", [40, 100])
    plo, phi = config.dataset.get("pitch_range", [60, 150])
    return {
        "structure.cd_nm": rng.uniform(lo, hi),
        "structure.height_nm": rng.uniform(hlo, hhi),
        "structure.pitch_nm": rng.uniform(plo, phi),
    }


def run_job(
    context: RuntimeContext,
    config: Config,
    out_dir: Path,
    n_samples: int = 1,
    master_seed: Optional[int] = None,
    write_outputs: bool = True,
    config_path: Optional[str] = None,
) -> JobResult:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    seed = int(master_seed or config.general.get("seed", 42))
    dataset_name = config.general.get("dataset_name", "demo")
    dataset_version = config.general.get("dataset_version", "0.1.0")

    plan = _sample_plan(config, n_samples, seed)
    sample_entries: List[Dict[str, Any]] = []
    types: List[str] = []

    for item in plan:
        sample_cfg = _with_overrides(config, item["overrides"])
        result = run_pipeline(
            context, sample_cfg, out_dir, item["sample_index"],
            dataset_name, seed, write_outputs=write_outputs,
        )
        types.append(item["structure_type"])
        entry = {
            "sample_index": item["sample_index"],
            "structure_type": item["structure_type"],
            "status": result.status,
            "artifacts": result.artifacts,
        }
        if result.error:
            entry["error"] = result.error
        sample_entries.append(entry)
        if result.status == "OK":
            log.info("sample %06d OK (%s) %.2fs", item["sample_index"], item["structure_type"], result.timing.get("total_s", 0))
        else:
            log.error("sample %06d FAILED: %s", item["sample_index"], result.error)

    result = JobResult(
        n_total=n_samples,
        n_ok=sum(1 for e in sample_entries if e["status"] == "OK"),
        n_failed=sum(1 for e in sample_entries if e["status"] != "OK"),
        failures=[e.get("error", "") for e in sample_entries if e["status"] != "OK"],
    )

    if write_outputs and n_samples > 1:
        splits = stratify_split(types, seed)
        from semicon.dataset.writer import finalize_dataset

        index = finalize_dataset(
            out_dir,
            dataset_name,
            dataset_version,
            sample_entries,
            seed,
            context.app_version,
            context.git_hash,
            config_snapshot=config.merged(),
            splits=splits,
        )
        result.index_path = str(index)
    return result


def _with_overrides(config: Config, overrides: Dict[str, Any]) -> Config:
    from semicon.orchestration.config import _apply_overrides, _to_config

    merged = _apply_overrides(config.merged(), overrides)
    return _to_config(merged)


def build_manifest(config: Config, n_samples: int, master_seed: int) -> Dict[str, Any]:
    plan = _sample_plan(config, n_samples, master_seed)
    return {
        "dataset": config.general.get("dataset_name", "demo"),
        "dataset_version": config.general.get("dataset_version", "0.1.0"),
        "master_seed": master_seed,
        "n_samples": n_samples,
        "samples": plan,
    }
