"""Terminalia layout stage — POI selection + composition image.

Selects object sites from terrain (flat areas, region centers, coastlines) and
optionally generates a composition image via ComfyUI img-edit models
(Qwen-Image-Edit GGUF / Flux Kontext — both installed).
"""
from __future__ import annotations

import math

import numpy as np


def flat_area_score(heightmap: np.ndarray, window: int = 16) -> np.ndarray:
    """Per-pixel flatness score (lower local std = flatter)."""
    h, w = heightmap.shape
    integral = np.zeros((h + 1, w + 1))
    integral[1:, 1:] = np.cumsum(np.cumsum(heightmap, axis=0), axis=1)
    k = window // 2

    def win_sum(y, x):
        y0, x0 = max(0, y - k), max(0, x - k)
        y1, x1 = min(h, y + k + 1), min(w, x + k + 1)
        return (integral[y1, x1] - integral[y0, x1]
                - integral[y1, x0] + integral[y0, x0])

    ys, xs = np.mgrid[0:h, 0:w]
    sums = win_sum(ys, xs) if False else None
    # vectorized box sum via slicing (simpler & fast enough for 1024²)
    cs = np.cumsum(np.cumsum(heightmap, axis=0), axis=1)
    cs = np.pad(cs, ((1, 0), (1, 0)))
    y0 = np.clip(ys - k, 0, h); y1 = np.clip(ys + k + 1, 0, h)
    x0 = np.clip(xs - k, 0, w); x1 = np.clip(xs + k + 1, 0, w)
    s = cs[y1, x1] - cs[y0, x1] - cs[y1, x0] + cs[y0, x0]
    n = (y1 - y0) * (x1 - x0)
    mean = s / np.maximum(n, 1)
    sq = np.cumsum(np.cumsum(heightmap ** 2, axis=0), axis=1)
    sq = np.pad(sq, ((1, 0), (1, 0)))
    ssq = (sq[y1, x1] - sq[y0, x1] - sq[y1, x0] + sq[y0, x0]) / np.maximum(n, 1)
    var = np.maximum(ssq - mean ** 2, 0)
    return 1.0 / (1.0 + np.sqrt(var))


def select_sites(heightmap: np.ndarray, region_masks: dict[str, np.ndarray],
                 objects_per_region: dict[str, list[dict]],
                 meters_per_pixel: float = 2.0,
                 min_separation_px: float = 30.0,
                 seed: int = 42) -> list[dict]:
    """Pick non-overlapping sites per region honoring per-object constraints."""
    rng = np.random.default_rng(seed)
    flat = flat_area_score(heightmap)
    chosen: list[dict] = []

    def far_enough(x, y, min_d):
        return all(math.hypot(x - c["px"], y - c["py"]) >= min_d for c in chosen)

    for region_name, objs in objects_per_region.items():
        mask = region_masks.get(region_name)
        if mask is None:
            continue
        region_flat = flat * (mask > 0.5)
        order = np.argsort(region_flat.ravel())[::-1]  # flattest first
        for obj in objs:
            placed = False
            for idx in order:
                py, px = divmod(int(idx), heightmap.shape[1])
                if region_flat[py, px] <= 0:
                    break
                if not far_enough(px, py, min_separation_px):
                    continue
                half_extent = obj.get("half_extent_px", 6)
                cr_samples = []
                for a in range(8):
                    ang = 2 * math.pi * a / 8
                    sx = int(np.clip(px + math.cos(ang) * half_extent, 0, heightmap.shape[1]-1))
                    sy = int(np.clip(py + math.sin(ang) * half_extent, 0, heightmap.shape[0]-1))
                    cr_samples.append(float(heightmap[sy, sx]))
                base = cr_samples[0]
                contact = sum(1 for v in cr_samples[1:]
                              if abs(v - base) <= 2.0 * meters_per_pixel) / (len(cr_samples)-1)
                if contact < obj.get("min_contact", 0.55):
                    continue
                chosen.append({"id": obj["id"], "px": px, "py": py,
                               "z": float(heightmap[py, px]),
                               "contact": contact, "region": region_name})
                placed = True
                break
            if not placed:
                chosen.append({"id": obj["id"], "px": -1, "py": -1, "z": 0.0,
                               "contact": 0.0, "region": region_name,
                               "unplaced": True})
    return chosen
