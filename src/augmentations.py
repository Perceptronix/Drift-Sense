import cv2
import numpy as np


def _transform_points(points, M):
    points = np.asarray(points, dtype=np.float32)
    if len(points) == 0:
        return points

    ones = np.ones((len(points), 1), dtype=np.float32)
    pts = np.hstack([points, ones])
    return pts @ M.T


def geometry_transform(image, contours, rotation=0.0, scale=1.0):
    h, w = image.shape[:2]

    cx, cy = w / 2, h / 2

    M = cv2.getRotationMatrix2D((cx, cy), rotation, scale)

    image = cv2.warpAffine(
        image,
        M,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT
    )

    new_contours = []

    for contour in contours:
        pts = np.asarray(contour, dtype=np.float32)

        if len(pts) == 0:
            new_contours.append(pts)
            continue

        new_pts = _transform_points(pts, M)
        new_contours.append(new_pts.tolist())

    return image, new_contours


def elastic_warp(image, contours, strength=2.0, smooth=80.0):
    h, w = image.shape[:2]

    dx = np.random.randn(h, w).astype(np.float32)
    dy = np.random.randn(h, w).astype(np.float32)

    dx = cv2.GaussianBlur(dx, (0, 0), smooth)
    dy = cv2.GaussianBlur(dy, (0, 0), smooth)

    dx = dx / (np.std(dx) + 1e-8) * strength
    dy = dy / (np.std(dy) + 1e-8) * strength

    xx, yy = np.meshgrid(
        np.arange(w, dtype=np.float32),
        np.arange(h, dtype=np.float32)
    )

    map_x = xx + dx
    map_y = yy + dy

    warped = cv2.remap(
        image,
        map_x,
        map_y,
        cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT
    )

    new_contours = []

    for contour in contours:
        pts = np.asarray(contour, dtype=np.float32)

        if len(pts) == 0:
            new_contours.append(pts)
            continue

        x = np.clip(np.round(pts[:, 0]).astype(int), 0, w - 1)
        y = np.clip(np.round(pts[:, 1]).astype(int), 0, h - 1)

        new_pts = np.column_stack([
            pts[:, 0] + dx[y, x],
            pts[:, 1] + dy[y, x]
        ])

        new_contours.append(new_pts.tolist())

    return warped, new_contours


def shot_noise(image, strength):
    image = np.clip(image, 0.0, 1.0)

    photons = 1000.0 / max(strength, 1e-3)

    noisy = np.random.poisson(
        image * photons
    ).astype(np.float32) / photons

    return np.clip(noisy, 0.0, 1.0)


def detector_noise(image, sigma):
    noise = np.random.normal(
        0.0,
        sigma,
        image.shape
    ).astype(np.float32)

    return np.clip(image + noise, 0.0, 1.0)


def psf_blur(image, sigma):
    if sigma <= 0:
        return image

    return cv2.GaussianBlur(
        image,
        (0, 0),
        sigma
    )


def charging_effect(image, strength):
    h, w = image.shape

    low_freq = np.random.randn(
        max(2, h // 64),
        max(2, w // 64)
    ).astype(np.float32)

    low_freq = cv2.resize(
        low_freq,
        (w, h),
        interpolation=cv2.INTER_CUBIC
    )

    low_freq -= low_freq.mean()
    low_freq /= low_freq.std() + 1e-8

    effect = 1.0 + low_freq * strength

    return np.clip(image * effect, 0.0, 1.0)


def augment_sample(
    image,
    contours,
    level="medium",
    geometry=True
):
    image = image.astype(np.float32)
    contours = contours if contours is not None else []

    if level == "low":
        rotation = np.random.uniform(-1.0, 1.0)
        scale = np.random.uniform(0.95, 1.05)
        elastic_strength = 0.5
        shot = 0.15
        detector = 0.008
        blur = 0.5
        charge = 0.01

    elif level == "medium":
        rotation = np.random.uniform(-2.0, 2.0)
        scale = np.random.uniform(0.90, 1.10)
        elastic_strength = 1.5
        shot = 0.35
        detector = 0.015
        blur = 1.0
        charge = 0.025

    elif level == "high":
        rotation = np.random.uniform(-3.0, 3.0)
        scale = np.random.uniform(0.80, 1.20)
        elastic_strength = 3.0
        shot = 0.60
        detector = 0.025
        blur = 1.8
        charge = 0.05

    else:
        raise ValueError(
            "level must be low, medium or high"
        )

    if geometry:
        image, contours = geometry_transform(
            image,
            contours,
            rotation,
            scale
        )

        image, contours = elastic_warp(
            image,
            contours,
            elastic_strength
        )

    image = shot_noise(image, shot)
    image = detector_noise(image, detector)
    image = psf_blur(image, blur)
    image = charging_effect(image, charge)

    return np.clip(image, 0.0, 1.0), contours