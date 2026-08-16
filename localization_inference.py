#!/usr/bin/env python3
"""Predict reference center (x, y) in a search image.

Usage:
    python localization_inference.py --reference-image <path> --search-image <path>

Output:
    x,y
"""

from __future__ import annotations

import argparse

import cv2
import numpy as np


def _read_grayscale(path: str) -> np.ndarray:
    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"Unable to read image: {path}")

    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image = image.astype(np.float32)
    image -= image.min()
    denom = image.max() if image.max() > 0 else 1.0
    return image / denom


def _candidate_scales(reference: np.ndarray, search: np.ndarray) -> list[float]:
    h_r, w_r = reference.shape
    h_s, w_s = search.shape

    max_scale = min(h_s / max(h_r, 1), w_s / max(w_r, 1), 1.25)
    min_scale = max(0.08, min(1.0 / max(h_r, 1), 1.0 / max(w_r, 1)))

    scales = np.geomspace(min_scale, max_scale, num=40)
    return sorted({float(s) for s in np.concatenate([scales, np.array([0.1, 0.2, 0.5, 1.0])]) if s > 0})


def predict_center(reference: np.ndarray, search: np.ndarray) -> tuple[float, float]:
    best_score = -1.0
    best_center = None

    for scale in _candidate_scales(reference, search):
        new_w = max(1, int(round(reference.shape[1] * scale)))
        new_h = max(1, int(round(reference.shape[0] * scale)))

        if new_h > search.shape[0] or new_w > search.shape[1] or new_h < 8 or new_w < 8:
            continue

        interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
        template = cv2.resize(reference, (new_w, new_h), interpolation=interp)

        response = cv2.matchTemplate(search, template, cv2.TM_CCOEFF_NORMED)
        _, score, _, max_loc = cv2.minMaxLoc(response)

        if score > best_score:
            best_score = score
            best_center = (max_loc[0] + new_w / 2.0, max_loc[1] + new_h / 2.0)

    if best_center is None:
        raise RuntimeError("No valid template scale could be evaluated")

    return best_center


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict localization center of a reference pattern")
    parser.add_argument("--reference-image", required=True, help="Path to the reference image")
    parser.add_argument("--search-image", required=True, help="Path to the search image")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    reference = _read_grayscale(args.reference_image)
    search = _read_grayscale(args.search_image)

    x, y = predict_center(reference, search)
    print(f"{x:.3f},{y:.3f}")


if __name__ == "__main__":
    main()
