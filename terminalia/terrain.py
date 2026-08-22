"""Terminalia terrain engine — agent-authored procedural heightfields.

Deterministic given seed + operator list. The agent composes operators;
this module executes them. Red-Blob-Games-style geomorphic ops.
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass

import numpy as np
from PIL import Image


@dataclass
class TerrainGrid:
    size: int  # grid resolution (square)
    meters_per_pixel: float
    seed: int

    def __post_init__(self):
        rng = np.random.default_rng(self.seed)
        self.height = np.zeros((self.size, self.size), dtype=np.float32)
        self._perm = rng.permutation(256)
        self.rng = rng

    # ---------- noise primitives ----------
    def _value_noise(self, freq: int) -> np.ndarray:
        rng = np.random.default_rng((self.seed + freq) % (2**32))
        grid = rng.random((freq, freq)).astype(np.float32)
        img = Image.fromarray((grid * 255).astype(np.uint8)).resize(
            (self.size, self.size), Image.BICUBIC)
        return np.asarray(img, dtype=np.float32) / 255.0

    def fbm(self, octaves: int = 6, base_freq: int = 4,
            persistence: float = 0.5) -> np.ndarray:
        out = np.zeros_like(self.height)
        amp, total = 1.0, 0.0
        freq = base_freq
        for _ in range(octaves):
            out += self._value_noise(freq) * amp
            total += amp
            amp *= persistence
            freq *= 2
        return out / max(total, 1e-6)

    def ridged(self, octaves: int = 5, base_freq: int = 3) -> np.ndarray:
        n = self.fbm(octaves, base_freq)
        return (1.0 - np.abs(n * 2 - 1)) ** 2

    # ---------- masks ----------
    def voronoi_regions(self, n_regions: int) -> list[np.ndarray]:
        pts = self.rng.random((n_regions, 2)) * self.size
        ys, xs = np.mgrid[0:self.size, 0:self.size]
        d = np.stack([((xs - px) ** 2 + (ys - py) ** 2) for px, py in pts])
        labels = d.argmin(axis=0)
        return [(labels == i).astype(np.float32) for i in range(n_regions)]

    def radial_mask(self, cx: float, cy: float, radius: float,
                    falloff: float = 2.5) -> np.ndarray:
        ys, xs = np.mgrid[0:self.size, 0:self.size]
        dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
        m = np.clip(1.0 - (dist / radius) ** falloff, 0, 1)
        return m.astype(np.float32)

    # ---------- geomorphic operators ----------
    def op_raise(self, mask: np.ndarray, height_m: float) -> None:
        self.height += mask * height_m

    def op_depress(self, mask: np.ndarray, depth_m: float) -> None:
        self.height -= mask * depth_m

    def op_mountains(self, mask: np.ndarray, height_m: float,
                     octaves: int = 5) -> None:
        self.height += mask * self.ridged(octaves) * height_m

    def op_carve_river(self, start: tuple[int, int], end: tuple[int, int],
                       width_px: int, meander: float = 40.0) -> None:
        x0, y0 = start
        x1, y1 = end
        steps = int(math.hypot(x1 - x0, y1 - y0)) + 1
        t = np.linspace(0, 1, steps)
        xs = x0 + (x1 - x0) * t + self.rng.normal(0, meander, steps).cumsum() * 0.05
        ys = y0 + (y1 - y0) * t + self.rng.normal(0, meander, steps).cumsum() * 0.05
        carve = np.zeros_like(self.height)
        for x, y in zip(xs.astype(int), ys.astype(int)):
            xi, yi = np.clip(x, 0, self.size-1), np.clip(y, 0, self.size-1)
            carve[yi, xi] = 1.0
        img = Image.fromarray((carve*255).astype(np.uint8))
        img = img.filter_image = img  # keep simple; blur below via resize trick
        big = img.resize((self.size//8, self.size//8), Image.BILINEAR).resize(
            (self.size, self.size), Image.BILINEAR)
        soft = np.asarray(big, dtype=np.float32)/255.0
        self.height -= soft * width_px * self.meters_per_pixel * 0.15

    def op_smooth_coast(self, sea_level_m: float, shelf_px: int = 24) -> None:
        below = self.height < sea_level_m
        self.height[below] = np.maximum(
            self.height[below], sea_level_m - shelf_px * self.meters_per_pixel)

    def op_terraces(self, mask: np.ndarray, step_m: float = 12.0) -> None:
        terraced = np.round(self.height / step_m) * step_m
        self.height = np.where(mask > 0.3, terraced, self.height)

    def normalize_to(self, min_m: float, max_m: float) -> None:
        lo, hi = self.height.min(), self.height.max()
        if hi - lo < 1e-6:
            return
        self.height = (self.height - lo) / (hi - lo) * (max_m - min_m) + min_m

    # ---------- io ----------
    def save_heightmap(self, path: str) -> str:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        lo, hi = self.height.min(), self.height.max()
        norm = ((self.height - lo) / max(hi - lo, 1e-6) * 65535).astype(np.uint16)
        Image.fromarray(norm).save(path)
        return path

    def save_mask(self, mask: np.ndarray, path: str) -> str:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        Image.fromarray((mask * 255).astype(np.uint8)).save(path)
        return path

    def sample_surface(self, x: float, y: float) -> float:
        """World-space height at continuous xy (pixel coords)."""
        xi = int(np.clip(round(x), 0, self.size - 1))
        yi = int(np.clip(round(y), 0, self.size - 1))
        return float(self.height[yi, xi])

    def surface_normal(self, x: float, y: float) -> tuple[float, float, float]:
        hL = self.sample_surface(max(x-1, 0), y)
        hR = self.sample_surface(min(x+1, self.size-1), y)
        hD = self.sample_surface(x, max(y-1, 0))
        hU = self.sample_surface(x, min(y+1, self.size-1))
        n = np.array([hL-hR, 2.0*self.meters_per_pixel, hD-hU])
        n /= np.linalg.norm(n)
        return tuple(float(v) for v in n)


def build_terrain(spec_ops: list[dict], size: int = 1024,
                  meters_per_pixel: float = 2.0, seed: int = 42) -> TerrainGrid:
    """Execute an operator program. Each op: {"op": name, ...params}.

    Supported ops: fbm, ridged_mountains, raise, depress, river,
    coast, terraces, radial_mask, voronoi, normalize.
    """
    g = TerrainGrid(size=size, meters_per_pixel=meters_per_pixel, seed=seed)
    masks: dict[str, np.ndarray] = {}
    last = np.ones((size, size), dtype=np.float32)

    for op in spec_ops:
        kind = op["op"]
        if kind == "voronoi":
            regions = g.voronoi_regions(op["n"])
            for i, m in enumerate(regions):
                masks[op.get("key", f"region{i}")] = m
            last = regions[-1]
        elif kind == "radial_mask":
            m = g.radial_mask(op["cx"], op["cy"], op["radius"], op.get("falloff", 2.5))
            key = op.get("key")
            if key:
                masks[key] = m
            last = m
        elif kind == "fbm":
            last = g.fbm(op.get("octaves", 6), op.get("base_freq", 4),
                         op.get("persistence", 0.5))
        elif kind == "raise":
            g.op_raise(masks.get(op.get("mask"), last), op["height_m"])
        elif kind == "mountains":
            g.op_mountains(masks.get(op.get("mask"), last), op["height_m"],
                           op.get("octaves", 5))
        elif kind == "depress":
            g.op_depress(masks.get(op.get("mask"), last), op["depth_m"])
        elif kind == "river":
            g.op_carve_river(op["start"], op["end"], op.get("width", 8))
        elif kind == "coast":
            g.op_smooth_coast(op["sea_level_m"], op.get("shelf", 24))
        elif kind == "terraces":
            g.op_terraces(masks.get(op.get("mask"), last), op.get("step", 12))
        elif kind == "normalize":
            g.normalize_to(op["min_m"], op["max_m"])
        else:
            raise ValueError(f"unknown terrain op: {kind}")
    return g
