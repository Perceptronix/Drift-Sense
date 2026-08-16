#!/usr/bin/env python3
"""Generate synthetic SEM localization image pairs.

Each generated pair contains:
- a search image
- a reference image cropped from the search image
- ground-truth center (x, y) of the reference pattern in search coordinates

Required parameters:
- architecture style: DRAM or FinFET
- number of pairs
- output directory
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import cv2
import numpy as np


def _add_noise_and_blur(image: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    noisy = image.astype(np.float32)
    shot = rng.poisson(np.clip(noisy, 0, 255)).astype(np.float32)
    detector = rng.normal(0.0, 8.0, size=noisy.shape).astype(np.float32)
    merged = 0.6 * noisy + 0.35 * shot + 0.05 * (noisy + detector)
    blurred = cv2.GaussianBlur(merged, (5, 5), sigmaX=1.1)
    return np.clip(blurred, 0, 255).astype(np.uint8)


def _generate_dram_canvas(size: int, rng: np.random.Generator) -> np.ndarray:
    img = np.full((size, size), 40, dtype=np.uint8)
    pitch = int(rng.integers(18, 34))
    line_w = int(rng.integers(2, 5))

    for x in range(0, size, pitch):
        cv2.line(img, (x, 0), (x, size - 1), color=155, thickness=line_w)

    for y in range(0, size, pitch):
        cv2.line(img, (0, y), (size - 1, y), color=140, thickness=max(1, line_w - 1))

    step = pitch * 2
    radius = max(2, int(pitch * 0.25))
    for x in range(pitch // 2, size, step):
        for y in range(pitch // 2, size, step):
            cv2.circle(img, (x, y), radius, color=210, thickness=-1)

    return _add_noise_and_blur(img, rng)


def _generate_finfet_canvas(size: int, rng: np.random.Generator) -> np.ndarray:
    img = np.full((size, size), 35, dtype=np.uint8)
    fin_pitch = int(rng.integers(16, 28))
    fin_w = int(rng.integers(3, 6))

    for x in range(0, size, fin_pitch):
        cv2.rectangle(img, (x, 0), (min(size - 1, x + fin_w), size - 1), color=170, thickness=-1)

    gate_pitch = int(rng.integers(42, 74))
    gate_h = int(rng.integers(4, 8))

    offset = int(rng.integers(0, gate_pitch))
    for y in range(offset, size, gate_pitch):
        cv2.rectangle(img, (0, y), (size - 1, min(size - 1, y + gate_h)), color=95, thickness=-1)

    for _ in range(35):
        x0 = int(rng.integers(0, size - 20))
        y0 = int(rng.integers(0, size - 20))
        w = int(rng.integers(8, 20))
        h = int(rng.integers(8, 20))
        cv2.rectangle(img, (x0, y0), (min(size - 1, x0 + w), min(size - 1, y0 + h)), color=int(rng.integers(60, 120)), thickness=-1)

    return _add_noise_and_blur(img, rng)


def _build_search_image(style: str, size: int, rng: np.random.Generator) -> np.ndarray:
    style_norm = style.strip().lower()
    if style_norm == "dram":
        return _generate_dram_canvas(size=size, rng=rng)
    if style_norm == "finfet":
        return _generate_finfet_canvas(size=size, rng=rng)
    raise ValueError("architecture style must be DRAM or FinFET")


def generate_pairs(architecture_style: str, num_pairs: int, output_dir: Path, seed: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    references_dir = output_dir / "reference"
    searches_dir = output_dir / "search"
    references_dir.mkdir(parents=True, exist_ok=True)
    searches_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(seed)

    records = []
    for idx in range(num_pairs):
        pair_id = f"pair_{idx:05d}"
        search = _build_search_image(architecture_style, size=512, rng=rng)

        ref_size = int(rng.integers(96, 161))
        x0 = int(rng.integers(0, search.shape[1] - ref_size + 1))
        y0 = int(rng.integers(0, search.shape[0] - ref_size + 1))

        reference = search[y0 : y0 + ref_size, x0 : x0 + ref_size].copy()

        search_path = searches_dir / f"{pair_id}_search.png"
        reference_path = references_dir / f"{pair_id}_reference.png"

        cv2.imwrite(str(search_path), search)
        cv2.imwrite(str(reference_path), reference)

        records.append(
            {
                "pair_id": pair_id,
                "architecture_style": architecture_style,
                "reference_image": str(reference_path.relative_to(output_dir)),
                "search_image": str(search_path.relative_to(output_dir)),
                "reference_size": ref_size,
                "center_x": x0 + ref_size / 2.0,
                "center_y": y0 + ref_size / 2.0,
            }
        )

    json_path = output_dir / "ground_truth.json"
    csv_path = output_dir / "ground_truth.csv"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "pair_id",
                "architecture_style",
                "reference_image",
                "search_image",
                "reference_size",
                "center_x",
                "center_y",
            ],
        )
        writer.writeheader()
        writer.writerows(records)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic localization image pairs")
    parser.add_argument(
        "--architecture-style",
        required=True,
        choices=["DRAM", "FinFET", "dram", "finfet"],
        help="Architecture style to generate (DRAM or FinFET)",
    )
    parser.add_argument(
        "--num-pairs",
        type=int,
        required=True,
        help="Number of image pairs to generate",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where generated image pairs and ground truth are saved",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible generation",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.num_pairs <= 0:
        raise SystemExit("--num-pairs must be > 0")

    generate_pairs(
        architecture_style=args.architecture_style,
        num_pairs=args.num_pairs,
        output_dir=args.output_dir,
        seed=args.seed,
    )
    print(f"Generated {args.num_pairs} pair(s) in: {args.output_dir}")


if __name__ == "__main__":
    main()
