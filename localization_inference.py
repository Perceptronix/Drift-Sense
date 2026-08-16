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


def _template_candidates(reference: np.ndarray, search: np.ndarray) -> list[dict]:
    candidates = []
    for scale in _candidate_scales(reference, search):
        new_w = max(1, int(round(reference.shape[1] * scale)))
        new_h = max(1, int(round(reference.shape[0] * scale)))
        if new_h > search.shape[0] or new_w > search.shape[1] or new_h < 8 or new_w < 8:
            continue

        interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
        template = cv2.resize(reference, (new_w, new_h), interpolation=interp)
        response = cv2.matchTemplate(search, template, cv2.TM_CCOEFF_NORMED)
        _, score, _, max_loc = cv2.minMaxLoc(response)
        candidates.append(
            {
                "score": float(score),
                "x": int(max_loc[0]),
                "y": int(max_loc[1]),
                "w": int(new_w),
                "h": int(new_h),
            }
        )

    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates[:8]


def _try_dino_rerank(reference: np.ndarray, search: np.ndarray, candidates: list[dict]) -> tuple[float, float] | None:
    if not candidates:
        return None

    try:
        import torch
        import torch.nn.functional as F
    except Exception:
        return None

    try:
        model = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14")
    except Exception:
        return None

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device).eval()

    def _embed(image_2d: np.ndarray) -> "torch.Tensor":
        patch = cv2.resize(image_2d, (224, 224), interpolation=cv2.INTER_AREA)
        tensor = torch.from_numpy(patch).float().unsqueeze(0).unsqueeze(0).to(device)
        tensor = tensor.repeat(1, 3, 1, 1)
        with torch.no_grad():
            features = model.forward_features(tensor)
            return features["x_norm_clstoken"]

    ref_embedding = _embed(reference)
    best = None
    best_sim = -1.0

    for item in candidates:
        crop = search[item["y"] : item["y"] + item["h"], item["x"] : item["x"] + item["w"]]
        if crop.size == 0:
            continue
        emb = _embed(crop)
        sim = float(F.cosine_similarity(ref_embedding, emb).item())
        if sim > best_sim:
            best_sim = sim
            best = item

    if best is None:
        return None

    return best["x"] + best["w"] / 2.0, best["y"] + best["h"] / 2.0


def predict_center(reference: np.ndarray, search: np.ndarray) -> tuple[float, float]:
    candidates = _template_candidates(reference, search)
    if not candidates:
        raise RuntimeError("No valid template scale could be evaluated")

    dino_center = _try_dino_rerank(reference, search, candidates)
    if dino_center is not None:
        return dino_center

    top = candidates[0]
    return top["x"] + top["w"] / 2.0, top["y"] + top["h"] / 2.0


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
