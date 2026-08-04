"""Image I/O helpers (Pillow-based; Phase 5.3 library decision).

Supports 8/16-bit TIFF/PNG with lossless compression. Deterministic.
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image

_Path = Union[str, Path]


def save_tiff(data: np.ndarray, path: _Path) -> None:
    """Save uint8 or uint16 array as lossless (LZW) TIFF."""
    path = Path(path)
    if data.dtype not in (np.uint8, np.uint16):
        raise ValueError(f"save_tiff requires uint8/uint16, got {data.dtype}")
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(data).save(str(path), compression="tiff_lzw")


def load_tiff(path: _Path) -> np.ndarray:
    """Load TIFF -> uint8/uint16 numpy array."""
    path = Path(path)
    with Image.open(str(path)) as im:
        arr = np.asarray(im)
    return arr


def save_png(data: np.ndarray, path: _Path) -> None:
    """Save uint8 RGB or single-channel array as lossless PNG."""
    path = Path(path)
    if data.dtype not in (np.uint8, np.uint16):
        raise ValueError(f"save_png requires uint8/uint16, got {data.dtype}")
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(data).save(str(path), compress_level=6)
