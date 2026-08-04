"""Command-line interface (DG1).

    generate.py build-library --out <gds>
    generate.py run     --config <yml> [--out DIR] [--seed N] [--tag NAME]
    generate.py batch   --config <yml> --n N [--out DIR] [--seed N]
    generate.py self-check
    generate.py version
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from semicon.orchestration.pipeline import APP_VERSION, RuntimeContext, build_context


def _default_lib_path() -> str:
    return str(Path(__file__).resolve().parents[3] / "structure_library" / "semicon.gds")


def _default_config_path() -> str:
    return str(Path(__file__).resolve().parents[3] / "configs" / "demo.yml")


def _defaults_path() -> str:
    return str(Path(__file__).resolve().parents[3] / "configs" / "defaults.yml")


def _log_level(level: str) -> int:
    return getattr(logging, level.upper(), logging.INFO)


def _parse_overrides(pairs: list) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for p in pairs:
        if "=" not in p:
            raise SystemExit(f"override must be key=value, got {p!r}")
        k, v = p.split("=", 1)
        out[k] = _coerce(v)
    return out


def _coerce(v: str) -> Any:
    try:
        return json.loads(v)
    except ValueError:
        return v


def build_library(args: argparse.Namespace) -> int:
    from semicon.geometry.structures import build_structure_library
    from semicon.geometry.raster import save_library

    lib = build_structure_library(fov_nm=args.fov, cd_nm=args.cd, height_nm=args.height, pitch_nm=args.pitch)
    out = Path(args.out)
    save_library(lib, out)
    print(f"[ok] wrote structure library with {len(lib.structures)} structures -> {out}")
    return 0


def _load_context(args) -> RuntimeContext:
    lib = getattr(args, "library", None) or _default_lib_path()
    mats = getattr(args, "materials", None)
    return build_context(lib, mats, app_version=APP_VERSION, git_hash=_git_hash())


def _git_hash() -> str:
    try:
        import subprocess

        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=Path(__file__).resolve().parents[3], text=True).strip()
    except Exception:
        return "dev"


def run_sample(args: argparse.Namespace) -> int:
    from semicon.orchestration.config import load_config
    from semicon.orchestration.pipeline import run_pipeline

    cfg = load_config(args.config, defaults_path=_defaults_path(), overrides=_parse_overrides(args.overrides or []))
    context = _load_context(args)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    seed = int(args.seed or cfg.general.get("seed", 42))
    result = run_pipeline(context, cfg, out, 0, cfg.general.get("dataset_name", "demo"), seed)
    print(json.dumps({"status": result.status, "timing": result.timing, "error": result.error, "artifacts": result.artifacts}, indent=2))
    return 0 if result.status == "OK" else 1


def batch(args: argparse.Namespace) -> int:
    from semicon.orchestration.config import load_config
    from semicon.orchestration.job import run_job

    cfg = load_config(args.config, defaults_path=_defaults_path(), overrides=_parse_overrides(args.overrides or []))
    context = _load_context(args)
    out = Path(args.out)
    seed = int(args.seed) if args.seed else None
    job = run_job(context, cfg, out, n_samples=int(args.n), master_seed=seed, config_path=args.config)
    print(
        json.dumps(
            {
                "n_total": job.n_total,
                "n_ok": job.n_ok,
                "n_failed": job.n_failed,
                "failures": job.failures,
                "index_path": job.index_path,
            },
            indent=2,
        )
    )
    return 0 if job.n_failed == 0 else 1


def self_check(args: argparse.Namespace) -> int:
    """Quick end-to-end sanity run (no outputs) + module import check."""
    from semicon.orchestration.config import load_config
    from semicon.orchestration.pipeline import run_pipeline

    print("[1/3] importing modules ...")
    import semicon.foundation  # noqa: F401
    import semicon.geometry  # noqa: F401
    import semicon.physics  # noqa: F401
    import semicon.dataset  # noqa: F401
    import semicon.orchestration  # noqa: F401

    print("[2/3] building context ...")
    context = _load_context(args)
    print(f"      structures in library: {len(context.library.structures)}")
    print(f"      materials: {len(context.materials.records)}")

    print("[3/3] running single-sample pipeline (no output files) ...")
    cfg = load_config(None, defaults_path=_defaults_path())
    result = run_pipeline(context, cfg, Path("."), 0, "selfcheck", 42, write_outputs=False)
    if result.status == "OK":
        print(f"      OK  total={result.timing['total_s']:.3f}s  SE range="
              f"{result.metadata['physics']['signal'].get('se_range')}")
        return 0
    print(f"      FAILED: {result.error}")
    return 1


def version(args: argparse.Namespace) -> int:
    print(f"semicon-sim {APP_VERSION}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="generate.py", description="SEMICON 2026 Synthetic SEM Image Generator (DG1)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("build-library", help="generate the GDSII structure library")
    p.add_argument("--out", default=_default_lib_path())
    p.add_argument("--fov", type=float, default=300.0)
    p.add_argument("--cd", type=float, default=30.0)
    p.add_argument("--height", type=float, default=60.0)
    p.add_argument("--pitch", type=float, default=None)
    p.set_defaults(func=build_library)

    p = sub.add_parser("run", help="generate a single sample")
    p.add_argument("--config", default=_default_config_path())
    p.add_argument("--out", default="demo_output")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--library", default=None)
    p.add_argument("--materials", default=None)
    p.add_argument("--overrides", action="append", default=None)
    p.set_defaults(func=run_sample)

    p = sub.add_parser("batch", help="generate a small batch dataset")
    p.add_argument("--config", default=_default_config_path())
    p.add_argument("--n", type=int, default=16)
    p.add_argument("--out", default="demo_output")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--library", default=None)
    p.add_argument("--materials", default=None)
    p.add_argument("--overrides", action="append", default=None)
    p.set_defaults(func=batch)

    p = sub.add_parser("self-check", help="end-to-end sanity check")
    p.add_argument("--library", default=None)
    p.set_defaults(func=self_check)

    p = sub.add_parser("version")
    p.set_defaults(func=version)

    args = parser.parse_args(argv)
    logging.basicConfig(level=_log_level(getattr(args, "log_level", "INFO")), format="%(levelname)s %(message)s")
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
