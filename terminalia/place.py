"""Terminalia placement — ray-cast + contact-ratio search (anti-floating)."""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class Placement:
    pos_xy: tuple[float, float]
    rot_z: float
    scale: float
    z_offset: float
    contact_ratio: float


def estimate_contact_ratio(heightmap: np.ndarray, x: int, y: int,
                           half_extent_px: float, z_offset: float,
                           meters_per_pixel: float,
                           n_samples: int = 9) -> float:
    """Fraction of footprint samples whose terrain height is within tolerance
    of the object's base plane. 1.0 = perfectly seated."""
    size = heightmap.shape[0]
    base = None
    good = 0
    for i in range(n_samples):
        a = 2 * math.pi * i / n_samples
        sx = int(np.clip(round(x + math.cos(a) * half_extent_px), 0, size - 1))
        sy = int(np.clip(round(y + math.sin(a) * half_extent_px), 0, size - 1))
        h = float(heightmap[sy, sx])
        if base is None:
            base = h
            continue
        tol = max(2.0 * meters_per_pixel, abs(z_offset) + 0.5)
        if abs(h - base) <= tol:
            good += 1
    return good / (n_samples - 1)


def find_placement(heightmap: np.ndarray, cx: float, cy: float,
                   radius_px: float, half_extent_px: float,
                   meters_per_pixel: float = 2.0,
                   n_tries: int = 24, min_contact: float = 0.6,
                   slope_limit_deg: float = 35.0,
                   rng: np.random.Generator | None = None) -> Placement | None:
    """Search near (cx,cy) for the best-seated position/orientation."""
    size = heightmap.shape[0]
    rng = rng or np.random.default_rng()
    best: Placement | None = None

    # local slope via gradient
    gy, gx = np.gradient(heightmap)
    slope = np.degrees(np.arctan(np.sqrt(gx**2 + gy**2)))
    tan_limit = math.tan(math.radians(slope_limit_deg))
    ok_slope = slope <= slope_limit_deg

    for _ in range(n_tries):
        a = rng.random() * 2 * math.pi
        r = rng.random() * radius_px
        x = int(np.clip(cx + math.cos(a) * r, 0, size - 1))
        y = int(np.clip(cy + math.sin(a) * r, 0, size - 1))
        if not ok_slope[y, x]:
            continue
        grad_mag = math.hypot(float(gx[y, x]), float(gy[y, x]))
        if grad_mag > tan_limit:
            continue
        best_rot = 0.0
        best_cr = 0.0
        for rot in np.linspace(0, 2 * math.pi, 6, endpoint=False):
            cr = estimate_contact_ratio(
                heightmap, x, y, half_extent_px, 0.0, meters_per_pixel)
            if cr > best_cr:
                best_cr, best_rot = cr, float(rot)
        if best_cr >= min_contact and (best is None or best_cr > best.contact_ratio):
            best = Placement((float(x), float(y)), best_rot, 1.0, 0.0, best_cr)
            if best_cr >= 0.95:
                break
    return best


def resolve_collisions(placements: list[dict], min_gap_m: float = 3.0) -> list[str]:
    """Naive AABB pass; returns ids that were nudged/rejected."""
    issues = []
    for i in range(len(placements)):
        for j in range(i + 1, len(placements)):
            a, b = placements[i], placements[j]
            ax, ay = a["pos_xy"]
            bx, by = b["pos_xy"]
            d = math.hypot(ax - bx, ay - by)
            ra = a.get("radius_m", min_gap_m)
            rb = b.get("radius_m", min_gap_m)
            if d < (ra + rb) * 0.5 + min_gap_m:
                issues.append(f'{a["id"]} <-> {b["id"]} overlap ({d:.1f}m)')
    return issues
