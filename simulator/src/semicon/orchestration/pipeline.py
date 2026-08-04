"""orch_pipeline (Phase 5.4): the 10-stage image-generation pipeline.

Stages
  S0  Load structure library (GDSII)
  S1  Rasterize -> MaskSet                       (I1)
  S2  Process   -> deterministic H + material    (I2)
  S3  Variability -> H_var, mat_var              (I3)
  S4  Signal    -> YieldMaps                     (I4)
  S5  Degrade   -> degraded SE map               (I5)
  S6  Formation -> SEMImage                      (I6)
  S7  Ground truth                               (I7)
  S8  Metadata assembly                          (D10)
  S9  Writer    -> canonical artifacts           (I8)

The pipeline is pure w.r.t. its inputs: identical (config, library,
material_library, seed) yields identical outputs.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from semicon.dataset.groundtruth import build_ground_truth
from semicon.dataset.writer import write_sample
from semicon.foundation.datatypes import Config
from semicon.foundation.rng_utils import SeedManager
from semicon.geometry import process, raster
from semicon.geometry._raster.mask_builder import MaskSet
from semicon.physics import degrade, formation, signal
from semicon.physics._shared.material_properties import MaterialLibrary, library_checksum, load_material_library

APP_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0"


@dataclass
class RuntimeContext:
    library: Any  # GdsLibrary
    materials: MaterialLibrary
    app_version: str = APP_VERSION
    git_hash: str = "dev"
    schema_version: str = SCHEMA_VERSION
    config_path: Optional[str] = None


def build_context(
    structure_library_path: str,
    material_library_path: Optional[str] = None,
    app_version: str = APP_VERSION,
    git_hash: str = "dev",
) -> RuntimeContext:
    lib = raster.load_library(structure_library_path)
    mats = load_material_library(material_library_path) if material_library_path else MaterialLibrary()
    return RuntimeContext(library=lib, materials=mats, app_version=app_version, git_hash=git_hash)


@dataclass
class SampleResult:
    sample_index: int
    status: str  # OK | FAILED
    artifacts: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timing: Dict[str, float] = field(default_factory=dict)
    warnings: list = field(default_factory=list)


def run_pipeline(
    context: RuntimeContext,
    config: Config,
    out_dir: Path,
    sample_index: int,
    dataset_name: str,
    master_seed: int,
    write_outputs: bool = True,
) -> SampleResult:
    """Execute the full 10-stage pipeline for one sample."""
    result = SampleResult(sample_index=sample_index, status="FAILED")
    t0 = time.perf_counter()
    try:
        st = config.structure
        stype = st["structure_type"]
        cd = float(st["cd_nm"])
        height = float(st["height_nm"])
        pitch = st.get("pitch_nm")
        pitch = float(pitch) if pitch is not None else None
        width_nm = float(st["width_nm"])
        height_fov = float(st["height_nm_fov"])
        ps = float(st["pixel_size_nm"])

        seeds = SeedManager(master_seed)
        seeds.set_image(dataset_name, sample_index)

        # S1 rasterize (I1)
        t = time.perf_counter()
        mask_set: MaskSet = raster.rasterize(
            context.library, stype, width_nm, height_fov, ps, ss=int(st.get("ss", 4))
        )
        result.timing["rasterize_s"] = time.perf_counter() - t

        # S2 process (I2)
        t = time.perf_counter()
        h_det, mat_det = process.build_geometry(
            mask_set, stype, cd, height, pitch, ps,
            substrate_top_nm=float(st.get("substrate_top_nm", 100.0)),
        )
        result.timing["process_s"] = time.perf_counter() - t

        # S3 variability (I3)
        t = time.perf_counter()
        h_var, mat_var, var_record = _variability_apply(h_det, mat_det, config, seeds)
        result.timing["variability_s"] = time.perf_counter() - t
        result.warnings.extend(var_record.warnings if hasattr(var_record, "warnings") else [])

        # S4 signal (I4)
        t = time.perf_counter()
        yields, sig_record = signal.compute_yields(h_var, mat_var, context.materials, config.physics)
        result.timing["signal_s"] = time.perf_counter() - t
        result.warnings.extend(sig_record.warnings)

        # S5 degrade (I5)
        t = time.perf_counter()
        se_degraded, deg_record = degrade.degrade_yields(yields, config.physics, seeds.stage_seed("degrade"))
        result.timing["degrade_s"] = time.perf_counter() - t

        # S6 formation (I6)
        t = time.perf_counter()
        image, form_record = formation.form_image(se_degraded, ps, config.detector)
        result.timing["formation_s"] = time.perf_counter() - t

        # S7 ground truth (I7)
        t = time.perf_counter()
        gt = build_ground_truth(h_var, mat_var, stype, cd, pitch)
        result.timing["groundtruth_s"] = time.perf_counter() - t

        # S8 metadata assembly (D10)
        metadata = _assemble_metadata(config, seeds, context, sig_record, deg_record, var_record)
        result.metadata = metadata

        # S9 write (I8)
        t = time.perf_counter()
        config_dict = config.merged()
        timing_dict = dict(result.timing)
        artifacts: Dict[str, str] = {}
        if write_outputs:
            artifacts = write_sample(
                out_dir, sample_index, image, gt, h_var, mat_var,
                config_dict, metadata, timing_dict, write_aux=True,
            )
        result.timing["write_s"] = time.perf_counter() - t
        result.artifacts = artifacts
        result.status = "OK"
    except Exception as exc:  # noqa: BLE001 - pipeline errors are reported
        result.error = f"{type(exc).__name__}: {exc}"
    result.timing["total_s"] = time.perf_counter() - t0
    return result


def _variability_apply(h_det, mat_det, config: Config, seeds: SeedManager):
    from semicon.geometry import variability

    var_cfg = dict(config.variability)
    var_cfg.setdefault("enabled", True)
    return variability.apply_variability(h_det, mat_det, var_cfg, seeds.stage_seed("variability"))


def _assemble_metadata(config, seeds, context, sig_record, deg_record, var_record) -> Dict[str, Any]:
    st = config.structure
    var_dict = var_record.to_dict() if hasattr(var_record, "to_dict") else {}
    return {
        "structure": {
            "structure_type": st.get("structure_type"),
            "cd_nm": st.get("cd_nm"),
            "height_nm": st.get("height_nm"),
            "pitch_nm": st.get("pitch_nm"),
        },
        "process": {
            "layer_stack": config.process.get("layer_stack", []),
            "substrate_top_nm": st.get("substrate_top_nm", 100.0),
        },
        "variability": var_dict,
        "physics": {
            "beam_energy_keV": config.physics.get("beam_energy_keV"),
            "probe_current_pA": config.physics.get("probe_current_pA"),
            "probe_diameter_nm": config.physics.get("probe_diameter_nm"),
            "signal": sig_record.to_dict() if hasattr(sig_record, "to_dict") else {},
            "degrade": dict(deg_record),
        },
        "seeds": seeds.snapshot(),
        "version": {
            "app_version": context.app_version,
            "git_hash": context.git_hash,
            "schema_version": context.schema_version,
            "material_library_hash": library_checksum(),
        },
        "provenance": {
            "generation_date": None,  # filled by writer if needed
            "dataset_name": seeds._dataset_name,
            "dataset_version": config.general.get("dataset_version", "0.1.0"),
            "warnings": [],
        },
    }
